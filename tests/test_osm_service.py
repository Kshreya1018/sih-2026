# Unit tests for OpenStreetMap service
from unittest.mock import patch
from app.core.constants import NEEDS_TO_OSM_TAG, NEEDS_TO_OSM_TAGS
from app.services.osm_service import build_overpass_query, extract_address, get_nearby_facilities


def test_osm_tag_mappings():
    assert NEEDS_TO_OSM_TAG["hospital"] == "amenity=hospital"
    assert NEEDS_TO_OSM_TAG["doctor"] == "amenity=doctors"
    assert NEEDS_TO_OSM_TAG["medical_store"] == "amenity=pharmacy"


def test_build_overpass_query_single_tag():
    query = build_overpass_query("amenity=hospital", 28.6139, 77.2090, 5000)
    assert '[out:json]' in query
    assert 'amenity"="hospital' in query
    assert '28.6139' in query
    assert '77.209' in query


def test_build_overpass_query_multi_tags():
    query = build_overpass_query(NEEDS_TO_OSM_TAGS["doctor"], 28.6139, 77.2090, 3000)
    assert 'amenity"="doctors' in query
    assert 'healthcare"="doctor' in query
    assert 'around:3000' in query


def test_build_overpass_query_key_only():
    query = build_overpass_query("healthcare", 28.6139, 77.2090, 1000)
    assert 'node["healthcare"](around:1000' in query
    assert 'way["healthcare"](around:1000' in query


def test_extract_address():
    # 1. Full address tag takes precedence
    assert extract_address({"addr:full": "10 Downing Street, London"}) == "10 Downing Street, London"

    # 2. House + Street + City + Postcode
    tags1 = {
        "addr:housenumber": "42",
        "addr:street": "Wallaby Way",
        "addr:city": "Sydney",
        "addr:postcode": "2000"
    }
    assert extract_address(tags1) == "42 Wallaby Way, Sydney, 2000"

    # 3. Street only
    assert extract_address({"addr:street": "Oxford St"}) == "Oxford St"

    # 4. City and suburb
    assert extract_address({"addr:suburb": "Connaught Place", "addr:postcode": "110001"}) == "Connaught Place, 110001"

    # 5. Empty tags
    assert extract_address({}) is None


@patch("app.services.osm_service.query_overpass")
def test_get_nearby_facilities_success(mock_query):
    mock_query.return_value = {
        "elements": [
            {
                "type": "node",
                "id": 1,
                "lat": 28.6200,
                "lon": 77.2100,
                "tags": {
                    "name": "Apollo Clinic",
                    "amenity": "clinic",
                    "phone": "+91-11-23456789",
                    "addr:street": "Barakhamba Road"
                }
            },
            {
                "type": "way",
                "id": 2,
                "center": {"lat": 28.6300, "lon": 77.2200},
                "tags": {
                    "name:en": "Max Hospital",
                    "amenity": "hospital"
                }
            },
            {
                # Unnamed facility with operator tag
                "type": "node",
                "id": 3,
                "lat": 28.6400,
                "lon": 77.2300,
                "tags": {
                    "operator": "Government Dispensary",
                    "healthcare": "doctor"
                }
            },
            {
                # Completely unnamed facility
                "type": "node",
                "id": 4,
                "lat": 28.6500,
                "lon": 77.2400,
                "tags": {}
            },
            {
                # Missing coordinates element - should be skipped
                "type": "node",
                "id": 5,
                "tags": {"name": "Ghost Clinic"}
            }
        ]
    }

    facilities = get_nearby_facilities("hospital", 28.6139, 77.2090, 5000)
    assert len(facilities) == 4

    assert facilities[0]["name"] == "Apollo Clinic"
    assert facilities[0]["lat"] == 28.6200
    assert facilities[0]["lng"] == 77.2100
    assert facilities[0]["phone"] == "+91-11-23456789"
    assert facilities[0]["address"] == "Barakhamba Road"

    assert facilities[1]["name"] == "Max Hospital"
    assert facilities[1]["lat"] == 28.6300
    assert facilities[1]["lng"] == 77.2200

    assert facilities[2]["name"] == "Government Dispensary"
    assert facilities[2]["type"] == "doctor"

    assert facilities[3]["name"] == "Unnamed Hospital"
    assert facilities[3]["type"] == "hospital"


@patch("app.services.osm_service.query_overpass")
def test_get_nearby_facilities_empty_or_failure(mock_query):
    # None returned (network / timeout error)
    mock_query.return_value = None
    assert get_nearby_facilities("hospital", 28.6139, 77.2090) == []

    # Elements empty
    mock_query.return_value = {"elements": []}
    assert get_nearby_facilities("doctor", 28.6139, 77.2090) == []

    # Malformed response dict without elements key
    mock_query.return_value = {"error": "rate limit"}
    assert get_nearby_facilities("medical_store", 28.6139, 77.2090) == []

