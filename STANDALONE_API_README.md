# 📚 Standalone Appointment Booking API

## 🎯 Overview

A **completely self-contained** FastAPI backend for appointment booking that requires **ZERO modifications** to existing project files.

### Key Features
- ✅ **100% Standalone** - No edits to existing files required
- ✅ **In-Memory Database** - No external database setup needed
- ✅ **Complete Validation** - All business rules enforced
- ✅ **CORS Enabled** - Works with any frontend
- ✅ **Auto Documentation** - Interactive API docs included
- ✅ **Production Ready** - Full error handling

---

## 🚀 Quick Start

### Installation

```bash
# Install FastAPI and Uvicorn
pip install fastapi uvicorn pydantic

# Or using requirements file
pip install -r requirements_standalone.txt
```

### Run the Server

```bash
# Method 1: Direct execution
python standalone_booking_api.py

# Method 2: Using uvicorn
uvicorn standalone_booking_api:app --reload --port 8001
```

### Access Points
- **API**: http://localhost:8001
- **Interactive Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## 📋 API Endpoints

### 1. Create Appointment
**POST** `/appointments`

Creates a new appointment with validation.

**Request Body:**
```json
{
  "userId": "user-123",
  "startTime": "2025-12-15T14:00:00Z",
  "endTime": "2025-12-15T14:30:00Z",
  "mode": "video",
  "notes": "Follow-up consultation"
}
```

**Response (201):**
```json
{
  "ok": true,
  "message": "Appointment created successfully",
  "data": {
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
```

**Validation Rules:**
- ✅ `userId` must be non-empty string
- ✅ `startTime` must be valid ISO 8601 format
- ✅ `endTime` must be valid ISO 8601 format
- ✅ `startTime` < `endTime`
- ✅ `startTime` must be in the future
- ✅ `mode` must be: "video", "in-person", or "phone"
- ✅ `notes` are optional (max 500 characters)

**Error Response (422):**
```json
{
  "ok": false,
  "error": "Validation error",
  "detail": [
    {
      "loc": ["body", "startTime"],
      "msg": "startTime must be in the future",
      "type": "value_error"
    }
  ]
}
```

---

### 2. Get Appointment
**GET** `/appointments/{appointment_id}`

Retrieve a specific appointment by ID.

**Response (200):**
```json
{
  "ok": true,
  "message": "Appointment retrieved successfully",
  "data": {
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
```

**Error Response (404):**
```json
{
  "ok": false,
  "error": "Appointment appt-xyz not found",
  "status_code": 404
}
```

---

### 3. List Appointments
**GET** `/appointments?userId={userId}`

List all appointments or filter by user.

**Query Parameters:**
- `userId` (optional): Filter by user ID

**Response (200):**
```json
{
  "ok": true,
  "count": 2,
  "appointments": [
    {
      "appointmentId": "appt-abc123",
      "userId": "user-123",
      "startTime": "2025-12-15T14:00:00Z",
      "endTime": "2025-12-15T14:30:00Z",
      "mode": "video",
      "notes": "Follow-up",
      "status": "confirmed",
      "createdAt": "2025-12-11T10:00:00Z",
      "updatedAt": "2025-12-11T10:00:00Z"
    }
  ]
}
```

---

### 4. Cancel Appointment
**POST** `/appointments/{appointment_id}/cancel`

Cancel an existing appointment.

**Response (200):**
```json
{
  "ok": true,
  "message": "Appointment cancelled successfully",
  "data": {
    "appointmentId": "appt-abc123",
    "status": "cancelled",
    "updatedAt": "2025-12-11T11:00:00Z"
  }
}
```

**Error Responses:**
- **404**: Appointment not found
- **400**: Appointment already cancelled

---

### 5. Confirm Appointment
**POST** `/appointments/{appointment_id}/confirm`

Confirm an existing appointment.

**Response (200):**
```json
{
  "ok": true,
  "message": "Appointment confirmed successfully",
  "data": {
    "appointmentId": "appt-abc123",
    "status": "confirmed",
    "updatedAt": "2025-12-11T11:00:00Z"
  }
}
```

