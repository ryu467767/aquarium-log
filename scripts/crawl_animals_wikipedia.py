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
HEADERS = {"User-Agent": "aquarium-log/1.0 (animal data check)"}
TIMEOUT = 15

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


def wiki_extract(title: str) -> str:
    """記事本文のプレーンテキストを返す。見つからなければ空文字。"""
    try:
        # まず検索してタイトルを確定する
        r = requests.get(API, headers=HEADERS, timeout=TIMEOUT, params={
            "action": "query", "list": "search", "srsearch": title,
            "srlimit": 1, "format": "json",
        })
        hits = r.json().get("query", {}).get("search", [])
        if not hits:
            return ""
        page_title = hits[0]["title"]

        # 水族館・動物園の記事以外を拾わないよう、館名との関連を軽く確認
        core = re.sub(r"[（(].*?[)）]|水族館|博物館|公園|科学館|センター|ミュージアム|\s", "", title)
        if core and core[:3] not in page_title and page_title[:3] not in title:
            return ""

        r2 = requests.get(API, headers=HEADERS, timeout=TIMEOUT, params={
            "action": "query", "prop": "extracts", "titles": page_title,
            "explaintext": 1, "format": "json",
        })
        pages = r2.json().get("query", {}).get("pages", {})
        for p in pages.values():
            return p.get("extract", "") or ""
    except Exception:
        return ""
    return ""


def main():
    data = json.loads(RESULT.read_text(encoding="utf-8"))
    empties = [n for n, f in data.items() if not any(f.values())]
    print(f"公式サイトでヒット0だった {len(empties)} 館を Wikipedia で確認します\n", flush=True)

    filled = 0
    for i, name in enumerate(empties, 1):
        text = wiki_extract(name)
        if not text:
            print(f"[{i:3}/{len(empties)}] {name} -> 記事なし", flush=True)
            time.sleep(0.3)
            continue

        flags = {k: (1 if p.search(text) else 0) for k, p in ANIMAL_PATTERNS.items()}
        if any(flags.values()):
            data[name] = flags
            filled += 1
            hit = " / ".join(k.replace("has_", "") for k, v in flags.items() if v)
            print(f"[{i:3}/{len(empties)}] {name} -> {hit}", flush=True)
        else:
            print(f"[{i:3}/{len(empties)}] {name} -> なし", flush=True)
        time.sleep(0.3)

    RESULT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{filled} 館を補完しました -> {RESULT}", flush=True)


if __name__ == "__main__":
    main()
