import json, random

specialties = [
    "Cardiology", "Dermatology", "Orthopedics", "Gynecology",
    "Neurology", "ENT", "Psychiatry", "Urology",
]

# Balanced counts
TOTAL = 500
PER_SPEC = TOTAL // len(specialties)

# Random Indian cities + coordinates (approx)
cities = [
    ("Bengaluru", 12.9716, 77.5946),
    ("Mumbai", 19.0760, 72.8777),
    ("Delhi", 28.7041, 77.1025),
    ("Kolkata", 22.5726, 88.3639),
    ("Chennai", 13.0827, 80.2707),
    ("Hyderabad", 17.3850, 78.4867),
    ("Pune", 18.5204, 73.8567),
    ("Ahmedabad", 23.0225, 72.5714),
    ("Jaipur", 26.9124, 75.7873),
    ("Lucknow", 26.8467, 80.9462)
]

first_names = ["Arjun","Meera","Kavita","Rohan","Sneha","Manish","Vikram","Ritu",
               "Farheen","Priya","Aditi","Nidhi","Jay","Anirban","Sayan","Latha",
               "Hina","Rupal","Anil","Rajesh","Rita","Nirmala","Sunita"]

last_names = ["Mehta","Sharma","Rao","Patel","Sengupta","Ghosh","Banerjee","Reddy",
              "Chakraborty","Verma","Singh","Kulkarni","Das","Shah","Krishnan","Khan"]

def random_phone():
    return "+91-" + str(random.randint(6000000000, 9999999999))

def jitter(coord):
    return coord + random.uniform(-0.02, 0.02)

doctors = []

for spec in specialties:
    for _ in range(PER_SPEC):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        name = f"Dr. {fname} {lname}"

        city, lat, lng = random.choice(cities)
        doc = {
            "name": name,
            "specialty": spec,
            "clinic": f"{lname} Health Clinic",
            "address": f"{random.randint(10,200)} {city} Main Road",
            "city": city,
            "state": "India",
            "pincode": random.randint(100000, 999999),
            "phone": random_phone(),
            "lat": jitter(lat),
            "lng": jitter(lng)
        }
        doctors.append(doc)

# ---------- EXPORT JSON ----------
with open("doctors.json", "w") as f:
    json.dump(doctors, f, indent=2)

# ---------- EXPORT ML READY JSON ----------
ml = [{
    "name": d["name"],
    "specialty": d["specialty"],
    "lat": d["lat"],
    "lng": d["lng"],
    "city": d["city"]
} for d in doctors]

with open("doctors_ml_dataset.json", "w") as f:
    json.dump(ml, f, indent=2)

# ---------- EXPORT SQL ----------
with open("doctors.sql", "w") as f:
    for d in doctors:
        f.write(
            f"INSERT INTO doctors "
            f"(name, specialty, clinic, address, city, state, pincode, phone, lat, lng) "
            f"VALUES ('{d['name']}', '{d['specialty']}', '{d['clinic']}', "
            f"'{d['address']}', '{d['city']}', '{d['state']}', "
            f"{d['pincode']}, '{d['phone']}', {d['lat']}, {d['lng']});\n"
        )

print("Generated: doctors.json, doctors.sql, doctors_ml_dataset.json")
