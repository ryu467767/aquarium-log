"""
update_latlng.py
================
aquariums_with_latlng.csv の情報を使って:
  1. ローカルの app.db (SQLite) を UPDATE（lat/lng/prefecture/city）
  2. aquariums_list.csv の lat/lng/prefecture/city 列を上書き更新

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
# Render 環境 (/data/app.db) を優先、なければローカルの data/app.db
_render_db = Path("/data/app.db")
DB_PATH    = _render_db if _render_db.exists() else BASE / "data" / "app.db"
# ─────────────────────────────────────────────────────

def load_src_csv():
    """ソースCSVを {name: {lat, lng, prefecture, city}} の辞書で返す"""
    data = {}
    with open(SRC_CSV, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = row["name"].strip()
            lat  = row.get("lat", "").strip()
            lng  = row.get("lng", "").strip()
            pref = row.get("prefecture", "").strip()
            city = row.get("city", "").strip()
            if lat and lng:
                try:
                    data[name] = {
                        "lat": float(lat),
                        "lng": float(lng),
                        "prefecture": pref,
                        "city": city,
                    }
                except ValueError:
                    print(f"  [SKIP] 無効な座標: {name} lat={lat} lng={lng}")
    return data


def update_db(data: dict):
    """app.db の aquariums テーブルを UPDATE"""
    if not DB_PATH.exists():
        print(f"[DB] ファイルが見つかりません: {DB_PATH}")
        print("  → Render から app.db をダウンロードして data/ フォルダに置いてください")
        return

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    updated = 0
    not_found = []

    for name, vals in data.items():
        cur.execute(
            "UPDATE aquariums SET lat=?, lng=?, prefecture=?, city=? WHERE name=?",
            (vals["lat"], vals["lng"], vals["prefecture"], vals["city"], name)
        )
        if cur.rowcount > 0:
            updated += 1
        else:
            not_found.append(name)

    con.commit()
    con.close()

    print(f"\n[DB] 更新完了: {updated} / {len(data)} 件")
    if not_found:
        print(f"[DB] DBに存在しない名前 ({len(not_found)} 件):")
        for n in not_found:
            print(f"  - {n}")


def update_list_csv(data: dict):
    """aquariums_list.csv の lat/lng/prefecture/city 列を上書き"""
    if not LIST_CSV.exists():
        print(f"[CSV] ファイルが見つかりません: {LIST_CSV}")
        return

    # 読み込み
    with open(LIST_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # 列がなければ追加
    for col in ["lat", "lng", "prefecture", "city"]:
        if col not in fieldnames:
            fieldnames.append(col)

    updated = 0
    for row in rows:
        name = row["name"].strip()
        if name in data:
            vals = data[name]
            row["lat"] = vals["lat"]
            row["lng"] = vals["lng"]
            row["prefecture"] = vals["prefecture"]
            row["city"] = vals["city"]
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

    data = load_src_csv()
    print(f"データを読み込みました: {len(data)} 件\n")

    update_db(data)
    update_list_csv(data)

    print("\n完了！")


if __name__ == "__main__":
    main()
