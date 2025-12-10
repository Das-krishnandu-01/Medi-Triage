# 🚀 QUICK START GUIDE - Standalone Booking API

## ⚡ 3-Step Setup

### Step 1: Install Dependencies (30 seconds)
```bash
pip install -r requirements_standalone.txt
```

### Step 2: Start the Server (5 seconds)
```bash
python standalone_booking_api.py
```

You should see:
```
======================================================================
🚀 Starting Standalone Appointment Booking API
======================================================================
📍 Server: http://localhost:8001
📚 API Docs: http://localhost:8001/docs
📖 ReDoc: http://localhost:8001/redoc
======================================================================
```

### Step 3: Test It! (30 seconds)
Open another terminal and run:
```bash
PowerShell -ExecutionPolicy Bypass -File test_standalone_api.ps1
```

✅ **You're done!** API is running and tested.

---

## 📋 What You Get

### API Server Running on Port 8001
- ✅ Complete appointment booking backend
- ✅ No database setup needed (in-memory)
- ✅ CORS enabled for frontend
- ✅ Auto-generated API documentation

### 6 Ready-to-Use Endpoints
1. **POST** `/appointments` - Create appointment
2. **GET** `/appointments/{id}` - Get appointment
3. **GET** `/appointments?userId=...` - List appointments
4. **POST** `/appointments/{id}/cancel` - Cancel appointment
5. **POST** `/appointments/{id}/confirm` - Confirm appointment
6. **DELETE** `/appointments/{id}` - Delete appointment

---

## 🎯 Quick Test with cURL

### Create an Appointment
```bash
curl -X POST http://localhost:8001/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "startTime": "2025-12-20T15:00:00Z",
    "endTime": "2025-12-20T15:30:00Z",
    "mode": "video",
    "notes": "Quick test"
  }'
```

**Expected Response:**
```json
{
  "ok": true,
  "message": "Appointment created successfully",
  "data": {
    "appointmentId": "appt-abc12345",
    "userId": "user-123",
    "startTime": "2025-12-20T15:00:00Z",
    "endTime": "2025-12-20T15:30:00Z",
    "mode": "video",
    "notes": "Quick test",
    "status": "confirmed",
    "createdAt": "2025-12-11T...",
    "updatedAt": "2025-12-11T..."
  }
}
```

### List All Appointments
```bash
curl http://localhost:8001/appointments
```

---

## 🌐 Interactive API Documentation

**Open in your browser:**
- http://localhost:8001/docs

You'll see Swagger UI where you can:
- ✅ Try all endpoints
- ✅ See request/response examples
- ✅ Test with different inputs
- ✅ See validation errors

---

## 💻 Frontend Integration Example

### JavaScript Fetch API
```javascript
// Create appointment when user clicks "Confirm Booking"
async function bookAppointment(userId, startTime, endTime, mode, notes) {
  try {
    const response = await fetch('http://localhost:8001/appointments', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
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
      // Success!
      console.log('Appointment ID:', data.data.appointmentId);
      showSuccessMessage('Appointment booked!');
      return data.data;
    } else {
      // Error
      showErrorMessage(data.error);
      return null;
    }
  } catch (error) {
    showErrorMessage('Network error: ' + error.message);
    return null;
  }
}

// Usage in your modal
document.getElementById('book-confirm').addEventListener('click', async () => {
  const result = await bookAppointment(
    'user-123',
    '2025-12-20T15:00:00Z',
    '2025-12-20T15:30:00Z',
    'video',
    'Follow-up'
  );

  if (result) {
    closeModal();
  }
});
```

---

## 🔧 Common Tasks

### Change Port
Edit `standalone_booking_api.py`, line 544:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to your port
```

### Add Authentication
Add to request body validation:
```python
class AppointmentCreate(BaseModel):
    token: str  # Add this field
    userId: str
    # ... rest of fields
```

### Enable HTTPS
```bash
uvicorn standalone_booking_api:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

---

## 📊 Validation Rules Summary

| Field | Rule |
|-------|------|
| **userId** | Non-empty string |
| **startTime** | Valid ISO 8601, must be in future |
| **endTime** | Valid ISO 8601, must be after startTime |
| **mode** | Must be: "video", "in-person", or "phone" |
| **notes** | Optional, max 500 characters |

---

## ❓ Troubleshooting

### Port Already in Use
```bash
# Change port in standalone_booking_api.py
# Or kill process on port 8001
# Windows:
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8001 | xargs kill
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements_standalone.txt
```

### CORS Errors
In `standalone_booking_api.py`, update:
```python
allow_origins=["http://localhost:3000", "http://localhost:5500"]  # Add your frontend URL
```

---

## 🎉 You're Ready!

**The API is:**
- ✅ Running on http://localhost:8001
- ✅ Documented at http://localhost:8001/docs
- ✅ Tested and working
- ✅ Ready for your frontend to use

**No other setup needed!**

---

## 📚 Next Steps

1. **Explore API Docs**: http://localhost:8001/docs
2. **Read Full Documentation**: STANDALONE_API_README.md
3. **Run Test Suite**: `PowerShell -File test_standalone_api.ps1`
4. **Integrate with Frontend**: Use fetch examples above

---

## 🆘 Need Help?

**API not starting?**
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements_standalone.txt`

**Can't connect from frontend?**
- Check CORS settings in `standalone_booking_api.py`
- Verify API is running: http://localhost:8001

**Validation errors?**
- See STANDALONE_API_README.md for validation rules
- Check API docs for examples: http://localhost:8001/docs

---

**Status**: ✅ Ready to Use - Zero Configuration Needed!

