# 10 MCQ Symptom Checker - QA Test Checklist

## Priority: High — Minimal Scope / Zero Side-Effects

**Test Date:** _______________  
**Tester:** _______________  
**Environment:** Local / Staging / Production (circle one)

---

## Pre-Test Setup

- [ ] Backend server running on `http://localhost:8000`
- [ ] Frontend accessible at local file path or server
- [ ] `doctors.json` file exists in `backend/` folder
- [ ] Patient account created for testing

---

## AC1: All 10 MCQs Display and Navigation Works

### Test 1.1: Start 10 MCQ Flow
- [ ] **Action:** Open patient page → Symptom checker → Enter symptom → Click "Start 10 MCQ"
- [ ] **Expected:** Test page loads with Question 1 of 10
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 1.2: All 10 Questions Display Correctly
For each question (1-10), verify:
- [ ] **Q1:** "Where is your main problem located?" with 3 options
- [ ] **Q2:** "Which best describes the pain?" with 3 options
- [ ] **Q3:** "Any fever or signs of infection?" with 3 options
- [ ] **Q4:** "Any recent skin changes (rash, bump, ulcer)?" with 3 options
- [ ] **Q5:** "Any problems with hearing, voice, or swallowing?" with 3 options
- [ ] **Q6:** "Any shortness of breath, chest pain, or palpitations?" with 3 options
- [ ] **Q7:** "Any digestive symptoms (abdominal pain, vomiting, blood in stool)?" with 3 options
- [ ] **Q8:** "Any recent injury or trauma to the affected area?" with 3 options
- [ ] **Q9:** "Any mood / sleep / concentration changes recently?" with 3 options
- [ ] **Q10:** "Are you pregnant or could you be pregnant? (if applicable)" with 3 options

### Test 1.3: Answer Selection Works
- [ ] **Action:** Click on each option for Q1
- [ ] **Expected:** Selected option highlights/shows as selected
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 1.4: Forward Navigation
- [ ] **Action:** Answer Q1, click "Next"
- [ ] **Expected:** Q2 displays
- [ ] **Action:** Continue through all 10 questions
- [ ] **Expected:** Progress bar updates, question number changes
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 1.5: Backward Navigation (Answer Persistence)
- [ ] **Action:** Answer Q1 (select option A), Q2 (select option B), then click "Prev"
- [ ] **Expected:** Returns to Q1 with option A still selected
- [ ] **Action:** Click "Next" again
- [ ] **Expected:** Q2 displays with option B still selected
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 1.6: Save & Exit
- [ ] **Action:** Answer first 3 questions, click "Save & Exit"
- [ ] **Expected:** Returns to main symptom page, progress saved message shown
- [ ] **Action:** Click "Start 10 MCQ" again
- [ ] **Expected:** Resumes at Q4 (or Q1 if resume not implemented - document behavior)
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 1.7: Cannot Proceed Without Answering
- [ ] **Action:** On Q1, do NOT select any option, click "Next"
- [ ] **Expected:** Alert/message shown: "Please select an option"
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## AC2: Recommendations Returned from Backend

### Test 2.1: Backend API Called on Submit
- [ ] **Action:** Answer all 10 questions, click "Finish"
- [ ] **Action:** Open browser DevTools → Network tab
- [ ] **Expected:** POST request to `http://localhost:8000/api/symptom-recommendations`
- [ ] **Expected:** Request body contains `answers` object with q1-q10 and `patientLocation`
- [ ] **Expected:** Response status 200 OK
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.2: Specialties Returned
- [ ] **Action:** Check API response in Network tab
- [ ] **Expected:** Response contains `specialties` array (e.g., ["ENT", "Cardiology"])
- [ ] **Expected:** Response contains `recommendations` array
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.3: Doctor Recommendations Displayed
- [ ] **Action:** After submitting answers, check UI
- [ ] **Expected:** Page shows "Suggested Specialty: [Specialty Names]"
- [ ] **Expected:** List of 1-5 doctors displayed per specialty
- [ ] **Expected:** Each doctor shows: Name, Phone, Address
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.4: Mapping Logic - ENT Symptoms
- [ ] **Action:** Answer Q1=a (Head/throat), Q5=a (Hearing loss)
- [ ] **Expected:** ENT specialty recommended
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.5: Mapping Logic - Cardiology Symptoms
- [ ] **Action:** Answer Q1=b (Chest/breathing), Q6=a (Severe breathlessness)
- [ ] **Expected:** Cardiology specialty recommended
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.6: Mapping Logic - Orthopedics Symptoms
- [ ] **Action:** Answer Q1=c (Arms/legs/joints), Q8=a (Major injury)
- [ ] **Expected:** Orthopedics specialty recommended
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.7: Mapping Logic - Dermatology Symptoms
- [ ] **Action:** Answer Q4=a (Rash/lesion)
- [ ] **Expected:** Dermatology specialty recommended
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.8: Mapping Logic - Multiple Specialties
- [ ] **Action:** Answer Q1=a (Head), Q3=a (High fever), Q5=a (Hearing loss)
- [ ] **Expected:** Multiple specialties returned (ENT, Infectious Diseases, etc.)
- [ ] **Expected:** Max 3 specialties shown
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 2.9: Fallback to GP
- [ ] **Action:** Answer all questions with "No" options (c for most)
- [ ] **Expected:** GP (General Practitioner) recommended as fallback
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## AC3: Google Maps Integration Works

