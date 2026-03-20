import streamlit as st
from datetime import datetime, date
import requests, time, jwt, calendar as cal_lib

st.set_page_config(
    page_title="NutriTrack",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

html, body, [class*="css"], .stApp, button, input, textarea, select {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp { background: #F5F3EE; }
.block-container { padding: 1.25rem 1rem 4rem; max-width: 680px; margin: 0 auto; }

/* ── Top nav tabs ───────────────────────────────────── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #E8E3D9;
    margin-bottom: 20px;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    padding: 7px 14px;
    color: #6B7280;
    border: none !important;
    background: transparent !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: #134E4A !important;
    color: #FFFFFF !important;
    font-weight: 600;
}

/* ── Meal cards ─────────────────────────────────────── */
.mc {
    background: #FFFFFF;
    border: 1px solid #EAE7E0;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 8px;
    transition: border-color .15s;
}
.mc.done    { border-left: 4px solid #0D9488; background: #FAFFFE; }
.mc.skipped { border-left: 4px solid #F87171; background: #FFFAFA; }
.mc-top     { display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }
.mc-info    { flex: 1; min-width: 0; }
.mc-slot    { font-size: 10px; font-weight: 700; letter-spacing: .08em;
              text-transform: uppercase; color: #9CA3AF; margin-bottom: 4px; }
.mc-desc    { font-size: 13.5px; color: #1F2937; line-height: 1.5; }
.mc-badge   { flex-shrink: 0; margin-top: 2px; }
.badge      { display: inline-block; padding: 3px 9px; border-radius: 20px;
              font-size: 11px; font-weight: 600; }
.badge-done    { background: #CCFBF1; color: #0D4B45; }
.badge-skipped { background: #FEE2E2; color: #7F1D1D; }
.badge-pending { background: #F3F4F6; color: #9CA3AF; }

/* ── Person headers ─────────────────────────────────── */
.p-hdr {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: 12px;
    margin-bottom: 12px; margin-top: 4px;
}
.p1-hdr { background: #EEF2FF; border: 1px solid #C7D2FE; }
.p2-hdr { background: #F0FDF4; border: 1px solid #BBF7D0; }
.p-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; flex-shrink: 0;
}
.p1-av { background: #6366F1; color: #fff; }
.p2-av { background: #16A34A; color: #fff; }
.p-name { font-size: 13px; font-weight: 600; }
.p1-name { color: #312E81; }
.p2-name { color: #14532D; }
.p-sub  { font-size: 11px; color: #6B7280; }

/* ── Snack cards ────────────────────────────────────── */
.sc {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 12px; padding: 11px 14px; margin-bottom: 8px;
}
.sc-label { font-size: 10px; font-weight: 700; letter-spacing: .08em;
            text-transform: uppercase; color: #92400E; margin-bottom: 3px; }
.sc-desc  { font-size: 13px; color: #1F2937; }

/* ── Calendar ───────────────────────────────────────── */
.cal-wrap  { background: #fff; border-radius: 14px; border: 1px solid #EAE7E0; padding: 14px; }
.cal-grid  { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 8px; }
.cal-hdr   { text-align: center; font-size: 10px; font-weight: 700; letter-spacing: .06em;
             text-transform: uppercase; color: #9CA3AF; padding: 4px 0; }
.cal-day   { text-align: center; font-size: 12px; padding: 7px 2px;
             border-radius: 8px; line-height: 1; font-weight: 500; }
.cal-empty  { background: transparent; }
.cal-future { color: #D1D5DB; }
.cal-none   { background: #F9FAFB; color: #9CA3AF; }
.cal-part   { background: #FEF3C7; color: #92400E; }
.cal-full   { background: #CCFBF1; color: #0D4B45; }
.cal-today  { box-shadow: 0 0 0 2px #0D9488; }
.cal-sel    { box-shadow: 0 0 0 2px #6366F1; font-weight: 700; }
.cal-legend { display: flex; gap: 14px; margin-top: 10px; flex-wrap: wrap; }
.cal-leg-item { display: flex; align-items: center; gap: 5px;
                font-size: 11px; color: #6B7280; }
.cal-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

/* ── Stat cards ─────────────────────────────────────── */
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 14px; }
.stat-card { background: #fff; border: 1px solid #EAE7E0; border-radius: 12px;
             padding: 12px 14px; text-align: center; }
.stat-val  { font-size: 22px; font-weight: 700; color: #134E4A; line-height: 1; margin-bottom: 3px; }
.stat-lbl  { font-size: 10px; font-weight: 600; letter-spacing: .07em;
             text-transform: uppercase; color: #9CA3AF; }

/* ── Progress bar ───────────────────────────────────── */
.prog-wrap { background: #EAE7E0; border-radius: 20px; height: 6px; margin-bottom: 16px; }
.prog-fill { height: 6px; border-radius: 20px; background: linear-gradient(90deg,#0D9488,#0F766E); }

/* ── Measurement cards ──────────────────────────────── */
.meas-section { background: #fff; border: 1px solid #EAE7E0; border-radius: 14px;
                padding: 16px; margin-bottom: 12px; }
.meas-title { font-size: 12px; font-weight: 700; letter-spacing: .07em;
              text-transform: uppercase; color: #374151; margin-bottom: 4px; }
.due-now { background: #FEF3C7; color: #92400E; padding: 3px 9px;
           border-radius: 20px; font-size: 11px; font-weight: 600;
           display: inline-block; margin-left: 8px; }
.due-ok  { background: #CCFBF1; color: #0D4B45; padding: 3px 9px;
           border-radius: 20px; font-size: 11px; font-weight: 600;
           display: inline-block; margin-left: 8px; }
.last-log { font-size: 11px; color: #9CA3AF; margin-top: 2px; }

/* ── Section dividers ───────────────────────────────── */
.section-label {
    font-size: 10px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: #9CA3AF;
    margin: 18px 0 10px;
    display: flex; align-items: center; gap: 8px;
}
.section-label::after {
    content: ''; flex: 1; height: 1px; background: #EAE7E0;
}

/* ── Note pill ──────────────────────────────────────── */
.note-pill { display: inline-flex; align-items: center; gap: 5px;
             background: #F3F4F6; border-radius: 8px;
             padding: 4px 9px; font-size: 12px; color: #6B7280;
             margin-top: 6px; font-style: italic; }

/* ── App header ─────────────────────────────────────── */
.app-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px; padding-bottom: 16px;
    border-bottom: 1px solid #EAE7E0;
}
.app-brand { display: flex; align-items: center; gap: 10px; }
.app-icon  { width: 36px; height: 36px; background: #134E4A; border-radius: 10px;
             display: flex; align-items: center; justify-content: center;
             font-size: 18px; }
.app-name  { font-family: 'Lora', serif; font-size: 20px; font-weight: 600; color: #111827; }
.app-sub   { font-size: 11px; color: #9CA3AF; margin-top: 1px; }

/* ── Buttons ─────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    border-color: #D1D5DB !important;
    color: #374151 !important;
    background: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: all .15s !important;
}
.stButton > button:hover {
    border-color: #0D9488 !important;
    color: #0D4B45 !important;
    background: #F0FDFA !important;
}

/* ── Expanders ──────────────────────────────────────── */
.streamlit-expanderHeader {
    font-size: 13px !important; font-weight: 500 !important;
    color: #374151 !important;
    background: #fff !important;
    border-radius: 10px !important;
    border: 1px solid #EAE7E0 !important;
}

/* ── Inputs ─────────────────────────────────────────── */
.stTextArea textarea, .stTextInput input, .stNumberInput input {
    border-radius: 10px !important;
    border-color: #E5E7EB !important;
    font-size: 13px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus, .stNumberInput input:focus {
    border-color: #0D9488 !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,.1) !important;
}

/* ── Login ──────────────────────────────────────────── */
.login-wrap { max-width: 340px; margin: 60px auto 0; text-align: center; }
.login-icon { font-size: 40px; margin-bottom: 12px; }
.login-title { font-family: 'Lora', serif; font-size: 26px; font-weight: 600;
               color: #111827; margin-bottom: 6px; }
.login-sub { font-size: 13px; color: #6B7280; margin-bottom: 24px; }

/* ── Misc ────────────────────────────────────────────── */
img { border-radius: 12px !important; }
.stCaption { font-size: 12px !important; color: #9CA3AF !important; }
hr { border-color: #EAE7E0 !important; margin: 12px 0 !important; }
div[data-testid="column"] { padding: 0 3px !important; }
</style>
""", unsafe_allow_html=True)

TODAY = date.today()
DAYS  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

DEFAULT_MEALS = {
    "Mon": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 banana or whole fruit + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200 ml water + 30 g moong sprouts"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C rich fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g sabzi/salad + 1 multigrain bread + 70 g tofu bhurji"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 500 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400 ml oats protein smoothie + 30 g moong sprouts"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites — bhurji or omelette"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 3 methi/cabbage parathas + 100 g tofu bhurji + 100 g skyr yogurt"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g roasted peanuts + ½ scoop whey in 200 ml water"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g sabzi/salad + 1 multigrain bread + 150 g tofu bhurji"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon (no sugar)"},
        ]
    },
    "Tue": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200 ml water + 30 g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g salad + 2 jowar bhakri + 50 g low fat pan fry paneer + 50 g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 600 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400 ml oats protein smoothie + 30 g boiled chickpeas"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 3 jowar bhakri + 100 g low fat pan fry paneer + 100 g plain curd"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g makhana + ½ scoop whey in 200 ml water"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g sabzi/salad + 2 jowar bhakri + 150 g low fat tossed paneer"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Wed": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 vegetable sandwich + 1 scoop whey in 200 ml water"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g salad + 1 jowar bhakri + 70 g low fat tossed paneer"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 500 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"2 veg sandwiches + 200 ml toned milk + 1 scoop whey"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites + 1 vit-C fruit"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 200 g mix veg pulao (rice + quinoa) + 100 g chicken kheema + 200 ml chaas"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g roasted peanuts + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g sabzi + boiled chickpeas/dal + 150 g air fried/pan sautee chicken + 100 g veggies"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Thu": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200 ml water + 30 g kala channa (soak overnight)"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g salad + 200 g mix veg pulao (rice + quinoa) + 100 g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 600 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400 ml oats protein smoothie + 30 g boiled kala channa"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 3 whole wheat roti + 150 g rajma masala + 100 g skyr yogurt"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g sabzi + 2 whole wheat roti + 150 g tofu stir fry"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Fri": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"2 bread toast + 1 scoop whey in 200 ml water"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g salad + 2 whole wheat roti + 100 g rajma masala + 50 g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 500 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"3 bread toast + 200 ml toned milk + 1 scoop whey"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites + 1 vit-C fruit"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 3 jowar bhakri + 100 g low fat palak paneer + 100 g plain curd"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g roasted peanuts + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g sabzi + 2 jowar bhakri + 150 g low fat palak paneer"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sat": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + Supply 6 salts in 500–600 ml during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200 ml water + 30 g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100 g salad + 2 methi/cabbage parathas + 50 g tofu bhurji + 150 ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100 g salad + 2 jowar bhakri + 50 g palak paneer + 50 g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts in 500 ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400 ml oats protein smoothie + 30 g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + tofu burrito wrap (2 wheat roti + 100 g tofu + 20 g rajma + 75 g veggies + 15 g salsa) + 200 ml chaas"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"250 g shirataki noodles (150 g noodles + 100 g veggies) + 150 g chicken stir fry + 200 ml tomato soup"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sun": {
        "p1": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"1 scoop whey in 200 ml water + 30 g kala channa"},
            {"slot":"Lunch · 12:30 PM",      "desc":"⭐ Enjoyment meal"},
            {"slot":"Evening · 4 PM",        "desc":"Green tea + 1 vit-C fruit"},
            {"slot":"Dinner · 7 PM",         "desc":"100 g salad + 200 g veg khichdi (75 g rice + 75 g dal + 50 g veggies) + 100 g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot":"Pre-training — long run","desc":"1 fruit/banana + 200 ml black coffee + Supply 6 salts + energy gel at 45 min + energy gel at 80 min"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400 ml oats smoothie + 30 g moong sprouts + 150 g yogurt bowl (100 g yogurt + ½ scoop whey + 1 fruit + 1 tsp chia)"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100 g salad + 250 g veg khichdi OR 250 g chicken biryani + 100 g cucumber raita"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit-C fruit + 20 g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"⭐ Enjoyment meal"},
            {"slot":"Bedtime",               "desc":"200 ml toned milk + 2 pinches cinnamon"},
        ]
    }
}


# ── Firebase REST ──────────────────────────────────────────────────────────────

_TK = {"v": None, "e": 0}

def get_token():
    now = int(time.time())
    if _TK["v"] and now < _TK["e"] - 60: return _TK["v"]
    c  = st.secrets["firebase_credentials"]
    pk = c["private_key"].replace("\\n", "\n")
    signed = jwt.encode(
        {"iss": c["client_email"], "sub": c["client_email"],
         "aud": "https://oauth2.googleapis.com/token",
         "iat": now, "exp": now + 3600,
         "scope": "https://www.googleapis.com/auth/datastore"},
        pk, algorithm="RS256")
    r = requests.post("https://oauth2.googleapis.com/token",
                      data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                            "assertion": signed}, timeout=10)
    r.raise_for_status()
    d = r.json(); _TK["v"] = d["access_token"]; _TK["e"] = now + d.get("expires_in", 3600)
    return _TK["v"]

def _h(): return {"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"}
def _u(p): return f"https://firestore.googleapis.com/v1/projects/{st.secrets['firebase_credentials']['project_id']}/databases/(default)/documents/{p}"

def _to(v):
    if isinstance(v, bool):  return {"booleanValue": v}
    if isinstance(v, int):   return {"integerValue": str(v)}
    if isinstance(v, float): return {"doubleValue": v}
    if isinstance(v, str):   return {"stringValue": v}
    if isinstance(v, dict):  return {"mapValue": {"fields": {k: _to(u) for k, u in v.items()}}}
    if isinstance(v, list):  return {"arrayValue": {"values": [_to(i) for i in v]}}
    return {"nullValue": None}

def _fr(v):
    if "stringValue"    in v: return v["stringValue"]
    if "booleanValue"   in v: return v["booleanValue"]
    if "integerValue"   in v: return int(v["integerValue"])
    if "doubleValue"    in v: return v["doubleValue"]
    if "nullValue"      in v: return None
    if "timestampValue" in v: return v["timestampValue"]
    if "mapValue"       in v: return {k: _fr(u) for k,u in v["mapValue"].get("fields",{}).items()}
    if "arrayValue"     in v: return [_fr(i) for i in v["arrayValue"].get("values",[])]
    return None

def fs_get(col, did):
    r = requests.get(_u(f"{col}/{did}"), headers=_h(), timeout=10)
    if r.status_code == 404: return None
    r.raise_for_status()
    return {k: _fr(v) for k, v in r.json().get("fields", {}).items()}

def fs_set(col, did, data):
    r = requests.patch(_u(f"{col}/{did}"), headers=_h(),
                       json={"fields": {k: _to(v) for k,v in data.items()}}, timeout=10)
    r.raise_for_status()

def fs_del(col, did):
    requests.delete(_u(f"{col}/{did}"), headers=_h(), timeout=10)

def fs_list(col, filters=None):
    r = requests.get(_u(col), headers=_h(), timeout=20)
    if r.status_code != 200: return []
    out = []
    for doc in r.json().get("documents", []):
        did    = doc["name"].split("/")[-1]
        fields = {k: _fr(v) for k,v in doc.get("fields",{}).items()}
        if filters and not all(fields.get(f["field"]) == f["value"] for f in filters): continue
        out.append({"id": did, **fields})
    return out

def fs_add(col, data):
    r = requests.post(_u(col), headers=_h(),
                      json={"fields": {k: _to(v) for k,v in data.items()}}, timeout=10)
    r.raise_for_status()
    return r.json()["name"].split("/")[-1]


# ── Cloudinary ─────────────────────────────────────────────────────────────────

def upload_photo(fb, fn) -> str:
    r = requests.post(
        f"https://api.cloudinary.com/v1_1/{st.secrets['cloudinary_cloud_name']}/image/upload",
        data={"upload_preset": st.secrets["cloudinary_upload_preset"]},
        files={"file": (fn, fb)}, timeout=30)
    return r.json().get("secure_url","") if r.status_code == 200 else ""


# ── Meal plan ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_custom_plan():
    return {d["id"]: d.get("desc","") for d in fs_list("meal_plan")}

def current_desc(day, person, idx, custom):
    return custom.get(f"{day}_{person}_{idx}") or DEFAULT_MEALS[day][person][idx]["desc"]

def slot_label(day, person, idx):
    return DEFAULT_MEALS[day][person][idx]["slot"]

def meal_count(day, person):
    return len(DEFAULT_MEALS[day][person])


# ── Tracking ───────────────────────────────────────────────────────────────────

def tk(d: date, person, idx): return f"{d.isoformat()}_{person}_{idx}"

@st.cache_data(ttl=20)
def load_day(date_str: str) -> dict:
    return {doc["id"]: doc for doc in fs_list("tracking") if doc["id"].startswith(date_str+"_")}

@st.cache_data(ttl=30)
def load_all_tracking() -> dict:
    return {doc["id"]: doc for doc in fs_list("tracking")}

def bust(date_str): load_day.clear(); load_all_tracking.clear()

def day_pct(d: date, all_t: dict) -> float:
    day_name = DAYS[d.weekday()]
    tot = done = 0
    for p in ["p1","p2"]:
        for i in range(meal_count(day_name, p)):
            tot += 1
            if all_t.get(tk(d,p,i),{}).get("status","pending") in ("done","skipped"): done += 1
    return done/tot if tot else 0


# ── Auth ───────────────────────────────────────────────────────────────────────

def check_password():
    if st.session_state.get("auth"): return True
    st.markdown("""
    <div class="login-wrap">
      <div class="login-icon">🌿</div>
      <div class="login-title">NutriTrack</div>
      <div class="login-sub">Your personalised nutrition companion</div>
    </div>""", unsafe_allow_html=True)
    pw = st.text_input("", type="password", placeholder="Enter password",
                       label_visibility="collapsed")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Sign in", use_container_width=True):
            if pw == st.secrets["app_password"]:
                st.session_state["auth"] = True; st.rerun()
            else:
                st.error("Incorrect password.")
    return False


# ── Calendar ───────────────────────────────────────────────────────────────────

def calendar_html(y, m, all_t, sel: date) -> str:
    fdow = cal_lib.monthrange(y, m)[0]
    ndays = cal_lib.monthrange(y, m)[1]
    hdr = "".join(f'<div class="cal-hdr">{d}</div>'
                  for d in ["Mo","Tu","We","Th","Fr","Sa","Su"])
    cells = '<div class="cal-empty"></div>' * fdow
    for n in range(1, ndays+1):
        d = date(y, m, n)
        ex = (" cal-today" if d==TODAY else "") + (" cal-sel" if d==sel else "")
        if d > TODAY:
            css = "cal-future"
        else:
            p = day_pct(d, all_t)
            css = "cal-none" if p==0 else "cal-part" if p<0.8 else "cal-full"
        cells += f'<div class="cal-day {css}{ex}">{n}</div>'
    legend = """
    <div class="cal-legend">
      <div class="cal-leg-item"><div class="cal-dot" style="background:#CCFBF1;border:1px solid #0D9488"></div>Fully tracked</div>
      <div class="cal-leg-item"><div class="cal-dot" style="background:#FEF3C7;border:1px solid #92400E"></div>Partial</div>
      <div class="cal-leg-item"><div class="cal-dot" style="background:#F9FAFB;border:1px solid #D1D5DB"></div>Not started</div>
    </div>"""
    return f'<div class="cal-wrap"><div class="cal-grid">{hdr}{cells}</div>{legend}</div>'


# ── Meal card ──────────────────────────────────────────────────────────────────

def meal_card(d: date, person, idx, custom, day_entries: dict):
    day_name  = DAYS[d.weekday()]
    slot      = slot_label(day_name, person, idx)
    plan_desc = current_desc(day_name, person, idx, custom)
    entry     = dict(day_entries.get(tk(d,person,idx),
                     {"status":"pending","comment":"","image_url":"","planned_desc":""}))
    status    = entry.get("status","pending")
    comment   = entry.get("comment","")
    image_url = entry.get("image_url","")
    # Use snapshotted description for past entries; fall back to current plan
    display_desc = entry.get("planned_desc") or plan_desc
    is_future = d > TODAY
    uid = f"{d.isoformat()}_{person}_{idx}"

    badge_html = {
        "done":    '<span class="badge badge-done">Done</span>',
        "skipped": '<span class="badge badge-skipped">Skipped</span>',
        "pending": '<span class="badge badge-pending">Pending</span>',
    }.get(status, "")

    css = "mc" + (" done" if status=="done" else " skipped" if status=="skipped" else "")
    st.markdown(f"""
    <div class="{css}">
      <div class="mc-top">
        <div class="mc-info">
          <div class="mc-slot">{slot}</div>
          <div class="mc-desc">{display_desc}</div>
        </div>
        <div class="mc-badge">{badge_html}</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True)

    if comment and not st.session_state.get(f"open_{uid}", False):
        st.markdown(f'<div class="note-pill">💬 {comment}</div>', unsafe_allow_html=True)

    if not is_future:
        c1, c2, c3 = st.columns([2,2,1])
        with c1:
            lbl = "Mark done" if status!="done" else "Undo done"
            if st.button(lbl, key=f"done_{uid}", use_container_width=True):
                entry["status"] = "done" if status!="done" else "pending"
                if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                fs_set("tracking", tk(d,person,idx), entry); bust(d.isoformat()); st.rerun()
        with c2:
            lbl = "Mark skipped" if status!="skipped" else "Undo skip"
            if st.button(lbl, key=f"skip_{uid}", use_container_width=True):
                entry["status"] = "skipped" if status!="skipped" else "pending"
                if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                fs_set("tracking", tk(d,person,idx), entry); bust(d.isoformat()); st.rerun()
        with c3:
            icon = "✏️" if (comment or image_url) else "📝"
            if st.button(icon, key=f"note_{uid}", use_container_width=True):
                st.session_state[f"open_{uid}"] = not st.session_state.get(f"open_{uid}", False)

        if st.session_state.get(f"open_{uid}", False):
            nc = st.text_area("Note", value=comment, key=f"ta_{uid}",
                              placeholder="Add a note, substitution, or observation…",
                              label_visibility="collapsed", height=72)
            up = st.file_uploader("Photo", type=["jpg","jpeg","png","heic"],
                                  key=f"up_{uid}", label_visibility="collapsed")
            cs, cr = st.columns(2)
            with cs:
                if st.button("Save note", key=f"sv_{uid}", use_container_width=True):
                    entry["comment"] = nc
                    if not entry.get("planned_desc"): entry["planned_desc"] = plan_desc
                    if up:
                        with st.spinner("Uploading…"):
                            url = upload_photo(up.read(), up.name)
                        if url: entry["image_url"] = url
                    fs_set("tracking", tk(d,person,idx), entry)
                    bust(d.isoformat())
                    st.session_state[f"open_{uid}"] = False; st.rerun()
            with cr:
                if image_url and st.button("Remove photo", key=f"rm_{uid}", use_container_width=True):
                    entry["image_url"] = ""
                    fs_set("tracking", tk(d,person,idx), entry); bust(d.isoformat()); st.rerun()

    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)


# ── Snacks ─────────────────────────────────────────────────────────────────────

def render_snacks(d: date, person):
    st.markdown('<div class="section-label">Extra & unplanned</div>', unsafe_allow_html=True)
    snacks = fs_list("snacks", filters=[{"field":"date","value":d.isoformat()},
                                        {"field":"person","value":person}])
    for s in snacks:
        ts = s.get("timestamp","")
        if "T" in ts:
            try: ts = datetime.fromisoformat(ts.replace("Z","+00:00")).strftime("%I:%M %p")
            except: ts = ""
        st.markdown(f'<div class="sc"><div class="sc-label">Snack{" · "+ts if ts else ""}</div>'
                    f'<div class="sc-desc">{s.get("desc","")}</div></div>',
                    unsafe_allow_html=True)
        if s.get("image_url"): st.image(s["image_url"], use_container_width=True)
        if st.button("Remove", key=f"del_{s['id']}"):
            fs_del("snacks", s["id"]); st.rerun()

    if d <= TODAY:
        ak = f"add_{d.isoformat()}_{person}"
        if st.button("+ Log a snack", key=f"btn_{ak}"):
            st.session_state[ak] = not st.session_state.get(ak, False)
        if st.session_state.get(ak, False):
            desc = st.text_input("What did you have?", key=f"desc_{ak}",
                                 label_visibility="collapsed",
                                 placeholder="e.g. 1 chai + 2 biscuits…")
            img  = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png","heic"],
                                    key=f"simg_{ak}", label_visibility="collapsed")
            if st.button("Save snack", key=f"log_{ak}", use_container_width=True):
                if desc.strip():
                    img_url = ""
                    if img:
                        with st.spinner("Uploading…"):
                            img_url = upload_photo(img.read(), img.name)
                    fs_add("snacks", {"date":d.isoformat(),"person":person,
                                      "desc":desc.strip(),"image_url":img_url,
                                      "timestamp":datetime.utcnow().isoformat()+"Z"})
                    st.session_state[ak] = False; st.rerun()
                else:
                    st.warning("Please describe what you had.")


# ── Page: Tracker ──────────────────────────────────────────────────────────────

def page_tracker():
    for k,v in [("sel_date",TODAY),("cal_year",TODAY.year),("cal_month",TODAY.month)]:
        if k not in st.session_state: st.session_state[k] = v

    # Date picker
    sel = st.date_input("", value=st.session_state.sel_date,
                        min_value=date(2025,1,1), max_value=TODAY,
                        label_visibility="collapsed")
    if sel != st.session_state.sel_date:
        st.session_state.update(sel_date=sel, cal_year=sel.year, cal_month=sel.month)
        st.rerun()

    d = st.session_state.sel_date

    # Calendar expander
    with st.expander("📅  Monthly overview", expanded=False):
        y, m = st.session_state.cal_year, st.session_state.cal_month
        all_t = load_all_tracking()
        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            if st.button("◀", key="cp", use_container_width=True):
                if m==1: st.session_state.cal_year-=1; st.session_state.cal_month=12
                else:    st.session_state.cal_month-=1
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center;font-weight:600;padding-top:6px;"
                        f"font-size:14px;color:#111827'>{cal_lib.month_name[m]} {y}</div>",
                        unsafe_allow_html=True)
        with c3:
            if (y,m) < (TODAY.year, TODAY.month):
                if st.button("▶", key="cn", use_container_width=True):
                    if m==12: st.session_state.cal_year+=1; st.session_state.cal_month=1
                    else:     st.session_state.cal_month+=1
                    st.rerun()
        st.markdown(calendar_html(y,m,all_t,d), unsafe_allow_html=True)

    # Stats bar
    day_name  = DAYS[d.weekday()]
    day_ent   = load_day(d.isoformat())
    custom    = load_custom_plan()
    done_n    = sum(1 for p in ["p1","p2"] for i in range(meal_count(day_name,p))
                    if day_ent.get(tk(d,p,i),{}).get("status","pending") in ("done","skipped"))
    total_n   = sum(meal_count(day_name,p) for p in ["p1","p2"])
    skipped_n = sum(1 for p in ["p1","p2"] for i in range(meal_count(day_name,p))
                    if day_ent.get(tk(d,p,i),{}).get("status","pending") == "skipped")
    pct       = round(done_n/total_n*100) if total_n else 0
    label     = "Today" if d==TODAY else d.strftime("%a, %d %b %Y")

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-card"><div class="stat-val">{done_n}</div><div class="stat-lbl">Tracked</div></div>
      <div class="stat-card"><div class="stat-val" style="color:#6366F1">{skipped_n}</div><div class="stat-lbl">Skipped</div></div>
      <div class="stat-card"><div class="stat-val">{pct}%</div><div class="stat-lbl">Complete</div></div>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)
    st.caption(label)

    # Person tabs·
    t1, t2 = st.tabs(["🏃  Madhura · Runner", "🏃  Jasraj · Runner"])
    with t1:
        st.markdown('<div class="p-hdr p1-hdr"><div class="p-avatar p1-av">P1</div>'
                    '<div><div class="p-name p1-name">Madhura</div>'
                    '<div class="p-sub">Vegetarian</div></div></div>', unsafe_allow_html=True)
        for i in range(meal_count(day_name,"p1")):
            meal_card(d,"p1",i,custom,day_ent)
        render_snacks(d,"p1")
    with t2:
        st.markdown('<div class="p-hdr p2-hdr"><div class="p-avatar p2-av">P2</div>'
                    '<div><div class="p-name p2-name">Jasraj</div>'
                    '<div class="p-sub">Non-Vegetarian</div></div></div>', unsafe_allow_html=True)
        for i in range(meal_count(day_name,"p2")):
            meal_card(d,"p2",i,custom,day_ent)
        render_snacks(d,"p2")


# ── Page: Measurements ─────────────────────────────────────────────────────────

def last_date(docs, field):
    hits = [d for d in docs if d.get(field) is not None]
    return hits[-1].get("date") if hits else None

def is_due(last_str, days):
    if not last_str: return True
    return (TODAY - date.fromisoformat(last_str)).days >= days

def page_measurements():
    st.markdown('<div class="section-label" style="margin-top:0">Body metrics</div>',
                unsafe_allow_html=True)
    t1, t2 = st.tabs(["🏃  Madhura", "🏃  Jasraj"])
    for tab, person in [(t1,"p1"),(t2,"p2")]:
        with tab:
            docs = sorted(fs_list("measurements",
                                  filters=[{"field":"person","value":person}]),
                          key=lambda x: x.get("date",""))

            # Weight
            lw   = last_date(docs,"weight")
            wdue = is_due(lw,7)
            wt_badge   = "due-now" if wdue else "due-ok"
            wt_status  = "Log now" if wdue else "Up to date"
            wt_lastlog = f'<div class="last-log">Last entry: {lw}</div>' if lw else ""
            st.markdown(
                f'<div class="meas-section">'
                f'<div class="meas-title">Weight (weekly)'
                f'<span class="{wt_badge}">{wt_status}</span></div>'
                f'{wt_lastlog}'
                f'</div>', unsafe_allow_html=True)
            with st.expander("Log weight", expanded=wdue):
                wv = st.number_input("Weight (kg)", 30.0, 200.0, step=0.1,
                                     key=f"wv_{person}", format="%.1f")
                wd = st.date_input("Date", TODAY, max_value=TODAY, key=f"wd_{person}")
                if st.button("Save weight", key=f"swt_{person}", use_container_width=True):
                    ex = fs_get("measurements",f"{person}_{wd.isoformat()}") or {}
                    ex.update({"person":person,"date":wd.isoformat(),"weight":float(wv)})
                    fs_set("measurements",f"{person}_{wd.isoformat()}",ex)
                    st.success(f"✓  {wv} kg saved for {wd}"); st.rerun()

            # Hip & waist
            lh   = last_date(docs,"hip")
            hdue = is_due(lh,14)
            hw_badge   = "due-now" if hdue else "due-ok"
            hw_status  = "Log now" if hdue else "Up to date"
            hw_lastlog = f'<div class="last-log">Last entry: {lh}</div>' if lh else ""
            st.markdown(
                f'<div class="meas-section" style="margin-top:8px">'
                f'<div class="meas-title">Hip & Waist (fortnightly)'
                f'<span class="{hw_badge}">{hw_status}</span></div>'
                f'{hw_lastlog}'
                f'</div>', unsafe_allow_html=True)
            with st.expander("Log hip & waist", expanded=hdue):
                hc1, hc2 = st.columns(2)
                with hc1:
                    hv = st.number_input("Hip (cm)", 50.0, 200.0, step=0.5,
                                         key=f"hv_{person}", format="%.1f")
                with hc2:
                    wstv = st.number_input("Waist (cm)", 40.0, 200.0, step=0.5,
                                           key=f"wstv_{person}", format="%.1f")
                hd = st.date_input("Date", TODAY, max_value=TODAY, key=f"hd_{person}")
                if st.button("Save measurements", key=f"shw_{person}", use_container_width=True):
                    ex = fs_get("measurements",f"{person}_{hd.isoformat()}") or {}
                    ex.update({"person":person,"date":hd.isoformat(),
                                "hip":float(hv),"waist":float(wstv)})
                    fs_set("measurements",f"{person}_{hd.isoformat()}",ex)
                    st.success(f"✓  Hip {hv} cm · Waist {wstv} cm saved"); st.rerun()

            # Trends
            if docs:
                st.markdown('<div class="section-label">Trends</div>', unsafe_allow_html=True)
                wt_rows = [(d["date"],d["weight"]) for d in docs if d.get("weight") is not None]
                if len(wt_rows) > 1:
                    st.caption("Weight over time (kg)")
                    st.line_chart({"Weight":  {r[0]:r[1] for r in wt_rows}})
                hw_rows = [(d["date"],d.get("hip"),d.get("waist"))
                           for d in docs if d.get("hip") is not None]
                if len(hw_rows) > 1:
                    st.caption("Hip & Waist over time (cm)")
                    st.line_chart({"Hip":   {r[0]:r[1] for r in hw_rows if r[1]},
                                   "Waist": {r[0]:r[2] for r in hw_rows if r[2]}})
            else:
                st.info("No measurements logged yet — start logging to see trends here.")


# ── Page: Edit Plan ────────────────────────────────────────────────────────────

def page_edit_plan():
    st.markdown('<div class="section-label" style="margin-top:0">Edit meal plan</div>',
                unsafe_allow_html=True)
    st.caption("Changes apply from the next occurrence of each day onwards. "
               "Past tracking entries always display what was planned at the time they were logged.")
    custom = load_custom_plan()
    day    = st.selectbox("Day", DAYS, label_visibility="collapsed")
    t1, t2 = st.tabs(["🏃  Madhura", "🏃  Jasraj"])
    for tab, person in [(t1,"p1"),(t2,"p2")]:
        with tab:
            for i in range(meal_count(day, person)):
                pk  = f"{day}_{person}_{i}"
                cur = current_desc(day, person, i, custom)
                is_custom = pk in custom
                with st.expander(
                    f"{slot_label(day,person,i)}"
                    f"{'  ·  ✏️ customised' if is_custom else ''}",
                    expanded=False
                ):
                    nd = st.text_area("Description", value=cur, key=f"ep_{pk}",
                                      height=80, label_visibility="collapsed")
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        if st.button("Save", key=f"sv_{pk}", use_container_width=True):
                            if nd.strip():
                                fs_set("meal_plan", pk, {"desc": nd.strip()})
                                load_custom_plan.clear(); st.success("Saved."); st.rerun()
                    with cc2:
                        if is_custom:
                            if st.button("Reset to default", key=f"rs_{pk}", use_container_width=True):
                                fs_del("meal_plan", pk)
                                load_custom_plan.clear(); st.success("Reset."); st.rerun()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not check_password(): return

    # App header
    today_str = TODAY.strftime("%a, %d %b %Y")
    st.markdown(f"""
    <div class="app-header">
      <div class="app-brand">
        <div class="app-icon">🌿</div>
        <div>
          <div class="app-name">NutriTrack</div>
          <div class="app-sub">6-month nutrition programme</div>
        </div>
      </div>
      <div style="text-align:right">
        <div style="font-size:13px;font-weight:600;color:#111827">{today_str}</div>
        <div style="font-size:11px;color:#9CA3AF">Personalised plan</div>
      </div>
    </div>""", unsafe_allow_html=True)

    page = st.radio("", ["📅  Tracker","📏  Measurements","✏️  Edit plan"],
                    horizontal=True, label_visibility="collapsed")

    if   page == "📅  Tracker":      page_tracker()
    elif page == "📏  Measurements": page_measurements()
    else:                             page_edit_plan()

    with st.expander("⚙️  Settings"):
        st.caption("App version 5.0 · NutriTrack")
        if st.button("Sign out", type="secondary"):
            st.session_state["auth"] = False; st.rerun()


if __name__ == "__main__":
    main()
