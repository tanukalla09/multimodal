# Objective QC Report

> **DISCLAIMER**: This report measures numbers computed from audio waveforms.
> It does **NOT** replace listening. A PASS means the numerical effect is in the
> expected direction and within tolerance; it does not mean the flaw sounds correct.

## Severity Table (from `src/dataset/flaws.py`)

| Flaw | Param | Sev 1 | Sev 2 | Sev 3 | Sev 4 | Sev 5 |
|------|-------|-------|-------|-------|-------|-------|
| too_fast | tempo_factor | 1.1 | 1.25 | 1.4 | 1.6 | 1.8 |
| too_slow | tempo_factor | 0.9 | 0.78 | 0.65 | 0.55 | 0.45 |
| monotone | f0_scale_kept | 0.8 | 0.6 | 0.4 | 0.2 | 0.0 |
| erratic_pitch | wobble_std_st | 0.5 | 1.0 | 2.0 | 3.0 | 4.0 |
| volume_drop | gain_dB | -3 | -6 | -9 | -12 | -18 |
| long_pause | pause_s | 0.4 | 0.7 | 1.0 | 1.5 | 2.5 |
| missing_pause | pause_cut_share | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |

## Tolerances

| Flaw | Primary Metric | Pass Condition | Tolerance |
|------|----------------|----------------|-----------|
| too_fast | duration_ratio | = expected tempo factor | +/-10% |
| too_slow | duration_ratio | = expected tempo factor | +/-10% |
| monotone | pitch_spread_chg_st | < 0 (spread decreases) | 0.5 st |
| erratic_pitch | pitch_spread_chg_st | any (NEVER measured before) | none |
| volume_drop | rms_change_db | = expected gain_dB | +/-2 dB |
| long_pause | sil_flaw | silence fraction > 0.80 | fixed |
| missing_pause | sil_chg | < 0 (pauses shortened) | must be negative |

## Expected vs Measured

