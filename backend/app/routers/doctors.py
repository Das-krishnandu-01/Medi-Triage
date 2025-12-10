from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import database, schemas, models, auth

router = APIRouter(prefix="/api/doctors", tags=["doctors"])

@router.post("/signup", response_model=schemas.Token)
def doctor_signup(data: schemas.DoctorSignup, db: Session = Depends(database.get_db)):
    if not data.username:
        data.username = data.name.lower().replace(" ", "")
    
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username taken")

    new_user = models.User(
        username=data.username,
        password_hash=auth.get_password_hash(data.password),
        name=data.name,
        role="doctor",
        specialty=data.specialty,
        location=data.location,
        email=data.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": new_user.username, "role": "doctor"})
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

@router.post("/signup/gmail", response_model=schemas.Token)
def doctor_gmail_signup(data: schemas.GmailSignup, db: Session = Depends(database.get_db)):
    # Logic similar to patient gmail signup but role=doctor
    base_username = data.email.split("@")[0]
    new_user = models.User(
        username=base_username,
        name=data.name,
        email=data.email,
        role="doctor",
        specialty="", # Default empty
        location=""
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.username, "role": "doctor"})
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

@router.get("/me/requests", response_model=List[schemas.RequestResponse])
def get_my_requests(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Filter: Status pending AND Specialty matches (contains)
    # Using ILIKE for case-insensitive partial match
    search_pattern = f"%{current_user.specialty}%"
    
    reqs = db.query(models.TriageRequest).filter(
        models.TriageRequest.status == "pending",
        models.TriageRequest.specialty.ilike(search_pattern)
    ).all()

    # Map to response (need to fetch patient name)
    results = []
    for r in reqs:
        results.append({
            "id": r.id,
            "symptom": r.symptom,
            "specialty": r.specialty,
            "status": r.status,
            "created_at": r.created_at,
            "answers": r.answers_json,
            "patient_name": r.patient.name if r.patient else "Unknown"
        })
    return results
