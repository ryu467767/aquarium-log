"""ローカルの水族館データ（localdata/app.db の aquariums）を本番とまったく同じにする。

本番の公開API（/api/public/aquariums）から全館を取ってきて、
館名・所在地・生き物・SNS・閉館/休館・ID番号まで本番にそろえる。
ローカルの訪問記録・写真・生き物メモは、館名で新しいID番号に付け直すので消えない。
本番には何も書き込まない（読むだけ）。

使い方（ローカルサーバーを止めてから、リポジトリのフォルダで）:
    python scripts/sync_local_from_prod.py
    python scripts/sync_local_from_prod.py --ip 216.24.57.20   # このPCで本番につながりにくいとき
    python scripts/sync_local_from_prod.py --json 保存したファイル.json

実行前に localdata/app.db.bak-日時 にバックアップを作る。
"""
import argparse
import datetime
import http.client
import json
import shutil
import socket
import sqlite3
import ssl
from pathlib import Path

HOST = "aquarium-log.onrender.com"
PATH = "/api/public/aquariums"
DB = Path(__file__).resolve().parent.parent / "localdata" / "app.db"
# 館のID番号を持っているテーブル（付け直しの対象）
LINKED = ["visits", "photos", "sightings"]


def fetch(ip=None):
    ctx = ssl.create_default_context()
    conn = http.client.HTTPSConnection(HOST, timeout=60, context=ctx)
    if ip:  # 名前解決で届かないIPに行ってしまうPC向けに、接続先IPを指定する
        sock = socket.create_connection((ip, 443), timeout=60)
        conn.sock = ctx.wrap_socket(sock, server_hostname=HOST)
    conn.request("GET", PATH, headers={"User-Agent": "aquarium-log-local-sync"})
    r = conn.getresponse()
    if r.status != 200:
        raise SystemExit(f"本番から取得できませんでした: HTTP {r.status}")
    return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ip", help="本番の接続先IP（例: 216.24.57.20）")
    ap.add_argument("--json", help="本番から保存した JSON ファイルを使う")
    args = ap.parse_args()

    prod = json.load(open(args.json, encoding="utf-8")) if args.json else fetch(args.ip)
    if not prod or "name" not in prod[0]:
        raise SystemExit("本番のデータが空か、形がおかしいので中止しました")
    if not DB.exists():
        raise SystemExit(f"{DB} がありません。先に .\\run-local.ps1 を一度起動してください")

    bak = DB.with_name(f"app.db.bak-{datetime.datetime.now():%Y%m%d-%H%M%S}")
    shutil.copy2(DB, bak)
    print(f"バックアップ: {bak.name}")

    con = sqlite3.connect(DB)
    cols = [r[1] for r in con.execute("PRAGMA table_info(aquariums)")]
    missing = [k for k in prod[0] if k.startswith(("has_", "suspended")) and k not in cols]
    if missing:
        raise SystemExit(f"ローカルDBに無い列があります {missing}。先に .\\run-local.ps1 を一度起動してください")

    old_name = {i: n for i, n in con.execute("SELECT id, name FROM aquariums")}
    new_id = {x["name"]: x["id"] for x in prod}
    remap = {old: new_id[n] for old, n in old_name.items() if n in new_id}
    lost = sorted(n for n in old_name.values() if n not in new_id)

    try:
        con.execute("BEGIN")
        # 館のID番号を付け直す（ぶつからないよう、いったん大きな番号に逃がしてから入れる）
        for t in LINKED:
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
                continue
            for old, new in remap.items():
                con.execute(f"UPDATE {t} SET aquarium_id=? WHERE aquarium_id=?", (new + 1_000_000, old))
            con.execute(f"UPDATE {t} SET aquarium_id=aquarium_id-1000000 WHERE aquarium_id>=1000000")
        # 館のデータを本番の内容で入れ直す
        con.execute("DELETE FROM aquariums")
        for x in prod:
            row = {k: (int(v) if isinstance(v, bool) else v) for k, v in x.items() if k in cols}
            for k in ("closed_at", "suspended_note", "twitter_id", "instagram_id"):
                if k in row and row[k] == "":
                    row[k] = None  # 本番DBでは空はNULL
            con.execute(
                f"INSERT INTO aquariums ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})",
                list(row.values()),
            )
        con.commit()
    except Exception:
        con.rollback()
        raise

    n_open = sum(1 for x in prod if not x.get("is_closed"))
    print(f"そろえました: {len(prod)}館（営業中 {n_open}・閉館 {len(prod) - n_open}）")
    print(f"ID番号を付け直した館: {sum(1 for o, n in remap.items() if o != n)}館")
    if lost:
        print(f"注意: 本番に無いのでローカルから消えた館（記録は残っていますが館が無い状態）: {lost}")


if __name__ == "__main__":
    main()
