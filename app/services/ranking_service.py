# Service for ranking and filtering medical facilities
from typing import List, Dict, Any
from app.utils.distance import haversine
from app.models.response_models import Facility


EXCLUDED_FACILITY_TYPES = {"pharmacy", "chemist", "medical_store"}


def rank_facilities(
    user_lat: float,
    user_lng: float,
    facilities: List[Dict[str, Any]],
    top_k: int = 3
) -> List[Facility]:
    """
    Computes distance between user and each facility, sorts ascending by distance,
    and returns the top K facilities mapped to Facility Pydantic models.
    Filters out any pharmacies or medical stores.

    Args:
        user_lat: User's latitude.
        user_lng: User's longitude.
        facilities: Raw or normalized facility dictionaries from OSM service.
        top_k: Number of nearest facilities to return (default: 3).

    Returns:
        List of Facility models sorted by distance ascending.
    """
    ranked_list: List[Facility] = []

    for fac in facilities:
        fac_type = str(fac.get("type", "")).lower()
        if fac_type in EXCLUDED_FACILITY_TYPES:
            continue

        fac_lat = fac["lat"]
        fac_lng = fac["lng"]
        dist_km = haversine(user_lat, user_lng, fac_lat, fac_lng)

        facility_obj = Facility(
            name=fac.get("name", "Unknown Facility"),
            type=fac.get("type", "hospital"),
            distance_km=dist_km,
            lat=fac_lat,
            lng=fac_lng,
            address=fac.get("address"),
            phone=fac.get("phone")
        )
        ranked_list.append(facility_obj)

    # Sort ascending by distance in kilometers
    ranked_list.sort(key=lambda f: f.distance_km)

    return ranked_list[:top_k]
