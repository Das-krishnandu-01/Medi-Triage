from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, patients, doctors, requests, appointments

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Triage API")

# Allow Frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins, including null (file://)
    allow_credentials=False, # We use Bearer tokens (headers), not cookies, so this is safe and allows '*' origin
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(requests.router)
app.include_router(appointments.router)
