"""
check_animals_toshitoshi.py
============================
https://toshitoshi.jp/aqua/ の各水族館ページをスクレイピングして
ペンギン・イルカ・アシカ・シャチ・クラゲの有無を判定し
aquariums_list.csv に書き込む。

toshitoshi.jp は92館収録で、個別ページに展示説明文がある。
公式サイトより精度が高い傾向がある。

使い方:
  python check_animals_toshitoshi.py            # 未チェック館のみ
  python check_animals_toshitoshi.py --force    # 全館再チェック
  python check_animals_toshitoshi.py --dry-run  # 実際には書かない（テスト用）
"""

import time
import re
import argparse
from difflib import SequenceMatcher
from datetime import date

import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://toshitoshi.jp"
INDEX_URL = "https://toshitoshi.jp/aqua/"
CSV_PATH = "aquariums_list.csv"
SLEEP_SEC = 1.5  # toshitoshi へのリクエスト間隔（秒）

UA = "AquariumLogBot/1.0 (+contact: aquarium-stamp-app)"

# check_animals.py と同じキーワード定義
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


def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": UA})
    return s


def fetch_index(sess: requests.Session) -> list[dict]:
    """
    toshitoshi.jp/aqua/ を取得し、全水族館の {name, url} リストを返す。
    リンクは 001.php のような相対パス形式。
    """
    r = sess.get(INDEX_URL, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    entries = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 001.php のような相対パスのリンクだけ対象（/aqua/ ベース）
        if re.match(r"^\d+\.php$", href):
            name_text = a.get_text(strip=True)
            # 画像リンクの場合は alt を使う
            if not name_text:
                img = a.find("img")
                name_text = img.get("alt", "").strip() if img else ""
            if name_text:
                entries.append({"name": name_text, "url": INDEX_URL + href})

    # 重複除去（同じhrefが複数ある場合）
    seen = set()
    unique = []
    for e in entries:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique.append(e)

    return unique


def fetch_page_name_and_text(sess: requests.Session, url: str) -> tuple[str, str]:
    """
    水族館個別ページを取得し (水族館名, 本文テキスト) を返す。
    名前は h3 タグ（toshitoshi の規則）から取得。
    """
    r = sess.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # 水族館名: h3 タグが最も確実
    name_tag = soup.find("h3")
    page_name = name_tag.get_text(strip=True) if name_tag else ""

    # 本文テキスト（script/style除外）
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)

    return page_name, text


def name_similarity(a: str, b: str) -> float:
    """2つの名前の類似度 0〜1 を返す（SequenceMatcher）"""
    return SequenceMatcher(None, a, b).ratio()


def find_best_match(our_name: str, toshi_entries: list[dict]) -> dict | None:
    """
    我々のCSVの水族館名に最も近い toshitoshi エントリを返す。
    類似度が 0.6 未満の場合は None を返す。
    """
    best = None
    best_score = 0.0

    for entry in toshi_entries:
        score = name_similarity(our_name, entry["name"])
        # 完全一致 or 一方が他方を含む場合はボーナス
        if our_name in entry["name"] or entry["name"] in our_name:
            score = max(score, 0.85)
        if score > best_score:
            best_score = score
            best = entry

    if best_score >= 0.6:
        return best
    return None


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
    parser.add_argument("--dry-run", action="store_true", help="CSVを書き込まずに結果だけ表示")
    args = parser.parse_args()

    sess = get_session()
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype=str).fillna("")

    # 必要な列を追加
    all_cols = list(ANIMAL_PATTERNS.keys()) + ["animal_checked_at"]
    for c in all_cols:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].astype("string").fillna("")

    # Step 1: toshitoshi インデックスを取得
    print("toshitoshi.jp インデックスを取得中...")
    toshi_entries = fetch_index(sess)
    print(f"  → {len(toshi_entries)} 館を発見")
    time.sleep(SLEEP_SEC)

    # Step 2: 各 toshitoshi ページを取得してキャッシュ
    # （各館のページ名→テキストを先にまとめて取得）
    print("\ntoshitoshi.jp 個別ページを取得中...")
    toshi_data = {}  # entry["url"] → {"page_name": str, "text": str}
    for entry in toshi_entries:
        try:
            page_name, text = fetch_page_name_and_text(sess, entry["url"])
            toshi_data[entry["url"]] = {
                "page_name": page_name or entry["name"],
                "text": text,
            }
            print(f"  [OK] {page_name or entry['name']}")
        except Exception as e:
            print(f"  [ERROR] {entry['url']}: {e}")
            toshi_data[entry["url"]] = None
        time.sleep(SLEEP_SEC)

    # toshitoshi エントリにページ名を反映（より正確な名前で再マッチング用）
    for entry in toshi_entries:
        data = toshi_data.get(entry["url"])
        if data:
            entry["page_name"] = data["page_name"]
        else:
            entry["page_name"] = entry["name"]

    # Step 3: CSV の各館をtoshitoshiにマッチングして動物判定
    print("\n--- CSVとのマッチング & 動物判定 ---")
    matched = 0
    updated = 0
    no_match = []

    for i, row in df.iterrows():
        our_name = str(row.get("name", "")).strip()

        # --force なしは既チェック済みスキップ
        if not args.force:
            already = str(row.get("animal_checked_at", "")).strip()
            if already:
                print(f"[SKIP done] {our_name}")
                continue

        # マッチング（index name と page_name 両方で試みる）
        # page_name ベースのエントリリストを作成
        page_entries = [
            {"name": e.get("page_name", e["name"]), "url": e["url"]}
            for e in toshi_entries
        ]
        match = find_best_match(our_name, page_entries)
        if match is None:
            # index name でも試みる
            match = find_best_match(our_name, toshi_entries)

        if match is None:
            no_match.append(our_name)
            print(f"[NO MATCH] {our_name}")
            continue

        data = toshi_data.get(match["url"])
        if data is None:
            print(f"[SKIP error] {our_name} (toshitoshi ページ取得失敗)")
            continue

        score = name_similarity(our_name, data["page_name"])
        print(f"[MATCH] {our_name} → {data['page_name']} (score={score:.2f})")

        results = detect_animals(data["text"])
        found = [k for k, v in results.items() if v == "true"]
        print(f"  → 検出: {', '.join(found) if found else 'なし'}")

        if not args.dry_run:
            for col, val in results.items():
                df.at[i, col] = val
            df.at[i, "animal_checked_at"] = str(date.today())

        matched += 1
        updated += 1

    # Step 4: 保存
    if not args.dry_run:
        df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
        print(f"\naquariums_list.csv を更新しました")

    print(f"\n===== 結果 =====")
    print(f"マッチ成功: {matched} 館")
    print(f"マッチなし: {len(no_match)} 館")
    if no_match:
        print("マッチなし一覧:")
        for n in no_match:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
