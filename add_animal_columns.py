"""
add_animal_columns.py
=====================
aquariums テーブルに生き物フラグ列を追加するマイグレーションスクリプト。
すでに列が存在する場合はスキップするので何度実行しても安全。

使い方:
  python add_animal_columns.py
"""

import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
_render_db = Path("/data/app.db")
DB_PATH = _render_db if _render_db.exists() else BASE / "data" / "app.db"

COLUMNS = [
    ("has_penguin",  "INTEGER NOT NULL DEFAULT 0"),
    ("has_dolphin",  "INTEGER NOT NULL DEFAULT 0"),
    ("has_sealion",  "INTEGER NOT NULL DEFAULT 0"),
    ("has_orca",     "INTEGER NOT NULL DEFAULT 0"),
    ("has_jellyfish","INTEGER NOT NULL DEFAULT 0"),
]


def main():
    if not DB_PATH.exists():
        print(f"[ERROR] DBが見つかりません: {DB_PATH}")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # 既存列を取得
    cur.execute("PRAGMA table_info(aquariums)")
    existing = {row[1] for row in cur.fetchall()}

    added = 0
    for col, typedef in COLUMNS:
        if col in existing:
            print(f"  [SKIP] {col} は既に存在")
        else:
            cur.execute(f"ALTER TABLE aquariums ADD COLUMN {col} {typedef}")
            print(f"  [ADD]  {col}")
            added += 1

    con.commit()
    con.close()
    print(f"\n完了: {added} 列追加しました（DB: {DB_PATH}）")


if __name__ == "__main__":
    main()
