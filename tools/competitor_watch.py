#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競合アプリ（App Store）の仕様更新ウォッチャー。

iTunes Lookup API で各アプリの version / releaseNotes / 更新日を取得し、
前回スナップショット（competitor_snapshot.json）と比較。変化があれば
Claude API で「自社アプリへの示唆」を分析し、メール本文(report.html)を生成する。

外部依存なし（標準ライブラリのurllibのみ）。GitHub Actions から実行する想定。

出力:
- competitor_snapshot.json を最新状態に更新（ベースライン作成も含む）
- 変化があれば report.html を生成
- GITHUB_OUTPUT に changed=true/false, subject=... を書き出す
"""
import os
import sys
import json
import html
import urllib.request
import urllib.parse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "competitors.json")
SNAPSHOT_PATH = os.path.join(HERE, "competitor_snapshot.json")
REPORT_PATH = os.path.join(os.getcwd(), "report.html")

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()


def fetch_app(app_id: str) -> dict:
    """iTunes Lookup API で1アプリの情報を取得する。"""
    qs = urllib.parse.urlencode({"id": app_id, "country": "jp"})
    url = f"https://itunes.apple.com/lookup?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "aquarium-log-competitor-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode("utf-8"))
    results = data.get("results") or []
    if not results:
        return {"found": False}
    r = results[0]
    return {
        "found": True,
        "name": r.get("trackName", ""),
        "version": r.get("version", ""),
        "releaseDate": r.get("currentVersionReleaseDate", ""),
        "releaseNotes": (r.get("releaseNotes") or "").strip(),
        "seller": r.get("sellerName", ""),
        "url": r.get("trackViewUrl", ""),
        # 「具体的な変化のヒント」用：説明文とスクリーンショット
        "description": (r.get("description") or "").strip(),
        "screenshots": list(r.get("screenshotUrls") or []) + list(r.get("ipadScreenshotUrls") or []),
    }


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def diff_app(prev: dict, cur: dict) -> list:
    """1アプリの変化点を文字列リストで返す。空なら変化なし。"""
    if not cur.get("found"):
        return []
    if prev is None:
        return []  # 初回はベースライン扱い（変化として報告しない）
    changes = []
    if prev.get("version") != cur.get("version"):
        changes.append(f"バージョン: {prev.get('version','?')} → {cur.get('version','?')}")
    if prev.get("releaseNotes") != cur.get("releaseNotes"):
        changes.append("リリースノート（更新内容）が変わりました")
    if prev.get("releaseDate") != cur.get("releaseDate"):
        changes.append(f"更新日: {prev.get('releaseDate','?')} → {cur.get('releaseDate','?')}")
    # 説明文/スクショは「prevに項目がある時だけ」比較（旧スナップショットでの誤検知を防ぐ）
    if "description" in prev and prev.get("description") != cur.get("description"):
        changes.append("アプリ説明文が変わりました")
    if "screenshots" in prev and prev.get("screenshots") != cur.get("screenshots"):
        pc, cc = len(prev.get("screenshots") or []), len(cur.get("screenshots") or [])
        changes.append(f"スクリーンショットが変わりました（{pc}枚→{cc}枚）")
    return changes


def description_diff(prev_desc: str, cur_desc: str, max_lines: int = 40) -> str:
    """説明文の行単位の差分（+追加 / -削除）を返す。変化なしor比較不能なら空文字。"""
    import difflib
    if (prev_desc or "") == (cur_desc or ""):
        return ""
    diff = difflib.unified_diff(
        (prev_desc or "").splitlines(), (cur_desc or "").splitlines(), lineterm="", n=1
    )
    body = [d for d in diff if d[:3] not in ("---", "+++") and not d.startswith("@@")]
    body = [d for d in body if d.strip() not in ("+", "-")]  # 空行の追加/削除は省く
    if not body:
        return ""
    if len(body) > max_lines:
        body = body[:max_lines] + ["…(以下省略)"]
    return "\n".join(body)


def screenshot_diff(prev_list, cur_list) -> dict:
    """スクリーンショットの増減と新規URLを返す。"""
    prev_set = set(prev_list or [])
    added = [u for u in (cur_list or []) if u not in prev_set]
    cur_set = set(cur_list or [])
    removed = len([u for u in (prev_list or []) if u not in cur_set])
    return {
        "prev_count": len(prev_list or []),
        "cur_count": len(cur_list or []),
        "added": added,
        "removed_count": removed,
    }


def call_claude(your_app: dict, changed_items: list) -> str:
    """変化点をもとに、自社アプリへの示唆をClaudeに分析させる。失敗時は空文字。"""
    if not ANTHROPIC_API_KEY:
        return ""
    lines = []
    for it in changed_items:
        cur = it["cur"]
        block = (
            f"## {it['label']}\n"
            f"- バージョン: {it.get('prev_version','?')} → {cur.get('version','?')}\n"
            f"- 更新日: {cur.get('releaseDate','')}\n"
            f"- 更新内容(リリースノート原文):\n{cur.get('releaseNotes','(なし)')}\n"
        )
        if it.get("desc_diff"):
            block += f"- アプリ説明文の変更差分(+追加/-削除):\n{it['desc_diff']}\n"
        ss = it.get("ss_info")
        if ss and (ss["added"] or ss["prev_count"] != ss["cur_count"]):
            block += (f"- スクリーンショット: {ss['prev_count']}枚→{ss['cur_count']}枚"
                      f"（新規{len(ss['added'])}枚）\n")
        lines.append(block)
    competitor_block = "\n".join(lines)
    user_msg = (
        f"私たちのアプリ:\n名称: {your_app.get('name')}\n概要: {your_app.get('summary')}\n\n"
        f"以下は競合アプリ（App Store）の今週の更新です。\n\n{competitor_block}\n\n"
        "各更新について、次の構成で日本語でまとめてください。\n"
        "1. 【事実】リリースノート・説明文差分・スクショ変化から確実に言えること。\n"
        "2. 【推測】上記から推測される具体的な変更内容（あくまで推測と明示。"
        "リリースノートが曖昧な場合は『公開情報からは詳細不明』と正直に書く）。\n"
        "3. 【自社への示唆】追随・対抗を検討すべき点を優先度（高/中/低）付きで。\n"
        "最後に全体の所感を2〜3行。Markdownの見出しと箇条書きで読みやすく。"
        "事実と推測は必ず分け、根拠のない断定はしないこと。"
    )
    body = json.dumps({
        "model": CLAUDE_MODEL,
        "max_tokens": 1500,
        "system": "あなたは競合分析を支援するアシスタントです。事実に忠実に、簡潔で実用的な日本語で答えます。",
        "messages": [{"role": "user", "content": user_msg}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            data = json.loads(res.read().decode("utf-8"))
        parts = data.get("content") or []
        return "".join(p.get("text", "") for p in parts if p.get("type") == "text").strip()
    except Exception as e:
        sys.stderr.write(f"[warn] Claude analysis failed: {e}\n")
        return ""


def md_to_html(text: str) -> str:
    """ごく簡易なMarkdown→HTML（見出し・箇条書き・改行のみ）。"""
    out = []
    for raw in text.split("\n"):
        line = html.escape(raw.rstrip())
        if line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            out.append(f"<h2>{line[2:]}</h2>")
        elif line.startswith("- ") or line.startswith("* "):
            out.append(f"<li>{line[2:]}</li>")
        elif line.strip() == "":
            out.append("<br>")
        else:
            out.append(f"<p>{line}</p>")
    # 連続する<li>を<ul>で囲む簡易処理
    htmlout, in_ul = [], False
    for el in out:
        if el.startswith("<li>"):
            if not in_ul:
                htmlout.append("<ul>"); in_ul = True
            htmlout.append(el)
        else:
            if in_ul:
                htmlout.append("</ul>"); in_ul = False
            htmlout.append(el)
    if in_ul:
        htmlout.append("</ul>")
    return "\n".join(htmlout)


def build_report_html(changed_items: list, analysis: str) -> str:
    rows = []
    for it in changed_items:
        cur = it["cur"]
        notes = html.escape(cur.get("releaseNotes", "")).replace("\n", "<br>")
        extra = ""
        # 説明文の差分
        if it.get("desc_diff"):
            dd = []
            for ln in it["desc_diff"].split("\n"):
                color = "#1a7f37" if ln.startswith("+") else ("#cf222e" if ln.startswith("-") else "#57606a")
                dd.append(f"<span style='color:{color};'>{html.escape(ln)}</span>")
            extra += (
                "<p style='margin:10px 0 2px;'><b>アプリ説明文の変更:</b></p>"
                "<div style='background:#f6f8fa;padding:10px;border-radius:6px;font-size:13px;"
                "white-space:pre-wrap;font-family:monospace;'>" + "<br>".join(dd) + "</div>"
            )
        # スクリーンショットの変化
        ss = it.get("ss_info")
        if ss and (ss["added"] or ss["prev_count"] != ss["cur_count"]):
            thumbs = "".join(
                f"<a href='{html.escape(u)}'><img src='{html.escape(u)}' "
                f"style='height:160px;margin:4px;border:1px solid #ccc;border-radius:6px;'></a>"
                for u in ss["added"][:6]
            )
            extra += (
                f"<p style='margin:10px 0 2px;'><b>スクリーンショット:</b> "
                f"{ss['prev_count']}枚 → {ss['cur_count']}枚（新規{len(ss['added'])}枚）</p>"
                f"<div>{thumbs}</div>"
            )
        rows.append(
            f"<div style='margin:0 0 20px;padding:14px;border:1px solid #ddd;border-radius:8px;'>"
            f"<h3 style='margin:0 0 6px;color:#0077b6;'>"
            f"<a href='{html.escape(cur.get('url',''))}' style='color:#0077b6;text-decoration:none;'>{html.escape(it['label'])}</a></h3>"
            f"<p style='margin:2px 0;'><b>バージョン:</b> {html.escape(str(it.get('prev_version','?')))} → "
            f"<b>{html.escape(str(cur.get('version','?')))}</b></p>"
            f"<p style='margin:2px 0;'><b>更新日:</b> {html.escape(cur.get('releaseDate',''))}</p>"
            f"<p style='margin:8px 0 2px;'><b>更新内容（リリースノート原文）:</b></p>"
            f"<div style='background:#f6f8fa;padding:10px;border-radius:6px;font-size:14px;'>{notes}</div>"
            f"{extra}"
            f"</div>"
        )
    analysis_html = md_to_html(analysis) if analysis else "<p>（Claudeによる分析は未生成です。ANTHROPIC_API_KEY未設定か生成失敗。）</p>"
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    return (
        "<html><body style='font-family:sans-serif;line-height:1.7;color:#222;max-width:680px;margin:auto;'>"
        f"<h1 style='color:#003d5c;'>🐠 競合アプリ 更新レポート</h1>"
        f"<p style='opacity:.7;font-size:13px;'>生成日時: {now} / 対象: {len(changed_items)}件の更新を検知</p>"
        "<h2 style='border-bottom:2px solid #0077b6;padding-bottom:4px;'>検知した更新</h2>"
        + "".join(rows) +
        "<h2 style='border-bottom:2px solid #0077b6;padding-bottom:4px;'>🤖 Claudeの分析（自社への示唆）</h2>"
        + analysis_html +
        "<hr><p style='font-size:12px;opacity:.6;'>このメールは GitHub Actions の競合ウォッチャーが自動送信しています。</p>"
        "</body></html>"
    )


def write_output(key: str, value: str):
    gh = os.getenv("GITHUB_OUTPUT")
    if gh:
        with open(gh, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    else:
        print(f"[output] {key}={value}")


def main():
    config = load_json(CONFIG_PATH)
    your_app = config.get("your_app", {})
    competitors = config.get("competitors", [])

    prev_snapshot = load_json(SNAPSHOT_PATH) or {}
    prev_apps = prev_snapshot.get("apps", {}) if isinstance(prev_snapshot, dict) else {}
    is_first_run = not prev_apps

    cur_apps = {}
    changed_items = []
    for c in competitors:
        app_id, label = c["id"], c["label"]
        try:
            cur = fetch_app(app_id)
        except Exception as e:
            sys.stderr.write(f"[warn] fetch failed for {label} ({app_id}): {e}\n")
            # 取得失敗時は前回値を引き継いで誤検知を防ぐ
            cur = prev_apps.get(app_id, {"found": False})
        cur_apps[app_id] = cur
        prev = prev_apps.get(app_id)
        changes = diff_app(prev, cur)
        if changes:
            prev_for = prev or {}
            # 説明文・スクショの差分（prevに項目がある時だけ＝誤検知防止）
            desc_diff = (description_diff(prev_for.get("description", ""), cur.get("description", ""))
                         if "description" in prev_for else "")
            ss_info = (screenshot_diff(prev_for.get("screenshots"), cur.get("screenshots") or [])
                       if "screenshots" in prev_for else None)
            changed_items.append({
                "id": app_id,
                "label": label,
                "prev_version": prev_for.get("version", "?"),
                "cur": cur,
                "changes": changes,
                "desc_diff": desc_diff,
                "ss_info": ss_info,
            })

    # スナップショットは常に最新化（初回ベースライン含む）
    new_snapshot = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "apps": cur_apps,
    }
    save_json(SNAPSHOT_PATH, new_snapshot)

    if is_first_run:
        sys.stderr.write("[info] first run: baseline snapshot created, no email.\n")
        write_output("changed", "false")
        return

    if not changed_items:
        sys.stderr.write("[info] no competitor changes this week.\n")
        write_output("changed", "false")
        return

    analysis = call_claude(your_app, changed_items)
    report = build_report_html(changed_items, analysis)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    labels = "、".join(it["label"] for it in changed_items)
    subject = f"[競合ウォッチ] {len(changed_items)}件の更新を検知: {labels}"
    # subjectが長すぎる場合は丸める
    if len(subject) > 120:
        subject = subject[:117] + "..."
    write_output("changed", "true")
    write_output("subject", subject)
    sys.stderr.write(f"[info] changes detected: {labels}\n")


if __name__ == "__main__":
    main()
