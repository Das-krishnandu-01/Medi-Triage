from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, schemas, models, auth

router = APIRouter(prefix="/api/patients", tags=["patients"])

@router.post("/signup", response_model=schemas.Token)
def patient_signup(data: schemas.PatientSignup, db: Session = Depends(database.get_db)):
    # Validate uniqueness
    if not data.username:
        data.username = data.name.lower().replace(" ", "") + str(int(auth.datetime.utcnow().timestamp()))
    
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = models.User(
        username=data.username,
        password_hash=auth.get_password_hash(data.password),
        name=data.name,
        role="patient",
        email=data.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": new_user.username, "role": "patient"})
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}

@router.post("/signup/gmail", response_model=schemas.Token)
def patient_gmail_signup(data: schemas.GmailSignup, db: Session = Depends(database.get_db)):
    if "@gmail.com" not in data.email:
        raise HTTPException(status_code=400, detail="Only Gmail addresses allowed")

    # Generate username from email
    base_username = data.email.split("@")[0]
    username = base_username
    
    # Simple conflict resolution
    if db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}_{int(auth.datetime.utcnow().timestamp())}"

    new_user = models.User(
        username=username,
        password_hash=None, # No password
        name=data.name,
        role="patient",
        email=data.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = auth.create_access_token(data={"sub": new_user.username, "role": "patient"})
    return {"access_token": access_token, "token_type": "bearer", "user": new_user}
