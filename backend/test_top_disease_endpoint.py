"""
Integration tests for /api/symptom/top-disease endpoint
Tests the complete flow: answers → disease mapping → doctor filtering → distance sorting
"""

import sys
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_without_location():
    """Test endpoint returns top disease and doctors without location"""
    print("Testing: POST /api/symptom/top-disease (no location)")
    
    payload = {
        "answers": {
            "q1": "a",  # Head/throat
            "q3": "a",  # High fever
            "q5": "a",  # Severe ENT symptoms
            "q2": "b", "q4": "c", "q6": "c", "q7": "c", "q8": "c", "q9": "c", "q10": "c"
        },
        "location": None
    }
    
    response = requests.post(f"{BASE_URL}/api/symptom/top-disease", json=payload)
    
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    
    data = response.json()
    assert data['ok'] == True, "Expected ok=True"
    assert 'topDisease' in data, "Missing topDisease in response"
    assert 'doctors' in data, "Missing doctors in response"
    
    disease = data['topDisease']
    assert disease['code'] == 'ACUTE_PHARYNGITIS', f"Expected ACUTE_PHARYNGITIS but got {disease['code']}"
    assert disease['specialty'] == 'ENT', f"Expected ENT specialty"
    assert disease['confidence'] > 0.5, "Confidence should be > 0.5 for clear symptoms"
    
    # Without location, doctors should not have distance_m field or it should be null
    doctors = data['doctors']
    assert len(doctors) > 0, "Should return at least one ENT doctor"
    assert doctors[0]['specialty'] == 'ENT', "First doctor should be ENT specialist"
    
    print(f"✓ Disease: {disease['name']} ({disease['confidence']*100}% confidence)")
    print(f"✓ Doctors: {len(doctors)} ENT specialists returned")
    print(f"✓ First doctor: {doctors[0]['name']} - {doctors[0]['phone']}")

def test_endpoint_with_location():
    """Test endpoint returns doctors sorted by distance"""
    print("\nTesting: POST /api/symptom/top-disease (with location)")
    
    # Use Kolkata coordinates
    payload = {
        "answers": {
            "q1": "b",  # Chest
            "q6": "a",  # Severe breathing
            "q2": "b", "q3": "b", "q4": "c", "q5": "c", "q7": "c", "q8": "c", "q9": "c", "q10": "c"
        },
        "location": {
            "lat": 22.5726,
            "lng": 88.3639
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/symptom/top-disease", json=payload)
    
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    
    data = response.json()
    assert data['ok'] == True
    
    disease = data['topDisease']
    assert disease['specialty'] == 'Cardiology', "Expected Cardiology for chest symptoms"
    
    doctors = data['doctors']
    assert len(doctors) > 0, "Should return cardiologists"
    
    # Check that doctors have distance_m field
    for doc in doctors:
        assert 'distance_m' in doc, "Doctor should have distance_m field"
        assert isinstance(doc['distance_m'], int), "distance_m should be integer"
    
    # Check that doctors are sorted by distance (ascending)
    distances = [doc['distance_m'] for doc in doctors]
    assert distances == sorted(distances), "Doctors should be sorted by distance (ascending)"
    
    print(f"✓ Disease: {disease['name']} ({disease['specialty']})")
    print(f"✓ Doctors: {len(doctors)} specialists returned")
    print(f"✓ Nearest doctor: {doctors[0]['name']} - {doctors[0]['distance_m']}m away")
    print(f"✓ Farthest doctor: {doctors[-1]['name']} - {doctors[-1]['distance_m']}m away")
    print(f"✓ Distance sorting: VERIFIED (ascending order)")

def test_endpoint_dermatology():
    """Test dermatology disease detection"""
    print("\nTesting: Dermatology disease detection")
    
    payload = {
        "answers": {
            "q4": "a",  # Rash
            "q2": "c",  # Burning/tingling
            "q1": "c", "q3": "c", "q5": "c", "q6": "c", "q7": "c", "q8": "c", "q9": "c", "q10": "c"
        },
        "location": None
    }
    
    response = requests.post(f"{BASE_URL}/api/symptom/top-disease", json=payload)
    data = response.json()
    
    disease = data['topDisease']
    assert disease['code'] == 'CONTACT_DERMATITIS', f"Expected CONTACT_DERMATITIS but got {disease['code']}"
    assert disease['specialty'] == 'Dermatology'
    
    doctors = data['doctors']
    assert all(doc['specialty'] == 'Dermatology' for doc in doctors), "All doctors should be dermatologists"
    
    print(f"✓ Disease: {disease['name']}")
    print(f"✓ Specialty filter: {len(doctors)} Dermatology specialists")

def test_endpoint_gp_fallback():
    """Test GP fallback for unclear symptoms"""
    print("\nTesting: GP fallback for unclear symptoms")
    
    payload = {
        "answers": {
            "q1": "d", "q2": "d", "q3": "c", "q4": "c", "q5": "c",
            "q6": "c", "q7": "c", "q8": "c", "q9": "c", "q10": "b"
        },
        "location": None
    }
    
    response = requests.post(f"{BASE_URL}/api/symptom/top-disease", json=payload)
    data = response.json()
    
    disease = data['topDisease']
    assert disease['code'] == 'GENERAL_MALAISE'
    assert disease['specialty'] == 'GP'
    assert disease['confidence'] < 0.5
    
    doctors = data['doctors']
    assert all(doc['specialty'] == 'GP' for doc in doctors), "All doctors should be GPs"
    
    print(f"✓ Disease: {disease['name']} (low confidence)")
    print(f"✓ Specialty: GP (fallback)")
    print(f"✓ Doctors: {len(doctors)} general practitioners")

def test_endpoint_response_structure():
    """Test that response has correct structure"""
    print("\nTesting: Response structure validation")
    
    payload = {
        "answers": {"q1": "a", "q2": "a", "q3": "a", "q4": "a", "q5": "a",
                   "q6": "a", "q7": "a", "q8": "a", "q9": "a", "q10": "a"},
        "location": {"lat": 22.5, "lng": 88.3}
    }
    
    response = requests.post(f"{BASE_URL}/api/symptom/top-disease", json=payload)
    data = response.json()
    
    # Check top-level structure
    assert 'ok' in data
    assert 'topDisease' in data
    assert 'doctors' in data
    
    # Check topDisease structure
    disease = data['topDisease']
    assert 'code' in disease
    assert 'name' in disease
    assert 'specialty' in disease
    assert 'confidence' in disease
    assert 'notes' in disease
    
    # Check doctor structure
    if len(data['doctors']) > 0:
        doctor = data['doctors'][0]
        assert 'name' in doctor
        assert 'specialty' in doctor
        assert 'phone' in doctor
        assert 'address' in doctor
        assert 'lat' in doctor
        assert 'lng' in doctor
        assert 'google_place_id' in doctor or 'place_id' in doctor
        assert 'distance_m' in doctor
    
    print(f"✓ Response structure: VALID")
    print(f"✓ All required fields present")

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("  TOP DISEASE ENDPOINT INTEGRATION TESTS")
    print("  (Requires backend server running on port 8000)")
    print("="*60 + "\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Server is running at {BASE_URL}\n")
    except requests.ConnectionError:
        print(f"✗ ERROR: Server not running at {BASE_URL}")
        print(f"  Please start the backend server first:")
        print(f"  cd backend && python api.py")
        return False
    
    tests = [
        test_endpoint_without_location,
        test_endpoint_with_location,
        test_endpoint_dermatology,
        test_endpoint_gp_fallback,
        test_endpoint_response_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"  RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
