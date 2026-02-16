from datetime import datetime
from sqlmodel import select
from .models import Aquarium, Visit

def list_aquariums(db):
    return db.exec(select(Aquarium).order_by(Aquarium.prefecture, Aquarium.name)).all()

def get_visit(db, user_id: str, aquarium_id: int):
    return db.exec(
        select(Visit).where(Visit.user_id == user_id, Visit.aquarium_id == aquarium_id)
    ).first()


def set_visited(db, user_id: str, aquarium_id: int, visited: bool):
    v = get_visit(db, user_id, aquarium_id)
    now = datetime.utcnow()
    if v is None:
        v = Visit(user_id=user_id, aquarium_id=aquarium_id)
    v.visited = visited
    v.updated_at = now
    v.visited_at = now if visited else None
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def set_note(db, user_id: str, aquarium_id: int, note: str):
    v = get_visit(db, user_id, aquarium_id)
    now = datetime.utcnow()
    if v is None:
        v = Visit(user_id=user_id, aquarium_id=aquarium_id)
    v.note = note
    v.updated_at = now
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

