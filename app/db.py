import os
import sqlite3 as _sqlite3
from sqlmodel import SQLModel, create_engine, Session

def get_db_path() -> str:
    # Renderでは永続ディスクを /data にマウントする（render.yaml参照）
    base = os.getenv("DB_DIR", "/data")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "app.db")

DATABASE_URL = f"sqlite:///{get_db_path()}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def _migrate():
    """既存テーブルに新しいカラムを追加するマイグレーション。"""
    con = _sqlite3.connect(get_db_path())
    migrations = [
        "ALTER TABLE visits ADD COLUMN visit_count INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE visits ADD COLUMN want_to_go INTEGER NOT NULL DEFAULT 0",
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
        except _sqlite3.OperationalError:
            pass  # 既にカラムが存在する場合は無視
    con.close()

def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    _migrate()

def session() -> Session:
    return Session(engine)
