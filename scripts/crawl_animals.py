"""
水族館公式サイトをクロールして生き物フラグをCSVに追加するスクリプト。
Usage: python scripts/crawl_animals.py
"""
import csv
import time
import re
import sys
import io
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# Windows コンソール UTF-8 対応
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

INPUT_CSV  = Path(__file__).parent.parent / "aquariums_with_latlng.csv"
OUTPUT_CSV = Path(__file__).parent.parent / "aquariums_with_animals.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept-Language": "ja,en;q=0.9",
}
TIMEOUT = 10

# 動物ごとのキーワード（正規表現）
ANIMAL_PATTERNS = {
    "has_penguin":  re.compile(r"ペンギン", re.IGNORECASE),
    "has_dolphin":  re.compile(r"イルカ|バンドウ|ミナミバンドウ|ハンドウ|ハナゴンドウ", re.IGNORECASE),
    "has_sealion":  re.compile(r"アシカ|カリフォルニアアシカ|オタリア", re.IGNORECASE),
    "has_orca":     re.compile(r"シャチ", re.IGNORECASE),
    "has_jellyfish":re.compile(r"クラゲ", re.IGNORECASE),
    "has_steller":  re.compile(r"トド|ステラーアシカ", re.IGNORECASE),
    "has_seal":     re.compile(r"アザラシ|ゴマフアザラシ|ワモンアザラシ|ゼニガタアザラシ", re.IGNORECASE),
    "has_shark":    re.compile(r"サメ|ジンベエ|ネコザメ|シュモクザメ|トラフザメ|オオセ|シロワニ", re.IGNORECASE),
    "has_beluga":   re.compile(r"シロイルカ|ベルーガ", re.IGNORECASE),
}

ANIMAL_COLS = list(ANIMAL_PATTERNS.keys())


def fetch_text(url: str) -> str:
    """URLのページ本文テキストを返す。失敗時は空文字。"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        # script/style 削除
        for tag in soup(["script", "style"]):
            tag.decompose()
        return soup.get_text(" ", strip=True)
    except Exception as e:
        return ""


def detect_animals(text: str) -> dict:
    return {key: (1 if pat.search(text) else 0) for key, pat in ANIMAL_PATTERNS.items()}


def main():
    rows = []
    with open(INPUT_CSV, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        orig_fields = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    total = len(rows)
    print(f"合計 {total} 館をクロールします\n")

    results = []
    for i, row in enumerate(rows, 1):
        name = row["name"]
        url  = row.get("url", "").strip()
        print(f"[{i:3}/{total}] {name}")

        if url:
            text = fetch_text(url)
            flags = detect_animals(text)
            status = " / ".join(k.replace("has_","") for k,v in flags.items() if v) or "なし"
            print(f"         → {status}")
        else:
            flags = {k: 0 for k in ANIMAL_COLS}
            print(f"         → URL なし、スキップ")

        results.append({**row, **flags})
        time.sleep(0.5)  # 連続アクセス抑制

    # 出力
    out_fields = orig_fields + [c for c in ANIMAL_COLS if c not in orig_fields]
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ 保存完了: {OUTPUT_CSV}")

    # サマリ
    print("\n--- 動物別ヒット数 ---")
    for col in ANIMAL_COLS:
        cnt = sum(1 for r in results if str(r.get(col,"")) == "1")
        print(f"  {col:20s}: {cnt} 館")


if __name__ == "__main__":
    main()
