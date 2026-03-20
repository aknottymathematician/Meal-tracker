"""
NutriTrack — Personalised Nutrition Tracker
Reads style.css from the same directory for all visual styling.
"""

import streamlit as st
from datetime import datetime, date, timezone, timedelta
import requests, time, jwt, calendar as cal_lib
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

st.set_page_config(
    page_title="NutriTrack",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Load external CSS ──────────────────────────────────────

def load_css():
    css_path = Path(__file__).parent / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)
    else:
        st.warning("style.css not found — place it in the same folder as meal_tracker.py")

load_css()

# ── Constants ──────────────────────────────────────────────

TODAY = datetime.now(IST).date()
DAYS  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── Meal plan data ─────────────────────────────────────────

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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training 6–7 AM: Supply 6 salts (1 sachet in 600 ml)"},
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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training 6–7 AM: Supply 6 salts (1 sachet in 600 ml)"},
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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During training 6:30–8 AM: 300–500 ml plain water + Supply 6 salts (1 sachet in 500 ml)"},
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
            {"slot": "Sip — first half of day", "desc": "1 L lemon chia seeds water (1 big lemon + 1 tbsp chia seeds + 2 pinches salt) — sip throughout morning"},
            {"slot": "Pre-training · 5:30–6 AM (long run)","desc": "1 fruit/banana OR 2–3 dry dates/figs + 200 ml black coffee (no sugar) | During run: Supply 6 salts (1 sachet in 500 ml) + energy gel with caffeine at 45 min + plain energy gel at 80 min"},
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
        _u(f"{col}/{did}"),
        headers=_h(),
        json={"fields": {k: _to(v) for k, v in data.items()}},
        timeout=10,
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
        _u(col),
        headers=_h(),
        json={"fields": {k: _to(v) for k, v in data.items()}},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["name"].split("/")[-1]


# ── Cloudinary ─────────────────────────────────────────────

def upload_photo(fb, fn) -> str:
    r = requests.post(
        f"https://api.cloudinary.com/v1_1/{st.secrets['cloudinary_cloud_name']}/image/upload",
        data={"upload_preset": st.secrets["cloudinary_upload_preset"]},
        files={"file": (fn, fb)},
        timeout=30,
    )
    return r.json().get("secure_url", "") if r.status_code == 200 else ""


# ── Plan helpers ───────────────────────────────────────────

@st.cache_data(ttl=300)
def load_custom_plan():
    return {d["id"]: d for d in fs_list("meal_plan")}

def current_desc(day, person, idx, custom):
    entry = custom.get(f"{day}_{person}_{idx}", {})
    if isinstance(entry, dict):
        return entry.get("desc") or DEFAULT_MEALS[day][person][idx]["desc"]
    return entry or DEFAULT_MEALS[day][person][idx]["desc"]

def slot_label(day, person, idx, custom=None):
    if custom is not None:
        entry = custom.get(f"{day}_{person}_{idx}", {})
        if isinstance(entry, dict) and entry.get("slot"):
            return entry["slot"]
    return DEFAULT_MEALS[day][person][idx]["slot"]

def meal_count(day, person):
    return len(DEFAULT_MEALS[day][person])


# ── Tracking helpers ───────────────────────────────────────

def tk(d: date, person, idx):
    return f"{d.isoformat()}_{person}_{idx}"

@st.cache_data(ttl=20)
def load_day(date_str: str) -> dict:
    return {
        doc["id"]: doc
        for doc in fs_list("tracking")
        if doc["id"].startswith(date_str + "_")
    }

@st.cache_data(ttl=30)
def load_all_tracking() -> dict:
    return {doc["id"]: doc for doc in fs_list("tracking")}

def bust(date_str: str):
    load_day.clear()
    load_all_tracking.clear()

