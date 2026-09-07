# Client integration for OpenStreetMap Overpass API
import logging
from typing import Optional, Dict, Any, List
import requests
from app.core.config import OVERPASS_API_URL

logger = logging.getLogger(__name__)

FALLBACK_ENDPOINTS: List[str] = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter"
]


def query_overpass(query_string: str, timeout_seconds: int = 25) -> Optional[Dict[str, Any]]:
    """
    Sends a POST request to the Overpass API interpreter with the built query string.
    Includes fallback mirror support if a server experiences high load or 504 Gateway Timeout.

    Args:
        query_string: Complete Overpass QL query string.
        timeout_seconds: Network timeout in seconds per endpoint attempt.

    Returns:
        Parsed JSON dictionary from Overpass API or None if all attempts fail.
    """
    endpoints: List[str] = list(dict.fromkeys([OVERPASS_API_URL] + FALLBACK_ENDPOINTS))

    headers = {
        "User-Agent": "medi-locator-api/1.0 (Emergency Medical Locator)",
        "Accept": "application/json, */*",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    for endpoint in endpoints:
        try:
            logger.info(f"Trying Overpass endpoint: {endpoint}")
            response = requests.post(
                endpoint,
                data={"data": query_string},
                headers=headers,
                timeout=timeout_seconds
            )
            response.raise_for_status()
            data = response.json()
            elements = data.get("elements", [])
            logger.info(f"Overpass '{endpoint}' returned {len(elements)} elements.")
            return data
        except requests.Timeout:
            logger.warning(f"Overpass endpoint '{endpoint}' timed out after {timeout_seconds}s, trying next...")
            continue
        except requests.HTTPError as exc:
            logger.warning(f"Overpass endpoint '{endpoint}' HTTP error {exc.response.status_code}: {exc}")
            continue
        except requests.RequestException as exc:
            logger.warning(f"Overpass API endpoint '{endpoint}' request error: {exc}")
            continue
        except Exception as exc:
            logger.error(f"Unexpected error querying Overpass endpoint '{endpoint}': {exc}", exc_info=True)
            continue

    logger.error("All Overpass endpoints failed or timed out.")
    return None
