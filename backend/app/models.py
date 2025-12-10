from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime as dt
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True) # Nullable for Gmail-only
    role = Column(String) # 'patient' or 'doctor'
    name = Column(String)
    email = Column(String, nullable=True)
    
    # Doctor specific fields
    specialty = Column(String, nullable=True)
    location = Column(String, nullable=True)

    created_at = Column(DateTime, default=dt.utcnow)

class TriageRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    symptom = Column(String)
    specialty = Column(String)
    answers_json = Column(JSON) # Stores list of answers
    status = Column(String, default="new") # new, viewed, accepted, rejected, booked
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    handled_by = Column(Integer, ForeignKey("users.id"), nullable=True) # Doctor who handled it
    handled_at = Column(DateTime, nullable=True) # When handled
    created_at = Column(DateTime, default=dt.utcnow)

    patient = relationship("User", foreign_keys=[patient_id])
    doctor = relationship("User", foreign_keys=[doctor_id])
    handler = relationship("User", foreign_keys=[handled_by])

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_time = Column(DateTime, index=True)  # ISO timestamp in UTC
    end_time = Column(DateTime)  # ISO timestamp in UTC
    mode = Column(String, default="in_person")  # video, in_person, phone
    status = Column(String, default="PENDING")  # PENDING, CONFIRMED, CANCELLED
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor who created
    created_at = Column(DateTime, default=dt.utcnow)

    request = relationship("TriageRequest")
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    creator = relationship("User", foreign_keys=[created_by])
