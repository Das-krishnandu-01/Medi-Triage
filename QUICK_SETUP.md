# Quick Setup Guide - Doctor Signup Enhancement

## 🚀 Get Started in 3 Steps

### Step 1: Get Google Maps API Key (5 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g., "MediTriage Dev")
3. Enable these APIs:
   - **Maps JavaScript API**
   - **Places API**
4. Go to Credentials → Create API Key
5. Copy your API key (starts with `AIza...`)

**Optional but Recommended - Restrict Your Key:**
- Application restrictions → HTTP referrers:
  - `http://localhost:*`
  - `http://127.0.0.1:*`
  - Your production domain
- API restrictions → Select:
  - Maps JavaScript API
  - Places API

### Step 2: Update index.html (30 seconds)

Open `index.html` and find line 161:
```html
<!-- BEFORE -->
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places" async defer></script>

<!-- AFTER -->
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyABC123XYZ789...&libraries=places" async defer></script>
```
Replace `YOUR_API_KEY` with your actual key from Step 1.

### Step 3: Test It Out (2 minutes)

#### Option A: Simple File Open
1. Open `index.html` directly in browser
2. Click "I am a Doctor" → "Create Account"
3. ⚠️ Note: Autocomplete may not work due to CORS (file:// protocol)

#### Option B: Local Server (Recommended)
```bash
# Python 3
python -m http.server 8080

# Node.js
npx http-server -p 8080

# PHP
php -S localhost:8080
```

Then open: http://localhost:8080/index.html

## ✅ Test the New Features

### Test Auto-Username Generation
1. Go to Doctor Signup
2. Fill in:
   - Full name: `Dr. Sarah Johnson`
   - Password: `test123`
   - Specialty: `Cardiology` (select from dropdown)
   - Leave username blank
3. Click "Create & Enter"
4. ✅ You should be logged in with auto-generated username like `sarah-johnson`

### Test Google Maps Autocomplete
1. Go to Doctor Signup
2. Click in "Clinic / Location" field
3. Start typing: `Apollo` or `Clinic` or any address
4. ✅ Autocomplete suggestions should appear
5. Select one
6. ✅ Map preview should appear below with a marker

### Test Marker Dragging
1. After selecting a location (map preview visible)
2. Click and drag the red marker
3. ✅ Coordinates should update in real-time below map

### Test Phone Validation
1. Fill form, enter phone: `1234567890` (invalid - no country code)
2. Click "Create & Enter"
3. ✅ Error should show: "Phone must be E.164 format (e.g., +91XXXXXXXXXX)"
4. Enter: `+919876543210`
5. ✅ Account should be created successfully

## 🔧 Troubleshooting

### Map not showing?
**Check console for errors:**
```javascript
// Open browser DevTools (F12) → Console tab
// Look for errors like:
// "Google Maps JavaScript API error: ApiNotActivatedMapError"
```
**Solutions:**
- Enable Maps JavaScript API in Cloud Console
- Enable Places API in Cloud Console
- Check API key is correct
- Verify no extra spaces in API key

### Autocomplete not working?
**Check:**
1. `&libraries=places` is in script tag
2. Places API is enabled in Cloud Console
3. You're using http:// not file:// protocol
4. Browser console for JavaScript errors

### "RefererNotAllowedMapError"?
**Your API key is restricted**
**Solutions:**
- Add your domain to HTTP referrers in Cloud Console
- Or temporarily remove restrictions for testing

## 📝 What Changed?

### Frontend (index.html)
- ✅ Specialty dropdown (17 options)
- ✅ Auto-username generation function
- ✅ Phone validation (E.164 format)
- ✅ Google Places Autocomplete integration
- ✅ Interactive map preview with draggable marker
- ✅ Inline error validation

### Backend (backend/api.py)
- ✅ Added fields to `UserSignup` model:
  - `phone: Optional[str]`
  - `clinicLat: Optional[float]`
  - `clinicLng: Optional[float]`
  - `clinicPlaceId: Optional[str]`
- ✅ Updated `/api/doctors/signup` endpoint to store new fields

### No Changes To:
- ❌ Patient signup flow (untouched)
- ❌ Doctor login flow (untouched)
- ❌ Symptom checker (untouched)
- ❌ Dashboard pages (untouched)

## 🎯 Feature Highlights

| Feature | Description | Required? |
|---------|-------------|-----------|
| **Auto-Username** | Generates from name: `john-doe`, `johndoe`, `john.doe` | ✅ Always active |
| **Specialty Dropdown** | 17 medical specialties | ✅ Required field |
| **Phone Validation** | E.164 format: `+91XXXXXXXXXX` | ⚪ Optional |
| **Maps Autocomplete** | Type clinic name, get suggestions | ⚪ Needs API key |
| **Map Preview** | Visual location picker with draggable marker | ⚪ Needs API key |
| **Inline Errors** | All validation shown below form | ✅ Always active |

## 📦 No Additional Dependencies

- ✅ Pure vanilla JavaScript (no React, Vue, etc.)
- ✅ No npm packages required
- ✅ No build step needed
- ✅ Just add Google Maps API key and go!

## 🔒 Production Notes

⚠️ **Before deploying to production:**

1. **Hash passwords** - Currently stored in plaintext (demo only)
   ```javascript
   // Use bcrypt or similar
   const hashedPassword = await bcrypt.hash(password, 10);
   ```

2. **Secure API key** - Don't commit to Git
   ```bash
   # Add to .gitignore
   echo "*.env" >> .gitignore
   
   # Use environment variable
   const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
   ```

3. **Enable HTTPS** - Google Maps requires secure context
   ```nginx
   # Use Let's Encrypt or Cloudflare SSL
   ```

4. **Rate limiting** - Prevent API abuse
   ```python
   # Add to FastAPI
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   ```

## 💡 Usage Tips

1. **Leave username blank** for best auto-generation results
2. **Use autocomplete** instead of typing full address
3. **Drag marker** to adjust exact clinic entrance location
4. **Phone is optional** but recommended for appointment confirmations
5. **Select specialty carefully** - affects patient recommendations

## 🐛 Known Limitations

1. Map preview requires internet connection (Google Maps API)
2. Autocomplete works best with well-known locations
3. Username generation may use random suffix for common names
4. Phone validation strict - must include country code (+91)

## 📚 Full Documentation

See `DOCTOR_SIGNUP_DOCUMENTATION.md` for:
- Complete API reference
- All test scenarios (10 test cases)
- Implementation details
- Security considerations
- Future enhancement ideas

## ❓ Need Help?

**Common Issues:**

Q: Map shows but no autocomplete?
A: Check `&libraries=places` in script tag

Q: Username keeps adding numbers?
A: Name collision - try different name or enter custom username

Q: Phone validation failing?
A: Must start with + and country code (e.g., +91)

Q: Map not loading at all?
A: Check API key, enable Maps JavaScript API in Cloud Console

---

**Ready to test?** 🎉
1. Add your API key to line 161 of index.html
2. Open in browser (via local server recommended)
3. Click "I am a Doctor" → "Create Account"
4. Start typing in "Clinic / Location" field
5. See the magic happen! ✨
