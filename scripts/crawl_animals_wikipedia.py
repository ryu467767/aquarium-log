"""公式サイトのクロールで何も取れなかった館を、日本語版Wikipediaで補完するスクリプト。

公式サイトが JavaScript でメニューを描く作りだと本文テキストが取れず、
海遊館などの大きな水族館でもヒット0になってしまう。
Wikipedia は静的HTMLで「主な展示生物」が書かれているので補完に使える。

scripts/animal_extra_result.json を読み、ヒット0の館だけ調べて同じファイルに書き戻す。

Usage:
  python scripts/crawl_animals_wikipedia.py
"""
import io
import json
import re
import sys
import time
from pathlib import Path

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

RESULT = Path(__file__).parent / "animal_extra_result.json"

API = "https://ja.wikipedia.org/w/api.php"
# Wikimedia は連絡先の分かる User-Agent を要求する。
# 曖昧なUAだと 429 を返されるので、サイトURLを必ず入れること。
HEADERS = {"User-Agent": "aquarium-log/1.0 (https://aquarium-log.onrender.com/)"}
TIMEOUT = 20

# crawl_animals_extra.py と同じパターン
ANIMAL_PATTERNS = {
    "has_otter":       re.compile(r"カワウソ|コツメカワウソ|ユーラシアカワウソ"),
    "has_seaotter":    re.compile(r"ラッコ"),
    "has_walrus":      re.compile(r"セイウチ"),
    "has_turtle":      re.compile(r"ウミガメ|アカウミガメ|アオウミガメ|タイマイ"),
    "has_whaleshark":  re.compile(r"ジンベエザメ|ジンベイザメ"),
    "has_ray":         re.compile(r"マンタ|アカエイ|イトマキエイ|ナンヨウマンタ|エイ類|エイ目"),
    "has_sunfish":     re.compile(r"マンボウ"),
    "has_gardeneel":   re.compile(r"チンアナゴ|ニシキアナゴ"),
    "has_seahorse":    re.compile(r"タツノオトシゴ|シードラゴン"),
    "has_clownfish":   re.compile(r"カクレクマノミ|クマノミ"),
    "has_coral":       re.compile(r"サンゴ|珊瑚"),
    "has_capybara":    re.compile(r"カピバラ"),
    "has_salamander":  re.compile(r"オオサンショウウオ|サンショウウオ"),
    "has_deepsea":     re.compile(r"深海生物|深海魚|ダイオウグソクムシ|オオグソクムシ|タカアシガニ"),
}
COLS = list(ANIMAL_PATTERNS.keys())


class WikiError(Exception):
    """通信・API側の失敗。『記事が無い』とは区別する。"""


def _api(params):
    """APIを叩く。429なら待って数回やり直す。失敗は例外にして黙って握りつぶさない。"""
    for attempt, wait in enumerate([5, 15, 30, 0]):
        r = requests.get(API, headers=HEADERS, timeout=TIMEOUT, params=params)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 429 and wait:
            print(f"        429（送りすぎ）… {wait}秒待って再試行", flush=True)
            time.sleep(wait)
            continue
        raise WikiError(f"HTTP {r.status_code}")
    raise WikiError("429 が続いたため中断")


def wiki_extract(title: str) -> str:
    """記事本文のプレーンテキストを返す。記事が無ければ空文字。通信失敗は例外。"""
    hits = _api({
        "action": "query", "list": "search", "srsearch": title,
        "srlimit": 1, "format": "json",
    }).get("query", {}).get("search", [])
    if not hits:
        return ""
    page_title = hits[0]["title"]

    # 水族館・動物園の記事以外を拾わないよう、館名との関連を軽く確認。
    # 記事名が英字表記のことがある（例: ニフレル -> NIFREL）ので、
    # 記事の冒頭に館名が出てくる場合も同じ施設とみなす。
    core = re.sub(r"[（(].*?[)）]|水族館|博物館|公園|科学館|センター|ミュージアム|\s", "", title)
    related = (not core) or core[:3] in page_title or page_title[:3] in title

    pages = _api({
        "action": "query", "prop": "extracts", "titles": page_title,
        "explaintext": 1, "format": "json",
    }).get("query", {}).get("pages", {})
    text = ""
    for p in pages.values():
        text = p.get("extract", "") or ""
        break
    if not text:
        return ""

    # 記事名が館名と違う場合は、本文の冒頭に館名が出てくるかで判断する
    if not related and core and core[:4] not in text[:400]:
        return ""
    return text


# 「かつて飼育していた」など、今はいない生き物の話を除くための目印
PAST_MARKER = re.compile(
    r"かつて|以前は|旧|閉館|死亡|亡くな|引退|譲渡|移送|搬出|until|展示を終了|飼育を終了|"
    r"していた|であった|だった|されていた"
)


def current_text(text: str) -> str:
    """過去の話をしている文を落として、今の展示に近い部分だけ返す。"""
    kept = []
    for sentence in re.split(r"(?<=[。\n])", text):
        if sentence.strip() and not PAST_MARKER.search(sentence):
            kept.append(sentence)
    return "".join(kept)


def main():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    empties = [n for n, f in data.items() if not any(f.values())]
    print(f"公式サイトでヒット0だった {len(empties)} 館を Wikipedia で確認します\n", flush=True)

    filled = 0
    failed = []
    for i, name in enumerate(empties, 1):
        try:
            text = wiki_extract(name)
        except WikiError as e:
            failed.append((name, str(e)))
            print(f"[{i:3}/{len(empties)}] {name} -> 取得失敗（{e}）", flush=True)
            time.sleep(2)
            continue

        if not text:
            print(f"[{i:3}/{len(empties)}] {name} -> 記事なし", flush=True)
            time.sleep(1)
            continue

        # 過去の飼育記録を拾わないよう、現在の話に絞ってから判定する
        flags = {k: (1 if p.search(current_text(text)) else 0)
                 for k, p in ANIMAL_PATTERNS.items()}
        if any(flags.values()):
            data[name] = flags
            filled += 1
            hit = " / ".join(k.replace("has_", "") for k, v in flags.items() if v)
            print(f"[{i:3}/{len(empties)}] {name} -> {hit}", flush=True)
        else:
            print(f"[{i:3}/{len(empties)}] {name} -> なし", flush=True)
        time.sleep(1)

    RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{filled} 館を補完しました -> {RESULT}", flush=True)
    if failed:
        print(f"\n取得に失敗した {len(failed)} 館（再実行が必要）:", flush=True)
        for n, e in failed:
            print(f"  - {n}（{e}）", flush=True)


if __name__ == "__main__":
    main()