def day_pct(d: date, all_t: dict) -> float:
    day_name = DAYS[d.weekday()]
    tot = done = 0
    for p in ["p1", "p2"]:
        for i in range(meal_count(day_name, p)):
            tot += 1
            if all_t.get(tk(d, p, i), {}).get("status", "pending") in ("done", "skipped"):
                done += 1
    return done / tot if tot else 0


# ── HTML component helpers ─────────────────────────────────

def badge_html(status: str) -> str:
    labels = {"done": "Done", "skipped": "Skipped", "pending": "Pending"}
    return f'<span class="nt-badge {status}">{labels.get(status, "Pending")}</span>'


def person_header(person: str) -> str:
    if person == "p1":
        return (
            '<div class="nt-person p1">'
            '<div class="nt-person-avatar">P1</div>'
            '<div>'
            '<div class="nt-person-name">Madhura</div>'
            '<div class="nt-person-role">Vegetarian</div>'
            '</div></div>'
        )
    return (
        '<div class="nt-person p2">'
        '<div class="nt-person-avatar">P2</div>'
        '<div>'
        '<div class="nt-person-name">Jasraj</div>'
        '<div class="nt-person-role">Non-Vegetarian</div>'
        '</div></div>'
    )


def section_label(text: str, margin_top: bool = True) -> str:
    mt = "margin-top:0" if not margin_top else ""
    return f'<div class="nt-section-label" style="{mt}">{text}</div>'


def calendar_html(y: int, m: int, all_t: dict, sel: date) -> str:
    fdow  = cal_lib.monthrange(y, m)[0]
    ndays = cal_lib.monthrange(y, m)[1]
    hdr   = "".join(
        f'<div class="nt-cal-hdr">{d}</div>'
        for d in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    )
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

    legend = """
    <div class="nt-cal-legend">
      <div class="nt-cal-leg">
        <div class="nt-cal-dot" style="background:var(--brand-200);border:1px solid var(--brand-400)"></div>Fully tracked
      </div>
      <div class="nt-cal-leg">
        <div class="nt-cal-dot" style="background:var(--gold-200);border:1px solid var(--gold-400)"></div>Partial
      </div>
      <div class="nt-cal-leg">
        <div class="nt-cal-dot" style="background:var(--neutral-150);border:1px solid var(--neutral-300)"></div>Not started
      </div>
    </div>"""

    return (
        f'<div class="nt-cal-wrap">'
        f'<div class="nt-cal-grid">{hdr}{cells}</div>'
        f'{legend}'
        f'</div>'
    )


# ── Auth ───────────────────────────────────────────────────

def check_password() -> bool:
    if st.session_state.get("auth"):
        return True
    st.markdown(
        '<div class="nt-login">'
        '<div class="nt-login-mark">🌿</div>'
        '<div class="nt-login-title">NutriTrack</div>'
        '<div class="nt-login-sub">Your personalised nutrition companion</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    pw = st.text_input("", type="password", placeholder="Enter password",
                       label_visibility="collapsed")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button("Sign in", use_container_width=True, type="primary"):
            if pw == st.secrets["app_password"]:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False


# ── Meal card ──────────────────────────────────────────────

