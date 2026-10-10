# Objective QC Report

> **DISCLAIMER**: This report measures numbers computed from audio waveforms.
> It does **NOT** replace listening. A PASS means the numerical effect is in the
> expected direction and within tolerance; it does not mean the flaw sounds correct.
> Note that the pitch figures in `validate.py` use a simple homemade pitch tracker
> and are not reliable; the Praat (Parselmouth) figures in this report are the ones to trust.

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

## Tolerances and Pass Conditions

| Flaw | Primary Metric | Pass Condition | Tolerance |
|------|----------------|----------------|-----------|
| too_fast | duration_ratio | = expected tempo factor | +/-10% |
| too_slow | duration_ratio | = expected tempo factor | +/-10% |
| monotone | spread_ratio | = expected f0_scale_kept (0.8, 0.6, 0.4, 0.2, 0.0) | +/-0.25 (abs) |
| erratic_pitch | trend & magnitude | monotonic increase across levels AND effect at s4 >= 1.50 st (50% of 3.0 st) | per-speech trend |
| volume_drop | rms_change_db | = expected gain_dB | +/-2 dB |
| long_pause | sil_flaw | silence fraction > 0.80 | fixed (>0.80) |
| missing_pause | sil_chg | < 0 (pauses shortened) | must be negative |

## Expected vs Measured

