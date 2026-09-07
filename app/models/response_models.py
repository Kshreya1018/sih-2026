# Pydantic models for outgoing API response schemas
from typing import Optional, List
from pydantic import BaseModel, Field


class Facility(BaseModel):
    """Details of a single nearby medical facility."""
    name: str = Field(..., description="Name of the facility")
    type: str = Field(..., description="Type of facility (e.g. hospital, clinic, pharmacy)")
    distance_km: float = Field(..., description="Calculated distance from user in kilometers")
    lat: float = Field(..., description="Latitude coordinate of facility")
    lng: float = Field(..., description="Longitude coordinate of facility")
    address: Optional[str] = Field(None, description="Full address or street information")
    phone: Optional[str] = Field(None, description="Contact phone number if available")


class FindHelpResponse(BaseModel):
    """Response payload containing triage assessment and ranked facilities."""
    needs: str = Field(..., description="Facility category needed: hospital, doctor, or medical_store")
    specialty: str = Field(..., description="Medical specialty or department recommended")
    urgency: str = Field(..., description="Urgency level: high or normal")
    results: List[Facility] = Field(default_factory=list, description="Ranked list of nearby medical facilities")
