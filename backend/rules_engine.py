import re

# Regex patterns to catch obvious keywords
RULES = [
    {
        "specialty": "Cardiology",
        "pattern": r"\b(chest pain|heart|palpitations|shortness of breath|breathless)\b",
        "reason": "Rule match: Symptoms describe chest or heart issues."
    },
    {
        "specialty": "Dermatology",
        "pattern": r"\b(rash|itch|skin|acne|blister|spots|eczema|redness)\b",
        "reason": "Rule match: Symptoms describe skin issues."
    },
    {
        "specialty": "Orthopedics",
        "pattern": r"\b(joint|knee|back pain|bone|fracture|sprain|muscle|stiffness|swelling)\b",
        "reason": "Rule match: Symptoms describe bone, joint, or muscle issues."
    },
    {
        "specialty": "Neurology",
        "pattern": r"\b(headache|numbness|seizure|stroke|paralysis|tremor|vision loss|dizziness)\b",
        "reason": "Rule match: Symptoms describe neurological issues."
    },
    {
        "specialty": "Pediatrics",
        "pattern": r"\b(child|infant|baby|toddler)\b",
        "reason": "Rule match: Patient is described as a child/infant."
    },
    {
        "specialty": "Gynecology",
        "pattern": r"\b(period|menstrual|pregnancy|pregnant|vaginal|pelvic)\b",
        "reason": "Rule match: Symptoms describe gynecological issues."
    },
    {
        "specialty": "Psychiatry",
        "pattern": r"\b(anxiety|depression|sad|panic|suicidal|mood|fear|hallucination)\b",
        "reason": "Rule match: Symptoms describe mental health issues."
    }
]

DEFAULT_SPECIALTY = "General Medicine"

def combine_ml_and_rules(ml_specialty, ml_confidence, symptoms_text, threshold=0.55):
    """
    Decides between ML prediction and Rule-based match.
    """
    text_lower = symptoms_text.lower()
    
    # 1. Check for Rule Match
    rule_match = None
    rule_reason = ""
    
    for rule in RULES:
        if re.search(rule["pattern"], text_lower):
            rule_match = rule["specialty"]
            rule_reason = rule["reason"]
            break # Stop at first match
            
    # 2. Decision Logic
    
    # CASE A: ML is very confident (>= threshold)
    if ml_confidence >= threshold:
        reason = f"ML Prediction (Confidence: {ml_confidence:.2f})"
        if rule_match and rule_match != ml_specialty:
            reason += f" [Note: Rule matched {rule_match}, but ML confidence was high]"
        return ml_specialty, ml_confidence, reason

    # CASE B: ML is unsure, but Rule matched
    if rule_match:
        reason = f"Rule Prediction (ML confidence {ml_confidence:.2f} was too low). {rule_reason}"
        return rule_match, ml_confidence, reason

    # CASE C: ML unsure, No Rule matched -> Default to ML or General Medicine
    reason = f"Low confidence ML ({ml_confidence:.2f}) and no rules matched."
    return ml_specialty, ml_confidence, reason
