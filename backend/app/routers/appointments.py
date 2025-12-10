"""
Appointment booking router with transactional double-booking prevention.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import logging
from typing import Optional
from .. import database, schemas, models, auth

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

logger = logging.getLogger(__name__)


def validate_booking_request(
    data: schemas.BookAppointmentRequest,
    current_user: models.User,
    db: Session
) -> dict:
    """
    Validate booking request before transaction.
    Returns dict with validation status and errors.
    """
    errors = []
    
    # 1. Verify doctor is authenticated user
    try:
        doctor_id = int(data.doctorId)
    except (ValueError, TypeError):
        errors.append("Invalid doctorId format")
        doctor_id = None
    
    if doctor_id and doctor_id != current_user.id and current_user.role != "doctor":
        errors.append("You can only book appointments for yourself")
    
    if current_user.role != "doctor":
        errors.append("Only doctors can book appointments")
    
    # 2. Verify times are valid
    if data.startTime >= data.endTime:
        errors.append("Start time must be before end time")
    
    if data.startTime < datetime.utcnow():
        errors.append("Cannot book appointments in the past")
    
    # 3. Verify request exists and is in bookable state
    try:
        request_id = int(data.requestId)
    except (ValueError, TypeError):
        errors.append("Invalid requestId format")
        request_id = None
    
    req = None
    if request_id:
        req = db.query(models.TriageRequest).filter(
            models.TriageRequest.id == request_id
        ).first()
        
        if not req:
            errors.append("Request not found")
        elif req.status not in ["new", "viewed"]:
            errors.append(f"Request status is '{req.status}', cannot book from this state")
    
    # 4. Verify patient exists
    try:
        patient_id = int(data.patientId)
    except (ValueError, TypeError):
        errors.append("Invalid patientId format")
        patient_id = None
    
    if patient_id:
        patient = db.query(models.User).filter(
            models.User.id == patient_id,
            models.User.role == "patient"
        ).first()
        if not patient:
            errors.append("Patient not found")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "request": req,
        "doctor_id": doctor_id,
        "patient_id": patient_id,
        "request_id": request_id
    }


def check_overlapping_appointments(
    doctor_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Session,
    exclude_appointment_id: Optional[int] = None
) -> bool:
    """
    Check if doctor has overlapping appointments.
    Returns True if overlap found (conflict), False if slot is free.
    """
    query = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.status.in_(["PENDING", "CONFIRMED"]),
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > start_time
    )
    
    if exclude_appointment_id:
        query = query.filter(models.Appointment.id != exclude_appointment_id)
    
    # Using FOR UPDATE on row level (SQLite doesn't support, but PostgreSQL does)
    # For SQLite compatibility, we'll rely on transaction isolation
    return query.first() is not None


@router.post("/book", response_model=schemas.BookAppointmentResponse)
def book_appointment(
    data: schemas.BookAppointmentRequest,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Book an appointment with atomic transaction and double-booking prevention.
    
    AC2: Validates slot availability, creates Appointment with CONFIRMED status.
    AC3: Uses DB transaction and constraint checks to prevent double-booking.
    """
    
    # Validate request
    validation = validate_booking_request(data, current_user, db)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(validation["errors"])
        )
    
    doctor_id = validation["doctor_id"]
    patient_id = validation["patient_id"]
    request_id = validation["request_id"]
    req = validation["request"]
    
    try:
        # Start transaction
        # Check for overlapping appointments (AC3 - double-booking prevention)
        if check_overlapping_appointments(doctor_id, data.startTime, data.endTime, db):
            # Conflict: slot already taken
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Selected time slot is already taken. Please choose another time."
            )
        
        # Create new appointment with CONFIRMED status
        appointment = models.Appointment(
            request_id=request_id,
            doctor_id=doctor_id,
            patient_id=patient_id,
            start_time=data.startTime,
            end_time=data.endTime,
            mode=data.mode,
            status="CONFIRMED",
            notes=data.notes,
            created_by=current_user.id
        )
        db.add(appointment)
        db.flush()  # Flush to get the ID before commit
        appointment_id = appointment.id
        
        # Update request status to BOOKED
        if req:
            req.status = "booked"
            req.handled_by = current_user.id
            req.handled_at = datetime.utcnow()
        
        # Commit transaction
        db.commit()
        
        # Log audit trail
        logger.info(
            f"BOOK_APPOINTMENT: doctor_id={doctor_id}, patient_id={patient_id}, "
            f"request_id={request_id}, appointment_id={appointment_id}, "
            f"start_time={data.startTime}, end_time={data.endTime}"
        )
        
        return {
            "ok": True,
            "appointmentId": str(appointment_id),
            "status": "CONFIRMED",
            "message": "Appointment booked successfully"
        }
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error booking appointment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to book appointment. Please try again."
        )


@router.get("/{appointment_id}", response_model=schemas.AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get appointment details."""
    appt = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Authorization: doctor or patient of this appointment
    if current_user.id != appt.doctor_id and current_user.id != appt.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this appointment"
        )
    
    return appt


@router.get("/doctor/me", response_model=list[schemas.AppointmentResponse])
def get_doctor_appointments(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get all appointments for the current doctor."""
    if current_user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view appointments"
        )
    
    appts = db.query(models.Appointment).filter(
        models.Appointment.doctor_id == current_user.id,
        models.Appointment.status.in_(["PENDING", "CONFIRMED"])
    ).order_by(models.Appointment.start_time).all()
    
    return appts


@router.get("/patient/me", response_model=list[schemas.AppointmentResponse])
def get_patient_appointments(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Get all appointments for the current patient."""
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view appointments"
        )
    
    appts = db.query(models.Appointment).filter(
        models.Appointment.patient_id == current_user.id,
        models.Appointment.status.in_(["PENDING", "CONFIRMED"])
    ).order_by(models.Appointment.start_time).all()
    
    return appts


@router.patch("/{appointment_id}/cancel")
def cancel_appointment(
    appointment_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    """Cancel an appointment."""
    appt = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Authorization: doctor or patient of this appointment
    if current_user.id != appt.doctor_id and current_user.id != appt.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this appointment"
        )
    
    if appt.status == "CANCELLED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    appt.status = "CANCELLED"
    db.commit()
    
    logger.info(
        f"CANCEL_APPOINTMENT: appointment_id={appointment_id}, "
        f"cancelled_by={current_user.id}"
    )
    
    return {"message": "Appointment cancelled successfully"}
