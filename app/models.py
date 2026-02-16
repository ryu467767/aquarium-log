from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint

class Aquarium(SQLModel, table=True):
    __tablename__ = "aquariums"   # ★ここが超重要（テーブル名を固定）

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    prefecture: str = ""
    city: str = ""
    location_raw: str = ""
    url: str = ""
    mola_star: int = 0

    # lat/lng も使うならここで持つ（既に列ある前提）
    lat: Optional[float] = None
    lng: Optional[float] = None

    __table_args__ = (
        UniqueConstraint("name", "location_raw", "url", name="uq_aquarium_identity"),
    )

class Visit(SQLModel, table=True):
    __tablename__ = "visits"  # ★固定

    # ★追加：ユーザーごとに訪問状態を分ける
    user_id: str = Field(primary_key=True, index=True)

    # ★変更：aquarium_id は複合主キーの片割れにする
    aquarium_id: int = Field(primary_key=True, foreign_key="aquariums.id")

    visited: bool = False
    visited_at: Optional[datetime] = None
    note: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)