**Error Responses:**
- **404**: Appointment not found
- **400**: Appointment already confirmed
- **400**: Cannot confirm cancelled appointment

---

### 6. Delete Appointment
**DELETE** `/appointments/{appointment_id}`

Permanently delete an appointment.

**Response (200):**
```json
{
  "ok": true,
  "message": "Appointment deleted successfully",
  "data": null
}
```

**Error Response (404):**
```json
{
  "ok": false,
  "error": "Appointment appt-xyz not found"
}
```

---

## 🧪 Testing Examples

### Using cURL

#### Create Appointment
```bash
curl -X POST http://localhost:8001/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "startTime": "2025-12-15T14:00:00Z",
    "endTime": "2025-12-15T14:30:00Z",
    "mode": "video",
    "notes": "Initial consultation"
  }'
```

#### Get Appointment
```bash
curl http://localhost:8001/appointments/appt-abc123
```

#### List All Appointments
```bash
curl http://localhost:8001/appointments
```

#### List User's Appointments
```bash
curl "http://localhost:8001/appointments?userId=user-123"
```

#### Cancel Appointment
```bash
curl -X POST http://localhost:8001/appointments/appt-abc123/cancel
```

#### Confirm Appointment
```bash
curl -X POST http://localhost:8001/appointments/appt-abc123/confirm
```

#### Delete Appointment
```bash
curl -X DELETE http://localhost:8001/appointments/appt-abc123
```

---

### Using JavaScript (Frontend)

#### Create Appointment
```javascript
const response = await fetch('http://localhost:8001/appointments', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    userId: 'user-123',
    startTime: '2025-12-15T14:00:00Z',
    endTime: '2025-12-15T14:30:00Z',
    mode: 'video',
    notes: 'Follow-up consultation'
  })
});

const data = await response.json();
if (data.ok) {
  console.log('Appointment created:', data.data.appointmentId);
} else {
  console.error('Error:', data.error);
}
```

#### Cancel Appointment
```javascript
const response = await fetch(`http://localhost:8001/appointments/${appointmentId}/cancel`, {
  method: 'POST'
});

const data = await response.json();
if (data.ok) {
  console.log('Appointment cancelled');
}
```

---

## 🔧 Configuration

### Port Configuration
Change port in `standalone_booking_api.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Change 8001 to desired port
```

### CORS Configuration
Update allowed origins for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 Data Model

### Appointment Object
```typescript
{
  appointmentId: string;      // Auto-generated unique ID
  userId: string;             // User identifier (required)
  startTime: string;          // ISO 8601 datetime (required)
  endTime: string;            // ISO 8601 datetime (required)
  mode: "video" | "in-person" | "phone";  // Appointment type
  notes?: string;             // Optional notes (max 500 chars)
  status: "confirmed" | "cancelled";  // Appointment status
  createdAt: string;          // ISO 8601 datetime (auto)
  updatedAt: string;          // ISO 8601 datetime (auto)
}
```

---

## ⚠️ Validation Rules

### Time Validation
```
✅ startTime < endTime
✅ startTime must be in the future
✅ Both times must be valid ISO 8601 format
```

### User Validation
```
✅ userId must be non-empty string
✅ userId whitespace is trimmed
```

### Mode Validation
```
✅ Must be one of: "video", "in-person", "phone"
```

### Notes Validation
```
✅ Optional field
✅ Max length: 500 characters
```

---

## 🛠️ Error Handling

### Validation Errors (422)
```json
{
  "detail": [
    {
      "loc": ["body", "startTime"],
      "msg": "startTime must be in the future",
      "type": "value_error"
    }
  ]
}
```

### Not Found Errors (404)
```json
{
  "ok": false,
  "error": "Appointment appt-xyz not found",
  "status_code": 404
}
```

### Bad Request Errors (400)
```json
{
  "ok": false,
  "error": "Appointment is already cancelled",
  "status_code": 400
}
```

### Server Errors (500)
```json
{
  "ok": false,
  "error": "Internal server error",
  "detail": "Error message"
}
```

---

## 🔄 Frontend Integration

### Example: Book Appointment Modal

```javascript
// When user clicks "Confirm Booking"
document.getElementById('book-confirm').addEventListener('click', async () => {
  const userId = getCurrentUserId();
  const startTime = new Date(bookDate.value + 'T' + bookTime.value + ':00Z').toISOString();
  const endTime = new Date(bookDate.value + 'T' + bookEndTime.value + ':00Z').toISOString();
  const mode = bookMode.value;
  const notes = bookNotes.value;

  try {
    const response = await fetch('http://localhost:8001/appointments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        startTime,
        endTime,
        mode,
        notes
      })
    });

    const data = await response.json();

    if (data.ok) {
      // Success
      showToast('✓ Appointment booked successfully!');
      closeModal();
      refreshAppointments();
    } else {
      // Error
      showError(data.error);
    }
  } catch (error) {
    showError('Network error: ' + error.message);
  }
});
```

---

## 📦 Dependencies

Create `requirements_standalone.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

