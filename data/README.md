# Contrastive Speech Dataset (Track C)

## Overview

This dataset supports contrastive speech analytics and temporal flaw grounding.
Each speech ID has one ideal recording and a set of paired flawed versions where
a single speech flaw is synthetically injected into a specific time region.
The ideal and flawed files can be directly compared: the label JSON records
exact start/end times in both the ideal and flawed files, plus a time map
for piecewise-linear alignment.

Currently available: sp01 (Gettysburg Address, speaker 1) and sp02 (same text,
speaker 2). Speeches 3 and 4 and the acted set are not yet done; see Known Limits.

---

## Sources and Licences

| Speech | Speaker (sex) | Text | Recording | Source file | Trim (source) | Licence |
|--------|---------------|------|-----------|-------------|---------------|---------|
| sp01 | Ernst Pattynama (male) | Gettysburg Address | LibriVox | gettysburgaddress_lincoln_eep_128kb.mp3 | 11.4 s to 96.84 s | Public Domain (LibriVox) |
| sp02 | Julia Niedermaier (female) | Gettysburg Address | LibriVox | gettysburgaddress_lincoln_jn_128kb.mp3 | 7.89 s to 73.96 s | Public Domain (LibriVox) |

LibriVox recordings are released into the public domain; modification is
permitted. Original recordings are available at:
https://librivox.org/the-gettysburg-address-150th-anniversary-by-abraham-lincoln/

Code in this repository: MIT Licence (see top-level LICENSE).

---

## Folder Layout

```
data/
  raw/        Ideal WAV files (spXX_ideal.wav, 16 kHz mono) + transcripts (spXX_ideal.txt)
  source/     Original MP3s and converted source WAVs (git-ignored)
  bad/        Generated flawed WAV files (rebuilt by generate.py; git-ignored)
  labels/     Label JSON files - one per audio file (including ideal and flawed)
  ab/         A/B listening clips (ideal then flawed, git-ignored)
  acted/      (Future) Hand-labelled recordings of acted flaws
```

---

## File Naming

| Pattern | Meaning |
|---------|---------|
| `spXX_ideal.wav` | Clean reference recording for speaker XX |
| `spXX_ideal.txt` | Verbatim transcript (filler words excluded on purpose) |
| `spXX_<flaw>_s<N>.wav` | Single flaw of type `<flaw>` at severity N (1=subtle, 5=botched) |
| `spXX_combined_s<N>.wav` | Three flaws injected simultaneously at severity N |

`<flaw>` is one of: `too_fast`, `too_slow`, `monotone`, `erratic_pitch`,
`volume_drop`, `long_pause`, `missing_pause`.

Label file: same stem + `.json`, stored in `data/labels/`.

---

## Severity Table

Severity levels 1 (subtle) through 5 (botched). Values are the parameter
passed to the flaw injector (see `src/dataset/flaws.py`).

| Flaw | Parameter | Sev 1 | Sev 2 | Sev 3 | Sev 4 | Sev 5 |
|------|-----------|-------|-------|-------|-------|-------|
| too_fast | tempo_factor | 1.10 | 1.25 | 1.40 | 1.60 | 1.80 |
| too_slow | tempo_factor | 0.90 | 0.78 | 0.65 | 0.55 | 0.45 |
| monotone | f0_scale_kept | 0.8 | 0.6 | 0.4 | 0.2 | 0.0 |
| erratic_pitch | wobble_std_st | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
| volume_drop | gain_dB | -3 | -6 | -9 | -12 | -18 |
| long_pause | pause_s | 0.4 | 0.7 | 1.0 | 1.5 | 2.5 |
| missing_pause | pause_cut_share | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |

---

## Label JSON Schema

Every audio file has a paired label JSON in `data/labels/`. Fields:

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | Filename of the audio file |
| `speech_id` | string | Speaker ID (e.g. "sp01") |
| `ideal_file` | string | Filename of the corresponding ideal WAV |
| `sr` | int | Sample rate (always 16000) |
| `duration` | float | Duration of **this** (flawed) file in seconds |
| `seed` | int | RNG seed used for generation |
| `overall_severity` | int | Severity level (0 = ideal, 1-5 = single/combined) |
| `flaws` | list | List of flaw objects (empty for ideal) |
| `time_map` | list | Piecewise-linear map [[ideal_t, flawed_t], ...] |

