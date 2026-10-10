"""FastAPI Backend Skeleton for Contrastive Speech Analytics & Temporal Flaw Grounding.

Multimodal AI Hackathon 2026 - Track C.
Stage D1: Backend Skeleton with health check and CORS configuration.
"""

from pathlib import Path
import json
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI application
app = FastAPI(
    title="Contrastive Speech Analytics API",
    version="0.1.0",
    description=(
        "Backend API for Contrastive Speech Analytics & Temporal Flaw Grounding. "
        "Compares participant speech delivery against ideal baselines, identifies flaws, "
        "and produces timestamped explanations and scores."
    ),
)

# CORS configuration for frontend development
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Locate sample_output.json for demo data serving
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_OUTPUT_PATH = REPO_ROOT / "sample_output.json"


@app.get("/", tags=["Info"])
def read_root():
    """Root endpoint providing service metadata and status."""
    return {
        "title": "Contrastive Speech Analytics API",
        "version": "0.1.0",
        "status": "online",
        "description": "Multimodal AI Hackathon 2026 - Track C",
        "docs_url": "/docs",
        "health_check": "/health",
        "demo_data": "/sample-output",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend availability."""
    return {
        "status": "ok",
        "service": "contrastive-speech-analytics",
        "version": "0.1.0",
        "stage": "D1",
    }


@app.get("/sample-output", tags=["Demo Data"])
def get_sample_output():
    """Return the shared sample_output.json contract as demo data.

    Note: This is strictly illustrative demo data, not real model inference results.
    """
    if not SAMPLE_OUTPUT_PATH.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="sample_output.json not found in repository root.",
        )
    try:
        with open(SAMPLE_OUTPUT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read sample_output.json: {str(exc)}",
        )


@app.post("/analyze", tags=["Analysis"])
def analyze_audio():
    """Placeholder endpoint for real audio analysis pipeline.

    Explicitly returns 501 Not Implemented during Stage D1 as pipeline integration
    (feature extraction, alignment, flaw detection, scoring) is scheduled for later stages.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=(
            "Speech analysis pipeline is not implemented yet in Stage D1. "
            "Pipeline components from Member B and Member C will be integrated in subsequent stages."
        ),
    )
