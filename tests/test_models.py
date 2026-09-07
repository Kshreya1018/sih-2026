# Unit tests for Pydantic models (request and response schemas)
import pytest
from pydantic import ValidationError
from app.models.request_models import FindHelpRequest
from app.models.response_models import Facility, FindHelpResponse


def test_find_help_request_valid():
    req = FindHelpRequest(text="High fever and chills", lat=28.6139, lng=77.2090)
    assert req.text == "High fever and chills"
    assert req.lat == 28.6139
    assert req.lng == 77.2090


def test_find_help_request_boundaries():
    # Min / Max boundary coordinates
    req_min = FindHelpRequest(text="Check", lat=-90.0, lng=-180.0)
    assert req_min.lat == -90.0
    assert req_min.lng == -180.0

    req_max = FindHelpRequest(text="Check", lat=90.0, lng=180.0)
    assert req_max.lat == 90.0
    assert req_max.lng == 180.0

    # Beyond boundary
    with pytest.raises(ValidationError):
        FindHelpRequest(text="Check", lat=90.1, lng=0.0)

    with pytest.raises(ValidationError):
        FindHelpRequest(text="Check", lat=-90.1, lng=0.0)

    with pytest.raises(ValidationError):
        FindHelpRequest(text="Check", lat=0.0, lng=180.1)

    with pytest.raises(ValidationError):
        FindHelpRequest(text="Check", lat=0.0, lng=-180.1)


def test_find_help_request_missing_fields():
    with pytest.raises(ValidationError):
        FindHelpRequest(lat=28.0, lng=77.0)

    with pytest.raises(ValidationError):
        FindHelpRequest(text="Missing coords")


def test_facility_model():
    # Full facility
    f1 = Facility(
        name="Apollo Hospital",
        type="hospital",
        distance_km=1.23,
        lat=28.6,
        lng=77.2,
        address="123 Main Road",
        phone="011-123456"
    )
    assert f1.name == "Apollo Hospital"
    assert f1.address == "123 Main Road"
    assert f1.phone == "011-123456"

    # Minimal facility (optional address and phone omitted)
    f2 = Facility(
        name="Local Clinic",
        type="doctor",
        distance_km=0.5,
        lat=28.6,
        lng=77.2
    )
    assert f2.address is None
    assert f2.phone is None


def test_find_help_response_model():
    resp = FindHelpResponse(
        needs="hospital",
        specialty="Emergency",
        urgency="high"
    )
    assert resp.needs == "hospital"
    assert resp.specialty == "Emergency"
    assert resp.urgency == "high"
    assert resp.results == []

    # Serialization test
    d = resp.model_dump()
    assert d["needs"] == "hospital"
    assert d["results"] == []
