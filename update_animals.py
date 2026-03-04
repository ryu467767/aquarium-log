"""
update_animals.py
=================
aquariums_list.csv の生き物フラグ列を app.db に反映する。

使い方:
  python update_animals.py
"""

import csv
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
SRC_CSV = BASE / "aquariums_list.csv"
_render_db = Path("/data/app.db")
DB_PATH = _render_db if _render_db.exists() else BASE / "data" / "app.db"

ANIMAL_COLS = ["has_penguin", "has_dolphin", "has_sealion", "has_orca", "has_jellyfish"]


def to_bool(val: str) -> int:
    return 1 if str(val).strip().lower() in ("true", "1", "yes") else 0


def main():
    print(f"ソースCSV: {SRC_CSV}")
    print(f"DB       : {DB_PATH}")
    print()

    if not SRC_CSV.exists():
        print(f"[ERROR] CSVが見つかりません: {SRC_CSV}")
        return

    if not DB_PATH.exists():
        print(f"[ERROR] DBが見つかりません: {DB_PATH}")
        print("  → Render から app.db をダウンロードして data/ フォルダに置いてください")
        return

    # CSV 読み込み
    rows = []
    with open(SRC_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue
            rows.append(row)

    print(f"CSV: {len(rows)} 件読み込み")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # DB にある列を確認（列がなければ add_animal_columns.py を先に実行するよう促す）
    cur.execute("PRAGMA table_info(aquariums)")
    existing_cols = {r[1] for r in cur.fetchall()}
    missing = [c for c in ANIMAL_COLS if c not in existing_cols]
    if missing:
        print(f"[ERROR] DB に列がありません: {missing}")
        print("  → 先に python add_animal_columns.py を実行してください")
        con.close()
        return

    updated = 0
    not_found = []

    for row in rows:
        name = row["name"].strip()
        vals = {col: to_bool(row.get(col, "")) for col in ANIMAL_COLS}

        cur.execute(
            f"""UPDATE aquariums SET
                has_penguin=?, has_dolphin=?, has_sealion=?, has_orca=?, has_jellyfish=?
                WHERE name=?""",
            (vals["has_penguin"], vals["has_dolphin"], vals["has_sealion"],
             vals["has_orca"], vals["has_jellyfish"], name)
        )
        if cur.rowcount > 0:
            updated += 1
        else:
            not_found.append(name)

    con.commit()
    con.close()

    print(f"\n[DB] 更新完了: {updated} / {len(rows)} 件")
    if not_found:
        print(f"[DB] DBに存在しない名前 ({len(not_found)} 件):")
        for n in not_found:
            print(f"  - {n}")

    print("\n完了！")


if __name__ == "__main__":
    main()
