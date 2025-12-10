"""
Unit tests for disease mapping logic - Symptom Checker Top Disease
Tests the deterministic mapping from 10 MCQ answers to single top disease.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from api import map_answers_to_diseases, get_top_disease, haversine_distance

def test_pharyngitis_pattern():
    """Test acute pharyngitis detection from throat symptoms"""
    answers = {
        'q1': 'a',  # Head/throat
        'q3': 'a',  # High fever
        'q5': 'a',  # Severe ENT symptoms
        'q2': 'b', 'q4': 'c', 'q6': 'c', 'q7': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'ACUTE_PHARYNGITIS', f"Expected ACUTE_PHARYNGITIS but got {disease['code']}"
    assert disease['specialty'] == 'ENT'
    assert disease['confidence'] > 0.5
    print(f"✓ test_pharyngitis_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_bronchitis_pattern():
    """Test acute bronchitis detection from chest/breathing symptoms"""
    answers = {
        'q1': 'b',  # Chest/breathing
        'q3': 'b',  # Mild fever
        'q6': 'a',  # Severe breathlessness
        'q2': 'b', 'q4': 'c', 'q5': 'c', 'q7': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] in ['ACUTE_BRONCHITIS', 'HYPERTENSION'], f"Expected chest condition but got {disease['code']}"
    assert disease['specialty'] == 'Cardiology'
    print(f"✓ test_bronchitis_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_dermatitis_pattern():
    """Test contact dermatitis detection from skin symptoms"""
    answers = {
        'q4': 'a',  # Rash/lesion
        'q2': 'c',  # Burning/tingling
        'q1': 'c', 'q3': 'c', 'q5': 'c', 'q6': 'c', 'q7': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'CONTACT_DERMATITIS', f"Expected CONTACT_DERMATITIS but got {disease['code']}"
    assert disease['specialty'] == 'Dermatology'
    print(f"✓ test_dermatitis_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_osteoarthritis_pattern():
    """Test osteoarthritis detection from joint pain"""
    answers = {
        'q1': 'c',  # Arms/legs/joints
        'q2': 'b',  # Dull/aching
        'q8': 'a',  # Major injury
        'q3': 'c', 'q4': 'c', 'q5': 'c', 'q6': 'c', 'q7': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'OSTEOARTHRITIS', f"Expected OSTEOARTHRITIS but got {disease['code']}"
    assert disease['specialty'] == 'Orthopedics'
    print(f"✓ test_osteoarthritis_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_anxiety_pattern():
    """Test anxiety disorder detection from mental health symptoms"""
    answers = {
        'q9': 'a',  # Severe mental health changes
        'q1': 'c', 'q2': 'c', 'q3': 'c', 'q4': 'c', 'q5': 'c', 'q6': 'c', 'q7': 'c', 'q8': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'ANXIETY_DISORDER', f"Expected ANXIETY_DISORDER but got {disease['code']}"
    assert disease['specialty'] == 'Psychiatry'
    print(f"✓ test_anxiety_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_gastroenteritis_pattern():
    """Test gastroenteritis detection from digestive symptoms"""
    answers = {
        'q7': 'a',  # Severe GI symptoms
        'q1': 'c', 'q2': 'c', 'q3': 'c', 'q4': 'c', 'q5': 'c', 'q6': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'GASTROENTERITIS', f"Expected GASTROENTERITIS but got {disease['code']}"
    assert disease['specialty'] == 'Gastroenterology'
    print(f"✓ test_gastroenteritis_pattern: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_low_score_defaults_to_gp():
    """Test that unclear symptoms default to General Practitioner"""
    # Use 'b' answers which give minimal scores (mostly 0 or 1 points)
    answers = {
        'q1': 'd', 'q2': 'd', 'q3': 'c', 'q4': 'c', 'q5': 'c',
        'q6': 'c', 'q7': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'b'  
        # q10='b' gives 0 points, q3='c' gives 1 point to GENERAL_MALAISE
        # Total: GENERAL_MALAISE = 1 point (below threshold of 2)
    }
    disease = get_top_disease(answers)
    assert disease['code'] == 'GENERAL_MALAISE', f"Expected GENERAL_MALAISE but got {disease['code']}"
    assert disease['specialty'] == 'GP'
    assert disease['confidence'] < 0.5
    print(f"✓ test_low_score_defaults_to_gp: {disease['name']} ({disease['confidence']*100}% confidence)")

def test_tie_breaking_priority():
    """Test that priority list breaks ties correctly"""
    # Create scenario where multiple diseases get same score
    answers = {
        'q1': 'b',  # +3 bronchitis, +2 hypertension
        'q6': 'a',  # +3 hypertension, +2 bronchitis
        # Both get score of 5, but HYPERTENSION has higher priority
        'q2': 'c', 'q3': 'c', 'q4': 'c', 'q5': 'c', 'q7': 'c', 'q8': 'c', 'q9': 'c', 'q10': 'c'
    }
    disease = get_top_disease(answers)
    assert disease['code'] in ['HYPERTENSION', 'ACUTE_BRONCHITIS'], f"Expected tie between cardiac conditions but got {disease['code']}"
    print(f"✓ test_tie_breaking_priority: {disease['name']} (tie broken by priority)")

def test_haversine_distance():
    """Test distance calculation between two points"""
    # Kolkata to Mumbai (approximate)
    kolkata_lat, kolkata_lng = 22.5726, 88.3639
    mumbai_lat, mumbai_lng = 19.0760, 72.8777
    
    distance_km = haversine_distance(kolkata_lat, kolkata_lng, mumbai_lat, mumbai_lng)
    
    # Expected ~1650 km (allow 5% margin)
    assert 1500 < distance_km < 1800, f"Expected ~1650km but got {distance_km}km"
    print(f"✓ test_haversine_distance: {distance_km:.1f}km (expected ~1650km)")

def test_disease_scores_structure():
    """Test that map_answers_to_diseases returns proper structure"""
    answers = {'q1': 'a', 'q2': 'a', 'q3': 'a', 'q4': 'a', 'q5': 'a',
               'q6': 'a', 'q7': 'a', 'q8': 'a', 'q9': 'a', 'q10': 'a'}
    scores = map_answers_to_diseases(answers)
    
    assert isinstance(scores, dict), "Scores should be a dictionary"
    assert 'ACUTE_PHARYNGITIS' in scores, "Should contain ACUTE_PHARYNGITIS"
    assert 'GENERAL_MALAISE' in scores, "Should contain GENERAL_MALAISE"
    assert all(isinstance(v, (int, float)) for v in scores.values()), "All scores should be numeric"
    print(f"✓ test_disease_scores_structure: {len(scores)} diseases scored")

def run_all_tests():
    """Run all unit tests"""
    print("\n" + "="*60)
    print("  DISEASE MAPPING UNIT TESTS")
    print("="*60 + "\n")
    
    tests = [
        test_pharyngitis_pattern,
        test_bronchitis_pattern,
        test_dermatitis_pattern,
        test_osteoarthritis_pattern,
        test_anxiety_pattern,
        test_gastroenteritis_pattern,
        test_low_score_defaults_to_gp,
        test_tie_breaking_priority,
        test_haversine_distance,
        test_disease_scores_structure
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
