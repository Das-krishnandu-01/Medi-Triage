# Code Review Checklist - 10 MCQ Symptom Checker

## Reviewer Information
- **Reviewer Name:** _______________
- **Review Date:** _______________
- **PR Number:** _______________

---

## ⚡ Quick Review (5 minutes)

### 1. Check Files Modified
- [ ] Only 2 files modified: `index.html` and `backend/api.py`
- [ ] No changes to other core files (app.js, styles.css, etc.)
- [ ] All new files are tests or documentation

### 2. Run Automated Tests
```bash
# Unit tests (30 seconds)
pytest backend/test_symptom_mapping.py -v

# Integration tests (2 minutes) - backend must be running
PowerShell -ExecutionPolicy Bypass -File backend/test_symptom_api.ps1
```
- [ ] All 13 unit tests PASS
- [ ] All 10 integration tests PASS

### 3. Quick Manual Test
- [ ] Start backend: `python backend/api.py`
- [ ] Open frontend in browser
- [ ] Go to Symptom Checker → Start 10 MCQ
- [ ] Answer all 10 questions
- [ ] Verify recommendations appear
- [ ] Click "Open in Maps" → Correct location opens

**If all above ✅ → Approve for merge**

---

## 🔍 Detailed Code Review (20 minutes)

### Frontend Changes (`index.html`)

#### Lines 742-780: New 10 MCQs Implementation
- [ ] All 10 questions present with exact text as specified
- [ ] Each question has exactly 3 options
- [ ] Options match requirements exactly
- [ ] No typos in question text
- [ ] answerKey correctly set (q1-q10)

**Review Code:**
```javascript
const standardQuestions = [
  {q:'Where is your main problem located?', opts:['Head / face / ears / nose / throat','Chest / breathing / heart','Arms / legs / joints / back'], answerKey:'q1'},
  // ... verify all 10
];
```

#### Lines 780-850: Scoring Algorithm
- [ ] All specialties initialized (GP, ENT, Cardiology, etc.)
- [ ] Q1-Q10 mappings match specification table
- [ ] Score increments correct (+2 for strong indicators, +1 for supportive)
- [ ] Top specialties selected with score >= 2
- [ ] Default to GP if no specialty reaches threshold
- [ ] Max 3 specialties enforced

**Spot Check:**
```javascript
// Q1 mapping
if (answers[0] === 'Head / face / ears / nose / throat') {
  scores.ENT += 2;        // ✓ Correct
  scores.Neurology += 1;  // ✓ Correct
}
```

#### Lines 850-950: API Integration & UI
- [ ] API endpoint URL correct: `http://localhost:8000/api/symptom-recommendations`
- [ ] Request body structure matches API contract
- [ ] Try-catch handles errors gracefully
- [ ] Client-side fallback works if API fails
- [ ] Recommendations display correctly
- [ ] Google Maps links use correct format (place_id or lat,lng)
- [ ] All doctor fields displayed (name, phone, address)
- [ ] No XSS vulnerabilities (safe HTML rendering)

**Security Check:**
```javascript
// Verify no innerHTML with user input
// Should use textContent or createElement
```

### Backend Changes (`backend/api.py`)

#### Lines 360-420: Scoring Algorithm (Backend)
- [ ] Same logic as frontend (consistency check)
- [ ] All 10 specialties included
- [ ] Scoring matches specification table
- [ ] Type hints correct (`dict`, `List[str]`)
- [ ] Returns list of strings

**Consistency Test:**
```python
# Should match frontend algorithm exactly
# Test same input → same output on both sides
```

#### Lines 422-440: Distance Calculation
- [ ] Haversine formula mathematically correct
- [ ] Handles None/missing lat/lng gracefully
- [ ] Returns distance in km (not miles)
- [ ] No division by zero errors

#### Lines 442-480: Doctor Filtering
- [ ] Loads doctors.json correctly
- [ ] Handles file not found (try-except)
- [ ] Case-insensitive specialty matching (or exact match documented)
- [ ] Distance calculated for all doctors
- [ ] Sorted by distance correctly
- [ ] Limit enforced (top 5 doctors)
- [ ] Returns dict with specialty as key

#### Lines 482-540: API Endpoint
- [ ] Endpoint path correct: `/api/symptom-recommendations`
- [ ] HTTP method: POST (not GET)
- [ ] Request model validated (Pydantic)
- [ ] Response model correct structure
- [ ] Error handling present (try-except)
- [ ] Privacy-compliant logging (no patient data)
- [ ] Returns 200 on success, 500 on error

**Privacy Audit:**
```python
# Line ~540: Should NOT log full answers
print(f"Error in symptom_recommendations: {str(e)}")  # ✅ OK
# NOT: print(f"Answers: {data.answers}")  # ❌ BAD
```

---

## 🧪 Test Coverage Review

### Unit Tests (`backend/test_symptom_mapping.py`)
- [ ] Tests all 10 specialties individually
- [ ] Tests multiple specialties scenario
- [ ] Tests default to GP
- [ ] Tests max 3 specialties limit
- [ ] Tests edge cases (missing answers)
- [ ] All tests have clear names
- [ ] All tests have assertions
- [ ] No flaky tests

**Run Tests:**
```bash
pytest backend/test_symptom_mapping.py -v --tb=short
```

