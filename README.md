# Contrastive Speech Analytics & Temporal Flaw Grounding

Multimodal AI Hackathon 2026 — IIT Mandi, Track C.

## Project Overview

An interpretable speech evaluation system that compares a participant's
speech delivery against an ideal baseline, identifies delivery flaws,
and provides timestamped explanations and rubric-based scores.

## Team Responsibilities

- Member A: Dataset construction and flaw injection.
- Member B: Audio preprocessing, forced alignment and feature extraction.
- Member C: Comparison, flaw detection, explanations and scoring.
- Member D: FastAPI backend, React dashboard, Docker and deployment.

## Project Structure

- `data/`: Audio datasets and labels.
- `src/dataset/`: Dataset construction scripts.
- `src/features/`: Alignment and feature extraction.
- `src/analysis/`: Flaw detection and scoring.
- `src/api/`: FastAPI backend.
- `frontend/`: React dashboard.
- `docs/`: Technical documentation.
- `tests/`: Automated tests.
- `sample_output.json`: Shared JSON contract and illustrative demo data.

## Development Status

Initial project skeleton. Backend, frontend and analysis modules
will be developed and integrated incrementally.

## Git Workflow

- `feature/dataset`
- `feature/features`
- `feature/analysis`
- `feature/dashboard`

Contributions should be submitted through pull requests.
Do not push directly to `main` after initial setup.