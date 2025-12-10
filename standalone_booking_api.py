#!/usr/bin/env python3
"""
Standalone Appointment Booking API
===================================
A completely self-contained FastAPI backend for appointment booking.
No external dependencies on existing project files required.

Features:
- In-memory database (no external DB needed)
- Complete validation
- Full CRUD operations
- CORS enabled for frontend integration
- Runs independently on port 8001

Usage:
    python standalone_booking_api.py

    or

    uvicorn standalone_booking_api:app --reload --port 8001
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, Field
from typing import Optional, Literal, Dict, List
from datetime import datetime, timezone
from uuid import uuid4
import uvicorn

# ============================================================================
# DATA MODELS (Pydantic Schemas)
# ============================================================================

class AppointmentCreate(BaseModel):
    """Request schema for creating an appointment"""
    userId: str = Field(..., min_length=1, description="User ID (required)")
    startTime: str = Field(..., description="Start time in ISO 8601 format")
    endTime: str = Field(..., description="End time in ISO 8601 format")
    mode: Literal["video", "in-person", "phone"] = Field(..., description="Appointment mode")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")

    @validator('userId')
    def validate_user_id(cls, v):
        """Ensure userId is not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError('userId must be a non-empty string')
        return v.strip()

    @validator('startTime', 'endTime')
    def validate_iso_format(cls, v):
        """Validate ISO 8601 datetime format"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError(f'Invalid ISO 8601 datetime format: {v}')

    @validator('endTime')
    def validate_time_range(cls, v, values):
        """Ensure endTime is after startTime"""
        if 'startTime' not in values:
            return v
        
        start = datetime.fromisoformat(values['startTime'].replace('Z', '+00:00'))
        end = datetime.fromisoformat(v.replace('Z', '+00:00'))
        
        if end <= start:
            raise ValueError('endTime must be after startTime')
        
        return v

    @validator('startTime')
    def validate_future_time(cls, v):
        """Ensure startTime is in the future"""
        start = datetime.fromisoformat(v.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        if start <= now:
            raise ValueError('startTime must be in the future')
        
        return v

    class Config:
        schema_extra = {
            "example": {
                "userId": "user-123",
                "startTime": "2025-12-15T14:00:00Z",
                "endTime": "2025-12-15T14:30:00Z",
                "mode": "video",
                "notes": "Follow-up consultation"
            }
        }


class AppointmentResponse(BaseModel):
    """Response schema for appointment operations"""
    appointmentId: str
    userId: str
    startTime: str
    endTime: str
    mode: str
    notes: Optional[str]
    status: str
    createdAt: str
    updatedAt: str

    class Config:
        schema_extra = {
            "example": {
                "appointmentId": "appt-abc123",
                "userId": "user-123",
                "startTime": "2025-12-15T14:00:00Z",
                "endTime": "2025-12-15T14:30:00Z",
                "mode": "video",
                "notes": "Follow-up consultation",
                "status": "confirmed",
                "createdAt": "2025-12-11T10:00:00Z",
                "updatedAt": "2025-12-11T10:00:00Z"
            }
        }


class SuccessResponse(BaseModel):
    """Generic success response"""
    ok: bool = True
    message: str
    data: Optional[AppointmentResponse] = None


class ErrorResponse(BaseModel):
    """Generic error response"""
    ok: bool = False
    error: str
    detail: Optional[str] = None


# ============================================================================
# IN-MEMORY DATABASE
# ============================================================================

class InMemoryDB:
    """Simple in-memory database for appointments"""
    
    def __init__(self):
        self.appointments: Dict[str, dict] = {}
        self.id_counter = 0
    
    def create(self, appointment_data: dict) -> dict:
        """Create a new appointment"""
        self.id_counter += 1
        appointment_id = f"appt-{uuid4().hex[:8]}"
        
        now = datetime.now(timezone.utc).isoformat()
        
        appointment = {
            "appointmentId": appointment_id,
            **appointment_data,
            "status": "confirmed",
            "createdAt": now,
            "updatedAt": now
        }
        
        self.appointments[appointment_id] = appointment
        return appointment
    
    def get(self, appointment_id: str) -> Optional[dict]:
        """Get appointment by ID"""
        return self.appointments.get(appointment_id)
    
    def update(self, appointment_id: str, updates: dict) -> Optional[dict]:
        """Update an appointment"""
        if appointment_id not in self.appointments:
            return None
        
        self.appointments[appointment_id].update(updates)
        self.appointments[appointment_id]["updatedAt"] = datetime.now(timezone.utc).isoformat()
        
        return self.appointments[appointment_id]
    
    def list_by_user(self, user_id: str) -> List[dict]:
        """Get all appointments for a user"""
        return [
            appt for appt in self.appointments.values()
            if appt["userId"] == user_id
        ]
    
    def list_all(self) -> List[dict]:
        """Get all appointments"""
        return list(self.appointments.values())
    
    def delete(self, appointment_id: str) -> bool:
        """Delete an appointment"""
        if appointment_id in self.appointments:
            del self.appointments[appointment_id]
            return True
        return False


# Initialize database
db = InMemoryDB()


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Standalone Appointment Booking API",
    description="Self-contained appointment booking backend with no external dependencies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration (allows frontend to connect from any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Standalone Appointment Booking API",
        "version": "1.0.0",
        "endpoints": {
            "create": "POST /appointments",
            "get": "GET /appointments/{id}",
            "list": "GET /appointments",
            "cancel": "POST /appointments/{id}/cancel",
            "confirm": "POST /appointments/{id}/confirm",
            "delete": "DELETE /appointments/{id}"
        }
    }


# ============================================================================
# APPOINTMENT ENDPOINTS
# ============================================================================

@app.post(
    "/appointments",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Appointments"]
)
def create_appointment(appointment: AppointmentCreate):
    """
    Create a new appointment
    
    Validations:
    - userId must be non-empty
    - startTime must be valid ISO 8601 format
    - endTime must be valid ISO 8601 format
    - startTime must be < endTime
    - startTime must be in the future
    - mode must be one of: video, in-person, phone
    - notes are optional (max 500 chars)
    
    Returns:
    - 201: Appointment created successfully
    - 422: Validation error
    """
    try:
        # Create appointment in database
        appointment_data = appointment.dict()
        created_appointment = db.create(appointment_data)
        
        return SuccessResponse(
            ok=True,
            message="Appointment created successfully",
            data=AppointmentResponse(**created_appointment)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create appointment: {str(e)}"
        )


@app.get(
    "/appointments/{appointment_id}",
    response_model=SuccessResponse,
    tags=["Appointments"]
)
def get_appointment(appointment_id: str):
    """
    Get appointment by ID
    
    Returns:
    - 200: Appointment found
    - 404: Appointment not found
    """
    appointment = db.get(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    return SuccessResponse(
        ok=True,
        message="Appointment retrieved successfully",
        data=AppointmentResponse(**appointment)
    )


@app.get(
    "/appointments",
    response_model=Dict,
    tags=["Appointments"]
)
def list_appointments(userId: Optional[str] = None):
    """
    List all appointments or filter by userId
    
    Query Parameters:
    - userId (optional): Filter appointments by user ID
    
    Returns:
    - 200: List of appointments
    """
    if userId:
        appointments = db.list_by_user(userId)
    else:
        appointments = db.list_all()
    
    return {
        "ok": True,
        "count": len(appointments),
        "appointments": [AppointmentResponse(**appt) for appt in appointments]
    }


@app.post(
    "/appointments/{appointment_id}/cancel",
    response_model=SuccessResponse,
    tags=["Appointments"]
)
def cancel_appointment(appointment_id: str):
    """
    Cancel an appointment
    
    Updates the appointment status to 'cancelled'
    
    Returns:
    - 200: Appointment cancelled successfully
    - 404: Appointment not found
    - 400: Appointment already cancelled
    """
    appointment = db.get(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    if appointment["status"] == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    updated = db.update(appointment_id, {"status": "cancelled"})
    
    return SuccessResponse(
        ok=True,
        message="Appointment cancelled successfully",
        data=AppointmentResponse(**updated)
    )


@app.post(
    "/appointments/{appointment_id}/confirm",
    response_model=SuccessResponse,
    tags=["Appointments"]
)
def confirm_appointment(appointment_id: str):
    """
    Confirm an appointment
    
    Updates the appointment status to 'confirmed'
    
    Returns:
    - 200: Appointment confirmed successfully
    - 404: Appointment not found
    - 400: Appointment already confirmed or cancelled
    """
    appointment = db.get(appointment_id)
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    if appointment["status"] == "confirmed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already confirmed"
        )
    
    if appointment["status"] == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot confirm a cancelled appointment"
        )
    
    updated = db.update(appointment_id, {"status": "confirmed"})
    
    return SuccessResponse(
        ok=True,
        message="Appointment confirmed successfully",
        data=AppointmentResponse(**updated)
    )


@app.delete(
    "/appointments/{appointment_id}",
    response_model=SuccessResponse,
    tags=["Appointments"]
)
def delete_appointment(appointment_id: str):
    """
    Delete an appointment
    
    Permanently removes the appointment from the database
    
    Returns:
    - 200: Appointment deleted successfully
    - 404: Appointment not found
    """
    if not db.delete(appointment_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment {appointment_id} not found"
        )
    
    return SuccessResponse(
        ok=True,
        message="Appointment deleted successfully",
        data=None
    )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return {
        "ok": False,
        "error": exc.detail,
        "status_code": exc.status_code
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler"""
    return {
        "ok": False,
        "error": "Internal server error",
        "detail": str(exc)
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Starting Standalone Appointment Booking API")
    print("=" * 70)
    print(f"📍 Server: http://localhost:8001")
    print(f"📚 API Docs: http://localhost:8001/docs")
    print(f"📖 ReDoc: http://localhost:8001/redoc")
    print("=" * 70)
    print("\n✨ API Endpoints:")
    print("   POST   /appointments              → Create appointment")
    print("   GET    /appointments/{id}         → Get appointment")
    print("   GET    /appointments?userId=...   → List appointments")
    print("   POST   /appointments/{id}/cancel  → Cancel appointment")
    print("   POST   /appointments/{id}/confirm → Confirm appointment")
    print("   DELETE /appointments/{id}         → Delete appointment")
    print("\n" + "=" * 70)
    print("Press Ctrl+C to stop\n")
    
    # Run with uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )
