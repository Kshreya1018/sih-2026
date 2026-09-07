# Unit tests for ranking service and distance calculations
from app.utils.distance import haversine
from app.services.ranking_service import rank_facilities


def test_haversine_same_point():
    assert haversine(28.6139, 77.2090, 28.6139, 77.2090) == 0.0


def test_haversine_known_distance():
    # Distance between New Delhi (28.6139, 77.2090) and Connaught Place (~28.6315, 77.2167) is ~2 km
    dist = haversine(28.6139, 77.2090, 28.6315, 77.2167)
    assert 1.5 < dist < 2.5


def test_haversine_negative_coordinates():
    # Distance between Sydney (-33.8688, 151.2093) and Melbourne (-37.8136, 144.9631) ~714 km
    dist = haversine(-33.8688, 151.2093, -37.8136, 144.9631)
    assert 700 < dist < 730


def test_rank_facilities_ordering_and_limit():
    user_lat, user_lng = 28.6139, 77.2090
    facilities = [
        {"name": "Far Hospital", "type": "hospital", "lat": 28.7000, "lng": 77.3000, "address": "Far Rd"},
        {"name": "Near Clinic", "type": "hospital", "lat": 28.6150, "lng": 77.2100, "address": "Near Rd"},
        {"name": "Mid Hospital", "type": "hospital", "lat": 28.6300, "lng": 77.2200, "address": "Mid Rd"},
        {"name": "Very Far", "type": "hospital", "lat": 29.0000, "lng": 78.0000, "address": "Very Far Rd"},
    ]

    results = rank_facilities(user_lat, user_lng, facilities, top_k=3)
    assert len(results) == 3
    assert results[0].name == "Near Clinic"
    assert results[1].name == "Mid Hospital"
    assert results[2].name == "Far Hospital"
    assert results[0].distance_km < results[1].distance_km < results[2].distance_km


def test_rank_facilities_empty():
    results = rank_facilities(28.6139, 77.2090, [], top_k=3)
    assert results == []


def test_rank_facilities_fewer_than_top_k():
    facilities = [
        {"name": "Only Clinic", "type": "doctor", "lat": 28.6150, "lng": 77.2100}
    ]
    results = rank_facilities(28.6139, 77.2090, facilities, top_k=5)
    assert len(results) == 1
    assert results[0].name == "Only Clinic"
    assert results[0].address is None
    assert results[0].phone is None


def test_rank_facilities_excludes_pharmacies_and_medical_stores():
    facilities = [
        {"name": "MedPlus Pharmacy", "type": "pharmacy", "lat": 28.6140, "lng": 77.2091},
        {"name": "City Medical Store", "type": "medical_store", "lat": 28.6141, "lng": 77.2092},
        {"name": "Local Chemist", "type": "chemist", "lat": 28.6142, "lng": 77.2093},
        {"name": "Dr. Verma Clinic", "type": "doctor", "lat": 28.6150, "lng": 77.2100},
        {"name": "City Hospital", "type": "hospital", "lat": 28.6200, "lng": 77.2150}
    ]
    results = rank_facilities(28.6139, 77.2090, facilities, top_k=5)
    assert len(results) == 2
    assert results[0].name == "Dr. Verma Clinic"
    assert results[1].name == "City Hospital"
    for r in results:
        assert r.type not in {"pharmacy", "medical_store", "chemist"}

