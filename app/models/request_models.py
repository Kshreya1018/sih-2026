# Pydantic models for incoming API request payloads
from pydantic import BaseModel, Field


class FindHelpRequest(BaseModel):
    """Payload for finding nearby medical help based on user description and coordinates."""
    text: str = Field(..., description="User description of their medical emergency or symptoms")
    lat: float = Field(..., description="Latitude of the user's current location", ge=-90.0, le=90.0)
    lng: float = Field(..., description="Longitude of the user's current location", ge=-180.0, le=180.0)