| File | Flaw | Sev | DurRatio | RMS_chg_dB | Pitch_chg_st | Sil_ideal | Sil_flaw | Verdict | Expected | Measured |
|------|------|-----|----------|------------|--------------|-----------|----------|---------|----------|----------|
| sp01_combined_s1.wav | monotone | 1 | 1.000 | -0.32 | -0.43 | 0.205 | 0.200 | PASS | pitch_chg<0.5st | pitch_chg=-0.43st |
| sp01_combined_s1.wav | too_fast | 1 | 1.100 | 0.02 | 1.09 | 0.425 | 0.405 | PASS | ratio~1.10+/-10% | ratio=1.100 |
| sp01_combined_s1.wav | volume_drop | 1 | 1.000 | -3.00 | 0.00 | 0.276 | 0.276 | PASS | rms_chg~-3+/-2dB | rms_chg=-3.00dB |
| sp01_combined_s2.wav | monotone | 2 | 1.000 | -0.51 | -0.80 | 0.205 | 0.195 | PASS | pitch_chg<0.5st | pitch_chg=-0.80st |
| sp01_combined_s2.wav | too_fast | 2 | 1.250 | 0.07 | -0.05 | 0.425 | 0.406 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp01_combined_s2.wav | volume_drop | 2 | 1.000 | -6.00 | -0.00 | 0.276 | 0.276 | PASS | rms_chg~-6+/-2dB | rms_chg=-6.00dB |
| sp01_combined_s3.wav | monotone | 3 | 1.000 | -0.72 | -1.22 | 0.205 | 0.203 | PASS | pitch_chg<0.5st | pitch_chg=-1.22st |
| sp01_combined_s3.wav | too_fast | 3 | 1.400 | -0.55 | 3.35 | 0.425 | 0.398 | PASS | ratio~1.40+/-10% | ratio=1.400 |
| sp01_combined_s3.wav | volume_drop | 3 | 1.000 | -9.00 | -0.00 | 0.276 | 0.276 | PASS | rms_chg~-9+/-2dB | rms_chg=-9.00dB |
| sp01_combined_s4.wav | monotone | 4 | 1.000 | -0.77 | -1.56 | 0.205 | 0.200 | PASS | pitch_chg<0.5st | pitch_chg=-1.56st |
| sp01_combined_s4.wav | too_fast | 4 | 1.600 | -0.18 | 0.82 | 0.425 | 0.402 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp01_combined_s4.wav | volume_drop | 4 | 1.000 | -12.00 | -0.00 | 0.276 | 0.276 | PASS | rms_chg~-12+/-2dB | rms_chg=-12.00dB |
| sp01_combined_s5.wav | monotone | 5 | 1.000 | -0.82 | -1.63 | 0.205 | 0.198 | PASS | pitch_chg<0.5st | pitch_chg=-1.63st |
| sp01_combined_s5.wav | too_fast | 5 | 1.800 | -0.23 | 2.46 | 0.425 | 0.371 | PASS | ratio~1.80+/-10% | ratio=1.800 |
| sp01_combined_s5.wav | volume_drop | 5 | 1.000 | -18.00 | 0.35 | 0.276 | 0.257 | PASS | rms_chg~-18+/-2dB | rms_chg=-18.00dB |
| sp01_erratic_pitch_s2.wav | erratic_pitch | 2 | 1.000 | -0.64 | 0.18 | 0.078 | 0.075 | MEASURED | wobble+/-1.0st (no baseline) | pitch_chg=0.18st |
| sp01_erratic_pitch_s4.wav | erratic_pitch | 4 | 1.000 | -1.08 | 2.65 | 0.078 | 0.071 | MEASURED | wobble+/-3.0st (no baseline) | pitch_chg=2.65st |
| sp01_long_pause_s2.wav | long_pause | 2 | 0.000 | nan | nan | nan | 1.000 | PASS | sil>0.80 (0.7s inserted) | sil=1.000 |
| sp01_long_pause_s4.wav | long_pause | 4 | 0.000 | nan | nan | nan | 1.000 | PASS | sil>0.80 (1.5s inserted) | sil=1.000 |
| sp01_missing_pause_s2.wav | missing_pause | 2 | 1.165 | 0.66 | -0.00 | 0.390 | 0.314 | PASS | sil_chg<0 | sil_chg=-0.076 |
| sp01_missing_pause_s4.wav | missing_pause | 4 | 1.394 | 1.44 | -0.46 | 0.390 | 0.186 | PASS | sil_chg<0 | sil_chg=-0.204 |
| sp01_monotone_s2.wav | monotone | 2 | 1.000 | -0.71 | 0.17 | 0.157 | 0.148 | PASS | pitch_chg<0.5st | pitch_chg=0.17st |
| sp01_monotone_s4.wav | monotone | 4 | 1.000 | -1.26 | -2.16 | 0.157 | 0.148 | PASS | pitch_chg<0.5st | pitch_chg=-2.16st |
| sp01_too_fast_s2.wav | too_fast | 2 | 1.250 | 0.39 | 1.16 | 0.323 | 0.333 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp01_too_fast_s4.wav | too_fast | 4 | 1.600 | 0.08 | 0.68 | 0.323 | 0.300 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp01_too_slow_s2.wav | too_slow | 2 | 0.780 | 0.68 | 0.08 | 0.250 | 0.263 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp01_too_slow_s4.wav | too_slow | 4 | 0.550 | 0.29 | 0.67 | 0.250 | 0.242 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp01_volume_drop_s2.wav | volume_drop | 2 | 1.000 | -6.00 | 0.00 | 0.179 | 0.176 | PASS | rms_chg~-6+/-2dB | rms_chg=-6.00dB |
| sp01_volume_drop_s4.wav | volume_drop | 4 | 1.000 | -12.00 | -0.00 | 0.179 | 0.167 | PASS | rms_chg~-12+/-2dB | rms_chg=-12.00dB |
| sp02_combined_s1.wav | too_slow | 1 | 0.900 | -0.01 | -0.08 | 0.229 | 0.213 | PASS | ratio~0.90+/-10% | ratio=0.900 |
| sp02_combined_s1.wav | erratic_pitch | 1 | 1.000 | -0.22 | -0.66 | 0.333 | 0.333 | MEASURED | wobble+/-0.5st (no baseline) | pitch_chg=-0.66st |
| sp02_combined_s1.wav | volume_drop | 1 | 1.000 | -2.98 | 0.02 | 0.405 | 0.403 | PASS | rms_chg~-3+/-2dB | rms_chg=-2.98dB |
| sp02_combined_s2.wav | too_slow | 2 | 0.780 | -0.19 | 0.46 | 0.229 | 0.199 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp02_combined_s2.wav | erratic_pitch | 2 | 1.000 | -0.46 | -0.72 | 0.333 | 0.333 | MEASURED | wobble+/-1.0st (no baseline) | pitch_chg=-0.72st |
| sp02_combined_s2.wav | volume_drop | 2 | 1.000 | -5.95 | 0.00 | 0.405 | 0.405 | PASS | rms_chg~-6+/-2dB | rms_chg=-5.95dB |
| sp02_combined_s3.wav | too_slow | 3 | 0.650 | -0.05 | 1.02 | 0.229 | 0.207 | PASS | ratio~0.65+/-10% | ratio=0.650 |
| sp02_combined_s3.wav | erratic_pitch | 3 | 1.000 | -0.69 | 0.09 | 0.333 | 0.333 | MEASURED | wobble+/-2.0st (no baseline) | pitch_chg=0.09st |
| sp02_combined_s3.wav | volume_drop | 3 | 1.000 | -8.90 | 0.00 | 0.405 | 0.405 | PASS | rms_chg~-9+/-2dB | rms_chg=-8.90dB |
| sp02_combined_s4.wav | too_slow | 4 | 0.550 | -0.33 | 0.40 | 0.229 | 0.214 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp02_combined_s4.wav | erratic_pitch | 4 | 1.000 | -0.69 | 0.54 | 0.333 | 0.337 | MEASURED | wobble+/-3.0st (no baseline) | pitch_chg=0.54st |
| sp02_combined_s4.wav | volume_drop | 4 | 1.000 | -11.80 | 0.02 | 0.405 | 0.403 | PASS | rms_chg~-12+/-2dB | rms_chg=-11.80dB |
| sp02_combined_s5.wav | too_slow | 5 | 0.450 | -0.31 | 0.73 | 0.229 | 0.197 | PASS | ratio~0.45+/-10% | ratio=0.450 |
| sp02_combined_s5.wav | erratic_pitch | 5 | 1.000 | -0.80 | 0.96 | 0.333 | 0.337 | MEASURED | wobble+/-4.0st (no baseline) | pitch_chg=0.96st |
| sp02_combined_s5.wav | volume_drop | 5 | 1.000 | -17.34 | -0.00 | 0.405 | 0.405 | PASS | rms_chg~-18+/-2dB | rms_chg=-17.34dB |
| sp02_erratic_pitch_s2.wav | erratic_pitch | 2 | 1.000 | -0.35 | 0.15 | 0.182 | 0.182 | MEASURED | wobble+/-1.0st (no baseline) | pitch_chg=0.15st |
| sp02_erratic_pitch_s4.wav | erratic_pitch | 4 | 1.000 | -0.85 | 1.28 | 0.182 | 0.180 | MEASURED | wobble+/-3.0st (no baseline) | pitch_chg=1.28st |
| sp02_long_pause_s2.wav | long_pause | 2 | 0.000 | nan | nan | nan | 1.000 | PASS | sil>0.80 (0.7s inserted) | sil=1.000 |
| sp02_long_pause_s4.wav | long_pause | 4 | 0.000 | nan | nan | nan | 1.000 | PASS | sil>0.80 (1.5s inserted) | sil=1.000 |
| sp02_missing_pause_s2.wav | missing_pause | 2 | 1.103 | 0.42 | -0.02 | 0.316 | 0.248 | PASS | sil_chg<0 | sil_chg=-0.069 |
| sp02_missing_pause_s4.wav | missing_pause | 4 | 1.229 | 0.89 | -0.03 | 0.316 | 0.180 | PASS | sil_chg<0 | sil_chg=-0.136 |
| sp02_monotone_s2.wav | monotone | 2 | 1.000 | -0.28 | -1.18 | 0.275 | 0.275 | PASS | pitch_chg<0.5st | pitch_chg=-1.18st |
| sp02_monotone_s4.wav | monotone | 4 | 1.000 | -0.52 | -2.32 | 0.275 | 0.285 | PASS | pitch_chg<0.5st | pitch_chg=-2.32st |
| sp02_too_fast_s2.wav | too_fast | 2 | 1.250 | 0.21 | -0.04 | 0.282 | 0.256 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp02_too_fast_s4.wav | too_fast | 4 | 1.600 | -0.08 | 0.14 | 0.282 | 0.264 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp02_too_slow_s2.wav | too_slow | 2 | 0.780 | -0.16 | 0.13 | 0.228 | 0.183 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp02_too_slow_s4.wav | too_slow | 4 | 0.550 | -0.44 | 0.73 | 0.228 | 0.174 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp02_volume_drop_s2.wav | volume_drop | 2 | 1.000 | -5.80 | 0.00 | 0.297 | 0.303 | PASS | rms_chg~-6+/-2dB | rms_chg=-5.80dB |
| sp02_volume_drop_s4.wav | volume_drop | 4 | 1.000 | -11.21 | 0.00 | 0.297 | 0.303 | PASS | rms_chg~-12+/-2dB | rms_chg=-11.21dB |

**Summary: 49 PASS / 0 FAIL / 9 MEASURED**

## Notes on erratic_pitch

The `erratic_pitch` flaw adds a smoothed Gaussian wobble (std = wobble_semitones)
to the Praat pitch contour. The expected direction of pitch spread change is
ambiguous: a wobble always increases instantaneous variation, but the measured
spread depends on the random seed and local voiced content.
This effect has **never been measured** in this codebase before this report.
Results are labelled MEASURED and require manual listening to confirm the
wobble is perceptible at each severity level.

## Limitations

- Pitch tracking uses Parselmouth (Praat PSOLA); voiced frames only.
- RMS is computed over the full region including inter-word silences.
- Silence share uses 5% of 95th-percentile RMS as threshold.
- Duration ratio for missing_pause reflects overall shortening.
- This report does **not** replace listening.
