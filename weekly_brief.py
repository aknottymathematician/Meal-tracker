"""
weekly_brief.py — Every Sunday 6:30 PM IST: full week ingredient list for P1 and P2.
Run by GitHub Actions on Sunday at 13:00 UTC.
"""

import os, sys, json, requests, time, jwt, re
from datetime import datetime, timezone, timedelta, date

IST  = timezone(timedelta(hours=5, minutes=30))
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

FIREBASE_CREDS = json.loads(os.environ["FIREBASE_CREDENTIALS"])
TWILIO_SID     = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_TOKEN   = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_FROM    = os.environ["TWILIO_WHATSAPP_FROM"]
P1_PHONE       = os.environ["P1_WHATSAPP"]
P2_PHONE       = os.environ["P2_WHATSAPP"]
DEFAULT_MEALS  = json.loads(open("default_meals.json").read())

def get_token():
    c = FIREBASE_CREDS
    pk = c["private_key"].replace("\\n", "\n")
    signed = jwt.encode(
        {"iss": c["client_email"], "sub": c["client_email"],
         "aud": "https://oauth2.googleapis.com/token",
         "iat": int(time.time()), "exp": int(time.time()) + 3600,
         "scope": "https://www.googleapis.com/auth/datastore"},
        pk, algorithm="RS256")
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

def get_plan(day, person, token):
    doc = fs_get("meal_plans", f"{day}_{person}", token)
    if doc and doc.get("meals"): return doc["meals"]
    return DEFAULT_MEALS[day][person]

def send_whatsapp(to, body):
    # Split into chunks ≤1600 chars (WhatsApp limit)
    chunks = [body[i:i+1550] for i in range(0, len(body), 1550)]
    for chunk in chunks:
        r = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
            auth=(TWILIO_SID, TWILIO_TOKEN),
            data={"From": TWILIO_FROM, "To": to, "Body": chunk}, timeout=15)
        if r.status_code not in (200, 201):
            print(f"✗ {r.text}", file=sys.stderr)

def extract_ingredients(desc):
    desc = desc.lower()
    desc = re.sub(r'\d+[\.\d]*\s*(g|ml|gm|mg|kg|l|cup|scoop|tbsp|tsp|pinch|sachet|piece)s?\b', '', desc)
    desc = re.sub(r'[½¼¾]\s*', '', desc)
    parts = re.split(r'[+/,|]|\bor\b|\band\b|\bduring\b|\bthroughout\b', desc, flags=re.IGNORECASE)
    skip = {'water','plain','during','training','run','throughout','morning','of','in','with',
            'no','sugar','sip','add','to','make','from','at','for','per','day','min','km',
            'energy','gel','caffeine','supply','salts','sachet','optional','if','needed',
            'black','coffee','substitute','instead'}
    ingredients = []
    for p in parts:
        p = p.strip(' .-()[]')
        words = [w.strip('()[].,') for w in p.split() if len(w) > 2 and w not in skip]
        if words:
            ingredients.append(' '.join(words[:4]))
    return [i for i in ingredients if i and len(i) > 2]

def main():
    token = get_token()
    now   = datetime.now(IST)
    # Next week Mon–Sun
    today     = now.date()
    days_to_mon = (7 - today.weekday()) % 7 or 7
    next_mon  = today + timedelta(days=days_to_mon)
    week_dates = [next_mon + timedelta(days=i) for i in range(7)]
    week_label = f"{next_mon.strftime('%d %b')} – {week_dates[-1].strftime('%d %b %Y')}"

    for person, phone, name in [("p1", P1_PHONE, "Person 1"), ("p2", P2_PHONE, "Person 2")]:
        # Collect all ingredients by day
        all_by_day = {}
        cumulative = {}
        for d in week_dates:
            day_name = DAYS[d.weekday()]
            meals    = get_plan(day_name, person, token)
            day_ings = []
            for meal in meals:
                day_ings.extend(extract_ingredients(meal.get("desc", "")))
            # Deduplicate per day
            seen, unique = set(), []
            for ing in day_ings:
                key = ing[:10].lower()
                if key not in seen:
                    seen.add(key)
                    unique.append(ing)
                    if key not in cumulative:
                        cumulative[key] = ing
            all_by_day[day_name] = unique

        # Build message
        day_sections = []
        for d in week_dates:
            day_name  = DAYS[d.weekday()]
            date_str  = d.strftime("%a %d")
            ings      = all_by_day[day_name]
            if ings:
                day_sections.append(f"*{date_str}:*\n" + "\n".join(f"  • {i.title()}" for i in ings))

        cumul_list = "\n".join(f"  🛒 {v.title()}" for v in cumulative.values())

        msg = (f"🌿 *NutriTrack — Week of {week_label}*\n"
               f"Weekly shopping list for {name}\n\n"
               f"*Cumulative ingredients:*\n{cumul_list}\n\n"
               f"──────────────────\n"
               f"*Daily breakdown:*\n\n" +
               "\n\n".join(day_sections))
        send_whatsapp(phone, msg)
        print(f"✓ Weekly brief sent to {name}")

if __name__ == "__main__":
    main()
