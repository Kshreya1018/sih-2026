# Service for querying OpenStreetMap data
import logging
from typing import List, Dict, Any, Optional, Union
from app.core.constants import NEEDS_TO_OSM_TAG, NEEDS_TO_OSM_TAGS
from app.clients.overpass_client import query_overpass

logger = logging.getLogger(__name__)


def build_overpass_query(
    tags: Union[str, List[str]],
    lat: float,
    lng: float,
    radius: int
) -> str:
    """
    Constructs an Overpass QL query string for nodes and ways within radius.
    Supports single tag string (e.g. 'amenity=hospital') or list of tags.
    """
    tag_list = [tags] if isinstance(tags, str) else tags

    query_statements: List[str] = []
    for tag_str in tag_list:
        key, _, value = tag_str.partition("=")
        tag_filter = f'["{key}"="{value}"]' if value else f'["{key}"]'
        query_statements.append(f"node{tag_filter}(around:{radius},{lat},{lng});")
        query_statements.append(f"way{tag_filter}(around:{radius},{lat},{lng});")

    statements_block = "\n      ".join(query_statements)

    return f"""
    [out:json][timeout:25];
    (
      {statements_block}
    );
    out center;
    """.strip()


def extract_address(tags: Dict[str, Any]) -> Optional[str]:
    """Helper to assemble a readable address from OSM tags if available."""
    if "addr:full" in tags:
        return str(tags["addr:full"])

    parts: List[str] = []
    house = tags.get("addr:housenumber")
    street = tags.get("addr:street")
    city = tags.get("addr:city") or tags.get("addr:suburb")
    postcode = tags.get("addr:postcode")

    if house and street:
        parts.append(f"{house} {street}")
    elif street:
        parts.append(street)

    if city:
        parts.append(city)
    if postcode:
        parts.append(postcode)

    return ", ".join(parts) if parts else None


def get_nearby_facilities(
    needs: str,
    lat: float,
    lng: float,
    radius: int = 5000
) -> List[Dict[str, Any]]:
    """
    Queries Overpass API for medical facilities matching the required needs category
    around the specified latitude and longitude within the given radius in meters.

    Args:
        needs: Category of need ('hospital' or 'doctor').
        lat: Center latitude.
        lng: Center longitude.
        radius: Search radius in meters (default 5000).

    Returns:
        List of raw or normalized facility dictionaries with at least name, lat, lng.
    """
    # Normalize needs category - strictly doctor or hospital
    if needs == "medical_store":
        needs = "doctor"
    elif needs not in NEEDS_TO_OSM_TAGS:
        needs = "hospital"

    osm_tags = NEEDS_TO_OSM_TAGS.get(needs, [NEEDS_TO_OSM_TAG.get(needs, "amenity=hospital")])
    query = build_overpass_query(osm_tags, lat, lng, radius)

    logger.info(f"Querying Overpass for needs={needs} (tags={osm_tags}) around ({lat}, {lng}) radius={radius}m")
    data = query_overpass(query)

    if not data or "elements" not in data:
        logger.warning("No elements returned or Overpass query failed.")
        return []

    facilities: List[Dict[str, Any]] = []
    elements = data.get("elements", [])
    excluded_types = {"pharmacy", "chemist", "medical_store"}

    for element in elements:
        tags = element.get("tags", {})

        amenity_val = (tags.get("amenity") or "").lower()
        healthcare_val = (tags.get("healthcare") or "").lower()
        if amenity_val in excluded_types or healthcare_val in excluded_types:
            continue

        # Determine coordinates (nodes have lat/lon, ways have center lat/lon)
        fac_lat: Optional[float] = element.get("lat")
        fac_lng: Optional[float] = element.get("lon")

        if fac_lat is None or fac_lng is None:
            center = element.get("center")
            if isinstance(center, dict):
                fac_lat = center.get("lat")
                fac_lng = center.get("lon")

        if fac_lat is None or fac_lng is None:
            continue

        facility_type = tags.get("amenity") or tags.get("healthcare") or needs
        if str(facility_type).lower() in excluded_types:
            continue

        name = (
            tags.get("name")
            or tags.get("name:en")
            or tags.get("operator")
            or f"Unnamed {needs.replace('_', ' ').title()}"
        )
        phone = tags.get("phone") or tags.get("contact:phone")
        address = extract_address(tags)

        facilities.append({
            "name": name,
            "type": facility_type,
            "lat": float(fac_lat),
            "lng": float(fac_lng),
            "address": address,
            "phone": phone
        })

    logger.info(f"Extracted {len(facilities)} facilities from Overpass response.")
    return facilities
