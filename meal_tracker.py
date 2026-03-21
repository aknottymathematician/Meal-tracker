"""
NutriTrack v7 — Personalised Nutrition Tracker
Full CRUD: add, edit, delete, reorder meals per day/person.
Reads style.css from the same directory for all visual styling.
"""

import streamlit as st
from datetime import datetime, date, timezone, timedelta
import requests, time, jwt, calendar as cal_lib
from pathlib import Path
import threading

IST   = timezone(timedelta(hours=5, minutes=30))
TODAY = datetime.now(IST).date()
DAYS  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

st.set_page_config(
    page_title="NutriTrack",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

def load_css():
    p = Path(__file__).parent / "style.css"
    if p.exists():
        st.markdown(f"<style>{p.read_text()}</style>", unsafe_allow_html=True)

load_css()

# ── Default meal plan ──────────────────────────────────────

DEFAULT_MEALS = {
    "Mon": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "500–600 ml of plain water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 scoop whey protein in 200 ml water + 30 g moong sprouts (15 g raw)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 1 multigrain bread slice + 70 g tofu bhurji"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training: plain water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400 ml oats protein smoothie + 30 g moong sprouts (15 g raw)"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites (bhurji or omelette)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 3 methi/cabbage parathas + 100 g tofu bhurji + 100 g skyr yogurt"},
            {"slot": "Evening · 4 PM",         "desc": "20 g roasted peanuts + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 1 multigrain bread + 150 g tofu bhurji"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Tue": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "300–400 ml of plain water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 scoop whey protein in 200 ml water + 30 g chickpeas (15 g raw)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 2 jowar bhakri + 50 g low fat pan fry paneer + 50 g plain curd + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 1 jowar bhakri + 70 g low fat tossed paneer"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400 ml oats protein smoothie + 30 g boiled chickpeas (15 g raw)"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 3 jowar bhakri + 100 g low fat pan fry paneer + 100 g plain curd"},
            {"slot": "Evening · 4 PM",         "desc": "20 g makhana + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 2 jowar bhakri + 150 g low fat tossed paneer"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Wed": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "500–600 ml of plain water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 vegetable sandwich + 1 scoop whey protein in 200 ml water"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 200 g mix veg pulao (rice + quinoa) + 100 g skyr protein yogurt + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "50 g boiled chickpeas / 150 ml dal (30 g raw) + 70 g air fried paneer & 100 g sautéed veggies OR 70 g pan sautéed paneer & 100 g veggies"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During training 6–7 AM: Supply 6 salts (1 sachet in 600 ml)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "2 veg sandwiches + 200 ml toned milk + 1 scoop whey protein"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 200 g mix veg pulao (rice + quinoa) + 100 g chicken kheema + 200 ml chaas"},
            {"slot": "Evening · 4 PM",         "desc": "20 g roasted peanuts + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi + 100 g boiled chickpeas / 150 ml dal (30 g) + 150 g air fried / pan sautéed chicken + 100 g sautéed veggies"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Thu": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "500–600 ml of plain water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 scoop whey protein in 200 ml water + 30 g kala channa (15 g raw, soak overnight)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 2 whole wheat roti + 100 g rajma masala (30 g dry rajma) + 50 g plain curd + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 1 whole wheat roti + 70 g tofu stir fry"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400 ml oats protein porridge + 30 g boiled kala channa (15 g raw)"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 3 whole wheat roti + 150 g rajma masala (50 g rajma) + 100 g skyr yogurt"},
            {"slot": "Evening · 4 PM",         "desc": "20 g makhana + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 2 whole wheat roti + 150 g tofu stir fry"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Fri": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "No specific instruction (rest/light day)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "2 bread toast + 1 scoop whey protein in 200 ml water + 30 g chickpeas (15 g raw)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 2 jowar bhakri + 50 g low fat palak paneer + 50 g plain curd + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 1 jowar bhakri + 70 g low fat palak paneer"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During training 6–7 AM: Supply 6 salts (1 sachet in 600 ml)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "3 bread toast + 4 egg whites (omelette/bhurji) + 200 ml toned milk + 1 scoop whey protein"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 3 jowar bhakri + 100 g low fat palak paneer + 100 g plain curd"},
            {"slot": "Evening · 4 PM",         "desc": "20 g roasted peanuts + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100 g sabzi/salad + 2 jowar bhakri + 150 g low fat palak paneer"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Sat": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "1 sachet Supply 6 salts in 500–600 ml water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 scoop whey protein in 200 ml water + 30 g chickpeas (15 g raw)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "Tofu burrito wrap (2 whole wheat roti + 50 g tofu + 100 g veggies + 15 g salsa) + 150 ml chaas + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "200 g shirataki noodles (100 g noodles + 100 g veggies) + 200 ml tomato soup + 100 g skyr protein yogurt"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400 ml oats protein smoothie + 30 g moong sprouts (15 g raw)"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + tofu burrito wrap (2 wheat roti + 100 g tofu + 20 g boiled rajma + 75 g veggies + 15 g salsa) + 200 ml chaas"},
            {"slot": "Evening · 4 PM",         "desc": "20 g makhana + ½ scoop whey in 200 ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "250 g shirataki noodles (150 g noodles + 100 g veggies) + 150 g chicken stir fry + 200 ml tomato soup"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
    "Sun": {
        "p1": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 glass of plain water + 1 med banana OR 1 whole fruit (Apple/Orange/Chickoo/Guava)"},
            {"slot": "During training",         "desc": "1 sachet Supply 6 salts in 500–600 ml water"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "1 scoop whey protein in 200 ml water + 30 g kala channa (15 g raw)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g raw salad + 200 g vegetable khichdi (75 g rice + 75 g dal + 50 g veggies) + 100 g skyr protein yogurt + 1 scoop samah powder"},
            {"slot": "Evening snack · 4 PM",   "desc": "1 cup green tea + 1 vit-C rich fruit"},
            {"slot": "Dinner · 7 PM",          "desc": "⭐ Enjoyment meal"},
        ],
        "p2": [
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt)"},
            {"slot": "Pre-training · 5:30–6 AM (long run)","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee | During run: Supply 6 salts (1 sachet in 500 ml) + energy gel with caffeine at 45 min + plain energy gel at 80 min"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400 ml oats protein smoothie + 30 g boiled chickpeas (15 g raw)"},
            {"slot": "Mid-morning · 10 AM",    "desc": "1 vit-C rich fruit + 4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100 g salad + 250 g veg khichdi (100 g rice + 100 g dal + 50 g veggies) OR 250 g chicken biryani (150 g rice + 100 g chicken curry) + 100 g cucumber raita"},
            {"slot": "Evening · 4 PM",         "desc": "150 g yogurt bowl (100 g yogurt + ½ scoop whey + 1 whole fruit + 1 tsp chia seeds)"},
            {"slot": "Dinner · 7 PM",          "desc": "⭐ Enjoyment meal"},
            {"slot": "Bedtime",                "desc": "200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ],
    },
}


# ── Firebase REST ──────────────────────────────────────────

_TK = {"v": None, "e": 0}

def get_token():
    now = int(time.time())
    if _TK["v"] and now < _TK["e"] - 60:
        return _TK["v"]
    c      = st.secrets["firebase_credentials"]
    pk     = c["private_key"].replace("\\n", "\n")
    signed = jwt.encode(
        {"iss": c["client_email"], "sub": c["client_email"],
         "aud": "https://oauth2.googleapis.com/token",
         "iat": now, "exp": now + 3600,
         "scope": "https://www.googleapis.com/auth/datastore"},
        pk, algorithm="RS256",
    )
    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": signed},
        timeout=10,
    )
    r.raise_for_status()
    d = r.json()
    _TK["v"] = d["access_token"]
    _TK["e"] = now + d.get("expires_in", 3600)
    return _TK["v"]

def _h():
    return {"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"}

def _u(path):
    pid = st.secrets["firebase_credentials"]["project_id"]
    return f"https://firestore.googleapis.com/v1/projects/{pid}/databases/(default)/documents/{path}"

def _to(v):
    if isinstance(v, bool):  return {"booleanValue": v}
    if isinstance(v, int):   return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str):   return {"stringValue": v}
    if isinstance(v, dict):  return {"mapValue":  {"fields": {k: _to(u) for k, u in v.items()}}}
    if isinstance(v, list):  return {"arrayValue": {"values": [_to(i) for i in v]}}
    return {"nullValue": None}

def _fr(v):
    if "stringValue"    in v: return v["stringValue"]
    if "booleanValue"   in v: return v["booleanValue"]
    if "integerValue"   in v: return int(v["integerValue"])
    if "doubleValue"    in v: return v["doubleValue"]
    if "nullValue"      in v: return None
    if "timestampValue" in v: return v["timestampValue"]
    if "mapValue"       in v: return {k: _fr(u) for k, u in v["mapValue"].get("fields", {}).items()}
    if "arrayValue"     in v: return [_fr(i) for i in v["arrayValue"].get("values", [])]
    return None

def fs_get(col, did):
    r = requests.get(_u(f"{col}/{did}"), headers=_h(), timeout=10)
    if r.status_code == 404: return None
    r.raise_for_status()
    return {k: _fr(v) for k, v in r.json().get("fields", {}).items()}

def fs_set(col, did, data):
    requests.patch(
        _u(f"{col}/{did}"), headers=_h(),
        json={"fields": {k: _to(v) for k, v in data.items()}}, timeout=10,
    ).raise_for_status()

def fs_del(col, did):
    requests.delete(_u(f"{col}/{did}"), headers=_h(), timeout=10)

def fs_list(col, filters=None):
    r = requests.get(_u(col), headers=_h(), timeout=20)
    if r.status_code != 200: return []
    out = []
    for doc in r.json().get("documents", []):
        did    = doc["name"].split("/")[-1]
        fields = {k: _fr(v) for k, v in doc.get("fields", {}).items()}
        if filters and not all(fields.get(f["field"]) == f["value"] for f in filters):
            continue
        out.append({"id": did, **fields})
    return out

def fs_add(col, data):
    r = requests.post(
        _u(col), headers=_h(),
        json={"fields": {k: _to(v) for k, v in data.items()}}, timeout=10,
    )
    r.raise_for_status()
    return r.json()["name"].split("/")[-1]


# ── Cloudinary ─────────────────────────────────────────────

def upload_photo(fb, fn) -> str:
    r = requests.post(
        f"https://api.cloudinary.com/v1_1/{st.secrets['cloudinary_cloud_name']}/image/upload",
        data={"upload_preset": st.secrets["cloudinary_upload_preset"]},
        files={"file": (fn, fb)}, timeout=30,
    )
    return r.json().get("secure_url", "") if r.status_code == 200 else ""


# ── Meal plan — dynamic, stored in Firestore ───────────────

def _default_plan(day: str, person: str) -> list:
    return [{"slot": m["slot"], "desc": m["desc"]} for m in DEFAULT_MEALS[day][person]]

def load_day_plan(day: str, person: str) -> list:
    """Session-state backed — instant on rerun, loads Firestore once per session."""
    sk = f"_plan_{day}_{person}"
    if sk not in st.session_state:
        doc = fs_get("meal_plans", f"{day}_{person}")
        if doc and doc.get("meals"):
            st.session_state[sk] = [
                {"slot": m.get("slot", ""), "desc": m.get("desc", "")}
                for m in doc["meals"]
            ]
        else:
            st.session_state[sk] = _default_plan(day, person)
    return st.session_state[sk]

def save_day_plan(day: str, person: str, meals: list):
    """
    Update session state instantly AND write to Firestore synchronously.
    Plan edits are infrequent so the ~300ms wait is acceptable.
    (Background threads cannot access st.secrets, so async writes silently fail.)
    """
    sk = f"_plan_{day}_{person}"
    frozen = [{"slot": m["slot"], "desc": m["desc"]} for m in meals]
    st.session_state[sk] = frozen
    fs_set("meal_plans", f"{day}_{person}", {"meals": frozen})

def reset_day_plan(day: str, person: str):
    sk = f"_plan_{day}_{person}"
    if sk in st.session_state:
        del st.session_state[sk]
    fs_del("meal_plans", f"{day}_{person}")


# ── Tracking ───────────────────────────────────────────────

def tk(d: date, person, idx):
    return f"{d.isoformat()}_{person}_{idx}"

@st.cache_data(ttl=60)
def load_all_tracking() -> dict:
    return {doc["id"]: doc for doc in fs_list("tracking")}

def load_day_entries(date_str: str) -> dict:
    """Session-state backed — instant on rerun."""
    sk = f"_de_{date_str}"
    if sk not in st.session_state:
        st.session_state[sk] = {
            doc["id"]: doc
            for doc in fs_list("tracking")
            if doc["id"].startswith(date_str + "_")
        }
    return st.session_state[sk]

def _write_entry_bg(doc_id: str, entry: dict, token: str, pid: str):
    """Background thread — all credentials pre-fetched on main thread."""
    try:
        url  = (f"https://firestore.googleapis.com/v1/projects/{pid}"
                f"/databases/(default)/documents/tracking/{doc_id}")
        hdrs = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        requests.patch(url, headers=hdrs,
                       json={"fields": {k: _to(v) for k, v in entry.items()}},
                       timeout=10)
    except Exception:
        pass

def update_entry(date_str: str, doc_id: str, entry: dict):
    """Update session state instantly, fire Firestore write in background.
    All st.secrets access happens on the main thread before thread spawn."""
    sk = f"_de_{date_str}"
    if sk not in st.session_state:
        st.session_state[sk] = {}
    st.session_state[sk][doc_id] = dict(entry)
    load_all_tracking.clear()
    try:
        token = get_token()
        pid   = st.secrets["firebase_credentials"]["project_id"]
    except Exception:
        return  # If we can't get creds, skip background write (already in session state)
    threading.Thread(target=_write_entry_bg,
                     args=(doc_id, dict(entry), token, pid),
                     daemon=True).start()

def bust_tracking(date_str: str):
    sk = f"_de_{date_str}"
    if sk in st.session_state:
        del st.session_state[sk]
    load_all_tracking.clear()

def day_pct(d: date, all_t: dict) -> float:
    day_name = DAYS[d.weekday()]
    meals    = load_day_plan(day_name, "p1") + load_day_plan(day_name, "p2")
    total    = len(meals)
    done     = sum(
        1 for p in ["p1", "p2"]
        for i in range(len(load_day_plan(day_name, p)))
        if all_t.get(tk(d, p, i), {}).get("status", "pending") in ("done", "skipped")
    )
    return done / total if total else 0


# ── Auth ───────────────────────────────────────────────────

def check_password() -> bool:
    if st.session_state.get("auth"): return True
    st.markdown(
        '<div class="nt-login">'
        '<div class="nt-login-mark">🌿</div>'
        '<div class="nt-login-title">NutriTrack</div>'
        '<div class="nt-login-sub">Your personalised nutrition companion</div>'
        '</div>', unsafe_allow_html=True)
    pw = st.text_input("", type="password", placeholder="Enter password",
                       label_visibility="collapsed")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Sign in", use_container_width=True, type="primary"):
            if pw == st.secrets["app_password"]:
                st.session_state["auth"] = True; st.rerun()
            else:
                st.error("Incorrect password.")
    return False


# ── HTML helpers ───────────────────────────────────────────

def badge_html(status: str) -> str:
    labels = {"done": "Done", "skipped": "Skipped", "pending": "Pending"}
    return f'<span class="nt-badge {status}">{labels.get(status, "Pending")}</span>'

def person_header(person: str) -> str:
    if person == "p1":
        return ('<div class="nt-person p1"><div class="nt-person-avatar">P1</div>'
                '<div><div class="nt-person-name">Person 1</div>'
                '<div class="nt-person-role">Vegetarian</div></div></div>')
    return ('<div class="nt-person p2"><div class="nt-person-avatar">P2</div>'
            '<div><div class="nt-person-name">Person 2</div>'
            '<div class="nt-person-role">Non-veg · Runner</div></div></div>')

def section_label(text: str, mt: bool = True) -> str:
    s = "margin-top:0" if not mt else ""
    return f'<div class="nt-section-label" style="{s}">{text}</div>'

def calendar_html(y, m, all_t, sel) -> str:
    fdow  = cal_lib.monthrange(y, m)[0]
    ndays = cal_lib.monthrange(y, m)[1]
    hdr   = "".join(f'<div class="nt-cal-hdr">{d}</div>'
                    for d in ["Mo","Tu","We","Th","Fr","Sa","Su"])
    cells = '<div class="nt-cal-empty"></div>' * fdow
    for n in range(1, ndays + 1):
        d   = date(y, m, n)
        ex  = (" nt-cal-today" if d == TODAY else "") + (" nt-cal-sel" if d == sel else "")
        if d > TODAY:
            css = "nt-cal-future"
        else:
            p   = day_pct(d, all_t)
            css = "nt-cal-none" if p == 0 else "nt-cal-part" if p < 0.8 else "nt-cal-full"
        cells += f'<div class="nt-cal-day {css}{ex}">{n}</div>'
    legend = """<div class="nt-cal-legend">
      <div class="nt-cal-leg"><div class="nt-cal-dot" style="background:var(--ocean-100);border:1px solid var(--ocean-400)"></div>Fully tracked</div>
      <div class="nt-cal-leg"><div class="nt-cal-dot" style="background:rgba(224,242,254,.7);border:1px solid var(--sky-400)"></div>Partial</div>
      <div class="nt-cal-leg"><div class="nt-cal-dot" style="background:rgba(255,255,255,.5);border:1px solid var(--border-md)"></div>Not started</div>
    </div>"""
    return (f'<div class="nt-cal-wrap">'
            f'<div class="nt-cal-grid">{hdr}{cells}</div>{legend}</div>')


# ── Meal card with CRUD controls ───────────────────────────

def meal_card_crud(
    d: date, person: str, idx: int,
    meal: dict, meals: list,
    day_entries: dict, is_future: bool
):
    """
    Renders a single meal card with:
    - Status tracking (done/skip)
    - Note + photo
    - Reorder (▲▼)
    - Inline edit (slot + desc)
    - Delete
    """
    day_name  = DAYS[d.weekday()]
    # Always read live slot/desc from session-state-backed plan
    _live_plan = load_day_plan(DAYS[d.weekday()], person)
    if idx < len(_live_plan):
        slot      = _live_plan[idx]["slot"]
        plan_desc = _live_plan[idx]["desc"]
    else:
        slot      = meal.get("slot", "")
        plan_desc = meal.get("desc", "")

    entry     = dict(day_entries.get(tk(d, person, idx),
                     {"status": "pending", "comment": "", "image_url": "", "planned_desc": ""}))
    status    = entry.get("status", "pending")
    comment   = entry.get("comment", "")
    image_url = entry.get("image_url", "")
    disp_desc = entry.get("planned_desc") or plan_desc

    uid       = f"{d.isoformat()}_{person}_{idx}"
    edit_key  = f"edit_{uid}"
    del_key   = f"del_confirm_{uid}"

    is_editing  = st.session_state.get(edit_key, False)
    is_noting   = st.session_state.get("active_note") == uid
    is_deleting = st.session_state.get(del_key, False)

    # ── Card HTML ──────────────────────────────────────────
    css = "nt-meal" + (" done" if status=="done" else " skipped" if status=="skipped" else "")
    st.markdown(
        f'<div class="{css}">'
        f'<div class="nt-meal-row">'
        f'<div class="nt-meal-body">'
        f'<div class="nt-meal-slot">{slot}</div>'
        f'<div class="nt-meal-desc">{disp_desc}</div>'
        f'</div>'
        f'<div>{badge_html(status)}</div>'
        f'</div></div>', unsafe_allow_html=True)

    if image_url:
        # Thumbnail row with expand toggle
        img_open_key = f"img_open_{uid}"
        thumb_col, expand_col = st.columns([4, 1])
        with thumb_col:
            st.image(image_url, width=90)
        with expand_col:
            expand_label = "🔍 Close" if st.session_state.get(img_open_key) else "🔍 View"
            if st.button(expand_label, key=f"imgbtn_{uid}", use_container_width=True):
                st.session_state[img_open_key] = not st.session_state.get(img_open_key, False)
        if st.session_state.get(img_open_key):
            st.image(image_url, use_container_width=True)

    if comment and not is_noting:
        st.markdown(f'<div class="nt-note">💬 {comment}</div>', unsafe_allow_html=True)

    # ── Action rows ────────────────────────────────────────
    if not is_future:
        # Row 1: status buttons
        c1, c2, c3, c4, c5, c6 = st.columns([4, 4, 1, 1, 1, 1])
        with c1:
            lbl = "Mark as done" if status != "done" else "↩ Undo done"
            if st.button(lbl, key=f"done_{uid}", use_container_width=True):
                entry["status"] = "done" if status != "done" else "pending"
                if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                update_entry(d.isoformat(), tk(d, person, idx), entry)
                st.rerun(scope="fragment")
        with c2:
            lbl = "Mark as skipped" if status != "skipped" else "↩ Undo skip"
            if st.button(lbl, key=f"skip_{uid}", use_container_width=True):
                entry["status"] = "skipped" if status != "skipped" else "pending"
                if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                update_entry(d.isoformat(), tk(d, person, idx), entry)
                st.rerun(scope="fragment")
        with c3:
            # Note/photo
            icon = "✏️" if (comment or image_url) else "📝"
            if st.button(icon, key=f"nbt_{uid}", use_container_width=True):
                st.session_state["active_note"] = uid if not is_noting else None
        with c4:
            # Move up
            if idx > 0:
                if st.button("▲", key=f"mup_{uid}", use_container_width=True):
                    meals[idx], meals[idx-1] = meals[idx-1], meals[idx]
                    save_day_plan(day_name, person, meals)
                    st.rerun(scope="fragment")
            else:
                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
        with c5:
            # Move down
            if idx < len(meals) - 1:
                if st.button("▼", key=f"mdn_{uid}", use_container_width=True):
                    meals[idx], meals[idx+1] = meals[idx+1], meals[idx]
                    save_day_plan(day_name, person, meals)
                    st.rerun(scope="fragment")
            else:
                st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)
        with c6:
            # Edit / delete toggle
            if st.button("⚙️", key=f"edt_{uid}", use_container_width=True):
                st.session_state[edit_key] = not is_editing
                if is_deleting:
                    st.session_state[del_key] = False

    else:
        # Future date — only allow edit/reorder, no tracking
        c4, c5, c6 = st.columns([1, 1, 1])
        with c4:
            if idx > 0:
                if st.button("▲", key=f"mup_f_{uid}", use_container_width=True):
                    meals[idx], meals[idx-1] = meals[idx-1], meals[idx]
                    save_day_plan(day_name, person, meals)
                    st.rerun(scope="fragment")
        with c5:
            if idx < len(meals) - 1:
                if st.button("▼", key=f"mdn_f_{uid}", use_container_width=True):
                    meals[idx], meals[idx+1] = meals[idx+1], meals[idx]
                    save_day_plan(day_name, person, meals)
                    st.rerun(scope="fragment")
        with c6:
            if st.button("⚙️", key=f"edt_f_{uid}", use_container_width=True):
                st.session_state[edit_key] = not is_editing

    # ── Note / photo panel ─────────────────────────────────
    if is_noting and not is_future:
        nc = st.text_area("Note", value=comment, key=f"ta_{uid}",
                          placeholder="Add a note, substitution, or observation…",
                          label_visibility="collapsed", height=72)
        up = st.file_uploader("Attach a photo", type=["jpg","jpeg","png","heic"],
                              key=f"slot_{uid}", label_visibility="collapsed")
        cs, cr = st.columns(2)
        with cs:
            if st.button("Save note", key=f"sv_{uid}", use_container_width=True):
                entry["comment"] = nc
                if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                if up:
                    with st.spinner("Uploading photo…"):
                        url = upload_photo(up.read(), up.name)
                    if url:
                        entry["image_url"] = url
                    else:
                        st.error("Upload failed — please try again.")
                        st.stop()
                update_entry(d.isoformat(), tk(d, person, idx), entry)
                st.session_state["active_note"] = None
                st.rerun(scope="fragment")
        with cr:
            if image_url and st.button("Remove photo", key=f"rm_{uid}", use_container_width=True):
                entry["image_url"] = ""
                update_entry(d.isoformat(), tk(d, person, idx), entry)
                st.rerun(scope="fragment")

    # ── Inline edit panel ──────────────────────────────────
    if is_editing:
        # Use session-state-backed draft values so widget state never goes stale.
        # On first open, seed from current plan. On rerun, keep draft as-is.
        draft_slot_key = f"draft_slot_{uid}"
        draft_desc_key = f"draft_desc_{uid}"
        if draft_slot_key not in st.session_state:
            st.session_state[draft_slot_key] = slot
        if draft_desc_key not in st.session_state:
            st.session_state[draft_desc_key] = plan_desc

        st.markdown('<div style="background:rgba(13,148,136,.04);border:1px solid var(--border-md);'
                    'border-radius:var(--r-md);padding:12px;margin-top:6px">', unsafe_allow_html=True)

        # Use on_change to keep draft in sync without needing Save to read widget value
        def _sync_slot():
            st.session_state[draft_slot_key] = st.session_state[f"nes_{uid}"]
        def _sync_desc():
            st.session_state[draft_desc_key] = st.session_state[f"ned_{uid}"]

        st.text_input("Slot / time",
                      value=st.session_state[draft_slot_key],
                      key=f"nes_{uid}",
                      label_visibility="collapsed",
                      placeholder="e.g. Breakfast · 8:30 AM",
                      on_change=_sync_slot)
        st.text_area("Description",
                     value=st.session_state[draft_desc_key],
                     key=f"ned_{uid}",
                     label_visibility="collapsed",
                     placeholder="Meal description",
                     height=72,
                     on_change=_sync_desc)

        e1, e2, e3 = st.columns(3)
        with e1:
            if st.button("Save", key=f"esv_{uid}", use_container_width=True):
                new_slot = st.session_state.get(draft_slot_key, slot).strip() or slot
                new_desc = st.session_state.get(draft_desc_key, plan_desc).strip() or plan_desc
                # Update the live plan
                live = load_day_plan(day_name, person)
                if idx < len(live):
                    live[idx] = {"slot": new_slot, "desc": new_desc}
                    save_day_plan(day_name, person, live)
                # Clear draft + close panel
                st.session_state.pop(draft_slot_key, None)
                st.session_state.pop(draft_desc_key, None)
                # Clear widget state so text inputs re-seed from new plan on next open
                st.session_state.pop(f"nes_{uid}", None)
                st.session_state.pop(f"ned_{uid}", None)
                st.session_state[edit_key] = False
                st.rerun(scope="fragment")
        with e2:
            if st.button("Cancel", key=f"ecn_{uid}", use_container_width=True):
                st.session_state.pop(draft_slot_key, None)
                st.session_state.pop(draft_desc_key, None)
                st.session_state.pop(f"nes_{uid}", None)
                st.session_state.pop(f"ned_{uid}", None)
                st.session_state[edit_key] = False
                st.rerun(scope="fragment")
        with e3:
            if st.button("🗑️ Delete", key=f"edel_{uid}", use_container_width=True):
                st.session_state[del_key] = not is_deleting
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Delete confirm ─────────────────────────────────────
    if is_deleting:
        st.warning(f"Delete **{slot}**? This cannot be undone.")
        dc1, dc2 = st.columns(2)
        with dc1:
            if st.button("Yes, delete", key=f"dyes_{uid}", use_container_width=True):
                meals.pop(idx)
                save_day_plan(day_name, person, meals)
                st.session_state.pop(del_key, None)
                st.session_state.pop(edit_key, None)
                st.rerun(scope="fragment")
        with dc2:
            if st.button("Cancel", key=f"dno_{uid}", use_container_width=True):
                st.session_state[del_key] = False
                st.rerun(scope="fragment")

    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


# ── Snacks ─────────────────────────────────────────────────

def render_snacks(d: date, person: str):
    st.markdown(section_label("Extra & unplanned"), unsafe_allow_html=True)
    snacks = fs_list("snacks", filters=[{"field":"date","value":d.isoformat()},
                                        {"field":"person","value":person}])
    for s in snacks:
        ts = s.get("timestamp", "")
        if "T" in ts:
            try: ts = datetime.fromisoformat(ts.replace("Z","+00:00")).strftime("%I:%M %p")
            except: ts = ""
        time_part = f" · {ts}" if ts else ""
        st.markdown(
            f'<div class="nt-snack"><div class="nt-snack-label">Snack{time_part}</div>'
            f'<div class="nt-snack-desc">{s.get("desc","")}</div></div>',
            unsafe_allow_html=True)
        if s.get("image_url"):
            simg_key = f"simg_open_{s['id']}"
            sc1, sc2 = st.columns([4, 1])
            with sc1:
                st.image(s["image_url"], width=90)
            with sc2:
                slbl = "🔍 Close" if st.session_state.get(simg_key) else "🔍 View"
                if st.button(slbl, key=f"sib_{s['id']}", use_container_width=True):
                    st.session_state[simg_key] = not st.session_state.get(simg_key, False)
            if st.session_state.get(simg_key):
                st.image(s["image_url"], use_container_width=True)
        if st.button("Remove", key=f"del_{s['id']}"):
            threading.Thread(target=fs_del, args=("snacks", s["id"]),
                             daemon=True).start()
            st.rerun(scope="fragment")

    if d <= TODAY:
        ak = f"add_{d.isoformat()}_{person}"
        if st.button("+ Log a snack", key=f"btn_{ak}"):
            st.session_state[ak] = not st.session_state.get(ak, False)
        if st.session_state.get(ak, False):
            desc = st.text_input("What did you have?", key=f"desc_{ak}",
                                 label_visibility="collapsed",
                                 placeholder="e.g. 1 chai + 2 biscuits…")
            img = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png","heic"],
                                   key=f"simg_{ak}", label_visibility="collapsed")
            if st.button("Save snack", key=f"log_{ak}", use_container_width=True):
                if desc.strip():
                    img_url = ""
                    if img:
                        with st.spinner("Uploading…"):
                            img_url = upload_photo(img.read(), img.name)
                    fs_add("snacks", {
                        "date": d.isoformat(), "person": person,
                        "desc": desc.strip(),  "image_url": img_url,
                        "timestamp": datetime.now(IST).isoformat(),
                    })
                    st.session_state[ak] = False; st.rerun(scope="fragment")
                else:
                    st.warning("Please describe what you had.")


# ── Add meal form ──────────────────────────────────────────

def add_meal_form(d: date, person: str, meals: list):
    day_name = DAYS[d.weekday()]
    ak = f"addmeal_{d.isoformat()}_{person}"

    if st.button("＋ Add a meal", key=f"ambt_{d.isoformat()}_{person}", use_container_width=True):
        st.session_state[ak] = not st.session_state.get(ak, False)

    if st.session_state.get(ak, False):
        st.markdown(
            '<div style="background:rgba(13,148,136,.04);border:1px solid var(--border-md);'
            'border-radius:var(--r-md);padding:12px;margin-top:6px">',
            unsafe_allow_html=True)
        ns = st.text_input("Slot / time", key=f"ams_{ak}",
                           label_visibility="collapsed",
                           placeholder="e.g. Post-workout · 9 AM")
        nd = st.text_area("Description", key=f"amd_{ak}",
                          label_visibility="collapsed",
                          placeholder="What will this meal contain?", height=72)
        a1, a2 = st.columns(2)
        with a1:
            if st.button("Add meal", key=f"amc_{ak}", use_container_width=True):
                if ns.strip() and nd.strip():
                    meals.append({"slot": ns.strip(), "desc": nd.strip()})
                    save_day_plan(day_name, person, meals)
                    st.session_state[ak] = False
                    st.rerun(scope="fragment")
                else:
                    st.warning("Both slot and description are required.")
        with a2:
            if st.button("Cancel", key=f"amx_{ak}", use_container_width=True):
                st.session_state[ak] = False; st.rerun(scope="fragment")
        st.markdown('</div>', unsafe_allow_html=True)


# ── Per-person meal list — fragment so note/edit reruns stay isolated ─────

@st.fragment
def render_person_meals(d: date, person: str, is_future: bool):
    """
    Fragment — partial reruns only.
    Always reads live plan + entries from session state.
    All st.rerun() inside use scope="fragment" to stay within this fragment.
    """
    day_name = DAYS[d.weekday()]
    meals    = load_day_plan(day_name, person)
    day_ent  = load_day_entries(d.isoformat())

    st.markdown(person_header(person), unsafe_allow_html=True)
    for i, meal in enumerate(meals):
        meal_card_crud(d, person, i, meal, meals, day_ent, is_future)
    add_meal_form(d, person, meals)
    if not is_future:
        render_snacks(d, person)


# ── Page: Tracker ──────────────────────────────────────────

def page_tracker():
    for k, v in [("sel_date", TODAY), ("cal_year", TODAY.year), ("cal_month", TODAY.month)]:
        if k not in st.session_state: st.session_state[k] = v

    sel = st.date_input("", value=st.session_state.sel_date,
                        min_value=date(2025, 1, 1), max_value=date(2026, 9, 30),
                        label_visibility="collapsed")
    if sel != st.session_state.sel_date:
        st.session_state.update(sel_date=sel, cal_year=sel.year, cal_month=sel.month)
        st.rerun()

    d = st.session_state.sel_date

    with st.expander("📅  Monthly overview", expanded=False):
        y, m  = st.session_state.cal_year, st.session_state.cal_month
        all_t = load_all_tracking()
        nc1, nc2, nc3 = st.columns([1, 4, 1])
        with nc1:
            if st.button("◀", key="cp", use_container_width=True):
                if m == 1: st.session_state.cal_year -= 1; st.session_state.cal_month = 12
                else:      st.session_state.cal_month -= 1
                st.rerun()
        with nc2:
            st.markdown(f'<div class="nt-cal-month" style="text-align:center;padding-top:6px">'
                        f'{cal_lib.month_name[m]} {y}</div>', unsafe_allow_html=True)
        with nc3:
            if (y, m) < (TODAY.year, TODAY.month):
                if st.button("▶", key="cn", use_container_width=True):
                    if m == 12: st.session_state.cal_year += 1; st.session_state.cal_month = 1
                    else:       st.session_state.cal_month += 1
                    st.rerun()
        st.markdown(calendar_html(y, m, all_t, d), unsafe_allow_html=True)

    day_name  = DAYS[d.weekday()]
    p1_meals  = load_day_plan(day_name, "p1")
    p2_meals  = load_day_plan(day_name, "p2")
    day_ent   = load_day_entries(d.isoformat())
    is_future = d > TODAY

    # Stats
    done_n = sum(
        1 for p, ms in [("p1", p1_meals), ("p2", p2_meals)]
        for i in range(len(ms))
        if day_ent.get(tk(d, p, i), {}).get("status", "pending") == "done"
    )
    skipped_n = sum(
        1 for p, ms in [("p1", p1_meals), ("p2", p2_meals)]
        for i in range(len(ms))
        if day_ent.get(tk(d, p, i), {}).get("status", "pending") == "skipped"
    )
    total_n   = len(p1_meals) + len(p2_meals)
    tracked_n = done_n + skipped_n
    pct       = round(tracked_n / total_n * 100) if total_n else 0
    label     = "Today" if d == TODAY else d.strftime("%A, %d %b %Y")

    st.markdown(
        f'<div class="nt-stats">'
        f'<div class="nt-stat"><div class="nt-stat-val">{done_n}</div>'
        f'<div class="nt-stat-lbl">Done</div></div>'
        f'<div class="nt-stat"><div class="nt-stat-val accent">{skipped_n}</div>'
        f'<div class="nt-stat-lbl">Skipped</div></div>'
        f'<div class="nt-stat"><div class="nt-stat-val">{pct}%</div>'
        f'<div class="nt-stat-lbl">Complete</div></div>'
        f'</div>'
        f'<div class="nt-progress-wrap">'
        f'<div class="nt-progress-fill" style="width:{pct}%"></div>'
        f'</div>'
        f'<div class="nt-progress-label">{label} · {tracked_n} of {total_n} meals tracked</div>',
        unsafe_allow_html=True)

    t1, t2 = st.tabs(["👤  Person 1 · Veg", "🏃  Person 2 · Runner"])

    with t1:
        render_person_meals(d, "p1", is_future)

    with t2:
        render_person_meals(d, "p2", is_future)


# ── Page: Measurements ─────────────────────────────────────

def last_date(docs, field):
    hits = [d for d in docs if d.get(field) is not None]
    return hits[-1].get("date") if hits else None

def is_due(last_str, days):
    if not last_str: return True
    return (TODAY - date.fromisoformat(last_str)).days >= days

def page_measurements():
    st.markdown(section_label("Body metrics", mt=False), unsafe_allow_html=True)
    t1, t2 = st.tabs(["👤  Person 1", "🏃  Person 2"])
    for tab, person in [(t1, "p1"), (t2, "p2")]:
        with tab:
            docs = sorted(
                fs_list("measurements", filters=[{"field": "person", "value": person}]),
                key=lambda x: x.get("date", ""),
            )
            lw      = last_date(docs, "weight")
            wdue    = is_due(lw, 7)
            wbadge  = "nt-due-now" if wdue else "nt-due-ok"
            wstatus = "Log now" if wdue else "Up to date"
            wlast   = f'<div class="nt-meas-last">Last entry: {lw}</div>' if lw else ""
            st.markdown(
                f'<div class="nt-meas-card"><div class="nt-meas-header">'
                f'<div class="nt-meas-title">Weight</div>'
                f'<span class="nt-due-badge {wbadge}">{wstatus}</span>'
                f'</div><div style="font-size:11px;color:var(--n400)">Log weekly</div>'
                f'{wlast}</div>', unsafe_allow_html=True)
            with st.expander("Log weight entry", expanded=wdue):
                wv = st.number_input("Weight (kg)", 30.0, 200.0, step=0.1,
                                     key=f"wv_{person}", format="%.1f")
                wd = st.date_input("Date", TODAY, max_value=TODAY, key=f"wd_{person}")
                if st.button("Save weight", key=f"swt_{person}", use_container_width=True):
                    ex = fs_get("measurements", f"{person}_{wd.isoformat()}") or {}
                    ex.update({"person": person, "date": wd.isoformat(), "weight": float(wv)})
                    fs_set("measurements", f"{person}_{wd.isoformat()}", ex)
                    st.success(f"✓  {wv} kg saved for {wd}"); st.rerun()

            lh      = last_date(docs, "hip")
            hdue    = is_due(lh, 14)
            hbadge  = "nt-due-now" if hdue else "nt-due-ok"
            hstatus = "Log now" if hdue else "Up to date"
            hlast   = f'<div class="nt-meas-last">Last entry: {lh}</div>' if lh else ""
            st.markdown(
                f'<div class="nt-meas-card" style="margin-top:4px"><div class="nt-meas-header">'
                f'<div class="nt-meas-title">Hip & Waist</div>'
                f'<span class="nt-due-badge {hbadge}">{hstatus}</span>'
                f'</div><div style="font-size:11px;color:var(--n400)">Log fortnightly</div>'
                f'{hlast}</div>', unsafe_allow_html=True)
            with st.expander("Log hip & waist entry", expanded=hdue):
                hc1, hc2 = st.columns(2)
                with hc1:
                    hv = st.number_input("Hip (cm)", 50.0, 200.0, step=0.5,
                                         key=f"hv_{person}", format="%.1f")
                with hc2:
                    wv2 = st.number_input("Waist (cm)", 40.0, 200.0, step=0.5,
                                          key=f"wstv_{person}", format="%.1f")
                hd = st.date_input("Date", TODAY, max_value=TODAY, key=f"hd_{person}")
                if st.button("Save measurements", key=f"shw_{person}", use_container_width=True):
                    ex = fs_get("measurements", f"{person}_{hd.isoformat()}") or {}
                    ex.update({"person": person, "date": hd.isoformat(),
                                "hip": float(hv), "waist": float(wv2)})
                    fs_set("measurements", f"{person}_{hd.isoformat()}", ex)
                    st.success(f"✓  Hip {hv} cm · Waist {wv2} cm saved"); st.rerun()

            if docs:
                st.markdown(section_label("Progress trends"), unsafe_allow_html=True)
                wt_rows = [(d["date"], d["weight"]) for d in docs if d.get("weight") is not None]
                if len(wt_rows) > 1:
                    st.caption("Weight (kg)")
                    st.line_chart({"Weight": {r[0]: r[1] for r in wt_rows}})
                hw_rows = [(d["date"], d.get("hip"), d.get("waist"))
                           for d in docs if d.get("hip") is not None]
                if len(hw_rows) > 1:
                    st.caption("Hip & Waist (cm)")
                    st.line_chart({"Hip":   {r[0]: r[1] for r in hw_rows if r[1]},
                                   "Waist": {r[0]: r[2] for r in hw_rows if r[2]}})
            else:
                st.info("No measurements logged yet. Start logging to see your progress trends here.")


# ── Page: Edit plan (week-level overview + reset) ──────────

def page_edit_plan():
    st.markdown(section_label("Edit meal plan", mt=False), unsafe_allow_html=True)
    st.caption(
        "Changes made here or in the Tracker tab persist for all future occurrences. "
        "Use Reset to restore any day back to the original plan."
    )
    day  = st.selectbox("Day", DAYS, label_visibility="collapsed")
    t1, t2 = st.tabs(["👤  Person 1", "🏃  Person 2"])

    for tab, person in [(t1, "p1"), (t2, "p2")]:
        with tab:
            st.markdown(person_header(person), unsafe_allow_html=True)
            meals     = load_day_plan(day, person)
            default   = [{"slot": m["slot"], "desc": m["desc"]} for m in DEFAULT_MEALS[day][person]]
            is_custom = meals != default

            if is_custom:
                st.info(f"This day has {len(meals)} meals (default has {len(default)}).")
                if st.button("Reset to default plan", key=f"rst_{day}_{person}",
                             use_container_width=True):
                    reset_day_plan(day, person)
                    st.success("Reset to default plan."); st.rerun()

            for i, meal in enumerate(meals):
                pk = f"ep_{day}_{person}_{i}"
                is_changed = i >= len(default) or meal != default[i]
                title = meal["slot"] + ("  ·  ✏️" if is_changed else "")
                with st.expander(title, expanded=False):
                    dsk = f"dslot_{pk}"
                    ddk = f"ddesc_{pk}"
                    if dsk not in st.session_state:
                        st.session_state[dsk] = meal["slot"]
                    if ddk not in st.session_state:
                        st.session_state[ddk] = meal["desc"]
                    def _ss(): st.session_state[dsk] = st.session_state[f"es_{pk}"]
                    def _sd(): st.session_state[ddk] = st.session_state[f"ed_{pk}"]
                    st.text_input("Slot / time",
                                  value=st.session_state[dsk],
                                  key=f"es_{pk}",
                                  label_visibility="collapsed",
                                  placeholder="e.g. Breakfast · 8:30 AM",
                                  on_change=_ss)
                    st.text_area("Description",
                                 value=st.session_state[ddk],
                                 key=f"ed_{pk}",
                                 height=80,
                                 label_visibility="collapsed",
                                 on_change=_sd)
                    cc1, cc2, cc3 = st.columns(3)
                    with cc1:
                        if st.button("Save", key=f"sv_{pk}", use_container_width=True):
                            new_slot = st.session_state.get(dsk, meal["slot"]).strip() or meal["slot"]
                            new_desc = st.session_state.get(ddk, meal["desc"]).strip() or meal["desc"]
                            meals[i] = {"slot": new_slot, "desc": new_desc}
                            save_day_plan(day, person, meals)
                            # Clear widget + draft state so expander re-seeds on reopen
                            for k in [dsk, ddk, f"es_{pk}", f"ed_{pk}"]:
                                st.session_state.pop(k, None)
                            st.success("Saved."); st.rerun()
                    with cc2:
                        if st.button("▲ Move up", key=f"mup_{pk}", use_container_width=True):
                            if i > 0:
                                meals[i], meals[i-1] = meals[i-1], meals[i]
                                save_day_plan(day, person, meals)
                                st.rerun()
                    with cc3:
                        if st.button("🗑️ Delete", key=f"del_{pk}", use_container_width=True):
                            meals.pop(i)
                            save_day_plan(day, person, meals)
                            st.success("Meal removed."); st.rerun()

            # Add new meal
            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
            nak = f"nadd_{day}_{person}"
            if st.button("＋ Add a meal to this day", key=f"nabt_{day}_{person}",
                         use_container_width=True):
                st.session_state[nak] = not st.session_state.get(nak, False)
            if st.session_state.get(nak, False):
                nns = st.text_input("Slot / time", key=f"nams_{nak}",
                                    label_visibility="collapsed",
                                    placeholder="e.g. Post-workout · 9 AM")
                nnd = st.text_area("Description", key=f"namd_{nak}",
                                   label_visibility="collapsed",
                                   placeholder="Meal description", height=72)
                na1, na2 = st.columns(2)
                with na1:
                    if st.button("Add", key=f"namc_{nak}", use_container_width=True):
                        if nns.strip() and nnd.strip():
                            meals.append({"slot": nns.strip(), "desc": nnd.strip()})
                            save_day_plan(day, person, meals)
                            st.session_state[nak] = False
                            st.rerun()
                        else:
                            st.warning("Both slot and description are required.")
                with na2:
                    if st.button("Cancel", key=f"nax_{nak}", use_container_width=True):
                        st.session_state[nak] = False; st.rerun()


# ── Main ───────────────────────────────────────────────────

def main():
    if not check_password(): return

    today_str = TODAY.strftime("%a, %d %b %Y")
    st.markdown(
        f'<div class="nt-header">'
        f'<div class="nt-brand"><div class="nt-logo">🌿</div>'
        f'<div><div class="nt-brand-name">NutriTrack</div>'
        f'<div class="nt-brand-sub">6-month nutrition programme</div></div></div>'
        f'<div class="nt-header-meta">'
        f'<div class="nt-header-date">{today_str}</div>'
        f'<div class="nt-header-plan">Personalised plan</div>'
        f'</div></div>', unsafe_allow_html=True)

    page = st.radio("", ["📅  Tracker", "📏  Measurements", "✏️  Edit plan"],
                    horizontal=True, label_visibility="collapsed")

    if   page == "📅  Tracker":       page_tracker()
    elif page == "📏  Measurements":  page_measurements()
    else:                              page_edit_plan()

    with st.expander("⚙️  Settings"):
        st.caption("NutriTrack · v7.0")
        if st.button("Sign out", type="secondary"):
            st.session_state["auth"] = False; st.rerun()


if __name__ == "__main__":
    main()
