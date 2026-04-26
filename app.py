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
LANG_COOKIE = "nb_lang"

TRANSLATIONS = {
    "en": {
        "title": "नागर ब्राहाम्ण समाज *शाखा-रतलाम*",
        "nav_home": "Home",
        "nav_auth": "Get Started",
        "nav_highlights": "See Highlights",
        "brand_name": "नागर ब्राहाम्ण समाज *शाखा-रतलाम*",
        "footer_motto": "जय हाटकेश",
        "footer_desc": "Simple matrimony experience with marriage guidance and profile discovery.",
        "hero_eyebrow": "Marriage guidance with astrology harmony",
        "hero_h1": "Find meaningful matches in a brighter, more elegant matrimony space.",
        "hero_desc": "A simple and clear landing page for families and individuals who want marriage information, trusted introductions, and astrology-inspired compatibility in one proper layout.",
        "get_started": "Get Started",
        "see_highlights": "See Highlights",
        "stat_flow": "3-step flow",
        "stat_flow_desc": "Landing, login, home",
        "stat_astro": "Astrology-ready",
        "stat_astro_desc": "Visuals and match themes",
        "stat_layout": "Neat layout",
        "stat_layout_desc": "Simple to browse and use",
        "info_marriage_h2": "Marriage Information",
        "info_marriage_p": "Keep the process clear with profile details, family values, education, and lifestyle preferences in one simple flow.",
        "info_astro_h2": "Astrology Insights",
        "info_astro_p": "Bring horoscope-friendly presentation into the journey with zodiac-inspired visuals and compatibility themes.",
        "info_flow_h2": "Neat User Flow",
        "info_flow_p": "Start on the landing page, continue to signup or login, and then manage your home dashboard after sign-in.",
        "gallery_eyebrow": "Visual Highlights",
        "gallery_h2": "Marriage and astrology in a richer landing page layout",
        "gallery_1_h3": "Warm Moments",
        "gallery_1_p": "Real imagery makes the landing page feel softer, more grounded, and more inviting for new users.",
        "gallery_2_h3": "Beautiful Layout",
        "gallery_2_p": "The new card arrangement gives the landing page more depth while keeping the interface neat and clear.",
        "gallery_3_h3": "Astrology Accent",
        "gallery_3_p": "Astrology remains part of the design language, now blended with your orange application theme.",
        "welcome": "Welcome",
        "personal_dashboard": "Personal Dashboard",
        "manage_profile_desc": "Manage your profile, review matches, and keep your marriage search organized in one clear space.",
        "profile_ready": "Profile ready",
        "match_browsing": "Match browsing",
        "simple_workflow": "Simple workflow",
        "metric_1_h": "Create or update your biodata",
        "metric_2_h": "Filter and review profiles faster",
        "panel_create_h2": "Create & Update Profile",
        "panel_create_p": "Add marriage details and contact information.",
        "step_1": "Basic Details",
        "step_2": "Family & Background",
        "step_3": "Contact & Photo",
        "full_name": "Full Name",
        "gender": "Gender",
        "dob": "Date of Birth",
        "birth_time": "Birth Time",
        "birth_place": "Birth Place",
        "height": "Height",
        "blood_group": "Blood Group",
        "caste": "Caste",
        "income": "Annual Income",
        "city": "Current City",
        "gotra": "Gotra",
        "manglik": "Manglik",
        "education": "Education",
        "occupation": "Occupation",
        "father_name": "Father's Name",
        "father_occupation": "Father's Occupation",
        "mother_name": "Mother's Name",
        "siblings": "Siblings",
        "address": "Full Address",
        "about": "About Me",
        "phone": "Your Phone",
        "parents_contact": "Parents' Contact",
        "email": "Email",
        "photo": "Photo",
        "prev": "Previous",
        "next": "Next",
        "save_profile": "Save Profile",
        "browse_profiles_h2": "Browse Profiles",
        "browse_profiles_p": "Filter by city and gender.",
        "filter_gender": "Gender",
        "filter_city": "City",
        "refresh": "Refresh",
        "available_profiles": "Available profiles",
        "profiles_count": "profiles",
        "select_gender": "Select gender",
        "male": "Male",
        "female": "Female",
        "select_option": "Select option",
        "yes": "Yes",
        "no": "No",
        "all": "All",
        "logout": "Logout",
        "signed_in_user": "Signed in user",
        "active_session": "Active session",
        "name": "Name",
        "status": "Status",
        "auth_title": "Login or Signup",
        "auth_welcome": "Welcome",
        "auth_h1": "Login or create your matrimony account.",
        "auth_p": "Continue from the landing page into a simple sign in flow. After login, you will reach your home page and can manage profiles there.",
        "login": "Login",
        "signup": "Signup",
        "welcome_back": "Welcome back",
        "signin_desc": "Sign in to continue to your home page.",
        "signup_desc": "Create an account to start your search.",
        "user_name_label": "User Name",
        "user_name_placeholder": "Enter your name",
        "email_label": "Email",
        "email_placeholder": "Enter your email",
        "password_label": "Password",
        "password_placeholder": "Enter your password",
        "back_to_landing": "Back to landing page",
        "no_profiles_found": "No profiles found."
    },
    "hi": {
        "title": "नागर ब्राहाम्ण समाज *शाखा-रतलाम*",
        "nav_home": "होम",
        "nav_auth": "शुरू करें",
        "nav_highlights": "खासियतें देखें",
        "brand_name": "नागर ब्राहाम्ण समाज *शाखा-रतलाम*",
        "footer_motto": "जय हाटकेश",
        "footer_desc": "विवाह मार्गदर्शन और प्रोफाइल खोज के साथ सरल वैवाहिक अनुभव।",
        "hero_eyebrow": "ज्योतिष सामंजस्य के साथ विवाह मार्गदर्शन",
        "hero_h1": "एक उज्जवल, अधिक सुंदर वैवाहिक स्थान में सार्थक मिलान खोजें।",
        "hero_desc": "उन परिवारों और व्यक्तियों के लिए एक सरल और स्पष्ट लैंडिंग पृष्ठ जो एक उचित लेआउट में विवाह की जानकारी, विश्वसनीय परिचय और ज्योतिष-प्रेरित अनुकूलता चाहते हैं।",
        "get_started": "शुरू करें",
        "see_highlights": "खासियतें देखें",
        "stat_flow": "3-चरणीय प्रवाह",
        "stat_flow_desc": "लैंडिंग, लॉगिन, होम",
        "stat_astro": "ज्योतिष-तैयार",
        "stat_astro_desc": "विजुअल्स और मैच थीम",
        "stat_layout": "साफ सुथरा लेआउट",
        "stat_layout_desc": "ब्राउज़ करने और उपयोग करने में आसान",
        "info_marriage_h2": "विवाह की जानकारी",
        "info_marriage_p": "एक सरल प्रवाह में प्रोफाइल विवरण, पारिवारिक मूल्यों, शिक्षा और जीवनशैली प्राथमिकताओं के साथ प्रक्रिया को स्पष्ट रखें।",
        "info_astro_h2": "ज्योतिष अंतर्दृष्टि",
        "info_astro_p": "राशि चक्र से प्रेरित दृश्यों और अनुकूलता विषयों के साथ यात्रा में राशिफल-अनुकूल प्रस्तुति लाएं।",
        "info_flow_h2": "व्यवस्थित यूजर फ्लो",
        "info_flow_p": "लैंडिंग पृष्ठ से शुरू करें, साइनअप या लॉगिन जारी रखें, और फिर साइन-इन के बाद अपने होम डैशबोर्ड को प्रबंधित करें।",
        "gallery_eyebrow": "दृश्य मुख्य अंश",
        "gallery_h2": "एक समृद्ध लैंडिंग पृष्ठ लेआउट में विवाह और ज्योतिष",
        "gallery_1_h3": "भावुक क्षण",
        "gallery_1_p": "वास्तविक चित्रण लैंडिंग पृष्ठ को नरम, अधिक जमीनी और नए उपयोगकर्ताओं के लिए अधिक आमंत्रित महसूस कराता है।",
        "gallery_2_h3": "सुंदर लेआउट",
        "gallery_2_p": "नई कार्ड व्यवस्था इंटरफ़ेस को साफ और स्पष्ट रखते हुए लैंडिंग पृष्ठ को अधिक गहराई देती है।",
        "gallery_3_h3": "ज्योतिष लहजा",
        "gallery_3_p": "ज्योतिष डिजाइन भाषा का हिस्सा बना हुआ है, जो अब आपके ऑरेंज एप्लिकेशन थीम के साथ मिश्रित है।",
        "welcome": "स्वागत है",
        "personal_dashboard": "व्यक्तिगत डैशबोर्ड",
        "manage_profile_desc": "अपनी प्रोफ़ाइल प्रबंधित करें, मिलान देखें और अपनी विवाह खोज को एक स्पष्ट स्थान पर व्यवस्थित रखें।",
        "profile_ready": "प्रोफ़ाइल तैयार",
        "match_browsing": "मैच ब्राउजिंग",
        "simple_workflow": "सरल वर्कफ़्लो",
        "metric_1_h": "अपना बायोडाटा बनाएं या अपडेट करें",
        "metric_2_h": "प्रोफाइल को तेजी से फ़िल्टर करें और समीक्षा करें",
        "panel_create_h2": "प्रोफ़ाइल बनाएं और अपडेट करें",
        "panel_create_p": "विवाह विवरण और संपर्क जानकारी जोड़ें।",
        "step_1": "बुनियादी विवरण",
        "step_2": "परिवार और पृष्ठभूमि",
        "step_3": "संपर्क और फोटो",
        "full_name": "पूरा नाम",
        "gender": "लिंग",
        "dob": "जन्म तिथि",
        "birth_time": "जन्म समय",
        "birth_place": "जन्म स्थान",
        "height": "ऊंचाई",
        "blood_group": "रक्त समूह",
        "caste": "जाति",
        "income": "वार्षिक आय",
        "city": "वर्तमान शहर",
        "gotra": "गोत्र",
        "manglik": "मांगलिक",
        "education": "शिक्षा",
        "occupation": "व्यवसाय",
        "father_name": "पिता का नाम",
        "father_occupation": "पिता का व्यवसाय",
        "mother_name": "माता का नाम",
        "siblings": "भाई/बहन",
        "address": "स्थायी पता",
        "about": "मेरे बारे में",
        "phone": "आपका फ़ोन",
        "parents_contact": "माता-पिता का नंबर",
        "email": "ईमेल",
        "photo": "फोटो",
        "prev": "पिछला",
        "next": "अगला",
        "save_profile": "प्रोफ़ाइल सहेजें",
        "browse_profiles_h2": "प्रोफाइल ब्राउज़ करें",
        "browse_profiles_p": "शहर और लिंग के आधार पर फ़िल्टर करें।",
        "filter_gender": "लिंग",
        "filter_city": "शहर",
        "refresh": "रिफ्रेश",
        "available_profiles": "उपलब्ध प्रोफाइल",
        "profiles_count": "प्रोफाइल",
        "select_gender": "लिंग चुनें",
        "male": "पुरुष",
        "female": "महिला",
        "select_option": "विकल्प चुनें",
        "yes": "हाँ",
        "no": "नहीं",
        "all": "सभी",
        "logout": "लॉगआउट",
        "signed_in_user": "साइन इन उपयोगकर्ता",
        "active_session": "सक्रिय सत्र",
        "name": "नाम",
        "status": "स्थिति",
        "auth_title": "लॉगिन या साइनअप",
        "auth_welcome": "स्वागत है",
        "auth_h1": "लॉगिन करें या अपना वैवाहिक खाता बनाएं।",
        "auth_p": "लैंडिंग पृष्ठ से एक सरल साइन इन प्रवाह में जारी रखें। लॉगिन के बाद, आप अपने होम पेज पर पहुंच जाएंगे और वहां प्रोफाइल प्रबंधित कर सकते हैं।",
        "login": "लॉगिन",
        "signup": "साइनअप",
        "welcome_back": "वापसी पर स्वागत है",
        "signin_desc": "अपने होम पेज पर जारी रखने के लिए साइन इन करें।",
        "signup_desc": "अपनी खोज शुरू करने के लिए एक खाता बनाएं।",
        "user_name_label": "उपयोगकर्ता नाम",
        "user_name_placeholder": "अपना नाम दर्ज करें",
        "email_label": "ईमेल",
        "email_placeholder": "अपना ईमेल दर्ज करें",
        "password_label": "पासवर्ड",
        "password_placeholder": "अपना पासवर्ड दर्ज करें",
        "back_to_landing": "लैंडिंग पृष्ठ पर वापस जाएं",
        "no_profiles_found": "कोई प्रोफाइल नहीं मिली।"
    }
}

