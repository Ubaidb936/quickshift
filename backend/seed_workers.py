"""
Seed 100 fake worker profiles via the registration endpoint.
Embeddings are generated automatically on each POST.

Run inside the backend container:
  docker compose exec backend python seed_workers.py
"""

import httpx
import random
import time

BASE_URL = "http://localhost:8000"

PROFESSIONS = [
    "Bartender", "Server", "Barista", "Line Cook", "Dishwasher",
    "Host/Hostess", "Cashier", "Warehouse Associate", "Forklift Operator",
    "Event Staff", "Security Guard", "Delivery Driver", "Stocker",
    "Prep Cook", "Busser", "Catering Staff", "Banquet Server", "Barback",
]

SKILLS_MAP = {
    "Bartender":          "cocktail mixing, POS systems, customer service, inventory management",
    "Server":             "table service, POS systems, upselling, food safety",
    "Barista":            "espresso, latte art, customer service, cash handling",
    "Line Cook":          "knife skills, grill, sauté, food prep, kitchen sanitation",
    "Dishwasher":         "kitchen sanitation, speed, teamwork, equipment cleaning",
    "Host/Hostess":       "reservation management, customer service, OpenTable, phone etiquette",
    "Cashier":            "cash handling, POS systems, customer service, stock counting",
    "Warehouse Associate":"inventory management, pallet jack, order picking, shipping",
    "Forklift Operator":  "forklift certified, pallet jack, inventory tracking, safety compliance",
    "Event Staff":        "crowd management, setup/teardown, customer service, ticketing",
    "Security Guard":     "crowd control, surveillance, conflict de-escalation, CPR certified",
    "Delivery Driver":    "route planning, GPS navigation, time management, vehicle maintenance",
    "Stocker":            "inventory management, stock rotation, heavy lifting, FIFO",
    "Prep Cook":          "knife skills, food prep, portion control, kitchen sanitation",
    "Busser":             "table clearing, teamwork, speed, restaurant sanitation",
    "Catering Staff":     "food service, setup/teardown, customer service, portioning",
    "Banquet Server":     "banquet service, tray carrying, formal dining, event setup",
    "Barback":            "bar restocking, glassware cleaning, ice management, speed",
}

LOCATIONS = [
    "San Francisco, CA", "Los Angeles, CA", "New York, NY", "Chicago, IL",
    "Austin, TX", "Seattle, WA", "Miami, FL", "Denver, CO",
    "Phoenix, AZ", "Portland, OR", "Nashville, TN", "Atlanta, GA",
    "Las Vegas, NV", "San Diego, CA", "Boston, MA",
]

AVAILABILITY_OPTIONS = [
    "Weekdays", "Weekends", "Mornings", "Evenings", "Nights",
    "Weekdays,Evenings", "Weekends,Nights", "Mornings,Weekdays",
    "Flexible", "Evenings,Weekends", "Nights,Weekends",
]

BIO_TEMPLATES = [
    "Reliable and hardworking {profession} with {years} years of experience. I thrive in fast-paced environments and always show up on time.",
    "Passionate {profession} who loves delivering great experiences. {years} years in the industry and still learning every day.",
    "Detail-oriented {profession} with a strong work ethic. I take pride in my craft and work well with any team.",
    "Energetic {profession} available for shifts on short notice. I have {years} years of hands-on experience and strong references.",
    "Experienced {profession} looking for consistent shifts. Known for being dependable, fast, and easy to work with.",
    "Customer-focused {profession} with {years} years in the field. I adapt quickly to new environments and team dynamics.",
    "Team player and seasoned {profession}. I bring {years} years of experience and a positive attitude to every shift.",
    "Self-motivated {profession} with a track record of reliability. I'm comfortable in high-volume settings and stay calm under pressure.",
]

FIRST_NAMES = [
    "James", "Maria", "Carlos", "Aisha", "Liam", "Emma", "Noah", "Olivia",
    "Ethan", "Sophia", "Marcus", "Priya", "Tyler", "Jasmine", "Derek",
    "Fatima", "Ryan", "Nina", "Kevin", "Zoe", "Andre", "Mia", "Jordan",
    "Elena", "Chris", "Aaliyah", "Brandon", "Yuki", "Trevor", "Layla",
    "Miguel", "Hannah", "Darius", "Sara", "Isaiah", "Chloe", "Nathan",
    "Amara", "Austin", "Lily", "Jerome", "Nadia", "Caleb", "Rosa",
    "Malik", "Dana", "Victor", "Tanya", "Joel", "Bianca",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Martinez",
    "Davis", "Lopez", "Wilson", "Anderson", "Taylor", "Thomas", "Hernandez",
    "Moore", "Martin", "Jackson", "Thompson", "White", "Lee", "Harris",
    "Clark", "Lewis", "Robinson", "Walker", "Hall", "Allen", "Young",
    "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker",
]


def make_worker(index: int) -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    profession = random.choice(PROFESSIONS)
    years = random.randint(0, 12)
    bio_template = random.choice(BIO_TEMPLATES)

    return {
        "name": f"{first} {last}",
        "email": f"worker{index}_{first.lower()}{last.lower()}@quickshift-test.com",
        "password": "TestPass123!",
        "location": random.choice(LOCATIONS),
        "profession": profession,
        "skills": SKILLS_MAP[profession],
        "experience_years": years,
        "availability": random.choice(AVAILABILITY_OPTIONS),
        "bio": bio_template.format(profession=profession.lower(), years=years),
    }


def seed():
    created = 0
    failed = 0

    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        for i in range(1, 101):
            worker = make_worker(i)
            try:
                resp = client.post("/auth/register/worker", json=worker)
                if resp.status_code == 200:
                    created += 1
                    print(f"[{i:3d}] ✓  {worker['name']} — {worker['profession']} ({worker['location']})")
                else:
                    failed += 1
                    print(f"[{i:3d}] ✗  {worker['name']} — HTTP {resp.status_code}: {resp.text[:80]}")
            except Exception as e:
                failed += 1
                print(f"[{i:3d}] ✗  {worker['name']} — error: {e}")

            # small delay so we don't hammer the OpenAI embedding API
            time.sleep(0.2)

    print(f"\nDone — {created} created, {failed} failed")


if __name__ == "__main__":
    seed()
