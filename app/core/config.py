# Application configuration and environment settings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
OVERPASS_API_URL: str = os.getenv("OVERPASS_API_URL", "https://overpass-api.de/api/interpreter").strip()
DEFAULT_SEARCH_RADIUS: int = int(os.getenv("DEFAULT_SEARCH_RADIUS", "5000"))
