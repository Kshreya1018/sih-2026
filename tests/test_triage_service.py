# Unit tests for triage service and safety rules
import json
from unittest.mock import patch
from app.services.safety_rules import check_red_flags, apply_safety_override
from app.services.triage_service import classify_problem, DEFAULT_FALLBACK_TRIAGE


def test_safety_rules_detection():
    assert check_red_flags("I have severe chest pain and can't breathe") is True
    assert check_red_flags("Patient is unconscious after trauma") is True
    assert check_red_flags("Possible heart attack or cardiac arrest") is True
    assert check_red_flags("Severe bleeding from head trauma") is True
    assert check_red_flags("I have a minor scrape on my elbow") is False
    assert check_red_flags("Looking for vitamin C supplements") is False


def test_safety_rules_override():
    assert apply_safety_override("severe chest pain", "normal") == "high"
    assert apply_safety_override("shortness of breath", "normal") == "high"
    assert apply_safety_override("minor papercut", "normal") == "normal"
    assert apply_safety_override("minor papercut", "high") == "high"


def test_classify_problem_llm_none_fallback():
    with patch("app.services.triage_service.call_groq_triage", return_value=None):
        res = classify_problem("I have a mild rash on my arm")
        assert res == DEFAULT_FALLBACK_TRIAGE


def test_classify_problem_groq_success_doctor():
    groq_json = json.dumps({
        "needs": "doctor",
        "specialty": "Dermatology",
        "urgency": "normal"
    })
    with patch("app.services.triage_service.call_groq_triage", return_value=groq_json):
        res = classify_problem("Itchy red bumps on my arm")
        assert res["needs"] == "doctor"
        assert res["specialty"] == "Dermatology"
        assert res["urgency"] == "normal"


def test_classify_problem_groq_success_medical_store():
    groq_json = json.dumps({
        "needs": "medical_store",
        "specialty": "Pharmacy",
        "urgency": "normal"
    })
    with patch("app.services.triage_service.call_groq_triage", return_value=groq_json):
        res = classify_problem("Bandages and paracetamol")
        # medical_store must be normalized to doctor
        assert res["needs"] == "doctor"
        assert res["specialty"] == "Pharmacy"
        assert res["urgency"] == "normal"


def test_classify_problem_groq_normalization_and_unknowns():
    # Needs is not in allowed set (falls back to hospital)
    # Urgency is unknown (falls back to normal)
    # Specialty is empty (falls back to General Medicine)
    groq_json = json.dumps({
        "needs": "spaceship_clinic",
        "specialty": "   ",
        "urgency": "super_critical"
    })
    with patch("app.services.triage_service.call_groq_triage", return_value=groq_json):
        res = classify_problem("Something weird happened")
        assert res["needs"] == "hospital"
        assert res["specialty"] == "General Medicine"
        assert res["urgency"] == "normal"


def test_classify_problem_malformed_json():
    # Non-json string
    with patch("app.services.triage_service.call_groq_triage", return_value="Invalid json format {"):
        res = classify_problem("Help")
        assert res == DEFAULT_FALLBACK_TRIAGE

    # JSON that parses to a list instead of dict
    with patch("app.services.triage_service.call_groq_triage", return_value='["hospital", "General Medicine"]'):
        res = classify_problem("Help")
        assert res == DEFAULT_FALLBACK_TRIAGE