app = FastAPI(title="नागर ब्राहाम्ण समाज *शाखा-रतलाम*")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

def get_lang(request: Request):
    return request.cookies.get(LANG_COOKIE, "hi")

@app.middleware("http")
async def add_lang_header(request: Request, call_next):
    lang = get_lang(request)
    request.state.lang = lang
    response = await call_next(request)
    return response

def t(request: Request, key: str):
    lang = getattr(request.state, "lang", "hi")
    return TRANSLATIONS.get(lang, TRANSLATIONS["hi"]).get(key, key)

templates.env.globals["t"] = t
templates.env.globals["TRANSLATIONS"] = TRANSLATIONS

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
        # Add new columns if they don't exist
        columns = [
            ("birth_time", "text"), ("birth_place", "text"), ("height", "text"),
            ("blood_group", "text"), ("caste", "text"), ("income", "text"),
            ("father_name", "text"), ("father_occupation", "text"), ("mother_name", "text"),
            ("siblings", "text"), ("address", "text"), ("parents_contact", "text")
        ]
        for col_name, col_type in columns:
            cur.execute(f"alter table nb_profiles add column if not exists {col_name} {col_type}")

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
                created_by_login,full_name,gender,dob,birth_time,birth_place,
                height,blood_group,caste,income,gotra,manglik,education,
                occupation,father_name,father_occupation,mother_name,siblings,
                city,address,about,contact_phone,parents_contact,contact_email,photo_b64
            ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                created_by_login,
                data["full_name"],
                data["gender"],
                data["dob"],
                data["birth_time"],
                data["birth_place"],
                data["height"],
                data["blood_group"],
                data["caste"],
                data["income"],
                data["gotra"],
                data["manglik"],
                data["education"],
                data["occupation"],
                data["father_name"],
                data["father_occupation"],
                data["mother_name"],
                data["siblings"],
                data["city"],
                data["address"],
                data["about"],
                data["contact_phone"],
                data["parents_contact"],
                data["contact_email"],
                photo_b64,
            ),
        )

