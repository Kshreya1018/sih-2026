# Main FastAPI application entrypoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.find_help import router as find_help_router

app = FastAPI(
    title="Medi-Locator API",
    description="Emergency medical triage and nearby facility locator API powered by OSM and Groq LLM",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(find_help_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify service availability."""
    return {
        "status": "healthy",
        "service": "medi-locator-api",
        "version": "1.0.0"
    }
