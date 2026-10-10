"""Unit tests for FastAPI backend skeleton (Stage D1)."""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify GET / returns basic API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Contrastive Speech Analytics API"
    assert data["status"] == "online"
    assert "version" in data


def test_health_endpoint():
    """Verify GET /health returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "contrastive-speech-analytics"
    assert data["stage"] == "D1"


def test_cors_headers():
    """Verify CORS headers allow Vite local development origin."""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"}
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_sample_output_endpoint():
    """Verify GET /sample-output returns valid sample contract data."""
    response = client.get("/sample-output")
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "features" in data
    assert "flaws" in data
    assert "scores" in data


def test_analyze_not_implemented():
    """Verify POST /analyze returns 501 Not Implemented during Stage D1."""
    response = client.post("/analyze")
    assert response.status_code == 501
    assert "not implemented yet" in response.json()["detail"].lower()
