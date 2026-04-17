import base64
import os
from datetime import date

import psycopg
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("SUPA_POOL_URL") or os.getenv("SUPA_BASS", "")

st.set_page_config(page_title="Nagar Brahmin Matrimony", page_icon="🧡", layout="centered")


def db():
    if not DB_URL:
        st.error("Missing DB URL. Set SUPA_POOL_URL in .env (recommended).")
        st.stop()
    try:
        return psycopg.connect(DB_URL)
    except Exception:
        st.error(
            "Database connection failed. Your direct Supabase URL is IPv6-only.\n\n"
            "Use shared pooler IPv4 URL in `.env`:\n"
            "`SUPA_POOL_URL=postgresql://postgres.<PROJECT_REF>:<PASSWORD>@<POOLER_HOST>:6543/postgres?sslmode=require`\n\n"
            "Get this exact string from Supabase Dashboard -> Connect -> Connection pooling."
        )
        st.stop()


def init_db():
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            create table if not exists nb_users(
                login text primary key,
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


def sign_up(login, password):
    with db() as conn, conn.cursor() as cur:
        cur.execute("insert into nb_users(login,password) values(%s,%s) on conflict (login) do nothing", (login.strip(), password))
        return cur.rowcount == 1


def sign_in(login, password):
    with db() as conn, conn.cursor() as cur:
        cur.execute("select login from nb_users where login=%s and password=%s", (login.strip(), password))
        return cur.fetchone()


def save_profile(user_login, form, photo):
    photo_b64 = base64.b64encode(photo.getvalue()).decode() if photo else ""
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            """
            insert into nb_profiles(created_by_login,full_name,gender,dob,gotra,manglik,education,occupation,city,about,contact_phone,contact_email,photo_b64)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (user_login, form["full_name"], form["gender"], form["dob"], form["gotra"], form["manglik"], form["education"], form["occupation"], form["city"], form["about"], form["contact_phone"], form["contact_email"], photo_b64),
        )


def list_profiles(gender, city):
    q = "select full_name,gender,dob,gotra,manglik,education,occupation,city,about,contact_phone,contact_email,photo_b64,created_at from nb_profiles where 1=1"
    args = []
    if gender != "All":
        q += " and gender=%s"
        args.append(gender)
    if city:
        q += " and city ilike %s"
        args.append(f"%{city.strip()}%")
    q += " order by created_at desc"
    with db() as conn, conn.cursor() as cur:
        cur.execute(q, args)
        return cur.fetchall()


init_db()
st.title("Nagar Brahmin Matrimony")
st.caption("Simple community prototype for families and elders")

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    mode = st.radio("Start", ["Sign In", "Sign Up"], horizontal=True)
    login = st.text_input("Email or Phone")
    password = st.text_input("Password", type="password")
    if st.button(mode):
        if not login or not password:
            st.warning("Please fill both fields.")
        elif mode == "Sign Up":
            if sign_up(login, password):
                st.success("Account created. Please sign in.")
            else:
                st.error("Account already exists.")
        else:
            user = sign_in(login, password)
            if user:
                st.session_state.user = {"login": user[0]}
                st.rerun()
            else:
                st.error("Invalid login.")
    st.stop()

nav = st.radio("Menu", ["Create Profile", "Browse Profiles", "My Account"], horizontal=True)

if nav == "Create Profile":
    with st.form("profile"):
        full_name = st.text_input("Full Name")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        dob = st.date_input("Date of Birth", value=date(1998, 1, 1), min_value=date(1960, 1, 1), max_value=date.today())
        gotra = st.text_input("Gotra")
        manglik = st.selectbox("Manglik", ["No", "Yes", "Not Sure"])
        education = st.text_input("Education")
        occupation = st.text_input("Occupation")
        city = st.text_input("City")
        contact_phone = st.text_input("Contact Phone")
        contact_email = st.text_input("Contact Email")
        about = st.text_area("About / Family Details")
        photo = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])
        ok = st.form_submit_button("Save Profile")
    if ok:
        if not full_name:
            st.warning("Full name is required.")
        else:
            save_profile(
                st.session_state.user["login"],
                {
                    "full_name": full_name,
                    "gender": gender,
                    "dob": dob,
                    "gotra": gotra,
                    "manglik": manglik,
                    "education": education,
                    "occupation": occupation,
                    "city": city,
                    "about": about,
                    "contact_phone": contact_phone,
                    "contact_email": contact_email,
                },
                photo,
            )
            st.success("Profile saved.")

elif nav == "Browse Profiles":
    c1, c2 = st.columns(2)
    with c1:
        g = st.selectbox("Filter Gender", ["All", "Male", "Female", "Other"])
    with c2:
        c = st.text_input("Filter City")
    rows = list_profiles(g, c)
    st.caption(f"{len(rows)} profile(s)")
    for r in rows:
        name, gender, dob, gotra, manglik, edu, occ, city, about, phone, email, photo_b64, created = r
        age = (date.today() - dob).days // 365 if dob else "-"
        img = (
            f"<img src='data:image/jpeg;base64,{photo_b64}' style='width:84px;height:84px;border-radius:12px;object-fit:cover;border:1px solid #ead7bf'/>"
            if photo_b64
            else ""
        )
        st.markdown(
            f"""
            <div class='card'>
                <div style='display:flex;gap:12px;align-items:center'>{img}<div><h4 style='margin:0'>{name}</h4><small>{gender} | {age} yrs | {city or '-'}</small></div></div>
                <p style='margin:.6rem 0 0'><b>Gotra:</b> {gotra or '-'} | <b>Manglik:</b> {manglik or '-'}<br><b>Education:</b> {edu or '-'}<br><b>Occupation:</b> {occ or '-'}<br><b>Contact:</b> {phone or '-'} / {email or '-'}<br><b>About:</b> {about or '-'}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

else:
    st.write(f"Signed in as: `{st.session_state.user['login']}`")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

st.markdown("---")
st.caption("Developed by Yash Mahesh Rawal | जय हत्केश")