### Integration Tests (`backend/test_symptom_api.ps1`)
- [ ] Tests all 10 specialty scenarios
- [ ] Tests with/without patient location
- [ ] Tests API response structure
- [ ] Tests required fields present (name, phone, address, lat, lng)
- [ ] Clear pass/fail output
- [ ] Error messages informative

**Run Tests:**
```bash
PowerShell -ExecutionPolicy Bypass -File backend/test_symptom_api.ps1
```

---

## 📝 Documentation Review

### `README_SYMPTOM_CHECKER.md`
- [ ] Clearly explains the feature
- [ ] API contract documented
- [ ] All 10 MCQs listed
- [ ] Scoring algorithm explained
- [ ] Google Maps integration documented
- [ ] Privacy policy stated
- [ ] Examples provided

### `QA_SYMPTOM_CHECKER.md`
- [ ] All 5 ACs covered
- [ ] Step-by-step test instructions
- [ ] Expected results stated
- [ ] Pass/fail criteria clear

### `IMPLEMENTATION_SUMMARY.md`
- [ ] Accurate summary of changes
- [ ] Files modified listed
- [ ] Testing status correct
- [ ] Metrics accurate

---

## 🔒 Security Review

### Privacy Compliance
- [ ] No patient answers stored in database
- [ ] No patient identifiable info in logs
- [ ] No sensitive data in error messages
- [ ] sessionStorage used (not localStorage for medical data)

### Code Security
- [ ] No SQL injection vulnerabilities (uses JSON file, not SQL)
- [ ] No XSS vulnerabilities (safe HTML rendering)
- [ ] No hardcoded secrets
- [ ] No eval() or Function() used
- [ ] Input validation on backend (Pydantic models)

### API Security
- [ ] CORS configured correctly
- [ ] No authentication bypass
- [ ] Rate limiting considered (if needed)

---

## 🚫 Breaking Changes Check

### Verify No Regressions
- [ ] Run existing patient signup flow → Works
- [ ] Run existing doctor dashboard flow → Works
- [ ] Run existing booking flow → Works
- [ ] No console errors in browser DevTools
- [ ] No 500 errors in backend logs

### Backward Compatibility
- [ ] Old symptom checker behavior replaced (intentional)
- [ ] No API version breaking changes
- [ ] No database migrations required
- [ ] No new dependencies added to requirements.txt

---

## 📊 Performance Review

### Frontend Performance
- [ ] No long-running loops
- [ ] No memory leaks (check DevTools)
- [ ] Page renders < 100ms after API response
- [ ] No unnecessary re-renders

### Backend Performance
- [ ] API responds < 500ms (typical)
- [ ] No N+1 queries (uses in-memory JSON)
- [ ] Distance calculation efficient (single pass)
- [ ] doctors.json loaded once (not per request)

**Test:**
```bash
Measure-Command { Invoke-RestMethod ... }
# Should be < 500ms
```

---

## 🎯 Acceptance Criteria Final Verification

### AC1: All 10 MCQs Display
- [ ] Manual test: Navigate through all 10 questions
- [ ] Verify answers persist on back navigation
- [ ] Verify progress bar updates
- [ ] Verify can't proceed without answer

### AC2: Backend Returns Recommendations
- [ ] API returns specialties array
- [ ] API returns 1-5 doctors per specialty
- [ ] Doctors have all required fields
- [ ] Distance calculated if location provided

### AC3: Google Maps Accurate
- [ ] Manually click "Open in Maps" for 3 doctors
- [ ] Verify correct location opens
- [ ] Verify URL format (place_id or lat,lng)
- [ ] Verify pin is accurate

### AC4: No Side Effects
- [ ] Git diff shows only 2 files modified
- [ ] Test other flows (dashboard, auth, booking)
- [ ] No unexpected UI changes

### AC5: Privacy Compliance
- [ ] Audit server logs (no patient data)
- [ ] Check browser console (no sensitive data)
- [ ] Review code (no public logging of answers)

---

## ✅ Final Decision

### Code Quality
- [ ] **EXCELLENT** - Well-structured, documented
- [ ] **GOOD** - Acceptable with minor notes
- [ ] **NEEDS WORK** - Request changes

### Test Coverage
- [ ] **EXCELLENT** - Comprehensive (23/23 tests)
- [ ] **GOOD** - Adequate coverage
- [ ] **NEEDS WORK** - Insufficient tests

### Documentation
- [ ] **EXCELLENT** - Complete and clear
- [ ] **GOOD** - Acceptable
- [ ] **NEEDS WORK** - Incomplete

### Risk Assessment
- [ ] **LOW** - Safe to merge (recommended)
- [ ] **MEDIUM** - Merge with monitoring
- [ ] **HIGH** - Do not merge

---

## 📝 Review Notes

**What I Liked:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Concerns / Questions:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Required Changes Before Merge:**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Optional Improvements (can be done later):**
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

## 🎉 Final Approval

- [ ] **APPROVE** - Merge immediately
- [ ] **APPROVE WITH COMMENTS** - Merge but address notes in follow-up
- [ ] **REQUEST CHANGES** - Do not merge until changes made

**Reviewer Signature:** _______________  
**Date:** _______________

---

## 📋 Post-Merge Checklist (for merger)

- [ ] Verify CI/CD pipeline passes
- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Monitor backend logs for errors
- [ ] Monitor API response times
- [ ] Check user feedback (if available)
- [ ] Schedule follow-up review in 1 week

---

**Review Time Estimate:**
- Quick Review: 5 minutes
- Detailed Review: 20 minutes
- Full Review with Testing: 30 minutes