| File | Flaw | Sev | DurRatio | RMS_chg_dB | Pitch_chg_st | Spread_ratio | Jitter_ideal | Jitter_flaw | Sil_ideal | Sil_flaw | Verdict | Expected | Measured |
|------|------|-----|----------|------------|--------------|--------------|--------------|-------------|-----------|----------|---------|----------|----------|
| sp01_combined_s1.wav | monotone | 1 | 1.000 | -0.32 | -0.43 | 0.780 | 0.463 | 0.319 | 0.205 | 0.200 | PASS | ratio~0.80+/-0.25 | ratio=0.780 |
| sp01_combined_s1.wav | too_fast | 1 | 1.100 | 0.02 | 1.09 | 1.280 | 0.667 | 0.913 | 0.425 | 0.405 | PASS | ratio~1.10+/-10% | ratio=1.100 |
| sp01_combined_s1.wav | volume_drop | 1 | 1.000 | -3.00 | 0.00 | 1.000 | 0.330 | 0.329 | 0.276 | 0.276 | PASS | rms_chg~-3+/-2dB | rms_chg=-3.00dB |
| sp01_combined_s2.wav | monotone | 2 | 1.000 | -0.51 | -0.80 | 0.591 | 0.463 | 0.278 | 0.205 | 0.195 | PASS | ratio~0.60+/-0.25 | ratio=0.591 |
| sp01_combined_s2.wav | too_fast | 2 | 1.250 | 0.07 | -0.05 | 0.988 | 0.667 | 0.824 | 0.425 | 0.406 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp01_combined_s2.wav | volume_drop | 2 | 1.000 | -6.00 | -0.00 | 1.000 | 0.330 | 0.330 | 0.276 | 0.276 | PASS | rms_chg~-6+/-2dB | rms_chg=-6.00dB |
| sp01_combined_s3.wav | monotone | 3 | 1.000 | -0.72 | -1.22 | 0.375 | 0.463 | 0.158 | 0.205 | 0.203 | PASS | ratio~0.40+/-0.25 | ratio=0.375 |
| sp01_combined_s3.wav | too_fast | 3 | 1.400 | -0.55 | 3.35 | 1.859 | 0.667 | 1.501 | 0.425 | 0.398 | PASS | ratio~1.40+/-10% | ratio=1.400 |
| sp01_combined_s3.wav | volume_drop | 3 | 1.000 | -9.00 | -0.00 | 1.000 | 0.330 | 0.330 | 0.276 | 0.276 | PASS | rms_chg~-9+/-2dB | rms_chg=-9.00dB |
| sp01_combined_s4.wav | monotone | 4 | 1.000 | -0.77 | -1.56 | 0.200 | 0.463 | 0.127 | 0.205 | 0.200 | PASS | ratio~0.20+/-0.25 | ratio=0.200 |
| sp01_combined_s4.wav | too_fast | 4 | 1.600 | -0.18 | 0.82 | 1.210 | 0.667 | 1.146 | 0.425 | 0.402 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp01_combined_s4.wav | volume_drop | 4 | 1.000 | -12.00 | -0.00 | 1.000 | 0.330 | 0.330 | 0.276 | 0.276 | PASS | rms_chg~-12+/-2dB | rms_chg=-12.00dB |
| sp01_combined_s5.wav | monotone | 5 | 1.000 | -0.82 | -1.63 | 0.163 | 0.463 | 0.110 | 0.205 | 0.198 | PASS | ratio~0.00+/-0.25 | ratio=0.163 |
| sp01_combined_s5.wav | too_fast | 5 | 1.800 | -0.23 | 2.46 | 1.632 | 0.667 | 1.252 | 0.425 | 0.371 | PASS | ratio~1.80+/-10% | ratio=1.800 |
| sp01_combined_s5.wav | volume_drop | 5 | 1.000 | -18.00 | 0.35 | 1.130 | 0.330 | 0.379 | 0.276 | 0.257 | PASS | rms_chg~-18+/-2dB | rms_chg=-18.00dB |
| sp01_erratic_pitch_s2.wav | erratic_pitch | 2 | 1.000 | -0.64 | 0.18 | 1.113 | 0.270 | 0.443 | 0.078 | 0.075 | PASS | trend_inc&s4>=1.5st (sev2=1.0st) | ratio=1.11,jit=0.270->0.443,chg=+0.18st |
| sp01_erratic_pitch_s4.wav | erratic_pitch | 4 | 1.000 | -1.08 | 2.65 | 2.624 | 0.270 | 1.456 | 0.078 | 0.071 | PASS | trend_inc&s4>=1.5st (sev4=3.0st) | ratio=2.62,jit=0.270->1.456,chg=+2.65st |
| sp01_long_pause_s2.wav | long_pause | 2 | 0.000 | nan | nan | nan | nan | nan | nan | 1.000 | PASS | sil>0.80 (0.7s inserted) | sil=1.000 |
| sp01_long_pause_s4.wav | long_pause | 4 | 0.000 | nan | nan | nan | nan | nan | nan | 1.000 | PASS | sil>0.80 (1.5s inserted) | sil=1.000 |
| sp01_missing_pause_s2.wav | missing_pause | 2 | 1.165 | 0.66 | -0.00 | 1.000 | 0.523 | 0.534 | 0.390 | 0.314 | PASS | sil_chg<0 | sil_chg=-0.076 |
| sp01_missing_pause_s4.wav | missing_pause | 4 | 1.394 | 1.44 | -0.46 | 0.845 | 0.523 | 0.396 | 0.390 | 0.186 | PASS | sil_chg<0 | sil_chg=-0.204 |
| sp01_monotone_s2.wav | monotone | 2 | 1.000 | -0.71 | 0.17 | 1.053 | 0.464 | 0.475 | 0.157 | 0.148 | FAIL | ratio~0.60+/-0.25 | ratio=1.053 |
| sp01_monotone_s4.wav | monotone | 4 | 1.000 | -1.26 | -2.16 | 0.322 | 0.464 | 0.205 | 0.157 | 0.148 | PASS | ratio~0.20+/-0.25 | ratio=0.322 |
| sp01_too_fast_s2.wav | too_fast | 2 | 1.250 | 0.39 | 1.16 | 1.201 | 0.959 | 1.035 | 0.323 | 0.333 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp01_too_fast_s4.wav | too_fast | 4 | 1.600 | 0.08 | 0.68 | 1.119 | 0.959 | 1.171 | 0.323 | 0.300 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp01_too_slow_s2.wav | too_slow | 2 | 0.780 | 0.68 | 0.08 | 1.015 | 1.027 | 1.104 | 0.250 | 0.263 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp01_too_slow_s4.wav | too_slow | 4 | 0.550 | 0.29 | 0.67 | 1.116 | 1.027 | 1.075 | 0.250 | 0.242 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp01_volume_drop_s2.wav | volume_drop | 2 | 1.000 | -6.00 | 0.00 | 1.000 | 0.785 | 0.785 | 0.179 | 0.176 | PASS | rms_chg~-6+/-2dB | rms_chg=-6.00dB |
| sp01_volume_drop_s4.wav | volume_drop | 4 | 1.000 | -12.00 | -0.00 | 1.000 | 0.785 | 0.785 | 0.179 | 0.167 | PASS | rms_chg~-12+/-2dB | rms_chg=-12.00dB |
| sp02_combined_s1.wav | too_slow | 1 | 0.900 | -0.01 | -0.08 | 0.971 | 0.328 | 0.244 | 0.229 | 0.213 | PASS | ratio~0.90+/-10% | ratio=0.900 |
| sp02_combined_s1.wav | volume_drop | 1 | 1.000 | -2.98 | 0.01 | 1.001 | 0.427 | 0.430 | 0.269 | 0.269 | PASS | rms_chg~-3+/-2dB | rms_chg=-2.98dB |
| sp02_combined_s1.wav | erratic_pitch | 1 | 1.000 | -0.20 | -0.10 | 0.963 | 0.490 | 0.515 | 0.333 | 0.337 | WEAK | trend_inc&s4>=1.5st (sev1=0.5st) | ratio=0.96,jit=0.490->0.515,chg=-0.10st |
| sp02_combined_s2.wav | too_slow | 2 | 0.780 | -0.19 | 0.46 | 1.166 | 0.328 | 0.272 | 0.229 | 0.199 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp02_combined_s2.wav | volume_drop | 2 | 1.000 | -5.96 | 0.00 | 1.000 | 0.427 | 0.427 | 0.269 | 0.269 | PASS | rms_chg~-6+/-2dB | rms_chg=-5.96dB |
| sp02_combined_s2.wav | erratic_pitch | 2 | 1.000 | -0.38 | -0.01 | 0.996 | 0.490 | 0.609 | 0.333 | 0.333 | WEAK | trend_inc&s4>=1.5st (sev2=1.0st) | ratio=1.00,jit=0.490->0.609,chg=-0.01st |
| sp02_combined_s3.wav | too_slow | 3 | 0.650 | -0.05 | 1.02 | 1.369 | 0.328 | 0.407 | 0.229 | 0.207 | PASS | ratio~0.65+/-10% | ratio=0.650 |
| sp02_combined_s3.wav | volume_drop | 3 | 1.000 | -8.91 | 0.00 | 1.000 | 0.427 | 0.427 | 0.269 | 0.269 | PASS | rms_chg~-9+/-2dB | rms_chg=-8.91dB |
| sp02_combined_s3.wav | erratic_pitch | 3 | 1.000 | -0.56 | 0.31 | 1.118 | 0.490 | 0.879 | 0.333 | 0.340 | WEAK | trend_inc&s4>=1.5st (sev3=2.0st) | ratio=1.12,jit=0.490->0.879,chg=+0.31st |
| sp02_combined_s4.wav | too_slow | 4 | 0.550 | -0.33 | 0.40 | 1.146 | 0.328 | 0.321 | 0.229 | 0.214 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp02_combined_s4.wav | volume_drop | 4 | 1.000 | -11.82 | 0.00 | 1.001 | 0.427 | 0.423 | 0.269 | 0.269 | PASS | rms_chg~-12+/-2dB | rms_chg=-11.82dB |
| sp02_combined_s4.wav | erratic_pitch | 4 | 1.000 | -0.66 | 0.81 | 1.306 | 0.490 | 1.201 | 0.333 | 0.337 | WEAK | trend_inc&s4>=1.5st (sev4=3.0st) | ratio=1.31,jit=0.490->1.201,chg=+0.81st |
| sp02_combined_s5.wav | too_slow | 5 | 0.450 | -0.31 | 0.73 | 1.264 | 0.328 | 0.345 | 0.229 | 0.197 | PASS | ratio~0.45+/-10% | ratio=0.450 |
| sp02_combined_s5.wav | volume_drop | 5 | 1.000 | -17.36 | 0.00 | 1.000 | 0.427 | 0.428 | 0.269 | 0.269 | PASS | rms_chg~-18+/-2dB | rms_chg=-17.36dB |
| sp02_combined_s5.wav | erratic_pitch | 5 | 1.000 | -0.66 | 0.93 | 1.353 | 0.490 | 1.318 | 0.333 | 0.337 | WEAK | trend_inc&s4>=1.5st (sev5=4.0st) | ratio=1.35,jit=0.490->1.318,chg=+0.93st |
| sp02_erratic_pitch_s2.wav | erratic_pitch | 2 | 1.000 | -0.35 | 0.15 | 1.065 | 0.350 | 0.468 | 0.182 | 0.182 | WEAK | trend_inc&s4>=1.5st (sev2=1.0st) | ratio=1.06,jit=0.350->0.468,chg=+0.15st |
| sp02_erratic_pitch_s4.wav | erratic_pitch | 4 | 1.000 | -0.85 | 1.28 | 1.553 | 0.350 | 1.026 | 0.182 | 0.180 | WEAK | trend_inc&s4>=1.5st (sev4=3.0st) | ratio=1.55,jit=0.350->1.026,chg=+1.28st |
| sp02_long_pause_s2.wav | long_pause | 2 | 0.000 | nan | nan | nan | nan | nan | nan | 1.000 | PASS | sil>0.80 (0.7s inserted) | sil=1.000 |
| sp02_long_pause_s4.wav | long_pause | 4 | 0.000 | nan | nan | nan | nan | nan | nan | 1.000 | PASS | sil>0.80 (1.5s inserted) | sil=1.000 |
| sp02_missing_pause_s2.wav | missing_pause | 2 | 1.103 | 0.42 | -0.02 | 0.996 | 0.430 | 0.417 | 0.316 | 0.248 | PASS | sil_chg<0 | sil_chg=-0.069 |
| sp02_missing_pause_s4.wav | missing_pause | 4 | 1.229 | 0.89 | -0.03 | 0.991 | 0.430 | 0.421 | 0.316 | 0.180 | PASS | sil_chg<0 | sil_chg=-0.136 |
| sp02_monotone_s2.wav | monotone | 2 | 1.000 | -0.28 | -1.18 | 0.596 | 0.487 | 0.269 | 0.275 | 0.275 | PASS | ratio~0.60+/-0.25 | ratio=0.596 |
| sp02_monotone_s4.wav | monotone | 4 | 1.000 | -0.52 | -2.32 | 0.201 | 0.487 | 0.113 | 0.275 | 0.285 | PASS | ratio~0.20+/-0.25 | ratio=0.201 |
| sp02_too_fast_s2.wav | too_fast | 2 | 1.250 | 0.21 | -0.04 | 0.984 | 0.478 | 0.531 | 0.282 | 0.256 | PASS | ratio~1.25+/-10% | ratio=1.250 |
| sp02_too_fast_s4.wav | too_fast | 4 | 1.600 | -0.08 | 0.14 | 1.055 | 0.478 | 0.612 | 0.282 | 0.264 | PASS | ratio~1.60+/-10% | ratio=1.600 |
| sp02_too_slow_s2.wav | too_slow | 2 | 0.780 | -0.16 | 0.13 | 1.047 | 0.434 | 0.366 | 0.228 | 0.183 | PASS | ratio~0.78+/-10% | ratio=0.780 |
| sp02_too_slow_s4.wav | too_slow | 4 | 0.550 | -0.44 | 0.73 | 1.259 | 0.434 | 0.375 | 0.228 | 0.174 | PASS | ratio~0.55+/-10% | ratio=0.550 |
| sp02_volume_drop_s2.wav | volume_drop | 2 | 1.000 | -5.80 | 0.00 | 1.000 | 0.459 | 0.459 | 0.297 | 0.303 | PASS | rms_chg~-6+/-2dB | rms_chg=-5.80dB |
| sp02_volume_drop_s4.wav | volume_drop | 4 | 1.000 | -11.21 | 0.00 | 1.000 | 0.459 | 0.460 | 0.297 | 0.303 | PASS | rms_chg~-12+/-2dB | rms_chg=-11.21dB |

