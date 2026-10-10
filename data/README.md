# Dataset: contrastive speech pairs (Track C)

## Contents
| Folder | What |
|---|---|
| `raw/` | Ideal recordings `spXX_ideal.wav` (16 kHz, mono, RMS -20 dBFS) + transcripts `spXX_ideal.txt` |
| `bad/` | Generated flawed versions (rebuilt by `src/dataset/generate.py`; shared via Drive) |
| `labels/` | One `.json` per audio file: flaw type, severity, exact start/end, time map |
| `acted/` | Held-out recordings where people acted the flaws (labelled by hand in Audacity) |

## Sources and licences (fill one row per ideal recording)
| Speech | Speaker (gender) | Text / source | Recording licence | Link |
|---|---|---|---|---|
| sp01 | | | | |

Self-recorded audio: released under CC BY 4.0 with the speaker's written consent.
Code: MIT (see top-level LICENSE).

## Naming
`spXX_ideal.wav`, `spXX_<flaw>_s<1-5>.wav`, `spXX_combined_s<1-5>.wav`; label = same stem + `.json`.

## Flaw recipes (level 1 subtle -> 5 botched)
| Flaw | Method | Levels 1..5 |
|---|---|---|
| too_fast | WSOLA time-stretch (pitch preserved) on the region | x1.10, 1.25, 1.40, 1.60, 1.80 |
| too_slow | WSOLA | x0.90, 0.78, 0.65, 0.55, 0.45 |
| monotone | Praat PSOLA, log-F0 deviation from median scaled | 0.8, 0.6, 0.4, 0.2, 0.0 |
| erratic_pitch | PSOLA, smoothed random wobble | 0.5, 1, 2, 3, 4 semitones |
| volume_drop | gain with 50 ms ramps | -3, -6, -9, -12, -18 dB |
| long_pause | silence inserted | 0.4, 0.7, 1.0, 1.5, 2.5 s |
| missing_pause | silent runs > 0.15 s shortened | 20, 40, 60, 80, 100 % |

## Label schema
See `labels/*.json`: `flaws[].start/end` are in the NEW file's timeline; `src_start/src_end`
are the same region in the ideal file; `time_map` maps ideal time -> new time (piecewise linear).

## Regenerate
`python src/dataset/generate.py configs/sp01_regions.yaml` (fixed seed -> byte-identical output).

## Known limitations
(Write honestly: synthetic flaws are cleaner than real ones; acted set is small; etc.)
