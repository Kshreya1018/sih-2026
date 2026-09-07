# Integration tests for FastAPI endpoints
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "medi-locator-api"
    assert data["version"] == "1.0.0"


def test_find_help_validation_error():
    # Lat must be between -90 and 90, lng between -180 and 180
    response = client.post(
        "/find-help",
        json={"text": "severe headache", "lat": 150.0, "lng": 250.0}
    )
    assert response.status_code == 422

    # Negative bounds error
    response_neg = client.post(
        "/find-help",
        json={"text": "severe headache", "lat": -95.0, "lng": -190.0}
    )
    assert response_neg.status_code == 422


def test_find_help_missing_fields():
    # Missing text and lng
    response = client.post("/find-help", json={"lat": 28.0})
    assert response.status_code == 422

    # Missing all fields
    response_empty = client.post("/find-help", json={})
    assert response_empty.status_code == 422


@patch("app.api.routes.find_help.get_nearby_facilities")
@patch("app.api.routes.find_help.classify_problem")
def test_find_help_success(mock_classify, mock_get_facilities):
    mock_classify.return_value = {
        "needs": "hospital",
        "specialty": "Cardiology",
        "urgency": "high"
    }
    mock_get_facilities.return_value = [
        {
            "name": "City General Hospital",
            "type": "hospital",
            "lat": 28.6200,
            "lng": 77.2100,
            "address": "123 Main Road",
            "phone": "011-12345678"
        },
        {
            "name": "Metro Medical Center",
            "type": "hospital",
            "lat": 28.6300,
            "lng": 77.2200,
            "address": "456 Metro Ave",
            "phone": None
        }
    ]

    payload = {
        "text": "Chest tightness and sweating",
        "lat": 28.6139,
        "lng": 77.2090
    }
    response = client.post("/find-help", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["needs"] == "hospital"
    assert data["specialty"] == "Cardiology"
    assert data["urgency"] == "high"
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "City General Hospital"
    assert "distance_km" in data["results"][0]
    assert data["results"][0]["distance_km"] > 0


@patch("app.api.routes.find_help.get_nearby_facilities")
@patch("app.api.routes.find_help.classify_problem")
def test_find_help_red_flag_safety_override(mock_classify, mock_get_facilities):
    # LLM incorrectly returns doctor and normal urgency for a life-threatening symptom
    mock_classify.return_value = {
        "needs": "doctor",
        "specialty": "General Medicine",
        "urgency": "normal"
    }
    mock_get_facilities.return_value = [
        {
            "name": "Emergency Trauma Hospital",
            "type": "hospital",
            "lat": 28.6150,
            "lng": 77.2100,
            "address": "Emergency Way",
            "phone": "999"
        }
    ]

    # Input contains 'chest pain' and 'cant breathe' red flags
    payload = {
        "text": "I have sudden severe chest pain and cant breathe",
        "lat": 28.6139,
        "lng": 77.2090
    }
    response = client.post("/find-help", json=payload)
    assert response.status_code == 200

    data = response.json()
    # Safety rules must have overridden both urgency to high and needs to hospital
    assert data["urgency"] == "high"
    assert data["needs"] == "hospital"
    mock_get_facilities.assert_called_once_with(needs="hospital", lat=28.6139, lng=77.2090)


@patch("app.api.routes.find_help.get_nearby_facilities")
@patch("app.api.routes.find_help.classify_problem")
def test_find_help_no_facilities_found(mock_classify, mock_get_facilities):
    # Even if an external classification says medical_store, it must map to doctor
    mock_classify.return_value = {
        "needs": "medical_store",
        "specialty": "General Medicine",
        "urgency": "normal"
    }
    mock_get_facilities.return_value = []

    payload = {
        "text": "Need bandages for a small cut",
        "lat": 28.6139,
        "lng": 77.2090
    }
    response = client.post("/find-help", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["needs"] == "doctor"
    assert data["results"] == []


@patch("app.api.routes.find_help.get_nearby_facilities")
def test_find_help_real_triage_pipeline_integration(mock_get_facilities):
    # Tests the actual triage fallback and safety override logic end-to-end
    mock_get_facilities.return_value = [
        {"name": "Hospital Alpha", "type": "hospital", "lat": 28.6140, "lng": 77.2091},
        {"name": "Hospital Beta", "type": "hospital", "lat": 28.6200, "lng": 77.2100}
    ]

    # Red-flag symptoms should trigger urgency=high and needs=hospital
    payload = {
        "text": "Critical emergency, severe chest pain and cannot breathe",
        "lat": 28.6139,
        "lng": 77.2090
    }
    response = client.post("/find-help", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"] == "high"
    assert data["needs"] == "hospital"
    assert len(data["results"]) == 2
    assert data["results"][0]["name"] == "Hospital Alpha"
    assert data["results"][0]["distance_km"] <= data["results"][1]["distance_km"]


@patch("app.api.routes.find_help.classify_problem")
def test_find_help_internal_server_error(mock_classify):
    mock_classify.side_effect = RuntimeError("Database/Service crashed")

    payload = {
        "text": "Feeling dizzy",
        "lat": 28.6139,
        "lng": 77.2090
    }
    response = client.post("/find-help", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert "unexpected error" in data["detail"].lower()