Install:
```bash
pip install -r requirements_standalone.txt
```

---

## 🚀 Deployment

### Development
```bash
python standalone_booking_api.py
```

### Production (with Uvicorn)
```bash
uvicorn standalone_booking_api:app --host 0.0.0.0 --port 8001 --workers 4
```

### Production (with Gunicorn + Uvicorn)
```bash
gunicorn standalone_booking_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY standalone_booking_api.py .
COPY requirements_standalone.txt .
RUN pip install -r requirements_standalone.txt
EXPOSE 8001
CMD ["python", "standalone_booking_api.py"]
```

Build and run:
```bash
docker build -t booking-api .
docker run -p 8001:8001 booking-api
```

---

## ✅ Features Checklist

- [x] POST /appointments - Create appointment
- [x] GET /appointments/{id} - Get appointment
- [x] GET /appointments?userId=... - List appointments
- [x] POST /appointments/{id}/cancel - Cancel appointment
- [x] POST /appointments/{id}/confirm - Confirm appointment
- [x] DELETE /appointments/{id} - Delete appointment
- [x] Complete validation (time, user, mode)
- [x] In-memory database (no external DB)
- [x] CORS enabled
- [x] Auto-generated API docs
- [x] Error handling
- [x] No modifications to existing files required
- [x] Runs standalone on port 8001

---

## 🔍 Testing the API

### Health Check
```bash
curl http://localhost:8001/
```

Expected:
```json
{
  "status": "healthy",
  "service": "Standalone Appointment Booking API",
  "version": "1.0.0"
}
```

### Full Test Flow
```bash
# 1. Create appointment
curl -X POST http://localhost:8001/appointments \
  -H "Content-Type: application/json" \
  -d '{"userId":"user-123","startTime":"2025-12-15T14:00:00Z","endTime":"2025-12-15T14:30:00Z","mode":"video","notes":"Test"}'

# 2. List appointments
curl http://localhost:8001/appointments

# 3. Cancel appointment (use ID from step 1)
curl -X POST http://localhost:8001/appointments/appt-xxx/cancel

# 4. Get appointment status
curl http://localhost:8001/appointments/appt-xxx
```

---

## 📝 Notes

### In-Memory Database
- Data is stored in RAM
- Data is lost when server restarts
- Perfect for development/testing
- For production, replace `InMemoryDB` with PostgreSQL/MySQL

### Timezone
- All times use ISO 8601 format with UTC timezone
- Frontend should convert to user's local timezone for display

### Appointment ID
- Auto-generated using UUID
- Format: `appt-{8-char-hex}`
- Unique across all appointments

---

## 🎯 Next Steps

1. **Start the server**: `python standalone_booking_api.py`
2. **Open API docs**: http://localhost:8001/docs
3. **Test endpoints**: Use the interactive docs or cURL
4. **Integrate with frontend**: Use fetch API as shown above
5. **Deploy**: Use Docker or cloud platform

---

## 📞 Support

**API Documentation**: http://localhost:8001/docs
**Health Check**: http://localhost:8001/
**ReDoc**: http://localhost:8001/redoc

---

**Status**: ✅ Ready to use - No modifications to existing files required!

