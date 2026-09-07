# API route handler for find help endpoints
import logging
from fastapi import APIRouter, HTTPException, status
from app.models.request_models import FindHelpRequest
from app.models.response_models import FindHelpResponse
from app.services.safety_rules import apply_safety_override, check_red_flags
from app.services.triage_service import classify_problem
from app.services.osm_service import get_nearby_facilities
from app.services.ranking_service import rank_facilities

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/find-help",
    response_model=FindHelpResponse,
    status_code=status.HTTP_200_OK,
    summary="Find nearest appropriate medical facilities based on symptoms and location"
)
async def find_help(request: FindHelpRequest) -> FindHelpResponse:
    """
    Orchestrates the medical triage and facility location pipeline:
    1. Receives FindHelpRequest
    2. Runs safety_rules check for critical red-flag symptoms
    3. Runs triage_service.classify_problem to determine need category and specialty
    4. Runs osm_service.get_nearby_facilities using the classified 'needs'
    5. Runs ranking_service.rank_facilities to calculate distances and sort nearest top 3
    6. Returns structured FindHelpResponse
    """
    try:
        # Step 2: Safety check
        has_red_flag = check_red_flags(request.text)

        # Step 3: Triage classification
        triage = classify_problem(request.text)
        needs = triage.get("needs", "hospital")
        specialty = triage.get("specialty", "General Medicine")
        urgency = triage.get("urgency", "normal")

        # Apply hard safety override if red flags found
        urgency = apply_safety_override(request.text, urgency)
        if has_red_flag and needs != "hospital":
            needs = "hospital"

        # Step 4: Fetch nearby facilities via OSM Overpass
        facilities = get_nearby_facilities(
            needs=needs,
            lat=request.lat,
            lng=request.lng
        )

        # Step 5: Rank facilities by proximity (top 3)
        ranked_results = rank_facilities(
            user_lat=request.lat,
            user_lng=request.lng,
            facilities=facilities,
            top_k=3
        )

        # Step 6: Return response
        return FindHelpResponse(
            needs=needs,
            specialty=specialty,
            urgency=urgency,
            results=ranked_results
        )

    except Exception as exc:
        logger.error(f"Error in find_help endpoint: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the medical locator request."
        )
