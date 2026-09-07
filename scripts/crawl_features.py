"""各水族館の「特徴」を、事実だけ構造化して集めるスクリプト。

紹介文に使う。文章そのものは引用せず、
- 開館年
- 展示している生き物の種類数
- 「日本最大級」などの位置づけ
- 愛称
といった事実だけを取り出して、表示側で自前の文を組み立てる。

出典は日本語版Wikipedia。静的HTMLで事実が書かれており、
公式サイトのようにJavaScriptで隠れていないため。

Usage:
  python scripts/crawl_features.py
"""
import io
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "localdata" / "app.db"
OUT_JSON = Path(__file__).parent / "features_result.json"

API = "https://ja.wikipedia.org/w/api.php"
# 連絡先の分かるUAでないと 429 で拒否される
HEADERS = {"User-Agent": "aquarium-log/1.0 (https://aquarium-log.onrender.com/)"}
TIMEOUT = 20


class WikiError(Exception):
    pass


def _api(params):
    for wait in [5, 15, 30, 0]:
        r = requests.get(API, headers=HEADERS, timeout=TIMEOUT, params=params)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429 and wait:
            print(f"        429… {wait}秒待って再試行", flush=True)
            time.sleep(wait)
            continue
        raise WikiError(f"HTTP {r.status_code}")
    raise WikiError("429 が続いたため中断")


def fetch_article(name: str):
    """(記事タイトル, 本文) を返す。無ければ (None, "")。"""
    hits = _api({"action": "query", "list": "search", "srsearch": name,
                 "srlimit": 1, "format": "json"}).get("query", {}).get("search", [])
    if not hits:
        return None, ""
    title = hits[0]["title"]

    pages = _api({"action": "query", "prop": "extracts", "titles": title,
                  "explaintext": 1, "format": "json"}).get("query", {}).get("pages", {})
    text = ""
    for p in pages.values():
        text = p.get("extract", "") or ""
        break
    if not text:
        return None, ""

    # 別施設の記事を掴んでいないか確認する
    core = re.sub(r"[（(].*?[)）]|水族館|博物館|公園|科学館|センター|ミュージアム|\s", "", name)
    ok = (not core) or core[:3] in title or title[:3] in name or core[:4] in text[:400]
    return (title, text) if ok else (None, "")


# 「かつて〜だった」の話を拾わないための目印
PAST = re.compile(r"かつて|以前は|閉館|旧館|廃止|移転前|であった|していた|された後")

OPEN_YEAR = re.compile(
    r"(\d{4})年(?:\d{1,2}月)?(?:\d{1,2}日)?に?(?:、)?(?:リニューアル)?(?:開館|開園|オープン|開設)")
SPECIES = re.compile(r"(?:約|およそ)?\s*([\d,]{1,6})\s*種(?:類)?(?:の(?:生(?:き|)物|魚|海洋生物|水生生物))?")
RANK = re.compile(
    r"(日本最大級|日本最大|国内最大級|国内最大|世界最大級|東洋一|日本初|国内初|世界初|"
    r"日本一|国内唯一|日本唯一|世界初公開)")

# 何に特化しているか（記事冒頭に出てくるものだけ拾う）
THEME = [
    ("クラゲ", r"クラゲの展示(?:種類数|数)?が(?:世界|日本|国内)|クラゲ展示|クラゲに特化|クラゲの水族館"),
    ("淡水魚", r"淡水魚(?:専門|に特化|のみを)|淡水生物専門"),
    ("サンゴ", r"サンゴに特化|サンゴ礁を再現|サンゴの展示"),
    ("ペンギン", r"ペンギンの(?:飼育|展示)(?:種類数|数)が|ペンギンに特化"),
    ("チョウザメ", r"チョウザメ"),
    ("サケ", r"サケ(?:の|に)(?:遡上|特化|専門)"),
    ("深海生物", r"深海(?:生物|魚)(?:に特化|を専門|の展示)"),
]


def first_sentences(text: str, n: int = 6) -> str:
    """記事の冒頭（定義文のあたり）だけを返す。事実の信頼度が高い。"""
    lead = text.split("\n")[0] if "\n" in text else text
    parts = re.split(r"(?<=。)", lead)
    return "".join(parts[:n])


def extract(name: str, text: str) -> dict:
    lead = first_sentences(text)
    out = {}

    # 開館年（冒頭に出てくる、過去形でない文から）
    for sent in re.split(r"(?<=。)", lead):
        if PAST.search(sent):
            continue
        m = OPEN_YEAR.search(sent)
        if m:
            y = int(m.group(1))
            if 1880 <= y <= 2026:
                out["open_year"] = y
                break

    # 展示種類数
    for sent in re.split(r"(?<=。)", lead):
        if PAST.search(sent):
            continue
        m = SPECIES.search(sent)
        if m:
            try:
                v = int(m.group(1).replace(",", ""))
            except ValueError:
                continue
            if 5 <= v <= 3000:
                out["species"] = v
                break

    # 位置づけ（日本最大級 など）
    m = RANK.search(lead)
    if m:
        out["rank"] = m.group(1)

    # 特化しているテーマ
    for label, pat in THEME:
        if re.search(pat, lead):
            out["theme"] = label
            break

    out["lead_chars"] = len(lead)
    return out


def main():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT name FROM aquariums ORDER BY id").fetchall()
    con.close()
    names = [r[0] for r in rows]

    print(f"{len(names)} 館を調べます\n", flush=True)
    result, failed = {}, []

    for i, name in enumerate(names, 1):
        try:
            title, text = fetch_article(name)
        except WikiError as e:
            failed.append(name)
            print(f"[{i:3}/{len(names)}] {name} -> 取得失敗（{e}）", flush=True)
            time.sleep(2)
            continue

        if not text:
            print(f"[{i:3}/{len(names)}] {name} -> 記事なし", flush=True)
            time.sleep(1)
            continue

        f = extract(name, text)
        f["wiki_title"] = title
        result[name] = f
        got = [f"{k}={v}" for k, v in f.items() if k in ("open_year", "species", "rank", "theme")]
        print(f"[{i:3}/{len(names)}] {name} -> {', '.join(got) if got else '事実なし'}", flush=True)
        time.sleep(1)

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n保存: {OUT_JSON}", flush=True)
    for key in ("open_year", "species", "rank", "theme"):
        print(f"  {key:10s}: {sum(1 for f in result.values() if key in f)} 館", flush=True)
    if failed:
        print(f"\n取得失敗: {len(failed)} 館", flush=True)


if __name__ == "__main__":
    main()
