# Client integration for Groq LLM service
import logging
from typing import Optional
from groq import Groq
from app.core.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert medical triage assistant.
Your job is to analyze the user's symptoms and classify their medical needs into valid JSON format.
You must respond ONLY with a JSON object conforming to this exact schema:
{
  "needs": "hospital" | "doctor",
  "specialty": "<specific medical specialty, e.g. Cardiology, Emergency, Pulmonology, General Medicine>",
  "urgency": "high" | "normal"
}

Rules for classification:
- "hospital": For emergencies, severe trauma, heart/stroke/breathing symptoms, severe acute pain, fractures, poisoning. Urgency must be "high".
- "doctor": For non-emergency consultations, general ailments, ongoing moderate or minor issues, skin conditions, fever, minor infections, headaches, minor injuries, medication queries. Urgency is typically "normal".

Do not return any text, markdown code blocks, or explanations outside of the JSON object.
"""


def call_groq_triage(text: str) -> Optional[str]:
    """
    Calls the Groq API using llama-3.3-70b-versatile with JSON response format.

    Args:
        text: User description of their medical situation.

    Returns:
        Raw JSON string from Groq, or None if the request fails or API key is missing.
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is not configured in .env. Skipping LLM request.")
        return None

    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        return None
    except Exception as exc:
        logger.error(f"Groq API call failed: {exc}", exc_info=True)
        return None
