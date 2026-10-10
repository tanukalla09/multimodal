# Contrastive Speech Analytics & Temporal Flaw Grounding

Multimodal AI Hackathon 2026 — IIT Mandi, Track C.

## Project Overview

An interpretable speech evaluation system that compares a participant's
speech delivery against an ideal baseline, identifies delivery flaws,
and provides timestamped explanations and rubric-based scores.

## Team Responsibilities

- **Member A**: Dataset construction and flaw injection (`data/`, `src/dataset/`).
- **Member B**: Audio preprocessing, forced alignment and feature extraction (`src/features/`).
- **Member C**: Comparison, flaw detection, explanations and scoring (`src/analysis/`).
- **Member D**: FastAPI backend, React dashboard, Docker and deployment (`src/api/`, `frontend/`, `Dockerfile`).

## Project Structure

- `data/`: Audio datasets and labels.
- `src/dataset/`: Dataset construction scripts.
- `src/features/`: Alignment and feature extraction.
- `src/analysis/`: Flaw detection and scoring.
- `src/api/`: FastAPI backend skeleton.
- `frontend/`: React + Vite dashboard.
- `docs/`: Technical documentation.
- `tests/`: Automated unit and integration tests.
- `sample_output.json`: Shared JSON contract and illustrative demo data.

## Product Interface: VocalLens

The frontend is packaged as **VocalLens**, an AI-powered speech coaching interface designed for contrastive delivery evaluation:
- **Headline**: *Understand your delivery. Improve your impact.*
- **Core Pillars**: Delivery Score, Temporal Analysis, Pitch & Energy.
- **FastAPI Skeleton**: Operational with CORS, health-check endpoint (`GET /health`), metadata endpoint (`GET /`), demo endpoint (`GET /sample-output`), and a 501 Not Implemented placeholder (`POST /analyze`).
- **Editorial Dashboard**: Responsive interface with warm ivory surfaces, ink typography, electric-violet accents, hero overall score card, millisecond-calibrated flaw timeline, synchronized local audio playback, interactive word token alignment, diagnostic inspector, and contrastive Recharts time-series contours.
- **Analysis Pipeline Status**: **Real speech analysis is not implemented yet.** All metrics, contours, and flaw annotations displayed are illustrative demo results sourced from `sample_output.json`. Audio files loaded in the dashboard are played locally for demonstration without being processed by the backend.

---

## Getting Started

### Prerequisites

- **Python**: 3.10+ (tested on Python 3.14)
- **Node.js**: 18+ (tested on Node.js v24.12.0, npm 11.6.2)

---

### Backend Setup (FastAPI)

1. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the FastAPI server**:
   ```bash
   uvicorn src.api.main:app --reload
   ```
   Or to specify host and port explicitly:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

3. **Backend URLs**:
   - API Root: [http://localhost:8000/](http://localhost:8000/)
   - Health Check: [http://localhost:8000/health](http://localhost:8000/health)
   - Interactive Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - Demo Data Endpoint: [http://localhost:8000/sample-output](http://localhost:8000/sample-output)

4. **Run automated backend tests**:
   ```bash
   pytest
   ```
   or:
   ```bash
   python -m pytest -v
   ```

---

### Frontend Setup (React + Vite)

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the local development server**:
   ```bash
   npm run dev
   ```

4. **Frontend URLs**:
   - Local Dashboard: [http://localhost:5173/](http://localhost:5173/)

5. **Build for production**:
   ```bash
   npm run build
   ```
   To preview the production build locally:
   ```bash
   npm run preview
   ```

---

## How Demo Data Is Loaded

- The dashboard uses the repository contract `sample_output.json` as the single source of truth for demo results.
- When the frontend loads, it automatically attempts to fetch the latest contract from `http://localhost:8000/sample-output` if the backend is running, or falls back seamlessly to the bundled `frontend/src/data/sample_output.json`.
- The dashboard clearly identifies all scores, contours, and flaws as demo data.

---

## Git Workflow

- `feature/dataset`
- `feature/features`
- `feature/analysis`
- `feature/dashboard`

Contributions should be submitted through pull requests.
Do not push directly to `main` after initial setup.