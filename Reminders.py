"""
reminders.py — Meal-time WhatsApp nudges for P1 and P2.
Run by GitHub Actions on a schedule (every 30 min, checks if any slot matches current IST time).
Reads reminder preferences from Firestore: reminders/{person} doc.
"""

import os, sys, json, requests, time, jwt
from datetime import datetime, timezone, timedelta

IST  = timezone(timedelta(hours=5, minutes=30))
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── Credentials from GitHub Secrets ─────────────────────────────────────────
FIREBASE_CREDS  = json.loads(os.environ["FIREBASE_CREDENTIALS"])
TWILIO_SID      = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN    = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM     = os.environ["TWILIO_WHATSAPP_FROM"]   # e.g. whatsapp:+14155238886
P1_PHONE        = os.environ["P1_WHATSAPP"]            # e.g. whatsapp:+919876543210
P2_PHONE        = os.environ["P2_WHATSAPP"]


# ── Firebase token ───────────────────────────────────────────────────────────
def get_token():
    c      = FIREBASE_CREDS
    pk     = c["private_key"].replace("\\n", "\n")
    signed = jwt.encode(
        {"iss": c["client_email"], "sub": c["client_email"],
         "aud": "https://oauth2.googleapis.com/token",
         "iat": int(time.time()), "exp": int(time.time()) + 3600,
         "scope": "https://www.googleapis.com/auth/datastore"},
        pk, algorithm="RS256",
    )
    r = requests.post("https://oauth2.googleapis.com/token",
                      data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                            "assertion": signed}, timeout=10)
    return r.json()["access_token"]

def fs_get(col, did, token):
    pid = FIREBASE_CREDS["project_id"]
    r   = requests.get(
        f"https://firestore.googleapis.com/v1/projects/{pid}/databases/(default)/documents/{col}/{did}",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    if r.status_code == 404: return None
    def _fr(v):
        if "stringValue" in v:  return v["stringValue"]
        if "booleanValue" in v: return v["booleanValue"]
        if "integerValue" in v: return int(v["integerValue"])
        if "mapValue" in v:     return {k: _fr(u) for k,u in v["mapValue"].get("fields",{}).items()}
        if "arrayValue" in v:   return [_fr(i) for i in v["arrayValue"].get("values",[])]
        return None
    return {k: _fr(v) for k,v in r.json().get("fields",{}).items()}


# ── Load meal plan for a day/person ──────────────────────────────────────────
DEFAULT_MEALS = json.loads(open("default_meals.json").read())

def get_plan(day, person, token):
    doc = fs_get("meal_plans", f"{day}_{person}", token)
    if doc and doc.get("meals"):
        return doc["meals"]
    return DEFAULT_MEALS[day][person]


# ── Send WhatsApp message via Twilio ─────────────────────────────────────────
def send_whatsapp(to: str, body: str):
    r = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
        auth=(TWILIO_SID, TWILIO_TOKEN),
        data={"From": TWILIO_FROM, "To": to, "Body": body},
        timeout=15,
    )
    if r.status_code in (200, 201):
        print(f"✓ Sent to {to}")
    else:
        print(f"✗ Failed to {to}: {r.text}", file=sys.stderr)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    now      = datetime.now(IST)
    day_name = DAYS[now.weekday()]
    # Format: "HH:MM" window — match within ±14 min of current time
    now_mins = now.hour * 60 + now.minute
    token    = get_token()

    for person, phone in [("p1", P1_PHONE), ("p2", P2_PHONE)]:
        # Load reminder preferences: reminders/{person} → {slots: [{"slot":"Breakfast · 8:30 AM","enabled":true}]}
        prefs = fs_get("reminders", person, token) or {}
        enabled_slots = {s["slot"] for s in prefs.get("slots", []) if s.get("enabled")}
        if not enabled_slots:
            continue

        meals = get_plan(day_name, person, token)
        for meal in meals:
            slot = meal.get("slot", "")
            if slot not in enabled_slots:
                continue
            # Parse time from slot label, e.g. "Breakfast · 8:30 AM" → 8:30
            import re
            m = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', slot, re.IGNORECASE)
            if not m:
                continue
            h, mn, ampm = int(m.group(1)), int(m.group(2)), m.group(3).upper()
            if ampm == "PM" and h != 12: h += 12
            if ampm == "AM" and h == 12: h = 0
            slot_mins = h * 60 + mn
            if abs(now_mins - slot_mins) <= 14:   # within 14 min window
                name = "Person 1" if person == "p1" else "Person 2"
                msg  = (f"🌿 *NutriTrack Reminder* — {name}\n\n"
                        f"⏰ *{slot}*\n{meal['desc']}")
                send_whatsapp(phone, msg)
                break


if __name__ == "__main__":
    main()
