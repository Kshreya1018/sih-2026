# Application-wide constants
from typing import Dict, List

# Primary single-tag mapping of medical needs classification to OpenStreetMap amenity tags
NEEDS_TO_OSM_TAG: Dict[str, str] = {
    "hospital": "amenity=hospital",
    "doctor": "amenity=doctors"
}

# Extended mapping supporting alternative healthcare tags (e.g. healthcare=doctor)
NEEDS_TO_OSM_TAGS: Dict[str, List[str]] = {
    "hospital": ["amenity=hospital"],
    "doctor": ["amenity=doctors", "healthcare=doctor"]
}
