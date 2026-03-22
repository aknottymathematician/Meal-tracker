"""
daily_brief.py — 6:30 PM IST: tomorrow's plan + ingredient list for P1 and P2.
Run by GitHub Actions every day at 13:00 UTC (= 18:30 IST).
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
    r = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json",
        auth=(TWILIO_SID, TWILIO_TOKEN),
        data={"From": TWILIO_FROM, "To": to, "Body": body}, timeout=15)
    status = "✓" if r.status_code in (200, 201) else "✗"
    print(f"{status} Sent to {to}" if status == "✓" else f"✗ {r.text}", file=sys.stderr if status == "✗" else sys.stdout)

# Extract ingredient keywords from meal description
def extract_ingredients(desc):
    desc = desc.lower()
    # Strip quantities like "100g", "200ml", "½ scoop" etc.
    desc = re.sub(r'\d+[\.\d]*\s*(g|ml|gm|mg|kg|l|cup|scoop|tbsp|tsp|pinch|sachet|piece)s?\b', '', desc)
    desc = re.sub(r'[½¼¾]\s*', '', desc)
    # Split on + / , / | / OR / and
    parts = re.split(r'[+/,|]|\bor\b|\band\b|\bduring\b|\bthroughout\b', desc, flags=re.IGNORECASE)
    ingredients = []
    skip = {'water','plain','during','training','run','throughout','morning','of','in','with',
            'no','sugar','sip','add','to','make','from','at','for','per','day','min','km',
            'energy','gel','caffeine','supply','salts','sachet','optional','if','needed'}
    for p in parts:
        p = p.strip(' .-()[]')
        words = [w.strip('()[].,') for w in p.split() if len(w) > 2 and w not in skip]
        if words:
            ingredients.append(' '.join(words[:4]))
    return [i for i in ingredients if i and len(i) > 2]

def main():
    now       = datetime.now(IST)
    tomorrow  = now.date() + timedelta(days=1)
    day_name  = DAYS[tomorrow.weekday()]
    day_label = tomorrow.strftime("%A, %d %b")
    token     = get_token()

    for person, phone, name in [("p1", P1_PHONE, "Person 1"), ("p2", P2_PHONE, "Person 2")]:
        meals = get_plan(day_name, person, token)
        plan_lines = []
        all_ingredients = []
        for meal in meals:
            slot = meal.get("slot","")
            desc = meal.get("desc","")
            if "enjoyment" in desc.lower():
                plan_lines.append(f"  🎉 *{slot}* — Enjoyment meal")
            else:
                plan_lines.append(f"  • *{slot}*\n    {desc}")
            all_ingredients.extend(extract_ingredients(desc))

        # Deduplicate ingredients
        seen, unique = set(), []
        for ing in all_ingredients:
            key = ing[:10].lower()
            if key not in seen:
                seen.add(key)
                unique.append(ing)

        plan_text = "\n".join(plan_lines)
        ing_text  = "\n".join(f"  🛒 {i.title()}" for i in unique[:20]) if unique else "  (check plan)"

        msg = (f"🌿 *NutriTrack — Tomorrow's Plan*\n"
               f"📅 {day_label} | {name}\n\n"
               f"*Meals:*\n{plan_text}\n\n"
               f"*Prep / Ingredients needed:*\n{ing_text}")
        send_whatsapp(phone, msg)

if __name__ == "__main__":
    main()
