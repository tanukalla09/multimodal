# Dataset Construction — Technical Notes

## Sourcing and Licences

The dataset uses two readings of the Gettysburg Address released by LibriVox
(https://librivox.org/the-gettysburg-address-150th-anniversary-by-abraham-lincoln/).
LibriVox recordings are dedicated to the public domain; no restrictions apply
to modification or redistribution. The reader for sp01 is Ernst Pattynama and
the reader for sp02 is Julia Niedermaier. Both are identified by name on the
LibriVox catalogue page.

The source files are MP3s downloaded from LibriVox and converted to WAV with
ffmpeg. Each WAV is then trimmed to the active speech region, resampled to
16 kHz mono, DC-offset removed, and RMS-normalised to -20 dBFS (with a 0.97 FS
peak limiter to prevent clipping). This step is performed by
`src/dataset/prepare.py` and is fully reproducible from the source file.

## Flaw Injection Method

Every flaw is injected into a single, hand-chosen region of the ideal recording.
The region boundaries land at natural silence gaps between phrases. The script
`src/dataset/generate.py` reads a YAML config that lists one start/end pair per
flaw type (or an `at` timestamp for long_pause), then calls the appropriate
function from `src/dataset/flaws.py`.

The injectors work as follows:

- **too_fast / too_slow**: WSOLA (Waveform Similarity Overlap-Add) time-stretch
  at the specified tempo factor. Pitch is preserved; only duration changes.
- **monotone**: Praat PSOLA via Parselmouth. The log-F0 deviation from the
  median is scaled by a factor between 0 (completely flat) and 1 (unchanged).
- **erratic_pitch**: Praat PSOLA with a smoothed Gaussian noise perturbation
  added to the pitch contour. Std of noise = wobble_semitones.
- **volume_drop**: Multiply by a gain factor with 50 ms onset/offset ramps.
- **long_pause**: Insert a block of zeros (silence) at a point in the recording.
- **missing_pause**: Find every silent run longer than 0.15 s within the region
  and remove a fraction of it from the centre.

All injectors are deterministic given a fixed random seed; the combined file
uses all three flaw types simultaneously at the same severity level.

## The Severity Gradient

Each flaw type has five severity levels. Level 1 is barely perceptible; level 5
is clearly wrong. The parameter values were chosen so that the progression is
roughly perceptually uniform, but this has not been formally validated with
listener studies. See the severity table in `data/README.md` for exact values.

The generated dataset includes levels 2 and 4 for single-flaw files, and all
levels 1-5 for the combined files. This gives five points on a severity curve
for each speaker, which is sufficient for ranking and correlation experiments.

## Labelling and Time Maps

Each flawed audio file has a paired JSON label in `data/labels/`. The label
records the flaw type and severity, and two time intervals: `start`/`end` in
the flawed file and `src_start`/`src_end` in the ideal file. For time-changing
flaws (too_fast, too_slow, missing_pause) these intervals have different lengths.

The `time_map` field provides a piecewise-linear correspondence between ideal
and flawed timestamps. Each entry is `[ideal_time, flawed_time]`. Code that
needs to locate a flawed event in the ideal file can interpolate between the
nearest pair of entries.

## Reproducibility

Labels are identical across machines and operating systems (fixed seed,
deterministic arithmetic). Audio files are deterministic on the same machine
with the same package versions (scipy, parselmouth). WSOLA and PSOLA use
platform-specific floating-point, so byte-identical audio is not guaranteed
across different OS or library versions. The label durations are the ground
truth; small float differences in audio length are within 2 ms.

## Limits

- Synthetic flaws are cleaner than real speech errors and do not capture
  prosodic context or speaker-specific naturalness.
- Only two speakers are available so far; sp03 and sp04 are planned.
- The acted set (where speakers deliberately perform the flaws) has not been
  recorded yet.
- erratic_pitch has not been validated with listener studies; the numerical
  QC report shows pitch spread changes but cannot confirm perceptibility.
- Speaker sex: sp01 speaker (Ernst Pattynama): male; sp02 speaker (Julia Niedermaier): female.
