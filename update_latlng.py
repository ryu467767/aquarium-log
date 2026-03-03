"""
update_latlng.py
================
aquariums_with_latlng.csv の座標を使って:
  1. ローカルの app.db (SQLite) を UPDATE
  2. aquariums_list.csv の lat/lng 列を上書き更新

使い方:
  python update_latlng.py
"""

import csv
import sqlite3
from pathlib import Path

# ── パス設定 ──────────────────────────────────────────
BASE = Path(__file__).parent
SRC_CSV   = BASE / "aquariums_with_latlng.csv"   # 座標のソース
LIST_CSV  = BASE / "aquariums_list.csv"            # 更新対象マスターCSV
DB_PATH   = BASE / "data" / "app.db"               # ローカルDB (Render は /data/app.db)
# ─────────────────────────────────────────────────────

def load_src_csv():
    """ソースCSVを {name: {lat, lng}} の辞書で返す"""
    coords = {}
    with open(SRC_CSV, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["name"].strip()
            lat  = row["lat"].strip()
            lng  = row["lng"].strip()
            if lat and lng:
                try:
                    coords[name] = (float(lat), float(lng))
                except ValueError:
                    print(f"  [SKIP] 無効な座標: {name} lat={lat} lng={lng}")
    return coords


def update_db(coords: dict):
    """app.db の aquariums テーブルを UPDATE"""
    if not DB_PATH.exists():
        print(f"[DB] ファイルが見つかりません: {DB_PATH}")
        print("  → Render から app.db をダウンロードして data/ フォルダに置いてください")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    updated = 0
    not_found = []

    for name, (lat, lng) in coords.items():
        cur.execute(
            "UPDATE aquariums SET lat=?, lng=? WHERE name=?",
            (lat, lng, name)
        )
        if cur.rowcount > 0:
            updated += 1
        else:
            not_found.append(name)

    con.commit()
    con.close()

    print(f"\n[DB] 更新完了: {updated} / {len(coords)} 件")
    if not_found:
        print(f"[DB] DBに存在しない名前 ({len(not_found)} 件):")
        for n in not_found:
            print(f"  - {n}")


def update_list_csv(coords: dict):
    """aquariums_list.csv の lat/lng 列を上書き"""
    if not LIST_CSV.exists():
        print(f"[CSV] ファイルが見つかりません: {LIST_CSV}")
        return

    # 読み込み
    with open(LIST_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # lat/lng 列がなければ追加
    if "lat" not in fieldnames:
        fieldnames = list(fieldnames) + ["lat"]
    if "lng" not in fieldnames:
        fieldnames = list(fieldnames) + ["lng"]

    updated = 0
    for row in rows:
        name = row["name"].strip()
        if name in coords:
            lat, lng = coords[name]
            row["lat"] = lat
            row["lng"] = lng
            updated += 1

    # 書き戻し（BOM付きUTF-8 で Excel でも開ける）
    with open(LIST_CSV, encoding="utf-8-sig", newline="", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[CSV] 更新完了: {updated} / {len(rows)} 件")


def main():
    print(f"ソースCSV : {SRC_CSV}")
    print(f"マスターCSV: {LIST_CSV}")
    print(f"DB        : {DB_PATH}")
    print()

    coords = load_src_csv()
    print(f"座標を読み込みました: {len(coords)} 件\n")

    update_db(coords)
    update_list_csv(coords)

    print("\n完了！")


if __name__ == "__main__":
    main()
