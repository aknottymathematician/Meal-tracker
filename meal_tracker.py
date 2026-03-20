import streamlit as st
from datetime import datetime
import requests
import json
import time
import jwt  # PyJWT — tiny package, replaces the entire firebase-admin SDK

st.set_page_config(
    page_title="Meal Tracker",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .block-container { padding: 1rem 0.75rem 3rem; max-width: 100%; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { padding: 6px 12px; font-size: 13px; }
    div[data-testid="column"] { padding: 0 3px; }
    .meal-box {
        border: 1px solid #e0e0e0; border-radius: 10px;
        padding: 10px 12px; margin-bottom: 4px; background: #fafafa;
    }
    .meal-box.done    { border-color: #1D9E75; background: #f0faf6; }
    .meal-box.skipped { border-color: #E24B4A; background: #fff5f5; }
    .meal-slot { font-size: 11px; color: #888; text-transform: uppercase;
                 letter-spacing: .05em; margin-bottom: 3px; }
    .meal-desc { font-size: 13px; color: #333; line-height: 1.4; }
    .snack-box { border: 1px solid #e0d890; border-radius: 10px;
                 padding: 10px 12px; margin-bottom: 8px; background: #fffef0; }
    .p1-header { background: #EEEDFE; color: #3C3489; font-size: 15px;
                 font-weight: 600; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; }
    .p2-header { background: #E1F5EE; color: #085041; font-size: 15px;
                 font-weight: 600; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; }
    .progress-bar-container { background: #eee; border-radius: 20px; height: 8px; margin: 6px 0 14px; }
    .progress-bar-fill { height: 8px; border-radius: 20px; background: #1D9E75; }
    .stButton > button { border-radius: 20px; font-size: 13px; padding: 4px 14px; }
    .stTextArea textarea { font-size: 13px; }
    h2 { font-size: 17px !important; }
    .login-wrap { max-width: 320px; margin: 80px auto 0; text-align: center; }
    img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

MEALS = {
    "Mon": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 banana or whole fruit + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "1 scoop whey in 200ml water + 30g moong sprouts"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C rich fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g sabzi/salad + 1 multigrain bread + 70g tofu bhurji"},
        ],
        "p2": [
            {"slot": "Pre-training · 6:30 AM", "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400ml oats protein smoothie + 30g moong sprouts"},
            {"slot": "Mid-morning · 10 AM",    "desc": "4 egg whites (bhurji/omelette)"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + 3 methi/cabbage parathas + 100g tofu bhurji + 100g skyr yogurt"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g roasted peanuts + ½ scoop whey in 200ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100g sabzi/salad + 1 multigrain bread + 150g tofu bhurji"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon (no sugar)"},
        ]
    },
    "Tue": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 fruit/banana + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "1 scoop whey in 200ml water + 30g boiled chickpeas"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g salad + 2 jowar bhakri + 50g low fat pan fry paneer + 50g curd + samah"},
        ],
        "p2": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 600ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400ml oats protein smoothie + 30g boiled chickpeas"},
            {"slot": "Mid-morning · 10 AM",    "desc": "4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + 3 jowar bhakri + 100g low fat pan fry paneer + 100g plain curd"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g makhana + ½ scoop whey in 200ml water"},
            {"slot": "Dinner · 7 PM",          "desc": "100g sabzi/salad + 2 jowar bhakri + 150g low fat tossed paneer"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Wed": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 fruit/banana + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "1 vegetable sandwich + 1 scoop whey in 200ml water"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g salad + 1 jowar bhakri + 70g low fat tossed paneer"},
        ],
        "p2": [
            {"slot": "Pre-training · 6:30 AM", "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "2 veg sandwiches + 200ml toned milk + 1 scoop whey"},
            {"slot": "Mid-morning · 10 AM",    "desc": "4 egg whites + 1 vit C fruit"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + 200g mix veg pulao (rice + quinoa) + 100g chicken kheema + 200ml chaas"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g roasted peanuts + ½ scoop whey"},
            {"slot": "Dinner · 7 PM",          "desc": "100g sabzi + boiled chickpeas/dal + 150g air fried/pan sautee chicken + 100g veggies"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Thu": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 fruit/banana + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "1 scoop whey in 200ml water + 30g kala channa (soak overnight)"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g salad + 200g mix veg pulao (rice + quinoa) + 100g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 600ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400ml oats protein smoothie + 30g boiled kala channa"},
            {"slot": "Mid-morning · 10 AM",    "desc": "4 egg whites"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + 3 whole wheat roti + 150g rajma masala + 100g skyr yogurt"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot": "Dinner · 7 PM",          "desc": "100g sabzi + 2 whole wheat roti + 150g tofu stir fry"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Fri": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 fruit/banana + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "2 bread toast + 1 scoop whey in 200ml water"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g salad + 2 whole wheat roti + 100g rajma masala + 50g curd + samah"},
        ],
        "p2": [
            {"slot": "Pre-training · 6:30 AM", "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "3 bread toast + 200ml toned milk + 1 scoop whey"},
            {"slot": "Mid-morning · 10 AM",    "desc": "4 egg whites + 1 vit C fruit"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + 3 jowar bhakri + 100g low fat palak paneer + 100g plain curd"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g roasted peanuts + ½ scoop whey"},
            {"slot": "Dinner · 7 PM",          "desc": "100g sabzi + 2 jowar bhakri + 150g low fat palak paneer"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sat": {
        "p1": [
            {"slot": "Pre-training · 6 AM",  "desc": "1 fruit/banana + Supply 6 salts in 500–600ml during training"},
            {"slot": "Breakfast · 8:30 AM",  "desc": "1 scoop whey in 200ml water + 30g boiled chickpeas"},
            {"slot": "Lunch · 12:30 PM",     "desc": "100g salad + 2 methi/cabbage parathas + 50g tofu bhurji + 150ml chaas + samah"},
            {"slot": "Evening · 4 PM",       "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",        "desc": "100g salad + 2 jowar bhakri + 50g palak paneer + 50g curd + samah"},
        ],
        "p2": [
            {"slot": "Pre-training · 6 AM",    "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts in 500ml during training"},
            {"slot": "Breakfast · 8:30 AM",    "desc": "400ml oats protein smoothie + 30g boiled chickpeas"},
            {"slot": "Lunch · 12:30 PM",       "desc": "100g salad + Tofu burrito wrap (2 wheat roti + 100g tofu + 20g rajma + 75g veggies + 15g salsa) + 200ml chaas"},
            {"slot": "Evening · 4 PM",         "desc": "1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot": "Dinner · 7 PM",          "desc": "250g shirataki noodles (150g noodles + 100g veggies) + 150g chicken stir fry + 200ml tomato soup"},
            {"slot": "Bedtime",                "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    },
    "Sun": {
        "p1": [
            {"slot": "Pre-training · 6 AM",     "desc": "1 fruit/banana + plain water during training"},
            {"slot": "Breakfast · 8:30 AM",     "desc": "1 scoop whey in 200ml water + 30g kala channa"},
            {"slot": "Lunch · 12:30 PM",        "desc": "⭐ Enjoyment meal"},
            {"slot": "Evening · 4 PM",          "desc": "Green tea + 1 vit C fruit"},
            {"slot": "Dinner · 7 PM",           "desc": "100g salad + 200g veg khichdi (75g rice + 75g dal + 50g veggies) + 100g skyr yogurt + samah"},
        ],
        "p2": [
            {"slot": "Pre-training (long run)", "desc": "1 fruit/banana + 200ml black coffee + Supply 6 salts + energy gel at 45 min + energy gel at 80 min"},
            {"slot": "Breakfast · 8:30 AM",     "desc": "400ml oats smoothie + 30g moong sprouts + 150g yogurt bowl (100g yogurt + ½ scoop whey + 1 fruit + 1 tsp chia)"},
            {"slot": "Lunch · 12:30 PM",        "desc": "100g salad + 250g veg khichdi OR 250g chicken biryani + 100g cucumber raita"},
            {"slot": "Evening · 4 PM",          "desc": "1 vit C fruit + 20g makhana + ½ scoop whey"},
            {"slot": "Dinner · 7 PM",           "desc": "⭐ Enjoyment meal"},
            {"slot": "Bedtime",                 "desc": "200ml toned milk + 2 pinches cinnamon"},
        ]
    }
}


# ── Firebase REST API (replaces firebase-admin — no heavy SDK needed) ──────────

TOKEN_CACHE = {"token": None, "expires_at": 0}

def get_access_token() -> str:
    """Get a short-lived OAuth2 token using the service account private key."""
    now = int(time.time())
    if TOKEN_CACHE["token"] and now < TOKEN_CACHE["expires_at"] - 60:
        return TOKEN_CACHE["token"]

    creds = st.secrets["firebase_credentials"]
    private_key = creds["private_key"].replace("\\n", "\n")

    payload = {
        "iss": creds["client_email"],
        "sub": creds["client_email"],
        "aud": "https://oauth2.googleapis.com/token",
        "iat": now,
        "exp": now + 3600,
        "scope": "https://www.googleapis.com/auth/datastore",
    }
    signed = jwt.encode(payload, private_key, algorithm="RS256")
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": signed,
        },
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    TOKEN_CACHE["token"] = data["access_token"]
    TOKEN_CACHE["expires_at"] = now + data.get("expires_in", 3600)
    return TOKEN_CACHE["token"]


def fs_url(path: str) -> str:
    project_id = st.secrets["firebase_credentials"]["project_id"]
    return f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{path}"


def fs_headers() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json"}


def _to_fs(value) -> dict:
    """Convert a Python value to Firestore REST value format."""
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, dict):
        return {"mapValue": {"fields": {k: _to_fs(v) for k, v in value.items()}}}
    if isinstance(value, list):
        return {"arrayValue": {"values": [_to_fs(v) for v in value]}}
    return {"nullValue": None}


def _from_fs(value: dict):
    """Convert a Firestore REST value to a Python value."""
    if "stringValue"  in value: return value["stringValue"]
    if "booleanValue" in value: return value["booleanValue"]
    if "integerValue" in value: return int(value["integerValue"])
    if "doubleValue"  in value: return value["doubleValue"]
    if "nullValue"    in value: return None
    if "mapValue"     in value:
        return {k: _from_fs(v) for k, v in value["mapValue"].get("fields", {}).items()}
    if "arrayValue"   in value:
        return [_from_fs(v) for v in value["arrayValue"].get("values", [])]
    if "timestampValue" in value: return value["timestampValue"]
    return None


def fs_get(collection: str, doc_id: str) -> dict | None:
    r = requests.get(fs_url(f"{collection}/{doc_id}"), headers=fs_headers(), timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    fields = r.json().get("fields", {})
    return {k: _from_fs(v) for k, v in fields.items()}


def fs_set(collection: str, doc_id: str, data: dict):
    fields = {k: _to_fs(v) for k, v in data.items()}
    r = requests.patch(
        fs_url(f"{collection}/{doc_id}"),
        headers=fs_headers(),
        json={"fields": fields},
        timeout=10,
    )
    r.raise_for_status()


def fs_list(collection: str, filters: list[dict] | None = None) -> list[dict]:
    """Simple collection fetch — returns list of {id, ...fields} dicts."""
    r = requests.get(fs_url(collection), headers=fs_headers(), timeout=15)
    if r.status_code == 200:
        docs = r.json().get("documents", [])
        result = []
        for doc in docs:
            doc_id = doc["name"].split("/")[-1]
            fields = {k: _from_fs(v) for k, v in doc.get("fields", {}).items()}
            if filters:
                if all(fields.get(f["field"]) == f["value"] for f in filters):
                    result.append({"id": doc_id, **fields})
            else:
                result.append({"id": doc_id, **fields})
        return result
    return []


def fs_add(collection: str, data: dict) -> str:
    fields = {k: _to_fs(v) for k, v in data.items()}
    r = requests.post(
        fs_url(collection),
        headers=fs_headers(),
        json={"fields": fields},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["name"].split("/")[-1]


def fs_delete(collection: str, doc_id: str):
    requests.delete(fs_url(f"{collection}/{doc_id}"), headers=fs_headers(), timeout=10)


# ── Cloudinary upload ──────────────────────────────────────────────────────────

def upload_to_cloudinary(file_bytes: bytes, filename: str) -> str:
    cloud_name    = st.secrets["cloudinary_cloud_name"]
    upload_preset = st.secrets["cloudinary_upload_preset"]
    r = requests.post(
        f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload",
        data={"upload_preset": upload_preset},
        files={"file": (filename, file_bytes)},
        timeout=30,
    )
    if r.status_code == 200:
        return r.json().get("secure_url", "")
    st.error(f"Photo upload failed: {r.text}")
    return ""


# ── Helpers ────────────────────────────────────────────────────────────────────

def load_entry(doc_id: str) -> dict:
    data = fs_get("meal_entries", doc_id)
    return data if data else {"status": "pending", "comment": "", "image_url": ""}


def save_entry(doc_id: str, data: dict):
    fs_set("meal_entries", doc_id, data)


@st.cache_data(ttl=30)
def load_all_stats() -> dict:
    docs = fs_list("meal_entries")
    return {d["id"]: d for d in docs}


def bust_stats_cache():
    load_all_stats.clear()


# ── Auth ───────────────────────────────────────────────────────────────────────

def check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("## 🥗 Meal Tracker")
    st.markdown("Enter the shared password to continue.")
    pw = st.text_input("Password", type="password",
                       label_visibility="collapsed", placeholder="Password")
    if st.button("Unlock", use_container_width=True):
        if pw == st.secrets["app_password"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password — try again.")
    st.markdown('</div>', unsafe_allow_html=True)
    return False


# ── Meal card ──────────────────────────────────────────────────────────────────

def render_meal_card(day, person, idx, meal):
    doc_id    = f"{day}_{person}_{idx}"
    entry     = load_entry(doc_id)
    status    = entry.get("status", "pending")
    comment   = entry.get("comment", "")
    image_url = entry.get("image_url", "")

    css = "meal-box" + (" done" if status == "done" else " skipped" if status == "skipped" else "")
    st.markdown(f"""
    <div class="{css}">
        <div class="meal-slot">{meal['slot']}</div>
        <div class="meal-desc">{meal['desc']}</div>
    </div>""", unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        lbl = "✅ Done" if status != "done" else "↩ Undo"
        if st.button(lbl, key=f"done_{doc_id}", use_container_width=True):
            entry["status"] = "done" if status != "done" else "pending"
            save_entry(doc_id, entry)
            bust_stats_cache()
            st.rerun()
    with c2:
        lbl = "❌ Skip" if status != "skipped" else "↩ Undo"
        if st.button(lbl, key=f"skip_{doc_id}", use_container_width=True):
            entry["status"] = "skipped" if status != "skipped" else "pending"
            save_entry(doc_id, entry)
            bust_stats_cache()
            st.rerun()
    with c3:
        icon = "✏️" if (comment or image_url) else "📝"
        if st.button(icon, key=f"exp_{doc_id}", use_container_width=True):
            k = f"open_{doc_id}"
            st.session_state[k] = not st.session_state.get(k, False)

    if st.session_state.get(f"open_{doc_id}", False):
        new_comment = st.text_area(
            "Note", value=comment, key=f"ta_{doc_id}",
            placeholder="Note or substitution…",
            label_visibility="collapsed", height=72
        )
        uploaded = st.file_uploader(
            "Attach photo", type=["jpg", "jpeg", "png", "heic"],
            key=f"up_{doc_id}", label_visibility="collapsed"
        )
        col_save, col_rm = st.columns(2)
        with col_save:
            if st.button("Save", key=f"save_{doc_id}", use_container_width=True):
                entry["comment"] = new_comment
                if uploaded:
                    with st.spinner("Uploading photo…"):
                        url = upload_to_cloudinary(uploaded.read(), uploaded.name)
                    if url:
                        entry["image_url"] = url
                save_entry(doc_id, entry)
                bust_stats_cache()
                st.session_state[f"open_{doc_id}"] = False
                st.rerun()
        with col_rm:
            if image_url and st.button("Remove photo", key=f"rm_{doc_id}", use_container_width=True):
                entry["image_url"] = ""
                save_entry(doc_id, entry)
                bust_stats_cache()
                st.rerun()

    if comment and not st.session_state.get(f"open_{doc_id}", False):
        st.caption(f"💬 {comment}")

    st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)


# ── Snacks ─────────────────────────────────────────────────────────────────────

def render_snacks(day, person):
    st.markdown("---")
    st.markdown("**Extra / unplanned snacks**")

    snacks = fs_list("snacks", filters=[
        {"field": "day",    "value": day},
        {"field": "person", "value": person},
    ])

    for snack in snacks:
        ts_str = snack.get("timestamp", "")
        if isinstance(ts_str, str) and "T" in ts_str:
            try:
                ts_str = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).strftime("%I:%M %p")
            except Exception:
                ts_str = ""
        st.markdown(
            f'<div class="snack-box">🍽 <b>{snack.get("desc","")}</b>'
            f'{" · " + ts_str if ts_str else ""}</div>',
            unsafe_allow_html=True
        )
        if snack.get("image_url"):
            st.image(snack["image_url"], use_container_width=True)
        if st.button("Delete", key=f"del_{snack['id']}"):
            fs_delete("snacks", snack["id"])
            st.rerun()

    add_key = f"add_{day}_{person}"
    if st.button("+ Log a snack", key=f"btn_{add_key}"):
        st.session_state[add_key] = not st.session_state.get(add_key, False)

    if st.session_state.get(add_key, False):
        desc = st.text_input(
            "What did you have?", key=f"desc_{add_key}",
            label_visibility="collapsed",
            placeholder="e.g. 1 chai + 2 biscuits…"
        )
        img = st.file_uploader(
            "Photo (optional)", type=["jpg", "jpeg", "png", "heic"],
            key=f"img_{add_key}", label_visibility="collapsed"
        )
        if st.button("Log", key=f"log_{add_key}", use_container_width=True):
            if desc.strip():
                img_url = ""
                if img:
                    with st.spinner("Uploading photo…"):
                        img_url = upload_to_cloudinary(img.read(), img.name)
                fs_add("snacks", {
                    "day": day, "person": person,
                    "desc": desc.strip(), "image_url": img_url,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
                st.session_state[add_key] = False
                st.rerun()
            else:
                st.warning("Please describe what you had.")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not check_password():
        return

    st.markdown("## 🥗 Meal Tracker")

    all_stats = load_all_stats()
    total = done = skipped = 0
    for day in DAYS:
        for p in ["p1", "p2"]:
            for i in range(len(MEALS[day][p])):
                total += 1
                s = all_stats.get(f"{day}_{p}_{i}", {}).get("status", "pending")
                if s == "done":      done += 1
                elif s == "skipped": skipped += 1

    pct = round((done + skipped) / total * 100) if total else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Done", done)
    c2.metric("Skipped", skipped)
    c3.metric("Week", f"{pct}%")
    st.markdown(f"""<div class="progress-bar-container">
        <div class="progress-bar-fill" style="width:{pct}%"></div></div>""",
                unsafe_allow_html=True)

    today_idx   = datetime.now().weekday()
    today_label = DAYS[today_idx] if today_idx < 7 else "Mon"
    default_idx = DAYS.index(today_label) if today_label in DAYS else 0

    selected_day = st.radio(
        "Day", DAYS, index=default_idx,
        horizontal=True, label_visibility="collapsed"
    )

    d_done = sum(
        1 for p in ["p1", "p2"]
        for i in range(len(MEALS[selected_day][p]))
        if all_stats.get(f"{selected_day}_{p}_{i}", {}).get("status", "pending") in ("done", "skipped")
    )
    d_total = sum(len(MEALS[selected_day][p]) for p in ["p1", "p2"])
    st.caption(f"{selected_day} — {d_done}/{d_total} meals tracked")

    st.divider()

    tab1, tab2 = st.tabs(["👤 Person 1 · Veg", "🏃 Person 2 · Runner"])

    with tab1:
        st.markdown('<div class="p1-header">Person 1 · Vegetarian</div>', unsafe_allow_html=True)
        for i, meal in enumerate(MEALS[selected_day]["p1"]):
            render_meal_card(selected_day, "p1", i, meal)
        render_snacks(selected_day, "p1")

    with tab2:
        st.markdown('<div class="p2-header">Person 2 · Non-veg · Runner</div>', unsafe_allow_html=True)
        for i, meal in enumerate(MEALS[selected_day]["p2"]):
            render_meal_card(selected_day, "p2", i, meal)
        render_snacks(selected_day, "p2")

    st.divider()

    with st.expander("Week overview"):
        for day in DAYS:
            dd = sum(
                1 for p in ["p1", "p2"]
                for i in range(len(MEALS[day][p]))
                if all_stats.get(f"{day}_{p}_{i}", {}).get("status", "pending") in ("done", "skipped")
            )
            dt = sum(len(MEALS[day][p]) for p in ["p1", "p2"])
            dp = round(dd / dt * 100) if dt else 0
            marker = " ← today" if day == today_label else ""
            st.markdown(f"**{day}{marker}** — {dd}/{dt} ({dp}%)")
            st.progress(dp / 100)

    with st.expander("Sign out"):
        if st.button("Sign out", type="secondary"):
            st.session_state["authenticated"] = False
            st.rerun()


if __name__ == "__main__":
    main()
