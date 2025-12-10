# Doctor Signup Enhancement Documentation

## Overview
Enhanced doctor account creation flow with auto-username generation, specialty selection, phone validation, and Google Maps clinic location picker with precise coordinate selection.

## Features Implemented

### 1. Auto-Username Generation
- **Behavior**: If username field is left blank, system auto-generates username from full name
- **Algorithm**:
  1. Try 3 format variations: `first-last`, `firstlast`, `first.last`
  2. Check availability for each format
  3. If all taken, append 2-digit random number (10-99) - 5 attempts
  4. Fallback: timestamp-based unique suffix
- **Manual Entry**: Users can still enter custom username (validated for format and uniqueness)
- **Collision Handling**: Inline error message suggests leaving blank for auto-generation

**Example:**
- Name: "Dr. Arup Sen"
- Generated usernames tried: `arup-sen` → `arupsen` → `arup.sen` → `arup-sen42` (if collisions occur)

### 2. Specialty Dropdown
- **Replaced**: Text input → Dropdown select
- **Specialties Available**:
  - Cardiology
  - Dermatology
  - Endocrinology
  - ENT (Ear, Nose, Throat)
  - Gastroenterology
  - General Practice
  - Hematology
  - Nephrology
  - Neurology
  - Oncology
  - Ophthalmology
  - Orthopedics
  - Pediatrics
  - Psychiatry
  - Pulmonology
  - Rheumatology
  - Urology
- **Validation**: Required field - shows inline error if not selected

### 3. Phone Number Validation
- **Format**: E.164 international format (e.g., `+91XXXXXXXXXX`)
- **Patterns Accepted**:
  - General E.164: `^\+[1-9]\d{1,14}$`
  - India-specific: `^\+91[6-9]\d{9}$`
- **Behavior**: Optional field - only validates if entered
- **Error Message**: "Phone must be E.164 format (e.g., +91XXXXXXXXXX)"

### 4. Google Places Autocomplete
- **Integration**: Google Maps Places API
- **Behavior**: 
  - Type clinic name or address in "Clinic / Location" field
  - Autocomplete suggestions appear as user types
  - Select from dropdown to auto-fill address and show map preview
- **Data Captured**:
  - `formatted_address` or `name`
  - Latitude (`lat`)
  - Longitude (`lng`)
  - Place ID (`place_id`)

### 5. Interactive Map Preview
- **Trigger**: Appears when location selected from autocomplete
- **Features**:
  - Embedded Google Map (250px height)
  - Draggable red marker for precise location adjustment
  - Live coordinate display updates on marker drag
  - Zoom level: 16 (street-level view)
- **Controls**: 
  - Map type control: Disabled
  - Street view: Disabled
  - Fullscreen: Disabled
- **Fallback**: If Google Maps API not loaded, gracefully degrades (no map shown, location still saved)

### 6. Inline Error Validation
- All validation errors display inline below form (no global modals)
- Error element: `#ds-error`
- Errors clear on next form submission attempt
- Validation order:
  1. Full name required
  2. Password required (min 6 chars)
  3. Specialty required
  4. Phone format (if provided)
  5. Username availability (if manually entered)

## Data Storage

### Frontend (localStorage)
Stored under `USERS_KEY` with following structure:
```javascript
{
  username: string,
  password: string,
  role: 'doctor',
  name: string,
  specialty: string,
  phone: string | null,
  location: string,
  clinicLat: float | null,
  clinicLng: float | null,
  clinicPlaceId: string | null
}
```

### Backend API (POST /api/doctors/signup)
Request body (Pydantic model `UserSignup`):
```python
{
  "name": str,
  "username": str | None,
  "password": str,
  "specialty": str | None,
  "location": str | None,
  "phone": str | None,
  "clinicLat": float | None,
  "clinicLng": float | None,
  "clinicPlaceId": str | None
}
```

Response:
```python
{
  "access_token": "fake-token-{user_id}",
  "user": {
    "id": int,
    "username": str,
    "name": str,
    "role": "doctor",
    "specialty": str,
    "location": str,
    "phone": str,
    "clinicLat": float,
    "clinicLng": float,
    "clinicPlaceId": str,
    "createdAt": ISO timestamp
  }
}
```

## Setup Instructions

### 1. Get Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable APIs:
   - Maps JavaScript API
   - Places API
