from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# --- Auth & Users ---
class UserBase(BaseModel):
    username: str
    name: str
    role: str

class UserResponse(UserBase):
    id: int
    email: Optional[str] = None
    specialty: Optional[str] = None
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

# --- Signup Inputs ---
class PatientSignup(BaseModel):
    name: str
    username: Optional[str] = None
    password: str
    email: Optional[EmailStr] = None

class GmailSignup(BaseModel):
    name: str
    email: EmailStr

class DoctorSignup(BaseModel):
    name: str
    username: Optional[str] = None
    password: str
    specialty: str
    location: str
    email: Optional[EmailStr] = None

# --- Requests ---
class RequestCreate(BaseModel):
    symptom: str
    specialty: str
    answers: List[str]

class RequestResponse(BaseModel):
    id: int
    symptom: str
    specialty: str
    status: str
    created_at: datetime
    patient_name: str # Enriched field
    answers: List[str]

    class Config:
        from_attributes = True

# --- Appointments ---
class AppointmentCreate(BaseModel):
    requestId: str
    doctorId: str
    patientId: str
    startTime: datetime
    endTime: datetime
    mode: str = "in_person"
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    mode: str
    status: str
    doctor_id: int
    patient_id: int
    request_id: Optional[int] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class BookAppointmentRequest(BaseModel):
    """Request body for POST /api/appointments/book"""
    requestId: str
    doctorId: str
    patientId: str
    startTime: datetime
    endTime: datetime
    mode: str = "in_person"
    notes: Optional[str] = None

class BookAppointmentResponse(BaseModel):
    """Response body for successful booking"""
    ok: bool
    appointmentId: str
    status: str
    message: str
