from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from .. import database, schemas, models, auth

router = APIRouter(prefix="/api/requests", tags=["requests"])

@router.post("", response_model=schemas.RequestResponse)
def create_request(
    data: schemas.RequestCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can create requests")

    new_req = models.TriageRequest(
        patient_id=current_user.id,
        symptom=data.symptom,
        specialty=data.specialty,
        answers_json=data.answers,
        status="pending"
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return {
        **new_req.__dict__,
        "patient_name": current_user.name,
        "answers": new_req.answers_json
    }

@router.post("/{req_id}/accept")
def accept_request(
    req_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Accept a request (mark as VIEWED/ACCEPTED state).
    Note: This endpoint is for viewing the request.
    Actual booking happens in /api/appointments/book
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can accept requests")

    req = db.query(models.TriageRequest).filter(models.TriageRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.status not in ["new", "viewed"]:
        raise HTTPException(status_code=409, detail="Request already handled")

    # Mark as viewed/accepted (doctor is viewing it)
    req.status = "viewed"
    req.doctor_id = current_user.id
    db.commit()

    return {
        "message": "Request viewed by doctor",
        "request_id": req.id,
        "status": req.status
    }

@router.post("/{req_id}/reject")
def reject_request(
    req_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can reject requests")

    req = db.query(models.TriageRequest).filter(models.TriageRequest.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.status = "rejected"
    db.commit()
    return {"message": "Request rejected"}