4. Create credentials → API Key
5. Restrict key (recommended):
   - HTTP referrers: `http://localhost:*`, `http://127.0.0.1:*`
   - API restrictions: Maps JavaScript API, Places API

### 2. Update HTML File
Replace `YOUR_API_KEY` in `index.html` line 161:
```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&libraries=places" async defer></script>
```

### 3. Local Testing
```bash
# No additional dependencies required - vanilla JavaScript implementation
# Just open index.html in browser or serve via:
python -m http.server 8080
# Then open http://localhost:8080/index.html
```

### 4. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python api.py
# Backend runs on http://localhost:8000
```

## File Changes Summary

### Modified Files
1. **index.html**
   - Lines 362-401: Doctor signup form HTML (added dropdown, map preview container)
   - Lines 730-820: Google Maps integration JavaScript (autocomplete + map preview)
   - Lines 818-918: Enhanced username generation + phone validation
   - Line 161: Google Maps API script tag

2. **backend/api.py**
   - Lines 81-91: Updated `UserSignup` model (added phone, clinicLat, clinicLng, clinicPlaceId)
   - Lines 287-310: Updated `doctor_signup` endpoint to store new fields

### Zero Side-Effects Verified
- ✅ No changes to patient signup flow
- ✅ No changes to doctor login flow
- ✅ No changes to dashboard rendering
- ✅ No changes to symptom checker
- ✅ No database schema changes (uses existing localStorage structure)
- ✅ No new external dependencies (except Google Maps API - optional)

## Testing Checklist

### Manual Testing Scenarios

#### Test 1: Auto-Username Generation (Happy Path)
1. Navigate to Doctor Signup page
2. Fill in:
   - Full name: "Dr. Sarah Johnson"
   - Password: "test123"
   - Specialty: "Cardiology"
   - Leave username blank
3. Submit form
4. **Expected**: Account created with username like `sarah-johnson` or `sarahjohnson`

#### Test 2: Username Collision Handling
1. Create first doctor: "Dr. John Doe" (username auto-generated: `john-doe`)
2. Create second doctor: "Dr. John Doe" (same name)
3. **Expected**: Second account gets username like `john-doe42` (random suffix)

#### Test 3: Manual Username Entry
1. Fill in custom username: "doc_sarah_2024"
2. Complete other fields
3. Submit
4. **Expected**: Account created with exact username entered

#### Test 4: Username Already Taken
1. Create account with username "testdoc"
2. Try creating another with same username "testdoc"
3. **Expected**: Inline error: "Username already taken. Try another or leave blank for auto-generation."

#### Test 5: Phone Validation
1. Enter invalid phone: "1234567890" (no country code)
2. Submit
3. **Expected**: Error: "Phone must be E.164 format (e.g., +91XXXXXXXXXX)"
4. Enter valid phone: "+919876543210"
5. Submit
6. **Expected**: Account created successfully

#### Test 6: Google Maps Autocomplete (with API key)
1. Start typing clinic name: "Apollo Hospital"
2. **Expected**: Autocomplete dropdown appears with suggestions
3. Select a suggestion
4. **Expected**: 
   - Map preview appears below input
   - Marker placed at selected location
   - Coordinates displayed

#### Test 7: Map Marker Dragging
1. Select location from autocomplete
2. Drag the red marker to new position
3. **Expected**: Coordinates update in real-time

#### Test 8: Form Validation Order
1. Click "Create & Enter" with empty form
2. **Expected**: Error: "Please enter full name."
3. Fill name, click submit
4. **Expected**: Error: "Please enter password."
5. Fill password (4 chars), submit
6. **Expected**: Error: "Password must be >=6 chars."
7. Fill password (6+ chars), submit
8. **Expected**: Error: "Please select your specialty."

#### Test 9: Specialty Dropdown
1. Check dropdown contains all 17 specialties
2. Select "Neurology"
3. Submit form
4. **Expected**: Account created with specialty = "Neurology"

#### Test 10: No Google Maps API Key (Graceful Degradation)
1. Remove/invalid API key in script tag
2. Fill form and select location
3. **Expected**: 
   - Autocomplete doesn't work (plain text input)
   - Map preview doesn't show
   - Form still submits successfully
   - Location saved as plain text

## Implementation Notes

### Why These Design Choices?

1. **Auto-Username Generation**
   - UX improvement: Reduces friction in signup flow
   - 3 format attempts: Increases chance of getting clean username
   - Random suffix: Better than sequential (prevents enumeration)
   - Fallback to timestamp: Ensures no signup failures

2. **Specialty Dropdown**
   - Data consistency: Prevents typos ("Cardio" vs "Cardiology")
   - Better UX: Faster than typing
   - Matches backend recommendation algorithm specialties

3. **Phone Validation (E.164)**
   - International standard format
   - Enables future features (SMS notifications, WhatsApp integration)
   - Optional field: Doesn't block signup

4. **Google Maps Integration**
   - Accuracy: Prevents address typos
   - Geocoding: Enables distance-based doctor search
   - Place ID: Stable identifier for clinic (survives address changes)
   - Draggable marker: Handles edge cases (entrance vs building center)

5. **Inline Validation**
   - Better UX: Errors appear contextually
   - No modal blocking: Users can see form while reading error
   - Matches existing pattern in patient signup

### Performance Considerations

- **Google Maps API**: Loaded async/defer - doesn't block page load
- **Map Initialization**: Delayed 1 second after page load
- **Autocomplete Debouncing**: Built-in by Google Places API
- **localStorage**: Minimal overhead for small user database

### Security Considerations

- ⚠️ **Password Storage**: Currently plaintext in demo - implement hashing for production
- ⚠️ **API Key Exposure**: Restrict key to specific domains in production
- ✅ **Input Validation**: All fields validated client-side and server-side
- ✅ **SQL Injection**: Not applicable (using in-memory storage)

## Future Enhancements

1. **Real-time username availability check** (debounced API call)
2. **Email verification** for doctor accounts
3. **License number validation** (medical council registration)
4. **Clinic working hours** input
5. **Multiple clinic locations** support
6. **Photo upload** for clinic/profile
7. **Integration with backend geocoding** (fallback if no API key)
8. **Map style customization** (dark mode matching app theme)

## Troubleshooting

### Map not showing
- Check browser console for Google Maps API errors
- Verify API key is correct and not restricted incorrectly
- Ensure Maps JavaScript API and Places API are enabled in Google Cloud Console
- Check for CORS issues (serve via http-server, not file://)

### Autocomplete not working
- Verify `libraries=places` in script tag
- Check if places service is enabled in API console
- Look for JavaScript errors in console

### Username generation always uses timestamp
- Check if many users with same name exist
- Verify `generateUsername` function logic
- Check browser console for errors

### Phone validation too strict
- Adjust regex patterns in `validatePhone` function
- Current patterns: E.164 and India-specific
- Add more country patterns as needed

## API Key Management (Production)

**Never commit API keys to version control!**

### Recommended approach:
1. Use environment variables:
   ```javascript
   const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY || '';
   ```

2. Server-side rendering with template injection:
   ```html
   <script src="https://maps.googleapis.com/maps/api/js?key={{ GOOGLE_MAPS_API_KEY }}&libraries=places"></script>
   ```

3. Build-time replacement (Webpack/Vite):
   ```javascript
   // vite.config.js
   define: {
     'process.env.GOOGLE_MAPS_API_KEY': JSON.stringify(process.env.GOOGLE_MAPS_API_KEY)
   }
   ```

## Acceptance Criteria Met ✅

1. ✅ **Auto-username generation**: 3 formats + collision handling + fallback
2. ✅ **Specialty dropdown**: 17 options, required validation
3. ✅ **Phone validation**: E.164 format, inline errors, optional
4. ✅ **Google Places Autocomplete**: Working with suggestions
5. ✅ **Map preview**: Embedded map with draggable marker
6. ✅ **Coordinate capture**: lat, lng, placeId stored
7. ✅ **Inline validation**: All errors shown in ds-error element
8. ✅ **Zero side-effects**: Only doctor signup flow modified
9. ✅ **Backend updated**: New fields added to API
10. ✅ **Minimal scope**: No new dependencies, vanilla JS only

## Contact & Support
For issues or questions about this implementation:
- Check browser console for JavaScript errors
- Verify Google Maps API setup in Cloud Console
- Review validation logic in `generateUsername()` and `validatePhone()` functions
- Test with and without API key to verify graceful degradation
