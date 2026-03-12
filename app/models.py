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

    # 生き物フラグ
    has_penguin: bool = Field(default=False)
    has_dolphin: bool = Field(default=False)
    has_sealion: bool = Field(default=False)
    has_orca: bool = Field(default=False)
    has_jellyfish: bool = Field(default=False)
    has_steller: bool = Field(default=False)   # トド
    has_seal: bool = Field(default=False)      # アザラシ
    has_shark: bool = Field(default=False)     # サメ
    has_beluga: bool = Field(default=False)    # シロイルカ（ベルーガ）

    # 閉館フラグ
    is_closed: bool = Field(default=False)
    closed_at: Optional[str] = Field(default=None)  # 例: "2024-03"

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
    visit_count: int = Field(default=0)
    visit_years: str = Field(default="[]")  # JSON array e.g. '["2024","2025"]'
    want_to_go: bool = Field(default=False)
    note: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profiles"

    user_id: str = Field(primary_key=True)
    email: str = ""
    name: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: datetime = Field(default_factory=datetime.utcnow)


class Inquiry(SQLModel, table=True):
    __tablename__ = "inquiries"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = ""
    email: str = ""
    message: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_read: bool = Field(default=False)


class Photo(SQLModel, table=True):
    __tablename__ = "photos"

    id: Optional[int] = Field(default=None, primary_key=True)

    # ログインユーザー単位で写真を紐付け
    user_id: str = Field(index=True)

    # aquariums テーブルの id に紐付け
    aquarium_id: int = Field(index=True, foreign_key="aquariums.id")

    # /uploads で配信する相対パスを保存
    path: str

    created_at: datetime = Field(default_factory=datetime.utcnow)
    __tablename__ = "photos"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    aquarium_id: int = Field(index=True, foreign_key="aquariums.id")

    # /uploads から配信する「相対パス」を保存する
    path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)