# Service for medical triage assessment
import json
import logging
from typing import Dict
from app.clients.llm_client import call_groq_triage

logger = logging.getLogger(__name__)

DEFAULT_FALLBACK_TRIAGE: Dict[str, str] = {
    "needs": "hospital",
    "specialty": "General Medicine",
    "urgency": "normal"
}


def classify_problem(text: str) -> Dict[str, str]:
    """
    Classifies the user's symptoms using Groq LLM client and parses the response safely.
    Handles malformed JSON or missing keys with robust fallbacks.

    Args:
        text: User description of their medical situation.

    Returns:
        Dictionary with keys: 'needs', 'specialty', 'urgency'.
    """
    raw_response = call_groq_triage(text)

    if not raw_response:
        logger.warning("No response received from LLM client. Using default fallback triage.")
        return DEFAULT_FALLBACK_TRIAGE.copy()

    try:
        data = json.loads(raw_response)
        if not isinstance(data, dict):
            raise ValueError("Parsed JSON is not a dictionary.")

        needs = str(data.get("needs", "hospital")).strip().lower()
        if needs == "medical_store":
            needs = "doctor"
        elif needs not in {"hospital", "doctor"}:
            needs = "hospital"

        specialty = str(data.get("specialty", "General Medicine")).strip()
        if not specialty:
            specialty = "General Medicine"

        urgency = str(data.get("urgency", "normal")).strip().lower()
        if urgency not in {"high", "normal"}:
            urgency = "normal"

        return {
            "needs": needs,
            "specialty": specialty,
            "urgency": urgency
        }
    except Exception as exc:
        logger.error(f"Failed to parse LLM triage output: {exc}. Raw content: {raw_response}")
        return DEFAULT_FALLBACK_TRIAGE.copy()
