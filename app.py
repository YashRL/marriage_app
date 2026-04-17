import base64
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DB_URL = os.getenv("SUPA_POOL_URL") or os.getenv("SUPA_BASS", "")
COOKIE_NAME = "nb_user"

app = FastAPI(title="Nagar Brahmin Matrimony")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def db():
    if not DB_URL:
        raise RuntimeError("Missing DB URL. Set SUPA_POOL_URL in .env.")
    try:
        return psycopg.connect(DB_URL)
    except Exception as exc:
        raise RuntimeError("Database connection failed. Check SUPA_POOL_URL in .env.") from exc


def init_db():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            create table if not exists nb_users(
                login text primary key,
                user_name text not null default '',
                password text not null,
                created_at timestamptz default now()
            );
            create table if not exists nb_profiles(
                id bigserial primary key,
                created_by_login text,
                full_name text not null,
                gender text,
                dob date,
                gotra text,
                manglik text,
                education text,
                occupation text,
                city text,
                about text,
                contact_phone text,
                contact_email text,
                photo_b64 text,
                created_at timestamptz default now()
            );
            create unique index if not exists nb_users_login_uidx on nb_users(login);
            create index if not exists nb_profiles_city_idx on nb_profiles(city);
            create index if not exists nb_profiles_gender_idx on nb_profiles(gender);
            """
        )
        cur.execute("alter table nb_users add column if not exists user_name text")
        cur.execute(
            """
            update nb_users
            set user_name = initcap(split_part(login, '@', 1))
            where user_name is null or btrim(user_name) = ''
            """
        )


def sign_up(login, user_name, password):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into nb_users(login,user_name,password)
            values(%s,%s,%s)
            on conflict (login) do nothing
            """,
            (login.strip(), user_name.strip(), password),
        )
        return cur.rowcount == 1


def sign_in(login, password):
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "select login, user_name from nb_users where login=%s and password=%s",
            (login.strip(), password),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"login": row[0], "user_name": row[1] or initcap_login(row[0])}


def initcap_login(login):
    return login.split("@", 1)[0].strip().replace(".", " ").replace("_", " ").title()


def get_user_by_login(login):
    if not login:
        return None
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "select login, user_name from nb_users where login=%s",
            (login.strip(),),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {"login": row[0], "user_name": row[1] or initcap_login(row[0])}


def save_profile(created_by_login, data, photo):
    photo_b64 = base64.b64encode(photo).decode() if photo else ""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into nb_profiles(
                created_by_login,full_name,gender,dob,gotra,manglik,education,
                occupation,city,about,contact_phone,contact_email,photo_b64
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                created_by_login,
                data["full_name"],
                data["gender"],
                data["dob"],
                data["gotra"],
                data["manglik"],
                data["education"],
                data["occupation"],
                data["city"],
                data["about"],
                data["contact_phone"],
                data["contact_email"],
                photo_b64,
            ),
        )


def list_profiles(gender, city):
    query = """
        select full_name,gender,dob,gotra,manglik,education,occupation,city,about,
               contact_phone,contact_email,photo_b64,created_at
        from nb_profiles
        where 1=1
    """
    args = []
    if gender and gender != "All":
        query += " and gender=%s"
        args.append(gender)
    if city:
        query += " and city ilike %s"
        args.append(f"%{city.strip()}%")
    query += " order by created_at desc"
    with db() as conn, conn.cursor() as cur:
        cur.execute(query, args)
        rows = cur.fetchall()
    profiles = []
    for row in rows:
        profiles.append(
            {
                "full_name": row[0],
                "gender": row[1],
                "dob": row[2].isoformat() if row[2] else "",
                "gotra": row[3] or "",
                "manglik": row[4] or "",
                "education": row[5] or "",
                "occupation": row[6] or "",
                "city": row[7] or "",
                "about": row[8] or "",
                "contact_phone": row[9] or "",
                "contact_email": row[10] or "",
                "photo_b64": row[11] or "",
                "created_at": row[12].isoformat() if row[12] else "",
            }
        )
    return profiles


def current_user_login(request: Request):
    return request.cookies.get(COOKIE_NAME, "").strip()


def current_user(request: Request):
    return get_user_by_login(current_user_login(request))


def avatar_text(login):
    cleaned = (login or "").strip()
    return (cleaned[:2] or "VJ").upper()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "user": current_user(request)},
    )


@app.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    if current_user_login(request):
        return RedirectResponse("/home", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="auth.html",
        context={"request": request},
    )


@app.get("/home", response_class=HTMLResponse)
def home_page(request: Request):
    user = current_user(request)
    if not user:
        return RedirectResponse("/auth", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "request": request,
            "user_name": user["user_name"],
            "user_email": user["login"],
            "avatar_text": avatar_text(user["login"]),
        },
    )


@app.get("/assets/1.jpg")
def image_asset():
    return FileResponse(BASE_DIR / "1.jpg")


@app.get("/favicon.ico")
def favicon():
    return FileResponse(BASE_DIR / "1.jpg")


@app.get("/api/session")
def session(request: Request):
    user = current_user(request)
    return {
        "logged_in": bool(user),
        "login": user["login"] if user else "",
        "user_name": user["user_name"] if user else "",
    }


@app.post("/api/signup")
async def api_signup(request: Request):
    data = await request.json()
    login = (data.get("login") or "").strip()
    user_name = (data.get("user_name") or "").strip()
    password = data.get("password") or ""
    if not user_name or not login or not password:
        raise HTTPException(status_code=400, detail="Please fill all fields.")
    if not sign_up(login, user_name, password):
        raise HTTPException(status_code=400, detail="Account already exists.")
    return {"message": "Account created. Please sign in."}


@app.post("/api/signin")
async def api_signin(request: Request):
    data = await request.json()
    login = (data.get("login") or "").strip()
    password = data.get("password") or ""
    user = sign_in(login, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid login.")
    response = JSONResponse({"message": "Signed in.", **user})
    response.set_cookie(COOKIE_NAME, user["login"], httponly=True, samesite="lax")
    return response


@app.post("/api/signout")
def api_signout():
    response = JSONResponse({"message": "Signed out."})
    response.delete_cookie(COOKIE_NAME)
    return response


@app.get("/api/profiles")
def api_profiles(gender: str = "All", city: str = ""):
    return {"profiles": list_profiles(gender, city)}


@app.post("/api/profiles")
async def api_create_profile(
    request: Request,
    full_name: str = Form(...),
    gender: str = Form(""),
    dob: str = Form(""),
    gotra: str = Form(""),
    manglik: str = Form(""),
    education: str = Form(""),
    occupation: str = Form(""),
    city: str = Form(""),
    about: str = Form(""),
    contact_phone: str = Form(""),
    contact_email: str = Form(""),
    photo: UploadFile | None = File(default=None),
):
    user = current_user_login(request)
    if not user:
        raise HTTPException(status_code=401, detail="Please sign in first.")
    photo_bytes = await photo.read() if photo and photo.filename else b""
    save_profile(
        user,
        {
            "full_name": full_name.strip(),
            "gender": gender,
            "dob": dob or None,
            "gotra": gotra.strip(),
            "manglik": manglik,
            "education": education.strip(),
            "occupation": occupation.strip(),
            "city": city.strip(),
            "about": about.strip(),
            "contact_phone": contact_phone.strip(),
            "contact_email": contact_email.strip(),
        },
        photo_bytes,
    )
    return {"message": "Profile saved."}


@app.get("/health")
def health():
    return {"ok": True}