def list_profiles(gender, city):
    query = """
        select full_name,gender,dob,birth_time,birth_place,height,blood_group,
               caste,income,gotra,manglik,education,occupation,father_name,
               father_occupation,mother_name,siblings,city,address,about,
               contact_phone,parents_contact,contact_email,photo_b64,created_at
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
                "birth_time": row[3] or "",
                "birth_place": row[4] or "",
                "height": row[5] or "",
                "blood_group": row[6] or "",
                "caste": row[7] or "",
                "income": row[8] or "",
                "gotra": row[9] or "",
                "manglik": row[10] or "",
                "education": row[11] or "",
                "occupation": row[12] or "",
                "father_name": row[13] or "",
                "father_occupation": row[14] or "",
                "mother_name": row[15] or "",
                "siblings": row[16] or "",
                "city": row[17] or "",
                "address": row[18] or "",
                "about": row[19] or "",
                "contact_phone": row[20] or "",
                "parents_contact": row[21] or "",
                "contact_email": row[22] or "",
                "photo_b64": row[23] or "",
                "created_at": row[24].isoformat() if row[24] else "",
            }
        )
    return profiles

def current_user_login(request: Request):
    return request.cookies.get(COOKIE_NAME, "").strip()

def current_user(request: Request):
    return get_user_by_login(current_user_login(request))

def avatar_text(login):
    cleaned = (login or "").strip()
    return (cleaned[:2] or "NB").upper()

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/api/lang/{lang}")
def set_lang(lang: str, request: Request):
    if lang not in TRANSLATIONS:
        lang = "hi"
    response = RedirectResponse(url=request.headers.get("referer", "/"))
    response.set_cookie(LANG_COOKIE, lang, max_age=31536000)
    return response

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
    birth_time: str = Form(""),
    birth_place: str = Form(""),
    height: str = Form(""),
    blood_group: str = Form(""),
    caste: str = Form(""),
    income: str = Form(""),
    gotra: str = Form(""),
    manglik: str = Form(""),
    education: str = Form(""),
    occupation: str = Form(""),
    father_name: str = Form(""),
    father_occupation: str = Form(""),
    mother_name: str = Form(""),
    siblings: str = Form(""),
    city: str = Form(""),
    address: str = Form(""),
    about: str = Form(""),
    contact_phone: str = Form(""),
    parents_contact: str = Form(""),
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
            "birth_time": birth_time.strip(),
            "birth_place": birth_place.strip(),
            "height": height.strip(),
            "blood_group": blood_group.strip(),
            "caste": caste.strip(),
            "income": income.strip(),
            "gotra": gotra.strip(),
            "manglik": manglik,
            "education": education.strip(),
            "occupation": occupation.strip(),
            "father_name": father_name.strip(),
            "father_occupation": father_occupation.strip(),
            "mother_name": mother_name.strip(),
            "siblings": siblings.strip(),
            "city": city.strip(),
            "address": address.strip(),
            "about": about.strip(),
            "contact_phone": contact_phone.strip(),
            "parents_contact": parents_contact.strip(),
            "contact_email": contact_email.strip(),
        },
        photo_bytes,
    )
    return {"message": "Profile saved."}

@app.get("/health")
def health():
    return {"ok": True}