### Test 3.1: Google Maps Link Present
- [ ] **Action:** Check doctor card in recommendations
- [ ] **Expected:** "📍 Open in Maps" button/link visible
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 3.2: Google Maps Link Opens Correct Location
- [ ] **Action:** Click "📍 Open in Maps" for first doctor
- [ ] **Expected:** Opens Google Maps in new tab
- [ ] **Expected:** Shows doctor's location on map with correct pin
- [ ] **Expected:** Address matches doctor's address
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 3.3: Verify lat/lng or place_id Used
- [ ] **Action:** Inspect Maps URL (should be `place_id:XXX` or `query=LAT,LNG`)
- [ ] **Expected:** URL contains either `place_id` or lat/lng coordinates
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 3.4: Multiple Doctors Have Maps Links
- [ ] **Action:** Verify each doctor in list has Maps link
- [ ] **Expected:** All doctors have working Maps links
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## AC4: No Code Outside Symptom Checker Changed

### Test 4.1: Files Changed Verification
- [ ] **Action:** Review file changes (git diff or file list)
- [ ] **Expected:** Only these files modified:
  - `index.html` (lines ~740-900, symptom checker section only)
  - `backend/api.py` (added symptom-recommendations endpoint at end)
- [ ] **Expected:** No changes to:
  - Doctor dashboard files
  - Patient dashboard (except symptom checker)
  - Authentication flows
  - Booking flows
  - Database schemas (unless minimal seed data added)
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 4.2: Other Flows Still Work
- [ ] **Action:** Test patient signup/login
- [ ] **Expected:** Works as before
- [ ] **Result:** Pass / Fail

- [ ] **Action:** Test doctor dashboard → Incoming Requests
- [ ] **Expected:** Works as before
- [ ] **Result:** Pass / Fail

- [ ] **Action:** Test booking appointment from doctor list (outside symptom checker)
- [ ] **Expected:** Works as before
- [ ] **Result:** Pass / Fail

### Test 4.3: No Visual Regressions
- [ ] **Action:** Navigate through all major pages (Home, Dashboard, etc.)
- [ ] **Expected:** No UI breaks, styles intact
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## AC5: Privacy & Security

### Test 5.1: No Public Logging of Patient Answers
- [ ] **Action:** Submit answers, check server console/logs
- [ ] **Expected:** Full answers NOT logged publicly
- [ ] **Expected:** Only anonymized data logged (e.g., specialty tags, request ID)
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 5.2: No Sensitive Data in Browser Console
- [ ] **Action:** Open browser console, submit answers
- [ ] **Expected:** No sensitive patient data (full name, medical history) logged
- [ ] **Expected:** Debug logs minimal or scrubbed
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 5.3: Phone Numbers Follow Privacy Rules
- [ ] **Action:** Check displayed doctor phone numbers
- [ ] **Expected:** Phone numbers shown in expected format
- [ ] **Expected:** No raw patient data exposed
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## Edge Cases & Error Handling

### Test 6.1: Backend Offline - Fallback Works
- [ ] **Action:** Stop backend server, submit 10 MCQ answers
- [ ] **Expected:** Frontend shows fallback recommendations (client-side logic)
- [ ] **Expected:** User still sees doctor recommendations
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 6.2: No Doctors in Database for Specialty
- [ ] **Action:** Trigger specialty with no doctors (if possible)
- [ ] **Expected:** Shows message like "No doctors available" or uses demo data
- [ ] **Expected:** No crash or blank screen
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 6.3: Invalid API Response
- [ ] **Action:** Mock invalid API response (if possible)
- [ ] **Expected:** Error handled gracefully, fallback used
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## Performance & UX

### Test 7.1: Response Time
- [ ] **Action:** Submit answers, measure time to show recommendations
- [ ] **Expected:** Recommendations appear within 1-2 seconds
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

### Test 7.2: Mobile Responsiveness (if applicable)
- [ ] **Action:** Open on mobile device or resize browser to mobile width
- [ ] **Expected:** 10 MCQ questions display correctly
- [ ] **Expected:** Buttons/options are tappable
- [ ] **Expected:** Maps links work on mobile
- [ ] **Result:** Pass / Fail
- [ ] **Notes:** _______________

---

## Final Approval

### Summary
- **Total Tests:** _______________
- **Passed:** _______________
- **Failed:** _______________
- **Blocked:** _______________

### Critical Issues Found
1. _______________
2. _______________
3. _______________

### Recommendation
- [ ] **APPROVE** - Ready for production
- [ ] **APPROVE WITH NOTES** - Deploy but monitor
- [ ] **REJECT** - Needs fixes before deployment

**Tester Signature:** _______________  
**Date:** _______________

---

## Notes for Developers

**Files Modified (document exact changes):**
- `index.html`: Lines _____ to _____
- `backend/api.py`: Lines _____ to _____
- Other: _______________

**Regression Risks:**
- Low / Medium / High (circle one)
- Explanation: _______________

**Rollback Plan:**
- Revert commits: _______________
- Restore backup: _______________
