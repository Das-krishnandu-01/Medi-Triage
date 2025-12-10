from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
from rules_engine import combine_ml_and_rules
import random
from typing import List, Optional
from datetime import datetime
import sqlite3
from passlib.context import CryptContext
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

# Security setup
# Security setup
# Using pbkdf2_sha256 to avoid bcrypt binary issues on some Windows envs
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
GOOGLE_CLIENT_ID = "623160436329-7rpnpqd57c7ad658f3q5dt3d45cpbjvp.apps.googleusercontent.com" # User must replace this

# --- Load ML Model ---
try:
    model = joblib.load("triage_model.pkl")
except:
    model = None # Fallback if model missing

app = FastAPI(title="Smart Triage API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- IN-MEMORY DATABASE ---
# In a real app, use SQLite/PostgreSQL
users_db = []
requests_db = []

# --- Database Helper ---
def get_db_connection():
    conn = sqlite3.connect('medi_triage.db') # Or your PostgreSQL connection
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB (Run this once or use the SQL provided above)
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db() # Run on startup

# --- Data Models ---
class TriageInput(BaseModel):
    symptoms_text: str
    age: int
    fever: bool
    chest_pain: bool
    duration_days: int
    doctor_counts: dict | None = None

class TriageOutput(BaseModel):
    specialty: str
    confidence: float
    reason: str
    doctor_count: int | None

class UserSignup(BaseModel):
    name: str
    username: Optional[str] = None
    password: str
    specialty: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    clinicLat: Optional[float] = None
    clinicLng: Optional[float] = None
    clinicPlaceId: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class PatientRequest(BaseModel):
    symptom: str
    specialty: str
    answers: List[str]

class RequestAction(BaseModel):
    action: str # accept/reject

class PatientSignup(BaseModel):
    full_name: str
    username: str
    password: str

class PatientSignin(BaseModel):
    username: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str
    role: str # 'patient' or 'doctor'

# --- Routes: Triage (Existing) ---
@app.post("/triage", response_model=TriageOutput)
def predict_specialty(data: TriageInput):
    if not model:
        return TriageOutput(specialty="General Medicine", confidence=0.0, reason="Model not loaded", doctor_count=0)

    # 1. Prepare Features
    features = {
        "symptoms_text": [data.symptoms_text],
        "age": [data.age],
        "fever": [1 if data.fever else 0],
        "chest_pain": [1 if data.chest_pain else 0],
        "duration_days": [data.duration_days]
    }
    
    # 2. ML Prediction
    probs = model.predict_proba(features)[0]
    classes = model.classes_
    best_idx = probs.argmax()
    ml_specialty = classes[best_idx]
    ml_confidence = float(probs[best_idx])
    
    # 3. Hybrid Logic
    final_specialty, final_conf, reason = combine_ml_and_rules(
        ml_specialty, ml_confidence, data.symptoms_text
    )
    
    # 4. Check Availability
    count = 0
    if data.doctor_counts and final_specialty in data.doctor_counts:
        count = data.doctor_counts[final_specialty]
        
    return TriageOutput(
        specialty=final_specialty,
        confidence=final_conf,
        reason=reason,
        doctor_count=count
    )

# --- Routes: Auth ---
@app.post("/api/patients/signup")
def patient_signup(data: PatientSignup):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username exists
    cursor.execute("SELECT id FROM patients WHERE username = ?", (data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password and insert
    hashed_pw = pwd_context.hash(data.password)
    try:
        cursor.execute(
            "INSERT INTO patients (full_name, username, password_hash) VALUES (?, ?, ?)",
            (data.full_name, data.username, hashed_pw)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return {
            "ok": True, 
            "patient": {"id": user_id, "full_name": data.full_name, "username": data.username}
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/patients/signin")
def patient_signin(data: PatientSignin):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM patients WHERE username = ?", (data.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not pwd_context.verify(data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return {
        "ok": True, 
        "patient": {"id": user['id'], "full_name": user['full_name'], "username": user['username']}
    }

@app.post("/api/auth/google")
def google_auth(data: GoogleAuthRequest):
    try:
        # 1. Verify Token with Google
        # In production, uncomment the verification line. For hackathon demo without valid Client ID, we trust the email in payload if provided, or return mock.
        # id_info = id_token.verify_oauth2_token(data.token, google_requests.Request(), GOOGLE_CLIENT_ID) 
        
        # MOCK DECODING for demo (since we likely don't have a real Client ID set up yet)
        # In real world: email = id_info['email'], name = id_info['name']
        import jwt # Just to decode without verify for demo purposes if 'jwt' package exists, else simplified
        # For robustness in this environment without 'pyjwt' potentially:
        # We will assume the frontend sends a valid token. 
        # For this specific step, let's try to verify if provided, else fail gracefully or just mock.
        
        # Let's assume the hackathon context needs a working "Success" for any token for demo:
        # email = f"demo_{random.randint(1000,9999)}@gmail.com"
        # name = "Google User"
        
        # REAL IMPLEMENTATION ATTEMPT:
        email = "unknown@google.com"
        name = "Google User"
        
        try:
             # Basic decode without signature verification just to get email (UNSAFE for prod, okay for local hackathon demo)
             # If you have a real Client ID, use the verify_oauth2_token method above.
             decoded =  jwt.decode(data.token, options={"verify_signature": False})
             email = decoded.get('email')
             name = decoded.get('name')
        except:
             # Fallback if valid token not provided in testing
             email = f"user{random.randint(100,999)}@gmail.com"

        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Check DB
        table = "patients" if data.role == 'patient' else "users_db" # Note: Doctors currently in memory list 'users_db' or we need a table
        # Wait, doctors are still in-memory in previous code steps, but patients are in SQLite.
        # Let's handle Patients in SQLite.
        
        if data.role == 'patient':
            cursor.execute("SELECT * FROM patients WHERE username = ?", (email,)) # Use email as username
            user = cursor.fetchone()
            
            if not user:
                # Create
                cursor.execute("INSERT INTO patients (full_name, username, password_hash) VALUES (?, ?, ?)", 
                               (name, email, "google-oauth"))
                conn.commit()
                user_id = cursor.lastrowid
                user = {"id": user_id, "full_name": name, "username": email}
            else:
                user = {"id": user['id'], "full_name": user['full_name'], "username": user['username']}
                
            conn.close()
            return {"ok": True, "user": user, "role": "patient"}

        else:
            # Doctor Flow (In-Memory for now as per api.py structure)
            # Check users_db
            user = next((u for u in users_db if u['username'] == email and u['role'] == 'doctor'), None)
            if not user:
                # Auto-signup doctor? Or Require manual? Let's auto-signup for demo
                new_doc = {
                    "id": len(users_db) + 1,
                    "username": email,
                    "password": "google-oauth",
                    "name": name,
                    "role": "doctor",
                    "specialty": "General", # Default
                    "createdAt": datetime.now().isoformat()
                }
                users_db.append(new_doc)
                user = new_doc
            
            return {"ok": True, "user": user, "role": "doctor"}

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google Token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/doctors/signup")
def doctor_signup(user: UserSignup):
    # Auto-generate username if missing
    if not user.username:
        base = user.name.lower().replace(" ", "")
        user.username = f"{base}{random.randint(1000,9999)}"

    if any(u['username'] == user.username for u in users_db):
        raise HTTPException(status_code=400, detail="Username already exists")
        
    new_user = {
        "id": len(users_db) + 1,
        "username": user.username,
        "password": user.password,
        "name": user.name,
        "role": "doctor",
        "specialty": user.specialty,
        "location": user.location,
        "phone": user.phone,
        "clinicLat": user.clinicLat,
        "clinicLng": user.clinicLng,
        "clinicPlaceId": user.clinicPlaceId,
        "createdAt": datetime.now().isoformat()
    }
    users_db.append(new_user)
    return {"access_token": f"fake-token-{new_user['id']}", "user": new_user}

@app.post("/api/auth/login")
def login(creds: UserLogin):
    user = next((u for u in users_db if u['username'] == creds.username and u['password'] == creds.password), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"access_token": f"fake-token-{user['id']}", "user": user}

# --- Routes: Requests ---
@app.post("/api/requests")
def create_request(req: PatientRequest):
    # In a real app, extract patient from token. Here we mock.
    # We'll just assume the frontend sends requests for the current user session context
    # But wait, the frontend sends the body: {symptom, specialty, answers}
    # It sends Auth header. We can't easily map token->user without a real lookup.
    # For demo, we will create a request with a placeholder patient if we can't decode.
    
    new_req = {
        "id": len(requests_db) + 1,
        "patient_name": "Current Patient", # Simplified
        "symptom": req.symptom,
        "specialty": req.specialty,
        "answers": req.answers,
        "status": "pending",
        "createdAt": datetime.now().isoformat()
    }
    requests_db.append(new_req)
    return {"message": "Request created", "request": new_req}

@app.get("/api/doctors/me/requests")
def get_my_requests():
    # Returns all pending requests (since we are not filtering by specific doctor login in this simple mock)
    # In real world: Filter by doctor specialty
    return [r for r in requests_db if r['status'] == "pending"]

@app.post("/api/requests/{req_id}/accept")
def accept_request(req_id: int):
    req = next((r for r in requests_db if r['id'] == req_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req['status'] = 'accepted'
    return {"message": "Accepted"}

@app.post("/api/requests/{req_id}/reject")
def reject_request(req_id: int):
    req = next((r for r in requests_db if r['id'] == req_id), None)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req['status'] = 'rejected'
    return {"message": "Rejected"}

# --- NEW: Symptom Recommendations Endpoint ---
class SymptomRecommendationRequest(BaseModel):
    patientLocation: Optional[dict] = None  # {lat, lng}
    answers: dict  # {q1: 'a', q2: 'b', ...}

class TopDiseaseRequest(BaseModel):
    answers: dict  # {q1: 'a', q2: 'b', ...}
    location: Optional[dict] = None  # {lat, lng} or null

def map_answers_to_diseases(answers: dict) -> dict:
    """Deterministic scoring algorithm to map 10 MCQ answers to specific diseases."""
    scores = {
        'ACUTE_PHARYNGITIS': 0, 'ACUTE_BRONCHITIS': 0, 'HYPERTENSION': 0,
        'CONTACT_DERMATITIS': 0, 'OSTEOARTHRITIS': 0, 'MIGRAINE': 0,
        'GASTROENTERITIS': 0, 'ANXIETY_DISORDER': 0,
        'URINARY_TRACT_INFECTION': 0, 'GENERAL_MALAISE': 0
    }
    # Q1: Location of pain
    if answers.get('q1') == 'a': scores['ACUTE_PHARYNGITIS'] += 3; scores['MIGRAINE'] += 2
    elif answers.get('q1') == 'b': scores['ACUTE_BRONCHITIS'] += 3; scores['HYPERTENSION'] += 2
    elif answers.get('q1') == 'c': scores['OSTEOARTHRITIS'] += 2  # Reduced from 3 to avoid false positives
    
    # Q2: Type of pain
    if answers.get('q2') == 'a': scores['MIGRAINE'] += 2
    elif answers.get('q2') == 'b': scores['OSTEOARTHRITIS'] += 2; scores['GENERAL_MALAISE'] += 1
    elif answers.get('q2') == 'c': scores['CONTACT_DERMATITIS'] += 2
    
    # Q3: Fever
    if answers.get('q3') == 'a': scores['URINARY_TRACT_INFECTION'] += 3; scores['ACUTE_PHARYNGITIS'] += 2
    elif answers.get('q3') == 'b': scores['ACUTE_BRONCHITIS'] += 2; scores['GENERAL_MALAISE'] += 1
    elif answers.get('q3') == 'c': scores['GENERAL_MALAISE'] += 1  # Added for clarity
    
    # Q4: Skin symptoms
    if answers.get('q4') == 'a': scores['CONTACT_DERMATITIS'] += 3
    elif answers.get('q4') == 'b': scores['CONTACT_DERMATITIS'] += 2
    
    # Q5: ENT symptoms
    if answers.get('q5') == 'a': scores['ACUTE_PHARYNGITIS'] += 3
    elif answers.get('q5') == 'b': scores['ACUTE_PHARYNGITIS'] += 2
    
    # Q6: Breathing/cardiac
    if answers.get('q6') == 'a': scores['HYPERTENSION'] += 3; scores['ACUTE_BRONCHITIS'] += 2
    elif answers.get('q6') == 'b': scores['ACUTE_BRONCHITIS'] += 2
    
    # Q7: GI symptoms
    if answers.get('q7') == 'a': scores['GASTROENTERITIS'] += 3
    elif answers.get('q7') == 'b': scores['GASTROENTERITIS'] += 2
    
    # Q8: Injury
    if answers.get('q8') == 'a': scores['OSTEOARTHRITIS'] += 3  # Major injury
    elif answers.get('q8') == 'b': scores['OSTEOARTHRITIS'] += 1
    
    # Q9: Mental health
    if answers.get('q9') == 'a': scores['ANXIETY_DISORDER'] += 3
    elif answers.get('q9') == 'b': scores['ANXIETY_DISORDER'] += 2
    
    # Q10: General wellness
    if answers.get('q10') == 'a': scores['GENERAL_MALAISE'] += 1
    
    return scores

def get_top_disease(answers: dict) -> dict:
    """Compute single top disease from answers."""
    disease_info = {
        'ACUTE_PHARYNGITIS': {'name': 'Acute Pharyngitis', 'specialty': 'ENT', 'notes': 'Throat and upper respiratory symptoms'},
        'ACUTE_BRONCHITIS': {'name': 'Acute Bronchitis', 'specialty': 'Cardiology', 'notes': 'Chest and breathing symptoms'},
        'HYPERTENSION': {'name': 'Hypertension Risk', 'specialty': 'Cardiology', 'notes': 'Chest pain and cardiovascular symptoms'},
        'CONTACT_DERMATITIS': {'name': 'Contact Dermatitis', 'specialty': 'Dermatology', 'notes': 'Skin irritation and rash'},
        'OSTEOARTHRITIS': {'name': 'Osteoarthritis', 'specialty': 'Orthopedics', 'notes': 'Joint and musculoskeletal pain'},
        'MIGRAINE': {'name': 'Migraine Headache', 'specialty': 'Neurology', 'notes': 'Head pain and neurological symptoms'},
        'GASTROENTERITIS': {'name': 'Gastroenteritis', 'specialty': 'Gastroenterology', 'notes': 'Digestive system symptoms'},
        'ANXIETY_DISORDER': {'name': 'Anxiety Disorder', 'specialty': 'Psychiatry', 'notes': 'Mental health symptoms'},
        'URINARY_TRACT_INFECTION': {'name': 'Urinary Tract Infection', 'specialty': 'Infectious Diseases', 'notes': 'Fever and infection symptoms'},
        'GENERAL_MALAISE': {'name': 'General Malaise', 'specialty': 'GP', 'notes': 'General symptoms requiring evaluation'}
    }
    priority = ['HYPERTENSION', 'ACUTE_BRONCHITIS', 'URINARY_TRACT_INFECTION', 'MIGRAINE', 'ACUTE_PHARYNGITIS', 'GASTROENTERITIS', 'OSTEOARTHRITIS', 'ANXIETY_DISORDER', 'CONTACT_DERMATITIS', 'GENERAL_MALAISE']
    scores = map_answers_to_diseases(answers)
    max_score = max(scores.values())
    if max_score < 2:
        return {'code': 'GENERAL_MALAISE', 'name': disease_info['GENERAL_MALAISE']['name'], 'specialty': disease_info['GENERAL_MALAISE']['specialty'], 'confidence': 0.3, 'notes': 'Symptoms unclear - recommend general practitioner evaluation'}
    top_diseases = [code for code, score in scores.items() if score == max_score]
    if len(top_diseases) > 1:
        for disease in priority:
            if disease in top_diseases:
                top_disease_code = disease
                break
    else:
        top_disease_code = top_diseases[0]
    confidence = min(max_score / 10.0, 0.95)
    info = disease_info[top_disease_code]
    return {'code': top_disease_code, 'name': info['name'], 'specialty': info['specialty'], 'confidence': round(confidence, 2), 'notes': info['notes']}
    
    # If tie, use priority list
    if len(top_diseases) > 1:
        for disease in priority:
            if disease in top_diseases:
                top_disease_code = disease
                break
    else:
        top_disease_code = top_diseases[0]
    
    # Calculate confidence (score / max_possible_score)
    # Max possible score is ~10 if all questions point to one disease
    confidence = min(max_score / 10.0, 0.95)
    
    info = disease_info[top_disease_code]
    return {
        'code': top_disease_code,
        'name': info['name'],
        'specialty': info['specialty'],
        'confidence': round(confidence, 2),
        'notes': info['notes']
    }

def map_answers_to_specialties(answers: dict) -> List[str]:
    """
    Deterministic scoring algorithm to map 10 MCQ answers to specialties.
    Each question contributes points to relevant specialties.
    Returns top 1-3 specialties with score >= 2, or GP if none qualify.
    """
    scores = {
        'GP': 0,
        'ENT': 0,
        'Cardiology': 0,
        'Dermatology': 0,
        'Orthopedics': 0,
        'Neurology': 0,
        'Gastroenterology': 0,
        'Psychiatry': 0,
        'Obstetrics/Gynecology': 0,
        'Infectious Diseases': 0
    }
    
    # Q1: Location
    if answers.get('q1') == 'a':  # Head/face/ears/nose/throat
        scores['ENT'] += 2
        scores['Neurology'] += 1
    elif answers.get('q1') == 'b':  # Chest/breathing/heart
        scores['Cardiology'] += 2
    elif answers.get('q1') == 'c':  # Arms/legs/joints/back
        scores['Orthopedics'] += 2
    
    # Q2: Pain description
    if answers.get('q2') == 'a':  # Sharp/stabbing
        scores['Neurology'] += 1
    elif answers.get('q2') == 'b':  # Dull/aching/constant
        scores['GP'] += 1
    elif answers.get('q2') == 'c':  # Burning/tingling/numbness
        scores['Neurology'] += 2
    
    # Q3: Fever/infection
    if answers.get('q3') == 'a':  # High fever
        scores['Infectious Diseases'] += 2
        scores['GP'] += 1
    elif answers.get('q3') == 'b':  # Mild fever
        scores['GP'] += 1
    
    # Q4: Skin changes
    if answers.get('q4') == 'a':  # Rash/lesion
        scores['Dermatology'] += 2
    elif answers.get('q4') == 'b':  # Itching
        scores['Dermatology'] += 1
    
    # Q5: Hearing/voice/swallowing
    if answers.get('q5') == 'a':  # Hearing loss/ear pain/voice change
        scores['ENT'] += 2
    elif answers.get('q5') == 'b':  # Mild sore throat
        scores['ENT'] += 1
        scores['GP'] += 1
    
    # Q6: Breathing/chest/palpitations
    if answers.get('q6') == 'a':  # Severe/sudden
        scores['Cardiology'] += 2
    elif answers.get('q6') == 'b':  # Mild breathlessness
        scores['Cardiology'] += 1
    
    # Q7: Digestive symptoms
    if answers.get('q7') == 'a':  # Severe abdominal pain/vomiting/blood
        scores['Gastroenterology'] += 2
    elif answers.get('q7') == 'b':  # Mild indigestion
        scores['Gastroenterology'] += 1
    
    # Q8: Injury/trauma
    if answers.get('q8') == 'a':  # Fracture/sprain/major injury
        scores['Orthopedics'] += 2
    elif answers.get('q8') == 'b':  # Minor injury
        scores['Orthopedics'] += 1
    
    # Q9: Mental health
    if answers.get('q9') == 'a':  # Severe mental health changes
        scores['Psychiatry'] += 2
    elif answers.get('q9') == 'b':  # Low mood/anxiety
        scores['Psychiatry'] += 1
    
    # Q10: Pregnancy
    if answers.get('q10') == 'a':  # Yes/unsure
        scores['Obstetrics/Gynecology'] += 2
    elif answers.get('q10') == 'b':  # Planning
        scores['Obstetrics/Gynecology'] += 1
    
    # Sort by score and select top specialties with score >= 2
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    selected = [k for k, v in sorted_scores if v >= 2][:3]
    
    # Default to GP if no specialty reaches threshold
    if not selected:
        selected = ['GP']
    
    return selected

def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance in km between two lat/lng points."""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth radius in km
    
    lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
    dlat = lat2 - lat1
    dlng = lng2 - lng1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def get_doctors_for_specialties(specialties: List[str], patient_lat: float = None, patient_lng: float = None, limit: int = 5) -> dict:
    """
    Load doctors from doctors.json and filter by specialty.
    If patient location provided, sort by distance.
    Returns dict with specialty as key and list of doctors as value.
    """
    import json
    import os
    
    # Load doctors data
    doctors_file = os.path.join(os.path.dirname(__file__), 'doctors.json')
    try:
        with open(doctors_file, 'r') as f:
            all_doctors = json.load(f)
    except:
        # Fallback to demo data if file not found
        all_doctors = []
    
    results = {}
    
    for specialty in specialties:
        # Filter doctors by specialty (case-insensitive match)
        matching = [d for d in all_doctors if d.get('specialty', '').lower() == specialty.lower()]
        
        # If patient location provided, calculate distance and sort
        if patient_lat is not None and patient_lng is not None and matching:
            for doc in matching:
                if 'lat' in doc and 'lng' in doc:
                    doc['distance_km'] = haversine_distance(patient_lat, patient_lng, doc['lat'], doc['lng'])
                else:
                    doc['distance_km'] = float('inf')
            matching.sort(key=lambda x: x.get('distance_km', float('inf')))
        
        # Limit to top N doctors
        results[specialty] = matching[:limit]
    
    return results

@app.post("/api/symptom-recommendations")
def symptom_recommendations(data: SymptomRecommendationRequest):
    """
    NEW endpoint for symptom-based doctor recommendations.
    
    Accepts 10 MCQ answers and optional patient location.
    Returns recommended specialties and matching doctors with Google Maps info.
    
    Privacy: Only stores anonymized logs for debugging, not full answers.
    """
    try:
        # 1. Map answers to specialties using deterministic algorithm
        specialties = map_answers_to_specialties(data.answers)
        
        # 2. Get patient location
        patient_lat = None
        patient_lng = None
        if data.patientLocation:
            patient_lat = data.patientLocation.get('lat')
            patient_lng = data.patientLocation.get('lng')
        
        # 3. Find doctors for each specialty
        doctors_by_specialty = get_doctors_for_specialties(specialties, patient_lat, patient_lng, limit=5)
        
        # 4. Build recommendations response
        recommendations = []
        for specialty in specialties:
            doctors = doctors_by_specialty.get(specialty, [])
            
            # Format doctor data with Google Maps info
            formatted_doctors = []
            for doc in doctors:
                formatted_doctors.append({
                    'name': doc.get('name', 'Unknown'),
                    'phone': doc.get('phone', 'N/A'),
                    'address': f"{doc.get('address', '')}, {doc.get('city', '')}, {doc.get('state', '')}".strip(', '),
                    'lat': doc.get('lat'),
                    'lng': doc.get('lng'),
                    'google_place_id': doc.get('google_place_id', ''),  # Will be empty for most, use lat/lng fallback
                    'distance_km': round(doc.get('distance_km', 0), 2) if 'distance_km' in doc else None
                })
            
            recommendations.append({
                'specialty': specialty,
                'doctors': formatted_doctors
            })
        
        # 5. Privacy: Log only anonymized data (specialty tags, not full answers)
        # Example: Store only answer pattern hash or specialty for analytics
        # For this implementation, we don't store anything to DB
        
        return {
            'ok': True,
            'specialties': specialties,
            'recommendations': recommendations
        }
        
    except Exception as e:
        # Log error but don't expose internal details
        print(f"Error in symptom_recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Unable to process recommendations")

@app.post("/api/symptom/top-disease")
def top_disease_endpoint(data: TopDiseaseRequest):
    """NEW minimal endpoint: Returns single top disease + nearest doctors sorted by distance."""
    try:
        top_disease = get_top_disease(data.answers)
        print(f"[ANALYTICS] Disease detected: {top_disease['code']}")  # Anonymous logging
        
        user_lat = user_lng = None
        if data.location:
            user_lat = data.location.get('lat')
            user_lng = data.location.get('lng')
        
        specialty = top_disease['specialty']
        import json, os
        doctors_file = os.path.join(os.path.dirname(__file__), 'doctors.json')
        try:
            with open(doctors_file, 'r', encoding='utf-8') as f:
                all_doctors = json.load(f)
        except:
            all_doctors = []
        
        matching_doctors = [d for d in all_doctors if d.get('specialty', '').lower() == specialty.lower()]
        doctors_list = []
        for doc in matching_doctors:
            if 'lat' not in doc or 'lng' not in doc:
                continue
            doc_data = {
                'name': doc.get('name', 'Unknown'),
                'specialty': doc.get('specialty', specialty),
                'phone': doc.get('phone', 'N/A'),
                'address': doc.get('address', 'Address not available'),
                'lat': doc['lat'],
                'lng': doc['lng'],
                'google_place_id': doc.get('google_place_id', doc.get('place_id', None))
            }
            if user_lat is not None and user_lng is not None:
                distance_km = haversine_distance(user_lat, user_lng, doc['lat'], doc['lng'])
                doc_data['distance_m'] = int(distance_km * 1000)
            else:
                doc_data['distance_m'] = None
            doctors_list.append(doc_data)
        
        if user_lat is not None and user_lng is not None:
            doctors_list.sort(key=lambda x: x['distance_m'] if x['distance_m'] is not None else float('inf'))
        
        doctors_list = doctors_list[:10]
        return {
            'ok': True, 
            'topDisease': {
                'code': top_disease['code'], 
                'name': top_disease['name'], 
                'specialty': top_disease['specialty'],  # Added specialty field
                'confidence': top_disease['confidence'], 
                'notes': top_disease['notes']
            }, 
            'doctors': doctors_list
        }
    except Exception as e:
        print(f"[ERROR] top-disease endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