def meal_card(d: date, person: str, idx: int, custom: dict, day_entries: dict):
    day_name    = DAYS[d.weekday()]
    slot        = slot_label(day_name, person, idx, custom)
    plan_desc   = current_desc(day_name, person, idx, custom)
    entry       = dict(day_entries.get(tk(d, person, idx),
                       {"status": "pending", "comment": "", "image_url": "", "planned_desc": ""}))
    status      = entry.get("status", "pending")
    comment     = entry.get("comment", "")
    image_url   = entry.get("image_url", "")
    display_desc = entry.get("planned_desc") or plan_desc
    uid          = f"{d.isoformat()}_{person}_{idx}"
    is_future    = d > TODAY

    # Card
    css = "nt-meal" + (" done" if status == "done" else " skipped" if status == "skipped" else "")
    st.markdown(
        f'<div class="{css}">'
        f'  <div class="nt-meal-row">'
        f'    <div class="nt-meal-body">'
        f'      <div class="nt-meal-slot">{slot}</div>'
        f'      <div class="nt-meal-desc">{display_desc}</div>'
        f'    </div>'
        f'    <div>{badge_html(status)}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if image_url:
        st.image(image_url, use_container_width=True)

    if comment and not st.session_state.get(f"open_{uid}", False):
        st.markdown(f'<div class="nt-note">💬 {comment}</div>', unsafe_allow_html=True)

    if not is_future:
        c1, c2, c3 = st.columns([5, 5, 2])
        with c1:
            lbl = "Mark as done" if status != "done" else "↩ Undo done"
            if st.button(lbl, key=f"done_{uid}", use_container_width=True):
                entry["status"] = "done" if status != "done" else "pending"
                if not entry.get("planned_desc"):
                    entry["planned_desc"] = plan_desc
                fs_set("tracking", tk(d, person, idx), entry)
                bust(d.isoformat())
                st.rerun()
        with c2:
            lbl = "Mark as skipped" if status != "skipped" else "↩ Undo skip"
            if st.button(lbl, key=f"skip_{uid}", use_container_width=True):
                entry["status"] = "skipped" if status != "skipped" else "pending"
                if not entry.get("planned_desc"):
                    entry["planned_desc"] = plan_desc
                fs_set("tracking", tk(d, person, idx), entry)
                bust(d.isoformat())
                st.rerun()
        with c3:
            icon = "✏️" if (comment or image_url) else "📝"
            if st.button(icon, key=f"note_{uid}", use_container_width=True):
                st.session_state[f"open_{uid}"] = not st.session_state.get(f"open_{uid}", False)

        if st.session_state.get(f"open_{uid}", False):
            nc = st.text_area(
                "Note", value=comment, key=f"ta_{uid}",
                placeholder="Add a note, substitution, or observation…",
                label_visibility="collapsed", height=72,
            )
            up = st.file_uploader(
                "Attach a photo", type=["jpg", "jpeg", "png", "heic"],
                key=f"up_{uid}", label_visibility="collapsed",
            )
            cs, cr = st.columns(2)
            with cs:
                if st.button("Save note", key=f"sv_{uid}", use_container_width=True):
                    entry["comment"] = nc
                    if not entry.get("planned_desc"):
                        entry["planned_desc"] = plan_desc
                    if up:
                        with st.spinner("Uploading photo…"):
                            url = upload_photo(up.read(), up.name)
                        if url:
                            entry["image_url"] = url
                    fs_set("tracking", tk(d, person, idx), entry)
                    bust(d.isoformat())
                    st.session_state[f"open_{uid}"] = False
                    st.rerun()
            with cr:
                if image_url and st.button("Remove photo", key=f"rm_{uid}", use_container_width=True):
                    entry["image_url"] = ""
                    fs_set("tracking", tk(d, person, idx), entry)
                    bust(d.isoformat())
                    st.rerun()

    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


# ── Snacks ─────────────────────────────────────────────────

def render_snacks(d: date, person: str):
    st.markdown(section_label("Extra & unplanned"), unsafe_allow_html=True)
    snacks = fs_list("snacks", filters=[
        {"field": "date",   "value": d.isoformat()},
        {"field": "person", "value": person},
    ])
    for s in snacks:
        ts = s.get("timestamp", "")
        if "T" in ts:
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%I:%M %p")
            except Exception:
                ts = ""
        time_part = f" · {ts}" if ts else ""
        st.markdown(
            f'<div class="nt-snack">'
            f'<div class="nt-snack-label">Snack{time_part}</div>'
            f'<div class="nt-snack-desc">{s.get("desc", "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if s.get("image_url"):
            st.image(s["image_url"], use_container_width=True)
        if st.button("Remove", key=f"del_{s['id']}"):
            fs_del("snacks", s["id"])
            st.rerun()

    if d <= TODAY:
        ak = f"add_{d.isoformat()}_{person}"
        if st.button("+ Log a snack", key=f"btn_{ak}"):
            st.session_state[ak] = not st.session_state.get(ak, False)
        if st.session_state.get(ak, False):
            desc = st.text_input(
                "What did you have?", key=f"desc_{ak}",
                label_visibility="collapsed",
                placeholder="e.g. 1 chai + 2 biscuits…",
            )
            img = st.file_uploader(
                "Photo (optional)", type=["jpg", "jpeg", "png", "heic"],
                key=f"simg_{ak}", label_visibility="collapsed",
            )
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
                    st.session_state[ak] = False
                    st.rerun()
                else:
                    st.warning("Please describe what you had.")


# ── Page: Tracker ──────────────────────────────────────────

def page_tracker():
    for k, v in [("sel_date", TODAY), ("cal_year", TODAY.year), ("cal_month", TODAY.month)]:
        if k not in st.session_state:
            st.session_state[k] = v

    # Date picker
    sel = st.date_input(
        "", value=st.session_state.sel_date,
        min_value=date(2025, 1, 1), max_value=TODAY,
        label_visibility="collapsed",
    )
    if sel != st.session_state.sel_date:
        st.session_state.update(sel_date=sel, cal_year=sel.year, cal_month=sel.month)
        st.rerun()

    d = st.session_state.sel_date

    # Calendar (collapsed)
    with st.expander("📅  Monthly overview", expanded=False):
        y, m  = st.session_state.cal_year, st.session_state.cal_month
        all_t = load_all_tracking()
        nc1, nc2, nc3 = st.columns([1, 4, 1])
        with nc1:
            if st.button("◀", key="cp", use_container_width=True):
                if m == 1:
                    st.session_state.cal_year  -= 1
                    st.session_state.cal_month  = 12
                else:
                    st.session_state.cal_month -= 1
                st.rerun()
        with nc2:
            st.markdown(
                f'<div class="nt-cal-month" style="text-align:center;padding-top:6px">'
                f'{cal_lib.month_name[m]} {y}</div>',
                unsafe_allow_html=True,
            )
        with nc3:
            if (y, m) < (TODAY.year, TODAY.month):
                if st.button("▶", key="cn", use_container_width=True):
                    if m == 12:
                        st.session_state.cal_year  += 1
                        st.session_state.cal_month  = 1
                    else:
                        st.session_state.cal_month += 1
                    st.rerun()
        st.markdown(calendar_html(y, m, all_t, d), unsafe_allow_html=True)

    # Stats
    day_name   = DAYS[d.weekday()]
    day_ent    = load_day(d.isoformat())
    custom     = load_custom_plan()
    done_n     = sum(
        1 for p in ["p1", "p2"] for i in range(meal_count(day_name, p))
        if day_ent.get(tk(d, p, i), {}).get("status", "pending") == "done"
    )
    skipped_n  = sum(
        1 for p in ["p1", "p2"] for i in range(meal_count(day_name, p))
        if day_ent.get(tk(d, p, i), {}).get("status", "pending") == "skipped"
    )
    total_n    = sum(meal_count(day_name, p) for p in ["p1", "p2"])
    tracked_n  = done_n + skipped_n
    pct        = round(tracked_n / total_n * 100) if total_n else 0
    label      = "Today" if d == TODAY else d.strftime("%A, %d %b %Y")

    st.markdown(
        f'<div class="nt-stats">'
        f'  <div class="nt-stat"><div class="nt-stat-val">{done_n}</div>'
        f'    <div class="nt-stat-lbl">Done</div></div>'
        f'  <div class="nt-stat"><div class="nt-stat-val accent">{skipped_n}</div>'
        f'    <div class="nt-stat-lbl">Skipped</div></div>'
        f'  <div class="nt-stat"><div class="nt-stat-val">{pct}%</div>'
        f'    <div class="nt-stat-lbl">Complete</div></div>'
        f'</div>'
        f'<div class="nt-progress-wrap">'
        f'  <div class="nt-progress-fill" style="width:{pct}%"></div>'
        f'</div>'
        f'<div class="nt-progress-label">{label} · {tracked_n} of {total_n} meals tracked</div>',
        unsafe_allow_html=True,
    )

    # Person tabs
    t1, t2 = st.tabs(["🏃  Madhura · Runner", "🏃  Jasraj · Runner"])
    with t1:
        st.markdown(person_header("p1"), unsafe_allow_html=True)
        for i in range(meal_count(day_name, "p1")):
            meal_card(d, "p1", i, custom, day_ent)
        render_snacks(d, "p1")
    with t2:
        st.markdown(person_header("p2"), unsafe_allow_html=True)
        for i in range(meal_count(day_name, "p2")):
            meal_card(d, "p2", i, custom, day_ent)
        render_snacks(d, "p2")


# ── Page: Measurements ─────────────────────────────────────

def last_date(docs: list, field: str):
    hits = [d for d in docs if d.get(field) is not None]
    return hits[-1].get("date") if hits else None

def is_due(last_str, days: int) -> bool:
    if not last_str:
        return True
    return (TODAY - date.fromisoformat(last_str)).days >= days

def page_measurements():
    st.markdown(section_label("Body metrics", margin_top=False), unsafe_allow_html=True)
    t1, t2 = st.tabs(["🏃  Madhura", "🏃  Jasraj"])
    for tab, person in [(t1, "p1"), (t2, "p2")]:
        with tab:
            docs = sorted(
                fs_list("measurements", filters=[{"field": "person", "value": person}]),
                key=lambda x: x.get("date", ""),
            )

            # Weight
            lw       = last_date(docs, "weight")
            wdue     = is_due(lw, 7)
            wbadge   = "nt-due-now" if wdue else "nt-due-ok"
            wstatus  = "Log now" if wdue else "Up to date"
            wlastlog = f'<div class="nt-meas-last">Last entry: {lw}</div>' if lw else ""
            st.markdown(
                f'<div class="nt-meas-card">'
                f'  <div class="nt-meas-header">'
                f'    <div class="nt-meas-title">Weight</div>'
                f'    <span class="nt-due-badge {wbadge}">{wstatus}</span>'
                f'  </div>'
                f'  <div style="font-size:11px;color:var(--neutral-400)">Log weekly</div>'
                f'  {wlastlog}'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander("Log weight entry", expanded=wdue):
                wv = st.number_input("Weight (kg)", 30.0, 200.0, step=0.1,
                                     key=f"wv_{person}", format="%.1f")
                wd = st.date_input("Date", TODAY, max_value=TODAY, key=f"wd_{person}")
                if st.button("Save weight", key=f"swt_{person}", use_container_width=True):
                    ex = fs_get("measurements", f"{person}_{wd.isoformat()}") or {}
                    ex.update({"person": person, "date": wd.isoformat(), "weight": float(wv)})
                    fs_set("measurements", f"{person}_{wd.isoformat()}", ex)
                    st.success(f"✓  {wv} kg saved for {wd}")
                    st.rerun()

            # Hip & Waist
            lh       = last_date(docs, "hip")
            hdue     = is_due(lh, 14)
            hbadge   = "nt-due-now" if hdue else "nt-due-ok"
            hstatus  = "Log now" if hdue else "Up to date"
            hlastlog = f'<div class="nt-meas-last">Last entry: {lh}</div>' if lh else ""
            st.markdown(
                f'<div class="nt-meas-card" style="margin-top:4px">'
                f'  <div class="nt-meas-header">'
                f'    <div class="nt-meas-title">Hip & Waist</div>'
                f'    <span class="nt-due-badge {hbadge}">{hstatus}</span>'
                f'  </div>'
                f'  <div style="font-size:11px;color:var(--neutral-400)">Log fortnightly</div>'
                f'  {hlastlog}'
                f'</div>',
                unsafe_allow_html=True,
            )
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
                    st.success(f"✓  Hip {hv} cm · Waist {wv2} cm saved")
                    st.rerun()

            # Trends
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
                    st.line_chart({
                        "Hip":   {r[0]: r[1] for r in hw_rows if r[1]},
                        "Waist": {r[0]: r[2] for r in hw_rows if r[2]},
                    })
            else:
                st.info("No measurements logged yet. Start logging to see your progress trends here.")


# ── Page: Edit Plan ────────────────────────────────────────

def page_edit_plan():
    st.markdown(section_label("Edit meal plan", margin_top=False), unsafe_allow_html=True)
    st.caption(
        "Changes apply from the next occurrence of each day onwards. "
        "Past entries always display what was planned when they were first logged."
    )
    custom = load_custom_plan()
    day    = st.selectbox("Select day", DAYS, label_visibility="collapsed")
    t1, t2 = st.tabs(["🏃  Madhura", "🏃  Jasraj"])
    for tab, person in [(t1, "p1"), (t2, "p2")]:
        with tab:
            st.markdown(person_header(person), unsafe_allow_html=True)
            for i in range(meal_count(day, person)):
                pk         = f"{day}_{person}_{i}"
                cur_entry  = custom.get(pk, {})
                is_custom  = pk in custom
                cur_desc   = current_desc(day, person, i, custom)
                cur_slot   = slot_label(day, person, i, custom)
                title      = slot_label(day, person, i, custom)
                if is_custom:
                    title += "  ·  ✏️ customised"
                with st.expander(title, expanded=False):
                    st.caption("Time / slot label")
                    ns = st.text_input(
                        "Slot", value=cur_slot, key=f"es_{pk}",
                        label_visibility="collapsed",
                        placeholder="e.g. Breakfast · 8:30 AM",
                    )
                    st.caption("Meal description")
                    nd = st.text_area(
                        "Description", value=cur_desc, key=f"ep_{pk}",
                        height=80, label_visibility="collapsed",
                    )
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("Save change", key=f"sv_{pk}", use_container_width=True):
                            if nd.strip() or ns.strip():
                                payload = {
                                    "desc": nd.strip() or cur_desc,
                                    "slot": ns.strip() or cur_slot,
                                }
                                fs_set("meal_plan", pk, payload)
                                load_custom_plan.clear()
                                st.success("Saved.")
                                st.rerun()
                    with cc2:
                        if is_custom:
                            if st.button("Reset to default", key=f"rs_{pk}",
                                         use_container_width=True):
                                fs_del("meal_plan", pk)
                                load_custom_plan.clear()
                                st.success("Reset to default.")
                                st.rerun()


# ── Main ───────────────────────────────────────────────────

def main():
    if not check_password():
        return

    # Header
    today_str = TODAY.strftime("%a, %d %b %Y")
    st.markdown(
        f'<div class="nt-header">'
        f'  <div class="nt-brand">'
        f'    <div class="nt-logo">🌿</div>'
        f'    <div class="nt-brand-text">'
        f'      <div class="nt-brand-name">NutriTrack</div>'
        f'      <div class="nt-brand-sub">6-month nutrition programme</div>'
        f'    </div>'
        f'  </div>'
        f'  <div class="nt-header-meta">'
        f'    <div class="nt-header-date">{today_str}</div>'
        f'    <div class="nt-header-plan">Personalised plan</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Navigation
    page = st.radio(
        "", ["📅  Tracker", "📏  Measurements", "✏️  Edit plan"],
        horizontal=True, label_visibility="collapsed",
    )

    if   page == "📅  Tracker":       page_tracker()
    elif page == "📏  Measurements":  page_measurements()
    else:                              page_edit_plan()

    with st.expander("⚙️  Settings"):
        st.caption("NutriTrack · v6.0")
        if st.button("Sign out", type="secondary"):
            st.session_state["auth"] = False
            st.rerun()


if __name__ == "__main__":
    main()
