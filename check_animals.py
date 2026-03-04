"""
check_animals.py
================
水族館の公式サイトをスクレイピングして、
各動物（ペンギン・イルカ・アシカ・シャチ・クラゲ）がいるかどうかを判定し
aquariums_list.csv に書き込む。

使い方:
  python check_animals.py           # 全館チェック（未チェック優先）
  python check_animals.py --force   # 既チェック済みも再実行

注意:
  - robots.txt を尊重する
  - サイト間に 2 秒の待機を入れる
  - URLがない館はスキップ
"""

import time
import re
import argparse
import pandas as pd
from datetime import date
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

CSV_PATH = "aquariums_list.csv"

# 動物ごとの判定キーワード
ANIMAL_PATTERNS = {
    "has_penguin": [
        r"ペンギン",
        r"\bPenguin\b",
        r"フンボルト", r"ジェンツー", r"キングペンギン", r"マゼラン", r"アデリー",
        r"コガタペンギン", r"イワトビ",
    ],
    "has_dolphin": [
        r"イルカ",
        r"ドルフィン",
        r"\bDolphin\b",
        r"バンドウイルカ", r"ハンドウイルカ", r"カマイルカ", r"スジイルカ",
    ],
    "has_sealion": [
        r"アシカ",
        r"オットセイ",
        r"アザラシ",
        r"\bSea\s*Lion\b",
        r"\bSeal\b",
        r"ゴマフアザラシ", r"ゼニガタアザラシ",
    ],
    "has_orca": [
        r"シャチ",
        r"\bOrca\b",
        r"\bKiller\s*Whale\b",
    ],
    "has_jellyfish": [
        r"クラゲ",
        r"くらげ",
        r"\bJellyfish\b",
        r"ミズクラゲ", r"タコクラゲ", r"エチゼンクラゲ",
    ],
}

UA = "AquariumLogBot/1.0 (+contact: aquarium-stamp-app)"
SLEEP_SEC = 2.0

_robot_cache = {}


def allowed_by_robots(url: str, user_agent: str) -> bool:
    try:
        p = urlparse(url)
        robots_url = f"{p.scheme}://{p.netloc}/robots.txt"
        rp = _robot_cache.get(robots_url)
        if rp is None:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            _robot_cache[robots_url] = rp
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True  # 読めない場合は許可扱い


def fetch_text(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text)


def detect_animals(text: str) -> dict:
    """テキストから各動物の有無を判定して {列名: "true"/"false"} を返す"""
    result = {}
    for col, patterns in ANIMAL_PATTERNS.items():
        found = any(re.search(pat, text, flags=re.IGNORECASE) for pat in patterns)
        result[col] = "true" if found else "false"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="既チェック済みも再実行")
    args = parser.parse_args()

    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype=str).fillna("")

    # 各列が無ければ追加
    all_cols = list(ANIMAL_PATTERNS.keys()) + ["animal_checked_at"]
    for c in all_cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].astype("string").fillna("")

    checked = 0
    skipped = 0

    for i, row in df.iterrows():
        name = str(row.get("name", "")).strip()
        url = str(row.get("url", "") or "").strip()

        if not url:
            print(f"[SKIP url] {name}")
            skipped += 1
            continue

        # --force なしの場合、既にチェック済みならスキップ
        if not args.force:
            already = str(row.get("animal_checked_at", "")).strip()
            if already:
                print(f"[SKIP done] {name}")
                skipped += 1
                continue

        if not allowed_by_robots(url, UA):
            print(f"[SKIP robots] {name} {url}")
            df.at[i, "animal_checked_at"] = str(date.today())
            for col in ANIMAL_PATTERNS:
                df.at[i, col] = "unknown"
            skipped += 1
            continue

        try:
            print(f"[CHECK] {name} -> {url}")
            text = fetch_text(url)
            results = detect_animals(text)
            for col, val in results.items():
                df.at[i, col] = val
            df.at[i, "animal_checked_at"] = str(date.today())

            found_animals = [k for k, v in results.items() if v == "true"]
            if found_animals:
                print(f"  → 検出: {', '.join(found_animals)}")
            else:
                print(f"  → 検出なし")

            checked += 1
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            df.at[i, "animal_checked_at"] = str(date.today())
            for col in ANIMAL_PATTERNS:
                df.at[i, col] = "unknown"

        time.sleep(SLEEP_SEC)

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print(f"\n完了: {checked} 館チェック, {skipped} 館スキップ")
    print("aquariums_list.csv を更新しました")


if __name__ == "__main__":
    main()
