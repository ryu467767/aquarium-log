"""
水族館公式サイトをクロールして「追加の生き物フラグ」を調べるスクリプト。

crawl_animals.py の拡張版。
- トップページだけでなく「生き物 / 展示 / いきもの / zukan / animal」系の
  内部リンクも数ページ辿るので、検出率が上がる。
- 結果は scripts/animal_extra_result.json に保存する。
  そこから app/animal_seeds_extra.py（本番DBへ反映するSQL用データ）を生成する。

Usage:
  python scripts/crawl_animals_extra.py
"""
import io
import json
import re
import sqlite3
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "localdata" / "app.db"
OUT_JSON = Path(__file__).parent / "animal_extra_result.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}
TIMEOUT = 12
MAX_SUBPAGES = 4          # トップpage以外に辿る最大ページ数
SLEEP_SEC = 0.4           # 連続アクセス抑制

# 「生き物一覧」系ページへ辿るためのリンク判定
SUBPAGE_HINT = re.compile(
    r"生き物|生きもの|いきもの|展示|館内|figure|zukan|zukan|animal|creature|fish|exhibit|guide",
    re.IGNORECASE,
)

# 追加動物ごとのキーワード。
# 誤検出を減らすため、一般名詞になりやすい語は具体的な種名を優先している。
ANIMAL_PATTERNS = {
    "has_otter":       re.compile(r"カワウソ|コツメカワウソ|ユーラシアカワウソ"),
    "has_seaotter":    re.compile(r"ラッコ"),
    "has_walrus":      re.compile(r"セイウチ"),
    "has_turtle":      re.compile(r"ウミガメ|アカウミガメ|アオウミガメ|タイマイ"),
    "has_whaleshark":  re.compile(r"ジンベエザメ|ジンベイザメ"),
    "has_ray":         re.compile(r"エイ|マンタ|アカエイ|ナンヨウマンタ|イトマキエイ"),
    "has_sunfish":     re.compile(r"マンボウ"),
    "has_gardeneel":   re.compile(r"チンアナゴ|ニシキアナゴ"),
    "has_seahorse":    re.compile(r"タツノオトシゴ|シードラゴン"),
    "has_clownfish":   re.compile(r"カクレクマノミ|クマノミ"),
    "has_coral":       re.compile(r"サンゴ|珊瑚"),
    "has_capybara":    re.compile(r"カピバラ"),
    "has_salamander":  re.compile(r"オオサンショウウオ|サンショウウオ"),
    "has_deepsea":     re.compile(r"深海生物|深海魚|ダイオウグソクムシ|オオグソクムシ|タカアシガニ"),
}

ANIMAL_COLS = list(ANIMAL_PATTERNS.keys())

# 「エイ」は "エイリアン" 等に誤反応しやすいので、単独ヒットは除外する語
RAY_FALSE = re.compile(r"エイリアン|エイジ|エイド|ディスプレイ|プレイ|エイプ")


def fetch(url: str):
    """(text, soup) を返す。失敗時は ("", None)。"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        if r.status_code >= 400:
            return "", None
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(" ", strip=True), soup
    except Exception:
        return "", None


def pick_subpages(base_url: str, soup) -> list:
    """生き物一覧っぽい内部リンクを最大 MAX_SUBPAGES 件返す。"""
    if soup is None:
        return []
    host = urlparse(base_url).netloc
    found, seen = [], set()
    for a in soup.find_all("a", href=True):
        label = (a.get_text(" ", strip=True) or "") + " " + a["href"]
        if not SUBPAGE_HINT.search(label):
            continue
        full = urljoin(base_url, a["href"])
        if urlparse(full).netloc != host:
            continue
        full = full.split("#")[0]
        if full in seen or full.rstrip("/") == base_url.rstrip("/"):
            continue
        seen.add(full)
        found.append(full)
        if len(found) >= MAX_SUBPAGES:
            break
    return found


def detect(text: str) -> dict:
    out = {}
    for key, pat in ANIMAL_PATTERNS.items():
        hit = bool(pat.search(text))
        if hit and key == "has_ray":
            # 「エイ」単体ヒットの誤検出よけ：具体名が無ければ前後を確認
            if not re.search(r"マンタ|アカエイ|イトマキエイ|エイ類|ナンヨウマンタ", text):
                cleaned = RAY_FALSE.sub("", text)
                hit = bool(re.search(r"エイ", cleaned))
        out[key] = 1 if hit else 0
    return out


def load_targets():
    con = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT name, url FROM aquariums WHERE url IS NOT NULL AND url != '' ORDER BY id"
    ).fetchall()
    con.close()
    return rows


def main():
    targets = load_targets()
    total = len(targets)
    print(f"合計 {total} 館を調査します（各館 最大 {MAX_SUBPAGES + 1} ページ）\n", flush=True)

    results = {}
    for i, (name, url) in enumerate(targets, 1):
        text, soup = fetch(url)
        pages = 1 if text else 0
        if text:
            for sub in pick_subpages(url, soup):
                t2, _ = fetch(sub)
                if t2:
                    text += " " + t2
                    pages += 1
                time.sleep(SLEEP_SEC)

        flags = detect(text) if text else {k: 0 for k in ANIMAL_COLS}
        results[name] = flags
        hit = " / ".join(k.replace("has_", "") for k, v in flags.items() if v) or "なし"
        print(f"[{i:3}/{total}] {name} ({pages}p) -> {hit}", flush=True)
        time.sleep(SLEEP_SEC)

    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n保存: {OUT_JSON}", flush=True)

    print("\n--- 動物別ヒット数 ---", flush=True)
    for col in ANIMAL_COLS:
        cnt = sum(1 for v in results.values() if v.get(col))
        print(f"  {col:20s}: {cnt} 館", flush=True)


if __name__ == "__main__":
    main()