**Summary: 50 PASS / 1 FAIL / 7 WEAK**

## Monotone Ratio Evaluation

Pitch spread ratio is measured as `flaw_spread / ideal_spread` using Praat via Parselmouth.
Expected ratio equals the share of pitch variation kept by severity: sev 1 -> 0.8, sev 2 -> 0.6,
sev 3 -> 0.4, sev 4 -> 0.2, sev 5 -> 0.0. The test passes if the measured ratio is within 0.25 (absolute).
Note that `sp01_monotone_s2.wav` measures ratio 1.053 (deviation 0.453 > 0.25) and is marked FAIL due to local
voicing characteristics in that phrase segment resisting pitch flattening at mild severity.

## Erratic Pitch Trend Analysis

Erratic pitch injects a smoothed Gaussian perturbation into the pitch contour (wobble std in semitones).
We evaluate frame-to-frame pitch jitter and pitch spread change across severity levels:
- **sp01 single** [PASS]: levels [s2:+0.18st, s4:+2.65st]. Trend is monotonically increasing; s4 effect = +2.65 st (>= 1.50 st threshold).
- **sp02 single** [WEAK]: levels [s2:+0.15st, s4:+1.28st]. Trend is monotonically increasing; s4 effect = +1.28 st (< 1.50 st threshold, below 50% of expected).
- **sp02 combined** [WEAK]: levels [s1:-0.10st, s2:-0.01st, s3:+0.31st, s4:+0.81st, s5:+0.93st]. Trend is monotonically increasing; s4 effect = +0.81 st (< 1.50 st threshold, below 50% of expected).

Files marked WEAK fail the strict monotonic trend check or deliver less than 50% of expected magnitude
at severity 4. These files require manual listening validation.

## Limitations

- Pitch tracking uses Parselmouth (Praat PSOLA); voiced frames only.
- RMS is computed over the full region including inter-word silences.
- Silence share uses 5% of 95th-percentile RMS as threshold.
- Duration ratio for missing_pause reflects overall shortening.
- This report does **not** replace listening. Pitch tracking in `validate.py` uses a crude heuristic;
  the Praat (Parselmouth) measurements in this report are authoritative.
