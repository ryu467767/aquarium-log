"""
水族館座標補完スクリプト
- 座標なしの行について:
  1. Nominatim（OSM）で館名＋都道府県を検索
  2. 見つからなければ各サイトをスクレイピングして住所を取得 → Nominatim
  3. それでも無ければ手動確認リストに追加
- 結果を aquariums_with_latlng.csv に書き戻す
"""

import csv
import time
import re
import sys
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Windowsターミナルのエンコードエラーを回避
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def safe_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        msg = " ".join(str(a) for a in args)
        print(msg.encode("ascii", errors="replace").decode("ascii"), **kwargs)

CSV_PATH = Path(__file__).parent / "aquariums_with_latlng.csv"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS_NOMINATIM = {"User-Agent": "aquarium-geocoder/1.0 (personal project)"}
HEADERS_SCRAPE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
}

# レート制限（Nominatim: 1req/sec, スクレイピング: 2sec間隔）
NOMINATIM_DELAY = 1.2
SCRAPE_DELAY = 2.0

# 住所を示すパターン
ADDRESS_PATTERNS = [
    r'〒\s*\d{3}[-－]\d{4}\s*[^\n<]{5,60}',
    r'(?:住所|所在地|アクセス)[^\n：:]*[：:]\s*([^\n<]{5,60})',
]


def nominatim_search(query: str) -> tuple[float, float] | None:
    """Nominatimで検索してlatとlngを返す。見つからなければNone。"""
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1, "countrycodes": "jp"},
            headers=HEADERS_NOMINATIM,
            timeout=10,
        )
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  [Nominatim error] {query}: {e}")
    return None


def scrape_address(url: str) -> str | None:
    """URLをスクレイピングして住所文字列を返す。見つからなければNone。"""
    try:
        resp = requests.get(url, headers=HEADERS_SCRAPE, timeout=12, allow_redirects=True)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        # script/style を除去
        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # Schema.org address を優先
        for tag in soup.find_all(attrs={"itemprop": "address"}):
            addr = tag.get_text(strip=True)
            if len(addr) > 5:
                return addr

        # 〒 パターン
        m = re.search(r'〒\s*\d{3}[-－]\d{4}\s*(.{5,60})', text)
        if m:
            return m.group(0).strip()

        # 住所ラベルパターン
        for pat in [
            r'住所[^\n：:\d]{0,5}[：:\s]\s*(.{5,60})',
            r'所在地[^\n：:\d]{0,5}[：:\s]\s*(.{5,60})',
        ]:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()

    except Exception as e:
        print(f"  [scrape error] {url}: {e}")
    return None


def geocode_row(row: dict) -> tuple[float, float] | None:
    """1行分の水族館の座標を取得する。"""
    name = row["name"]
    pref = row["prefecture"]
    city = row["city"]

    # --- Step 1: Nominatim (名前 + 都道府県) ---
    print(f"  [Nominatim] {name} {pref}")
    result = nominatim_search(f"{name} {pref}")
    time.sleep(NOMINATIM_DELAY)
    if result:
        return result

    # --- Step 2: Nominatim (名前のみ) ---
    result = nominatim_search(name)
    time.sleep(NOMINATIM_DELAY)
    if result:
        return result

    # --- Step 3: ウェブサイトから住所を取得 ---
    url = row.get("url", "").strip()
    if url:
        print(f"  [Scrape] {url}")
        address = scrape_address(url)
        time.sleep(SCRAPE_DELAY)
        if address:
            print(f"  [Found address] {address[:60]}")
            result = nominatim_search(address)
            time.sleep(NOMINATIM_DELAY)
            if result:
                return result

            # 住所が長すぎる場合は都道府県+市区町村部分だけ試す
            # (例: "〒123-4567 北海道小樽市xxxx 1-2-3" → "北海道小樽市")
            short = f"{pref}{city}"
            result = nominatim_search(short)
            time.sleep(NOMINATIM_DELAY)
            if result:
                return result

    # --- Step 4: 都道府県+市区町村で大まかな位置 (最終手段) ---
    print(f"  [Fallback] {pref}{city}")
    result = nominatim_search(f"{pref} {city}")
    time.sleep(NOMINATIM_DELAY)
    return result


def main():
    # CSV読み込み
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"合計 {len(rows)} 館読み込み")

    needs_geocode = [r for r in rows if not r.get("lat") or not r.get("lng")]
    print(f"座標なし: {len(needs_geocode)} 館\n")

    found = 0
    fallback = 0  # 市区町村フォールバック使用
    not_found = []

    for i, row in enumerate(rows):
        if row.get("lat") and row.get("lng"):
            continue  # 既にあればスキップ

        idx = needs_geocode.index(row) + 1
        print(f"[{idx}/{len(needs_geocode)}] {row['name']}")

        result = geocode_row(row)

        if result:
            lat, lng = result
            row["lat"] = str(lat)
            row["lng"] = str(lng)
            print(f"  → {lat}, {lng}")
            found += 1
        else:
            print(f"  → 取得失敗")
            not_found.append(row["name"])

    # CSV書き戻し
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n=== 完了 ===")
    print(f"取得成功: {found}/{len(needs_geocode)}")
    if not_found:
        print(f"取得失敗 ({len(not_found)} 館):")
        for name in not_found:
            print(f"  - {name}")

    print(f"\nCSV更新済み: {CSV_PATH}")


if __name__ == "__main__":
    main()
