import os
import asyncio
import httpx
import sqlite3
import traceback


from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import select
from .db import init_db, session
from .models import Aquarium, Visit
from .crud import list_aquariums, set_visited, set_note
from .import_csv import import_csv



BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
DEBUG_ERRORS = os.getenv("DEBUG_ERRORS", "").lower() in ("1", "true", "yes")
BUILD = os.getenv("BUILD", "dev")


def require_key(request: Request):
    # API以外（静的）は触らない
    if not request.url.path.startswith("/api/"):
        return

    # 認証不要API
    if request.url.path in ("/api/health", "/api/me"):
        return

    # Googleログイン済みならOK
    uid = (request.session.get("user_id") or "").strip()
    if uid:
        return

    # 未ログインは401（500にしない）
    raise HTTPException(401, "Not logged in")


def get_user_id(request: Request) -> str:
    uid = (request.session.get("user_id") or "").strip()
    if not uid:
        raise HTTPException(401, "Not logged in")
    return uid


from starlette.middleware import Middleware

middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=SESSION_SECRET,
        same_site="lax",
        https_only=BASE_URL.startswith("https://"),
    )
]

app = FastAPI(middleware=middleware)


oauth = OAuth()
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={"scope": "openid email profile"},
)

async def geocode(query: str):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": query, "format": "jsonv2", "limit": 1}
    headers = {"User-Agent": "aquarium-stamp-app/1.0"}
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    try:
        require_key(request)
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
       # Renderのログにも出す
        traceback.print_exc()
        # デバッグ時だけ、画面にもエラー原因を返す
        if DEBUG_ERRORS:
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "type": type(e).__name__, "msg": str(e)},
            )
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.on_event("startup")
def on_startup():
    init_db()
    # 初回だけ自動インポートしたい場合：CSV_PATH をRenderの環境変数にセットしておく
    csv_path = os.getenv("CSV_PATH", "")
    if csv_path:
        with session() as db:
            count = db.exec(select(Aquarium)).first()
        if not count:
            try:
                import_csv(csv_path)
            except Exception:
                # 失敗してもサーバは起動させる（ログはRender側で見える）
                pass

@app.get("/debug/build")
def debug_build():
    return {"build": BUILD, "base_url": BASE_URL, "debug_errors": DEBUG_ERRORS}

class VisitToggleIn(BaseModel):
    visited: bool

class NoteIn(BaseModel):
    note: str

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/debug/oauth")
def debug_oauth():
    cid = os.getenv("GOOGLE_CLIENT_ID")
    csec = os.getenv("GOOGLE_CLIENT_SECRET")
    return {
        "BASE_URL": BASE_URL,
        "has_client_id": bool(cid),
        "client_id_tail": (cid[-12:] if cid else None),  # 末尾だけ（安全）
        "has_client_secret": bool(csec),
        "redirect_uri": f"{BASE_URL}/auth/callback",
    }

@app.get("/login")
async def login(request: Request):
    redirect_uri = f"{BASE_URL}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo:
        userinfo = await oauth.google.userinfo(token=token)

    sub = userinfo["sub"]
    request.session["user_id"] = f"google:{sub}"
    request.session["email"] = userinfo.get("email")
    request.session["name"] = userinfo.get("name")
    request.session["picture"] = userinfo.get("picture")

    return RedirectResponse(url="/")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.get("/api/me")
def me(request: Request):
    uid = (request.session.get("user_id") or "").strip()
    if not uid:
        return {"logged_in": False}
    return {
        "logged_in": True,
        "user_id": uid,
        "email": request.session.get("email"),
        "name": request.session.get("name"),
        "picture": request.session.get("picture"),
    }

@app.get("/api/stats")
def stats(request: Request):
    uid = get_user_id(request)
    with session() as db:
        total = db.exec(select(Aquarium)).all()
        total_n = len(total)
        visited_n = db.exec(
            select(Visit).where(Visit.user_id == uid, Visit.visited == True)
        ).all()
        return {"total": total_n, "visited": len(visited_n)}


@app.get("/api/aquariums")
def aquariums(request: Request):
    uid = get_user_id(request)
    with session() as db:
        aq = list_aquariums(db)
        visits = {
            v.aquarium_id: v
            for v in db.exec(select(Visit).where(Visit.user_id == uid)).all()
        }
        out = []
        for a in aq:
            v = visits.get(a.id)
            out.append({
                "id": a.id,
                "name": a.name,
                "prefecture": a.prefecture,
                "city": a.city,
                "location_raw": a.location_raw,
                "url": a.url,
                "mola_star": a.mola_star,
                "visited": bool(v.visited) if v else False,
                "visited_at": v.visited_at.isoformat() if (v and v.visited_at) else None,
                "note": v.note if v else "",
                "updated_at": v.updated_at.isoformat() if v else None,
                "lat": a.lat,
                "lng": a.lng,
            })
        return out


@app.put("/api/aquariums/{aquarium_id}/visited")
def toggle_visited(aquarium_id: int, body: VisitToggleIn, request: Request):
    uid = get_user_id(request)
    with session() as db:
        a = db.get(Aquarium, aquarium_id)
        if not a:
            raise HTTPException(404, "Aquarium not found")
        v = set_visited(db, uid, aquarium_id, body.visited)
        return {"aquarium_id": aquarium_id, "visited": v.visited, "visited_at": v.visited_at}


@app.put("/api/aquariums/{aquarium_id}/note")
def update_note(aquarium_id: int, body: NoteIn, request: Request):
    uid = get_user_id(request)
    with session() as db:
        a = db.get(Aquarium, aquarium_id)
        if not a:
            raise HTTPException(404, "Aquarium not found")
        v = set_note(db, uid, aquarium_id, body.note)
        return {"aquarium_id": aquarium_id, "note": v.note, "updated_at": v.updated_at}


# 静的フロント
app.mount("/", StaticFiles(directory="web", html=True), name="web")

