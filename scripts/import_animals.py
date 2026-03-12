"""
aquariums_with_animals.csv の生き物フラグを DB に反映するスクリプト。

Usage:
  python scripts/import_animals.py              # data/app.db（ローカル）
  python scripts/import_animals.py /data/app.db # Render 本番
"""
import csv
import sqlite3
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

CSV_PATH = Path(__file__).parent.parent / "aquariums_with_animals.csv"
DB_PATH  = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent.parent / "data" / "app.db"

ANIMAL_COLS = [
    "has_penguin", "has_dolphin", "has_sealion", "has_orca", "has_jellyfish",
    "has_steller", "has_seal", "has_shark", "has_beluga",
]

def ensure_columns(con):
    """新しい生き物カラムが無ければ追加（init_db相当）"""
    migrations = [
        "ALTER TABLE aquariums ADD COLUMN has_steller INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_seal INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_shark INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_beluga INTEGER NOT NULL DEFAULT 0",
        # 既存カラムも念のため
        "ALTER TABLE aquariums ADD COLUMN has_penguin INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_dolphin INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_sealion INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_orca INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE aquariums ADD COLUMN has_jellyfish INTEGER NOT NULL DEFAULT 0",
    ]
    for sql in migrations:
        try:
            con.execute(sql)
            con.commit()
        except sqlite3.OperationalError:
            pass  # 既存カラムは無視

def main():
    print(f"DB: {DB_PATH}")
    if not DB_PATH.exists():
        print("ERROR: DB が見つかりません。パスを確認してください。")
        sys.exit(1)

    con = sqlite3.connect(DB_PATH)
    ensure_columns(con)
    cur = con.cursor()

    updated = 0
    skipped = 0
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = row["name"]
            vals = {col: int(row.get(col, 0) or 0) for col in ANIMAL_COLS}

            # 1つでもフラグが立っていれば UPDATE（全て0なら SKIP）
            if all(v == 0 for v in vals.values()):
                skipped += 1
                continue

            set_clause = ", ".join(f"{c} = ?" for c in ANIMAL_COLS)
            params = list(vals.values()) + [name]
            cur.execute(f"UPDATE aquariums SET {set_clause} WHERE name = ?", params)
            if cur.rowcount > 0:
                flags = " / ".join(c.replace("has_","") for c, v in vals.items() if v)
                print(f"  ✅ {name}: {flags}")
                updated += 1
            else:
                print(f"  ⚠️  {name}: DB に見つかりません")

    con.commit()
    con.close()
    print(f"\n完了: {updated} 館更新, {skipped} 館スキップ（全フラグ0）")

if __name__ == "__main__":
    main()