Each flaw object:

| Field | Description |
|-------|-------------|
| `type` | Flaw name (one of the 7 flaw types) |
| `severity` | Severity level 1-5 |
| `start` | Start of flaw region in the **flawed** file (seconds) |
| `end` | End of flaw region in the **flawed** file (seconds) |
| `src_start` | Start of the same region in the **ideal** file (seconds) |
| `src_end` | End of the same region in the **ideal** file (seconds) |
| `params` | Dict of the injector parameter and value |

The `time_map` is a list of `[ideal_time, flawed_time]` pairs. Between
consecutive pairs, time is mapped linearly. Use it to convert a timestamp
in the flawed file back to the ideal file or vice versa.

---

## Processing Pipeline

1. Source MP3 downloaded from LibriVox.
2. Converted to WAV with ffmpeg.
3. `src/dataset/prepare.py`: trim to ideal region, resample to 16 kHz mono,
   RMS-normalise to -20 dBFS, remove DC offset, peak-limit to 0.97 FS.
4. `src/dataset/generate.py <config>`: inject flaws per the regions YAML,
   write flawed WAVs and label JSONs.
5. `src/dataset/validate.py`: sanity check (sample rate, duration, clipping,
   time map ordering, region bounds).

---

## How to Regenerate

```bash
# sp01
python src\dataset\generate.py configs\sp01_regions.yaml
python src\dataset\validate.py

# sp02
python src\dataset\generate.py configs\sp02_regions.yaml
python src\dataset\validate.py
```

Labels and duration values are identical across machines (fixed seed).
Audio is byte-identical only on the same machine with the same package
versions (WSOLA and PSOLA are deterministic but platform-dependent).

---

## Proposing Regions for New Speeches (Speeches 3 and 4)

To generate a draft regions configuration for a new reference audio file (e.g. speech 3):

```bash
python src/dataset/propose_regions.py data/raw/sp03_ideal.wav sp03 [--seed 42] [--out configs/sp03_regions.draft.yaml]
```

The tool detects pause boundaries using frame RMS energy, selects valid 3–5 s speech regions separated by at least 1.0 s, ensures the `missing_pause` region contains a pause > 0.15 s, keeps regions >= 6 s away from the clip end, spreads flaws across the recording, and outputs a draft YAML matching `configs/sp01_regions.yaml`.

---

## QC Report Summary

The file `data/qc_report.md` contains objective measurements for every
flawed file vs its ideal counterpart.

Results (run 2026-10-10):
- **50 PASS** out of 58 flaw instances
- **1 FAIL** (`sp01_monotone_s2.wav`: pitch spread ratio is 1.053 vs expected 0.60 +/- 0.25)
- **7 WEAK** (`sp02` erratic_pitch across combined and single series: fails monotonic trend or effect at s4 is below 50% of expected size)

> These numbers do NOT replace listening. Pitch figures in `validate.py` use a simple
> homemade tracker and are not reliable; the Praat (Parselmouth) figures in `data/qc_report.md`
> are the ones to trust. See `data/qc_report.md` for the full table and methodology.

---

## Known Limits

- **Synthetic flaws only**: injected flaws are cleaner and more consistent
  than real speech errors. The acted set (planned for `data/acted/`) will
  provide naturalistic examples.
- **Speeches 3 and 4**: not yet sourced. Only sp01 and sp02 exist.
- **The acted set**: not yet recorded or labelled.
- **erratic_pitch baseline**: the effect of the pitch wobble on measurable
  pitch spread has never been benchmarked before this dataset; MEASURED
  results in qc_report.md require listening to confirm.
- **Filler words excluded**: transcripts do not include "um", "uh", etc.
  because including them would change the canonical text.
- **Speaker sex**: sp01 speaker (Ernst Pattynama): male; sp02 speaker (Julia Niedermaier): female.
- **Single machine reproducibility**: byte-identical audio only on same
  OS + same scipy/parselmouth versions.
