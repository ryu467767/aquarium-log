import time
import re
import pandas as pd
from datetime import date
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

CSV_PATH = "aquariums_list.csv"

# ペンギン判定キーワード（必要なら増やせる）
PENGUIN_PATTERNS = [
    r"ペンギン",
    r"\bPenguin\b",
    r"フンボルト", r"ジェンツー", r"キングペンギン", r"マゼラン", r"アデリー",
]

UA = "AquariumLogBot/1.0 (+contact: you)"
SLEEP_SEC = 2.0  # 礼儀としてサイト間に待ち時間

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
        # robotsが読めない場合は「安全側」で許可しないのもアリだが、
        # ここでは運用しやすさ優先で許可扱いにしている（必要ならFalseに）
        return True

def fetch_text(url: str) -> str:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # 余計なもの除去
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text

def has_penguin(text: str) -> bool:
    for pat in PENGUIN_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False

def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig", dtype=str).fillna("")

    # ★追加：文字列列として扱う（float扱いになるのを防ぐ）
    for c in ["has_penguin", "penguin_source_url", "penguin_checked_at", "penguin_status"]:
        if c not in df.columns:
            df[c] = ""
    df[c] = df[c].astype("string").fillna("")

    # 対象：source_urlがある行だけ（まずはここから）
    for i, row in df.iterrows():
        src = str(row.get("penguin_source_url", "") or "").strip()
        if not src:
            continue

        # すでに true/false が入ってるならスキップしたい場合はここを有効化
        # cur = str(row.get("has_penguin", "")).strip().lower()
        # if cur in ("true", "false"):
        #     continue

        if not allowed_by_robots(src, UA):
            print(f"[SKIP robots] {row['name']} {src}")
            df.at[i, "has_penguin"] = "unknown"
            df.at[i, "penguin_status"] = "unknown"
            df.at[i, "penguin_checked_at"] = str(date.today())
            continue

        try:
            print(f"[CHECK] {row['name']} -> {src}")
            text = fetch_text(src)
            df.at[i, "has_penguin"] = "true" if has_penguin(text) else "unknown"
            df.at[i, "penguin_checked_at"] = str(date.today())
            if df.at[i, "penguin_status"] == "" or pd.isna(df.at[i, "penguin_status"]):
                df.at[i, "penguin_status"] = "unknown"
        except Exception as e:
            print(f"[ERROR] {row['name']} {e}")
            df.at[i, "has_penguin"] = "unknown"
            df.at[i, "penguin_checked_at"] = str(date.today())

        time.sleep(SLEEP_SEC)

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    print("完了：aquariums_list.csv を更新しました")

if __name__ == "__main__":
    main()