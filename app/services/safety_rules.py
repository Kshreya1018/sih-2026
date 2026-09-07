# Service rule definitions for medical safety checks
from typing import List

# Critical red-flag symptoms and emergencies requiring immediate high-urgency care
RED_FLAG_KEYWORDS: List[str] = [
    "chest pain",
    "can't breathe",
    "cant breathe",
    "cannot breathe",
    "shortness of breath",
    "difficulty breathing",
    "unconscious",
    "unresponsive",
    "severe bleeding",
    "heavy bleeding",
    "bleeding heavily",
    "heart attack",
    "stroke",
    "seizure",
    "head injury",
    "head trauma",
    "anaphylaxis",
    "poisoning",
    "overdose",
    "choking",
    "cardiac arrest",
    "loss of consciousness"
]


def check_red_flags(text: str) -> bool:
    """
    Checks if any critical emergency keywords are present in the user text.

    Args:
        text: User description of the medical situation.

    Returns:
        True if any red-flag keyword matches, False otherwise.
    """
    cleaned_text = text.lower()
    return any(keyword in cleaned_text for keyword in RED_FLAG_KEYWORDS)


def apply_safety_override(text: str, current_urgency: str = "normal") -> str:
    """
    Overrides urgency to 'high' if any red-flag keyword is detected in the input text.
    Acts as an independent, deterministic safety net.

    Args:
        text: User description of the medical situation.
        current_urgency: Urgency level determined by earlier steps (e.g. LLM).

    Returns:
        'high' if a red flag is matched, otherwise the existing urgency.
    """
    if check_red_flags(text):
        return "high"
    return current_urgency
