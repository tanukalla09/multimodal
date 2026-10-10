# Acted Flaw Speech Dataset (`data/acted/`)

## Purpose

This folder contains hand-recorded and hand-labelled audio files of speakers deliberately performing speech delivery flaws (such as speaking too fast, speaking in a monotone pitch, or introducing awkward pauses).

These naturalistic recordings complement the synthetically injected flaws in `data/bad/`.

---

## File Naming Conventions

- **Audio files**: `spXX_acted_<flaw>.wav`
  - Examples: `sp03_acted_too_fast.wav`, `sp03_acted_monotone.wav`, `sp03_acted_combined.wav`
- **Label files**: `spXX_acted_<flaw>.json`
  - Generated from exported Audacity label tracks using `src/dataset/audacity_to_labels.py`.

Valid flaw names:
`too_fast`, `too_slow`, `monotone`, `erratic_pitch`, `volume_drop`, `long_pause`, `missing_pause`, `combined`.

---

## Strict Held-Out Evaluation Set Rule

> [!CRITICAL]
> **This dataset is strictly held out.**
> Teammates developing models, acoustic extractors, or anomaly detection pipelines
> **MUST NOT** use files in `data/acted/` for training, validation, or threshold tuning.
> These files are reserved solely for final blind testing to assess how well detectors
> trained on synthetic flaws generalize to real human performance errors.
