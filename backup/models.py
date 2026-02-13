from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, UniqueConstraint

class Aquarium(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    prefecture: str = ""
    city: str = ""
    location_raw: str = ""
    url: str = ""
    mola_star: int = 0
    lat: Optional[float] = None
    lng: Optional[float] = None


    __table_args__ = (
        UniqueConstraint("name", "location_raw", "url", name="uq_aquarium_identity"),
    )

class Visit(SQLModel, table=True):
    aquarium_id: int = Field(primary_key=True, foreign_key="aquarium.id")
    visited: bool = False
    visited_at: Optional[datetime] = None
    note: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)
