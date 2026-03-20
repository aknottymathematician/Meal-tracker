import streamlit as st
from datetime import datetime, date, timedelta
import requests
import time
import jwt
import calendar as cal_lib

st.set_page_config(
    page_title="Meal Tracker",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding: 0.75rem 0.75rem 3rem; max-width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { padding: 6px 10px; font-size: 13px; }
    div[data-testid="column"] { padding: 0 3px; }
    .meal-box { border: 1px solid #e0e0e0; border-radius: 10px;
                padding: 10px 12px; margin-bottom: 4px; background: #fafafa; }
    .meal-box.done    { border-color: #1D9E75; background: #f0faf6; }
    .meal-box.skipped { border-color: #E24B4A; background: #fff5f5; }
    .meal-slot { font-size: 11px; color: #888; text-transform: uppercase;
                 letter-spacing: .05em; margin-bottom: 3px; }
    .meal-desc { font-size: 13px; color: #333; line-height: 1.4; }
    .snack-box { border: 1px solid #e0d890; border-radius: 10px;
                 padding: 10px 12px; margin-bottom: 8px; background: #fffef0; }
    .p1-hdr { background:#EEEDFE; color:#3C3489; font-size:14px; font-weight:600;
              padding:7px 12px; border-radius:8px; margin-bottom:10px; }
    .p2-hdr { background:#E1F5EE; color:#085041; font-size:14px; font-weight:600;
              padding:7px 12px; border-radius:8px; margin-bottom:10px; }
    .cal-grid { display:grid; grid-template-columns:repeat(7,1fr);
                gap:3px; margin:8px 0 12px; }
    .cal-hdr  { text-align:center; font-size:11px; font-weight:600;
                color:#888; padding:4px 0; }
    .cal-day  { text-align:center; font-size:12px; padding:6px 2px;
                border-radius:6px; cursor:default; line-height:1.2; }
    .cal-empty { background:transparent; }
    .cal-future { background:#f5f5f5; color:#bbb; }
    .cal-none   { background:#f0f0f0; color:#666; }
    .cal-part   { background:#FAEEDA; color:#633806; }
    .cal-full   { background:#E1F5EE; color:#085041; }
    .cal-today  { outline:2px solid #378ADD; outline-offset:-2px; }
    .cal-sel    { outline:2px solid #7F77DD; outline-offset:-2px; font-weight:600; }
    .meas-card  { background:#fafafa; border:1px solid #e0e0e0; border-radius:10px;
                  padding:12px; margin-bottom:10px; }
    .meas-lbl   { font-size:11px; color:#888; text-transform:uppercase;
                  letter-spacing:.05em; margin-bottom:6px; }
    .due-badge  { display:inline-block; padding:2px 8px; border-radius:12px;
                  font-size:11px; font-weight:600; margin-left:6px; }
    .due-now  { background:#FAEEDA; color:#633806; }
    .due-ok   { background:#E1F5EE; color:#085041; }
    .stButton > button { border-radius:20px; font-size:13px; padding:4px 14px; }
    .stTextArea textarea { font-size:13px; }
    h2 { font-size:17px !important; }
    h3 { font-size:15px !important; }
    .login-wrap { max-width:320px; margin:80px auto 0; text-align:center; }
    img { border-radius:8px; }
</style>
""", unsafe_allow_html=True)

TODAY = date.today()
DAYS  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

DEFAULT_MEALS = {
    "Mon": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 banana or whole fruit + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200ml water + 30g moong sprouts"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C rich fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g sabzi/salad + 1 multigrain bread + 70g tofu bhurji"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400ml oats protein smoothie + 30g moong sprouts"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites (bhurji/omelette)"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 3 methi/cabbage parathas + 100g tofu bhurji + 100g skyr yogurt"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g roasted peanuts + ½ scoop whey in 200ml water"},
            {"slot":"Dinner · 7 PM",         "desc":"100g sabzi/salad + 1 multigrain bread + 150g tofu bhurji"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon (no sugar)"},
        ]
    },
    "Tue": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200ml water + 30g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 2 jowar bhakri + 50g low fat pan fry paneer + 50g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 600ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400ml oats protein smoothie + 30g boiled chickpeas"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 3 jowar bhakri + 100g low fat pan fry paneer + 100g plain curd"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g makhana + ½ scoop whey in 200ml water"},
            {"slot":"Dinner · 7 PM",         "desc":"100g sabzi/salad + 2 jowar bhakri + 150g low fat tossed paneer"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Wed": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 vegetable sandwich + 1 scoop whey in 200ml water"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 1 jowar bhakri + 70g low fat tossed paneer"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"2 veg sandwiches + 200ml toned milk + 1 scoop whey"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites + 1 vit C fruit"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 200g mix veg pulao (rice + quinoa) + 100g chicken kheema + 200ml chaas"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g roasted peanuts + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100g sabzi + boiled chickpeas/dal + 150g air fried/pan sautee chicken + 100g veggies"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Thu": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200ml water + 30g kala channa (soak overnight)"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 200g mix veg pulao (rice + quinoa) + 100g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 600ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400ml oats protein smoothie + 30g boiled kala channa"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 3 whole wheat roti + 150g rajma masala + 100g skyr yogurt"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100g sabzi + 2 whole wheat roti + 150g tofu stir fry"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Fri": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"2 bread toast + 1 scoop whey in 200ml water"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 2 whole wheat roti + 100g rajma masala + 50g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6:30 AM","desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"3 bread toast + 200ml toned milk + 1 scoop whey"},
            {"slot":"Mid-morning · 10 AM",   "desc":"4 egg whites + 1 vit C fruit"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 3 jowar bhakri + 100g low fat palak paneer + 100g plain curd"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g roasted peanuts + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"100g sabzi + 2 jowar bhakri + 150g low fat palak paneer"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sat": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + Supply 6 salts in 500–600ml during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200ml water + 30g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",     "desc":"100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 2 jowar bhakri + 50g palak paneer + 50g curd + samah"},
        ],
        "p2": [
            {"slot":"Pre-training · 6 AM",   "desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400ml oats protein smoothie + 30g boiled chickpeas"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + Tofu burrito wrap (2 wheat roti + 100g tofu + 20g rajma + 75g veggies + 15g salsa) + 200ml chaas"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"250g shirataki noodles (150g noodles + 100g veggies) + 150g chicken stir fry + 200ml tomato soup"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sun": {
        "p1": [
            {"slot":"Pre-training · 6 AM",  "desc":"1 fruit/banana + plain water during training"},
            {"slot":"Breakfast · 8:30 AM",  "desc":"1 scoop whey in 200ml water + 30g kala channa"},
            {"slot":"Lunch · 12:30 PM",     "desc":"⭐ Enjoyment meal"},
            {"slot":"Evening · 4 PM",       "desc":"Green tea + 1 vit C fruit"},
            {"slot":"Dinner · 7 PM",        "desc":"100g salad + 200g veg khichdi (75g rice + 75g dal + 50g veggies) + 100g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot":"Pre-training (long run)","desc":"1 fruit/banana + 200ml black coffee + Supply 6 salts + energy gel at 45 min + energy gel at 80 min"},
            {"slot":"Breakfast · 8:30 AM",   "desc":"400ml oats smoothie + 30g moong sprouts + 150g yogurt bowl (100g yogurt + ½ scoop whey + 1 fruit + 1 tsp chia)"},
            {"slot":"Lunch · 12:30 PM",      "desc":"100g salad + 250g veg khichdi OR 250g chicken biryani + 100g cucumber raita"},
            {"slot":"Evening · 4 PM",        "desc":"1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot":"Dinner · 7 PM",         "desc":"⭐ Enjoyment meal"},
            {"slot":"Bedtime",               "desc":"200ml toned milk + 2 pinches cinnamon"},
        ]
    }
}


# ── Firebase REST ──────────────────────────────────────────────────────────────

_TOKEN = {"value": None, "exp": 0}

def get_token() -> str:
    now = int(time.time())
    if _TOKEN["value"] and now < _TOKEN["exp"] - 60:
        return _TOKEN["value"]
    c = st.secrets["firebase_credentials"]
    pk = c["private_key"].replace("\\n", "\n")
    payload = {
        "iss": c["client_email"], "sub": c["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now, "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/datastore",
    }
    signed = jwt.encode(payload, pk, algorithm="RS256")
    r = requests.post("https://oauth2.googleapis.com/token",
                      data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                            "assertion": signed}, timeout=10)
    r.raise_for_status()
    d = r.json()
    _TOKEN["value"] = d["access_token"]
    _TOKEN["exp"]   = now + d.get("expires_in", 3600)
    return _TOKEN["value"]

def _hdrs():
    return {"Authorization": f"Bearer {get_token()}", "Content-Type": "application/json"}

def _fs_url(path):
    pid = st.secrets["firebase_credentials"]["project_id"]
    return f"https://firestore.googleapis.com/v1/projects/{pid}/databases/(default)/documents/{path}"

def _to(v):
    if isinstance(v, bool):   return {"booleanValue": v}
    if isinstance(v, int):    return {"integerValue": str(v)}
    if isinstance(v, float):  return {"doubleValue": v}
    if isinstance(v, str):    return {"stringValue": v}
    if isinstance(v, dict):   return {"mapValue": {"fields": {k: _to(val) for k, val in v.items()}}}
    if isinstance(v, list):   return {"arrayValue": {"values": [_to(i) for i in v]}}
    return {"nullValue": None}

def _fr(v):
    if "stringValue"    in v: return v["stringValue"]
    if "booleanValue"   in v: return v["booleanValue"]
    if "integerValue"   in v: return int(v["integerValue"])
    if "doubleValue"    in v: return v["doubleValue"]
    if "nullValue"      in v: return None
    if "timestampValue" in v: return v["timestampValue"]
    if "mapValue"       in v: return {k: _fr(val) for k, val in v["mapValue"].get("fields",{}).items()}
    if "arrayValue"     in v: return [_fr(i) for i in v["arrayValue"].get("values",[])]
    return None

def fs_get(col, doc_id):
    r = requests.get(_fs_url(f"{col}/{doc_id}"), headers=_hdrs(), timeout=10)
    if r.status_code == 404: return None
    r.raise_for_status()
    return {k: _fr(v) for k, v in r.json().get("fields", {}).items()}

def fs_set(col, doc_id, data):
    fields = {k: _to(v) for k, v in data.items()}
    r = requests.patch(_fs_url(f"{col}/{doc_id}"), headers=_hdrs(),
                       json={"fields": fields}, timeout=10)
    r.raise_for_status()

def fs_delete(col, doc_id):
    requests.delete(_fs_url(f"{col}/{doc_id}"), headers=_hdrs(), timeout=10)

def fs_list(col, filters=None):
    r = requests.get(_fs_url(col), headers=_hdrs(), timeout=20)
    if r.status_code != 200: return []
    result = []
    for doc in r.json().get("documents", []):
        did    = doc["name"].split("/")[-1]
        fields = {k: _fr(v) for k, v in doc.get("fields", {}).items()}
        if filters and not all(fields.get(f["field"]) == f["value"] for f in filters):
            continue
        result.append({"id": did, **fields})
    return result

def fs_add(col, data):
    fields = {k: _to(v) for k, v in data.items()}
    r = requests.post(_fs_url(col), headers=_hdrs(),
                      json={"fields": fields}, timeout=10)
    r.raise_for_status()
    return r.json()["name"].split("/")[-1]


# ── Cloudinary ─────────────────────────────────────────────────────────────────

def upload_photo(file_bytes, filename) -> str:
    r = requests.post(
        f"https://api.cloudinary.com/v1_1/{st.secrets['cloudinary_cloud_name']}/image/upload",
        data={"upload_preset": st.secrets["cloudinary_upload_preset"]},
        files={"file": (filename, file_bytes)},
        timeout=30,
    )
    return r.json().get("secure_url", "") if r.status_code == 200 else ""


# ── Meal plan (default + Firestore overrides) ──────────────────────────────────

@st.cache_data(ttl=300)
def load_custom_plan():
    return {d["id"]: d.get("desc","") for d in fs_list("meal_plan")}

def get_desc(day, person, idx, custom):
    return custom.get(f"{day}_{person}_{idx}") or DEFAULT_MEALS[day][person][idx]["desc"]

def get_slot(day, person, idx):
    return DEFAULT_MEALS[day][person][idx]["slot"]

def meal_count(day, person):
    return len(DEFAULT_MEALS[day][person])


# ── Tracking (date-based) ──────────────────────────────────────────────────────

def t_key(d: date, person, idx):
    return f"{d.isoformat()}_{person}_{idx}"

def load_entry(d: date, person, idx):
    data = fs_get("tracking", t_key(d, person, idx))
    return data or {"status":"pending","comment":"","image_url":""}

def save_entry(d: date, person, idx, data):
    fs_set("tracking", t_key(d, person, idx), data)

@st.cache_data(ttl=30)
def load_all_tracking():
    return {doc["id"]: doc for doc in fs_list("tracking")}

def bust_tracking():
    load_all_tracking.clear()

def day_completion(d: date, all_tracking: dict) -> float:
    """Returns fraction of meals tracked (done or skipped) for a date."""
    day_name = DAYS[d.weekday()]
    total = done = 0
    for p in ["p1","p2"]:
        for i in range(meal_count(day_name, p)):
            total += 1
            e = all_tracking.get(t_key(d, p, i), {})
            if e.get("status","pending") in ("done","skipped"):
                done += 1
    return done / total if total else 0


# ── Auth ───────────────────────────────────────────────────────────────────────

def check_password():
    if st.session_state.get("auth"): return True
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("## 🥗 Meal Tracker")
    pw = st.text_input("Password", type="password",
                       label_visibility="collapsed", placeholder="Enter password")
    if st.button("Unlock", use_container_width=True):
        if pw == st.secrets["app_password"]:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.markdown('</div>', unsafe_allow_html=True)
    return False


# ── Calendar HTML ──────────────────────────────────────────────────────────────

def calendar_html(year, month, all_tracking, selected: date) -> str:
    first_dow = cal_lib.monthrange(year, month)[0]  # 0=Mon
    num_days  = cal_lib.monthrange(year, month)[1]
    hdr = "".join(f'<div class="cal-hdr">{d}</div>' for d in ["Mo","Tu","We","Th","Fr","Sa","Su"])
    cells = '<div class="cal-empty"></div>' * first_dow
    for day_n in range(1, num_days + 1):
        d = date(year, month, day_n)
        is_future   = d > TODAY
        is_today    = d == TODAY
        is_selected = d == selected
        extra = ""
        if is_today:    extra += " cal-today"
        if is_selected: extra += " cal-sel"
        if is_future:
            css = "cal-future"
        else:
            pct = day_completion(d, all_tracking)
            if pct == 0:      css = "cal-none"
            elif pct < 0.8:   css = "cal-part"
            else:             css = "cal-full"
        cells += f'<div class="cal-day {css}{extra}">{day_n}</div>'
    return f"""
    <div class="cal-grid">{hdr}{cells}</div>
    <div style="display:flex;gap:10px;font-size:11px;color:#888;margin-bottom:8px;flex-wrap:wrap">
      <span>🟩 Fully tracked</span><span>🟨 Partial</span>
      <span>⬜ Not tracked</span><span style="border:2px solid #7F77DD;border-radius:4px;padding:0 4px">Selected</span>
    </div>"""


# ── Meal card ──────────────────────────────────────────────────────────────────

def meal_card(d: date, person, idx, custom):
    day_name  = DAYS[d.weekday()]
    slot      = get_slot(day_name, person, idx)
    desc      = get_desc(day_name, person, idx, custom)
    entry     = load_entry(d, person, idx)
    status    = entry.get("status","pending")
    comment   = entry.get("comment","")
    image_url = entry.get("image_url","")
    is_future = d > TODAY

    css = "meal-box" + (" done" if status=="done" else " skipped" if status=="skipped" else "")
    st.markdown(f'<div class="{css}"><div class="meal-slot">{slot}</div>'
                f'<div class="meal-desc">{desc}</div></div>', unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True)

    uid = f"{d.isoformat()}_{person}_{idx}"
    if not is_future:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅" if status!="done" else "↩", key=f"done_{uid}", use_container_width=True):
                entry["status"] = "done" if status!="done" else "pending"
                save_entry(d, person, idx, entry); bust_tracking(); st.rerun()
        with c2:
            if st.button("❌" if status!="skipped" else "↩", key=f"skip_{uid}", use_container_width=True):
                entry["status"] = "skipped" if status!="skipped" else "pending"
                save_entry(d, person, idx, entry); bust_tracking(); st.rerun()
        with c3:
            icon = "✏️" if (comment or image_url) else "📝"
            if st.button(icon, key=f"note_{uid}", use_container_width=True):
                k = f"open_{uid}"
                st.session_state[k] = not st.session_state.get(k, False)

        if st.session_state.get(f"open_{uid}", False):
            new_comment = st.text_area("Note", value=comment, key=f"ta_{uid}",
                                       placeholder="Note or substitution…",
                                       label_visibility="collapsed", height=68)
            up = st.file_uploader("Photo", type=["jpg","jpeg","png","heic"],
                                  key=f"up_{uid}", label_visibility="collapsed")
            cs, cr = st.columns(2)
            with cs:
                if st.button("Save", key=f"sv_{uid}", use_container_width=True):
                    entry["comment"] = new_comment
                    if up:
                        with st.spinner("Uploading…"):
                            url = upload_photo(up.read(), up.name)
                        if url: entry["image_url"] = url
                    save_entry(d, person, idx, entry)
                    bust_tracking()
                    st.session_state[f"open_{uid}"] = False
                    st.rerun()
            with cr:
                if image_url and st.button("Remove photo", key=f"rm_{uid}", use_container_width=True):
                    entry["image_url"] = ""
                    save_entry(d, person, idx, entry); bust_tracking(); st.rerun()

    if comment and not st.session_state.get(f"open_{uid}", False):
        st.caption(f"💬 {comment}")
    st.markdown("<div style='margin-bottom:5px'></div>", unsafe_allow_html=True)


# ── Snacks ─────────────────────────────────────────────────────────────────────

def render_snacks(d: date, person):
    st.markdown("---")
    st.markdown("**Extra / unplanned snacks**")
    snacks = fs_list("snacks", filters=[{"field":"date","value":d.isoformat()},
                                        {"field":"person","value":person}])
    for s in snacks:
        ts = s.get("timestamp","")
        if "T" in ts:
            try: ts = datetime.fromisoformat(ts.replace("Z","+00:00")).strftime("%I:%M %p")
            except: ts = ""
        st.markdown(f'<div class="snack-box">🍽 <b>{s.get("desc","")}</b>'
                    f'{" · "+ts if ts else ""}</div>', unsafe_allow_html=True)
        if s.get("image_url"): st.image(s["image_url"], use_container_width=True)
        if st.button("Delete", key=f"del_{s['id']}"):
            fs_delete("snacks", s["id"]); st.rerun()

    if d <= TODAY:
        ak = f"add_{d.isoformat()}_{person}"
        if st.button("+ Log a snack", key=f"btn_{ak}"):
            st.session_state[ak] = not st.session_state.get(ak, False)
        if st.session_state.get(ak, False):
            desc = st.text_input("What?", key=f"desc_{ak}", label_visibility="collapsed",
                                 placeholder="e.g. 1 chai + 2 biscuits…")
            img  = st.file_uploader("Photo (optional)", type=["jpg","jpeg","png","heic"],
                                    key=f"simg_{ak}", label_visibility="collapsed")
            if st.button("Log", key=f"log_{ak}", use_container_width=True):
                if desc.strip():
                    img_url = ""
                    if img:
                        with st.spinner("Uploading…"):
                            img_url = upload_photo(img.read(), img.name)
                    fs_add("snacks", {"date": d.isoformat(), "person": person,
                                      "desc": desc.strip(), "image_url": img_url,
                                      "timestamp": datetime.utcnow().isoformat()+"Z"})
                    st.session_state[ak] = False; st.rerun()
                else:
                    st.warning("Please describe what you had.")


# ── Page: Tracker ──────────────────────────────────────────────────────────────

def page_tracker():
    all_tracking = load_all_tracking()
    custom       = load_custom_plan()

    # Month navigation
    if "cal_year"  not in st.session_state: st.session_state.cal_year  = TODAY.year
    if "cal_month" not in st.session_state: st.session_state.cal_month = TODAY.month
    if "sel_date"  not in st.session_state: st.session_state.sel_date  = TODAY

    y, m = st.session_state.cal_year, st.session_state.cal_month
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if st.button("◀", use_container_width=True):
            if m == 1: st.session_state.cal_year -= 1; st.session_state.cal_month = 12
            else:      st.session_state.cal_month -= 1
            st.rerun()
    with c2:
        st.markdown(f"<div style='text-align:center;font-weight:500;padding-top:6px'>"
                    f"{cal_lib.month_name[m]} {y}</div>", unsafe_allow_html=True)
    with c3:
        max_y, max_m = TODAY.year, TODAY.month
        if (y, m) < (max_y, max_m):
            if st.button("▶", use_container_width=True):
                if m == 12: st.session_state.cal_year += 1; st.session_state.cal_month = 1
                else:       st.session_state.cal_month += 1
                st.rerun()

    st.markdown(calendar_html(y, m, all_tracking, st.session_state.sel_date),
                unsafe_allow_html=True)

    # Date picker
    sel = st.date_input("Select a date", value=st.session_state.sel_date,
                        min_value=date(2025, 1, 1), max_value=TODAY,
                        label_visibility="collapsed")
    if sel != st.session_state.sel_date:
        st.session_state.sel_date  = sel
        st.session_state.cal_year  = sel.year
        st.session_state.cal_month = sel.month
        st.rerun()

    d        = st.session_state.sel_date
    day_name = DAYS[d.weekday()]
    label    = "Today" if d == TODAY else d.strftime("%a, %d %b %Y")

    # Day completion summary
    pct = day_completion(d, all_tracking)
    done_n = sum(
        1 for p in ["p1","p2"]
        for i in range(meal_count(day_name, p))
        if all_tracking.get(t_key(d,p,i),{}).get("status","pending") in ("done","skipped")
    )
    total_n = sum(meal_count(day_name, p) for p in ["p1","p2"])
    st.caption(f"{label} · {done_n}/{total_n} meals tracked")

    st.divider()

    tab1, tab2 = st.tabs(["👤 Person 1 · Veg", "🏃 Person 2 · Runner"])
    with tab1:
        st.markdown('<div class="p1-hdr">Person 1 · Vegetarian</div>', unsafe_allow_html=True)
        for i in range(meal_count(day_name, "p1")):
            meal_card(d, "p1", i, custom)
        render_snacks(d, "p1")
    with tab2:
        st.markdown('<div class="p2-hdr">Person 2 · Non-veg · Runner</div>', unsafe_allow_html=True)
        for i in range(meal_count(day_name, "p2")):
            meal_card(d, "p2", i, custom)
        render_snacks(d, "p2")


# ── Page: Measurements ─────────────────────────────────────────────────────────

def load_measurements(person):
    docs = fs_list("measurements", filters=[{"field":"person","value":person}])
    docs.sort(key=lambda x: x.get("date",""))
    return docs

def last_measurement_date(docs, field):
    hits = [d for d in docs if d.get(field) is not None]
    return hits[-1].get("date") if hits else None

def is_due(last_date_str, frequency_days):
    if not last_date_str: return True
    last = date.fromisoformat(last_date_str)
    return (TODAY - last).days >= frequency_days

def page_measurements():
    st.markdown("### 📏 Measurements")
    tab1, tab2 = st.tabs(["👤 Person 1", "🏃 Person 2"])
    for tab, person, label in [(tab1,"p1","Person 1"),(tab2,"p2","Person 2")]:
        with tab:
            docs = load_measurements(person)

            # ── Weight (weekly) ──────────────────────
            last_wt = last_measurement_date(docs, "weight")
            wt_due  = is_due(last_wt, 7)
            badge   = '<span class="due-badge due-now">Log now</span>' if wt_due \
                      else '<span class="due-badge due-ok">Up to date</span>'
            st.markdown(f'<div class="meas-lbl">Weight (weekly) {badge}</div>',
                        unsafe_allow_html=True)
            if last_wt:
                st.caption(f"Last logged: {last_wt}")

            wk = f"wt_{person}"
            with st.expander("Log weight", expanded=wt_due):
                wt_val  = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0,
                                          step=0.1, key=f"wtval_{person}", format="%.1f")
                wt_date = st.date_input("Date", value=TODAY, max_value=TODAY,
                                        key=f"wtdate_{person}")
                if st.button("Save weight", key=f"svwt_{person}", use_container_width=True):
                    doc_id = f"{person}_{wt_date.isoformat()}"
                    existing = fs_get("measurements", doc_id) or {}
                    existing.update({"person": person, "date": wt_date.isoformat(),
                                     "weight": float(wt_val)})
                    fs_set("measurements", doc_id, existing)
                    st.success(f"Saved {wt_val} kg for {wt_date}")
                    st.rerun()

            # ── Hip & Waist (fortnightly) ────────────
            last_hw = last_measurement_date(docs, "hip")
            hw_due  = is_due(last_hw, 14)
            badge2  = '<span class="due-badge due-now">Log now</span>' if hw_due \
                      else '<span class="due-badge due-ok">Up to date</span>'
            st.markdown(f'<div class="meas-lbl" style="margin-top:14px">Hip & Waist (fortnightly) {badge2}</div>',
                        unsafe_allow_html=True)
            if last_hw:
                st.caption(f"Last logged: {last_hw}")

            with st.expander("Log hip & waist", expanded=hw_due):
                c1, c2 = st.columns(2)
                with c1:
                    hip_val = st.number_input("Hip (cm)", min_value=50.0, max_value=200.0,
                                              step=0.5, key=f"hipval_{person}", format="%.1f")
                with c2:
                    wst_val = st.number_input("Waist (cm)", min_value=40.0, max_value=200.0,
                                              step=0.5, key=f"wstval_{person}", format="%.1f")
                hw_date = st.date_input("Date", value=TODAY, max_value=TODAY,
                                        key=f"hwdate_{person}")
                if st.button("Save measurements", key=f"svhw_{person}", use_container_width=True):
                    doc_id = f"{person}_{hw_date.isoformat()}"
                    existing = fs_get("measurements", doc_id) or {}
                    existing.update({"person": person, "date": hw_date.isoformat(),
                                     "hip": float(hip_val), "waist": float(wst_val)})
                    fs_set("measurements", doc_id, existing)
                    st.success(f"Saved hip {hip_val}cm, waist {wst_val}cm for {hw_date}")
                    st.rerun()

            # ── Trends ───────────────────────────────
            if docs:
                st.markdown("---")
                st.markdown("**Trends**")

                wt_rows = [(d["date"], d["weight"]) for d in docs if d.get("weight") is not None]
                if wt_rows:
                    st.caption("Weight (kg)")
                    wt_data = {"Weight (kg)": {r[0]: r[1] for r in wt_rows}}
                    st.line_chart(wt_data)

                hw_rows = [(d["date"], d.get("hip"), d.get("waist"))
                           for d in docs if d.get("hip") is not None]
                if hw_rows:
                    st.caption("Hip & Waist (cm)")
                    chart_data = {
                        "Hip (cm)":   {r[0]: r[1] for r in hw_rows if r[1]},
                        "Waist (cm)": {r[0]: r[2] for r in hw_rows if r[2]},
                    }
                    st.line_chart(chart_data)
            else:
                st.info("No measurements logged yet.")


# ── Page: Edit Meal Plan ───────────────────────────────────────────────────────

def page_edit_plan():
    st.markdown("### ✏️ Edit meal plan")
    st.caption("Changes apply to all future weeks. Current tracking data is not affected.")

    custom = load_custom_plan()

    day = st.selectbox("Day", DAYS, label_visibility="collapsed")
    tab1, tab2 = st.tabs(["👤 Person 1", "🏃 Person 2"])

    for tab, person in [(tab1,"p1"),(tab2,"p2")]:
        with tab:
            st.markdown(f'<div class="{"p1-hdr" if person=="p1" else "p2-hdr"}">'
                        f'{"Person 1 · Vegetarian" if person=="p1" else "Person 2 · Non-veg · Runner"}'
                        f'</div>', unsafe_allow_html=True)
            for i in range(meal_count(day, person)):
                slot     = get_slot(day, person, i)
                cur_desc = get_desc(day, person, i, custom)
                plan_key = f"{day}_{person}_{i}"

                with st.expander(slot):
                    new_desc = st.text_area(
                        "Meal description", value=cur_desc,
                        key=f"edit_{plan_key}", height=80,
                        label_visibility="collapsed"
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Save change", key=f"sv_{plan_key}", use_container_width=True):
                            if new_desc.strip():
                                fs_set("meal_plan", plan_key, {"desc": new_desc.strip()})
                                load_custom_plan.clear()
                                st.success("Saved.")
                                st.rerun()
                    with c2:
                        if plan_key in custom:
                            if st.button("Reset to default", key=f"rst_{plan_key}", use_container_width=True):
                                fs_delete("meal_plan", plan_key)
                                load_custom_plan.clear()
                                st.success("Reset to default.")
                                st.rerun()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not check_password():
        return

    page = st.radio("", ["📅 Tracker", "📏 Measurements", "✏️ Edit plan"],
                    horizontal=True, label_visibility="collapsed")
    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

    if page == "📅 Tracker":
        page_tracker()
    elif page == "📏 Measurements":
        page_measurements()
    else:
        page_edit_plan()

    with st.expander("⚙️ Settings"):
        if st.button("Sign out", type="secondary"):
            st.session_state["auth"] = False
            st.rerun()


if __name__ == "__main__":
    main()
