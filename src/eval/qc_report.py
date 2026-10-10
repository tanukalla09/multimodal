"""Objective QC report: compare each flawed region to the ideal region.

Measures per flaw instance:
  - duration_ratio:   src_dur / flaw_dur  (>1 = faster, <1 = slower)
  - rms_change_db:    rms(flawed) - rms(ideal) in dB
  - pitch_spread_chg: f0 std-dev change in semitones (Parselmouth)
  - silence_share:    fraction of the flawed region that is silence

Expected direction per flaw type (from flaws.py SEVERITY table):
  too_fast:      duration_ratio > 1.0
  too_slow:      duration_ratio < 1.0
  monotone:      pitch_spread_chg < 0  (spread decreases)
  erratic_pitch: pitch_spread_chg != 0 (effect varies; no threshold)
  volume_drop:   rms_change_db < 0  (level drops)
  long_pause:    silence_share high, duration_ratio N/A
  missing_pause: silence_share lower in flawed vs ideal

Tolerance used: see table in output report.
This report does NOT replace listening.

Usage:
  python src/eval/qc_report.py [--labels data/labels] [--bad data/bad] [--raw data/raw]
  Output: data/qc_report.md
"""
import argparse
import glob
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dataset'))
from common import read_wav, rms_db  # noqa: E402
from flaws import SEVERITY  # noqa: E402


EXPECTED = {
    "too_fast":      {"metric": "duration_ratio",     "values": SEVERITY["too_fast"],      "tolerance": 0.10},
    "too_slow":      {"metric": "duration_ratio",     "values": SEVERITY["too_slow"],      "tolerance": 0.10},
    "monotone":      {"metric": "pitch_spread_chg_st","values": SEVERITY["monotone"],      "tolerance": 0.5},
    "erratic_pitch": {"metric": "pitch_spread_chg_st","values": SEVERITY["erratic_pitch"], "tolerance": None},
    "volume_drop":   {"metric": "rms_change_db",      "values": SEVERITY["volume_drop"],   "tolerance": 2.0},
    "long_pause":    {"metric": "silence_share",      "values": SEVERITY["long_pause"],    "tolerance": None},
    "missing_pause": {"metric": "silence_share_chg",  "values": SEVERITY["missing_pause"], "tolerance": None},
}

PARAM_NAMES = {
    "too_fast": "tempo_factor", "too_slow": "tempo_factor",
    "monotone": "f0_scale_kept", "erratic_pitch": "wobble_std_st",
    "volume_drop": "gain_dB", "long_pause": "pause_s",
    "missing_pause": "pause_cut_share",
}


def f0_spread_st(x, sr, hop=0.01, fmin=75, fmax=400):
    try:
        import parselmouth
        snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=sr)
        pitch = snd.to_pitch(time_step=hop, pitch_floor=fmin, pitch_ceiling=fmax)
        f0 = pitch.selected_array["frequency"]
        f0 = f0[f0 > 0]
        if len(f0) < 5:
            return float("nan")
        return float(np.std(12.0 * np.log2(f0)))
    except Exception:
        return float("nan")


def silence_share(x, sr, rms_floor_factor=0.05, hop=0.01):
    h = int(hop * sr)
    n = len(x) // h
    if n < 5:
        return float("nan")
    fr = x[:n * h].reshape(n, h)
    rms_vals = np.sqrt(np.mean(fr.astype(np.float64) ** 2, axis=1))
    thr = rms_floor_factor * (np.percentile(rms_vals, 95) + 1e-12)
    return float(np.mean(rms_vals < thr))


def cut(x, sr, t0, t1):
    i0 = max(0, int(round(t0 * sr)))
    i1 = min(len(x), int(round(t1 * sr)))
    return x[i0:i1]


def measure_flaw(xi, xb, sr, flaw):
    ft = flaw["type"]
    ss, se = flaw["src_start"], flaw["src_end"]
    fs, fe = flaw["start"], flaw["end"]
    sev = flaw["severity"]
    ideal_seg = cut(xi, sr, ss, se)
    flaw_seg = cut(xb, sr, fs, fe)
    ideal_dur = se - ss
    flaw_dur = fe - fs
    dur_ratio = (ideal_dur / flaw_dur) if flaw_dur > 0 else float("nan")
    ideal_rms = rms_db(ideal_seg) if len(ideal_seg) > 10 else float("nan")
    flaw_rms = rms_db(flaw_seg) if len(flaw_seg) > 10 else float("nan")
    rms_chg = (flaw_rms - ideal_rms) if not (math.isnan(ideal_rms) or math.isnan(flaw_rms)) else float("nan")
    ideal_spread = f0_spread_st(ideal_seg, sr)
    flaw_spread = f0_spread_st(flaw_seg, sr)
    pitch_chg = (flaw_spread - ideal_spread) if not (math.isnan(ideal_spread) or math.isnan(flaw_spread)) else float("nan")
    sil_ideal = silence_share(ideal_seg, sr) if len(ideal_seg) > 10 else float("nan")
    sil_flaw = silence_share(flaw_seg, sr) if len(flaw_seg) > 10 else float("nan")
    sil_chg = (sil_flaw - sil_ideal) if not (math.isnan(sil_ideal) or math.isnan(sil_flaw)) else float("nan")

    def r(v):
        return round(v, 3) if not math.isnan(v) else "nan"
    def r2(v):
        return round(v, 2) if not math.isnan(v) else "nan"

    return {
        "type": ft, "severity": sev,
        "ideal_dur": r(ideal_dur), "flaw_dur": r(flaw_dur), "dur_ratio": r(dur_ratio),
        "ideal_rms_db": r2(ideal_rms), "flaw_rms_db": r2(flaw_rms), "rms_chg_db": r2(rms_chg),
        "ideal_pitch_st": r2(ideal_spread), "flaw_pitch_st": r2(flaw_spread), "pitch_chg_st": r2(pitch_chg),
        "sil_ideal": r(sil_ideal), "sil_flaw": r(sil_flaw), "sil_chg": r(sil_chg),
    }


def pass_fail(m, flaw_type, sev):
    exp = EXPECTED.get(flaw_type, {})
    if not exp:
        return "MEASURED", "?", "?"
    sev_idx = int(sev) - 1
    ft = flaw_type

    if ft in ("too_fast", "too_slow"):
        ev = exp["values"][sev_idx]
        mv = m["dur_ratio"]
        tol = exp["tolerance"]
        if mv == "nan":
            return "FAIL", f"ratio={ev:.2f}", "nan"
        ok = abs(mv - ev) <= tol * ev
        return ("PASS" if ok else "FAIL", f"ratio~{ev:.2f}+/-{tol*100:.0f}%", f"ratio={mv:.3f}")

    if ft == "monotone":
        mv = m["pitch_chg_st"]
        tol = exp["tolerance"]
        if mv == "nan":
            return "FAIL", "pitch_chg<0", "nan"
        ok = mv < tol
        return ("PASS" if ok else "FAIL", f"pitch_chg<{tol:.1f}st", f"pitch_chg={mv:.2f}st")

    if ft == "erratic_pitch":
        mv = m["pitch_chg_st"]
        ev = exp["values"][sev_idx]
        if mv == "nan":
            return "MEASURED", "any change", "nan"
        return ("MEASURED", f"wobble+/-{ev:.1f}st (no baseline)", f"pitch_chg={mv:.2f}st")

    if ft == "volume_drop":
        ev = exp["values"][sev_idx]
        mv = m["rms_chg_db"]
        tol = exp["tolerance"]
        if mv == "nan":
            return "FAIL", f"rms_chg~{ev:.0f}dB", "nan"
        ok = abs(mv - ev) <= tol
        return ("PASS" if ok else "FAIL", f"rms_chg~{ev:.0f}+/-{tol:.0f}dB", f"rms_chg={mv:.2f}dB")

    if ft == "long_pause":
        ev = exp["values"][sev_idx]
        sf = m["sil_flaw"]
        if sf == "nan":
            return "FAIL", f"sil>0.80 ({ev:.1f}s inserted)", "nan"
        ok = sf > 0.8
        return ("PASS" if ok else "FAIL", f"sil>0.80 ({ev:.1f}s inserted)", f"sil={sf:.3f}")

    if ft == "missing_pause":
        mv = m["sil_chg"]
        if mv == "nan":
            return "FAIL", "sil_chg<0", "nan"
        ok = mv < 0
        return ("PASS" if ok else "FAIL", "sil_chg<0", f"sil_chg={mv:.3f}")

    return "MEASURED", "?", "?"


def fmt(v, spec=".3f"):
    if v == "nan" or (isinstance(v, float) and math.isnan(v)):
        return "nan"
    return format(v, spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="data/labels")
    ap.add_argument("--bad", default="data/bad")
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--out", default="data/qc_report.md")
    a = ap.parse_args()

    label_files = sorted(glob.glob(os.path.join(a.labels, "*.json")))
    label_files = [f for f in label_files
                   if not os.path.basename(f).startswith("demo_")
                   and not os.path.basename(f).endswith("_ideal.json")]

    ideal_cache = {}
    rows = []

    for lf in label_files:
        lab = json.load(open(lf))
        bad_path = os.path.join(a.bad, lab["file"])
        ideal_path = os.path.join(a.raw, lab["ideal_file"])
        if not os.path.exists(bad_path):
            print(f"[SKIP missing bad] {lab['file']}")
            continue
        if not os.path.exists(ideal_path):
            print(f"[SKIP missing ideal] {lab['ideal_file']}")
            continue
        xb, sr = read_wav(bad_path)
        if ideal_path not in ideal_cache:
            ideal_cache[ideal_path] = read_wav(ideal_path)[0]
        xi = ideal_cache[ideal_path]

        for flaw in lab["flaws"]:
            m = measure_flaw(xi, xb, sr, flaw)
            verdict, exp_str, meas_str = pass_fail(m, flaw["type"], flaw["severity"])
            rows.append((lab["file"], flaw, m, verdict, exp_str, meas_str))
            print(f"  [{verdict:8s}] {lab['file']:38s}  {flaw['type']:14s} sev{flaw['severity']}  "
                  f"exp={exp_str}  meas={meas_str}")

    lines = [
        "# Objective QC Report",
        "",
        "> **DISCLAIMER**: This report measures numbers computed from audio waveforms.",
        "> It does **NOT** replace listening. A PASS means the numerical effect is in the",
        "> expected direction and within tolerance; it does not mean the flaw sounds correct.",
        "",
        "## Severity Table (from `src/dataset/flaws.py`)",
        "",
        "| Flaw | Param | Sev 1 | Sev 2 | Sev 3 | Sev 4 | Sev 5 |",
        "|------|-------|-------|-------|-------|-------|-------|",
    ]
    for ft, vals in SEVERITY.items():
        pn = PARAM_NAMES.get(ft, ft)
        vstr = " | ".join(str(v) for v in vals)
        lines.append(f"| {ft} | {pn} | {vstr} |")

    lines += [
        "",
        "## Tolerances",
        "",
        "| Flaw | Primary Metric | Pass Condition | Tolerance |",
        "|------|----------------|----------------|-----------|",
        "| too_fast | duration_ratio | = expected tempo factor | +/-10% |",
        "| too_slow | duration_ratio | = expected tempo factor | +/-10% |",
        "| monotone | pitch_spread_chg_st | < 0 (spread decreases) | 0.5 st |",
        "| erratic_pitch | pitch_spread_chg_st | any (NEVER measured before) | none |",
        "| volume_drop | rms_change_db | = expected gain_dB | +/-2 dB |",
        "| long_pause | sil_flaw | silence fraction > 0.80 | fixed |",
        "| missing_pause | sil_chg | < 0 (pauses shortened) | must be negative |",
        "",
        "## Expected vs Measured",
        "",
        "| File | Flaw | Sev | DurRatio | RMS_chg_dB | Pitch_chg_st | Sil_ideal | Sil_flaw | Verdict | Expected | Measured |",
        "|------|------|-----|----------|------------|--------------|-----------|----------|---------|----------|----------|",
    ]

    n_pass = n_fail = n_meas = 0
    for (fname, flaw, m, verdict, exp_str, meas_str) in rows:
        marks = {"PASS": "PASS", "FAIL": "FAIL", "MEASURED": "MEASURED"}
        tag = marks.get(verdict, verdict)
        if verdict == "PASS":
            n_pass += 1
        elif verdict == "FAIL":
            n_fail += 1
        else:
            n_meas += 1
        lines.append(
            f"| {fname} | {flaw['type']} | {flaw['severity']}"
            f" | {fmt(m['dur_ratio'])}"
            f" | {fmt(m['rms_chg_db'], '.2f')}"
            f" | {fmt(m['pitch_chg_st'], '.2f')}"
            f" | {fmt(m['sil_ideal'], '.3f')}"
            f" | {fmt(m['sil_flaw'], '.3f')}"
            f" | {tag} | {exp_str} | {meas_str} |"
        )

    lines += [
        "",
        f"**Summary: {n_pass} PASS / {n_fail} FAIL / {n_meas} MEASURED**",
        "",
        "## Notes on erratic_pitch",
        "",
        "The `erratic_pitch` flaw adds a smoothed Gaussian wobble (std = wobble_semitones)",
        "to the Praat pitch contour. The expected direction of pitch spread change is",
        "ambiguous: a wobble always increases instantaneous variation, but the measured",
        "spread depends on the random seed and local voiced content.",
        "This effect has **never been measured** in this codebase before this report.",
        "Results are labelled MEASURED and require manual listening to confirm the",
        "wobble is perceptible at each severity level.",
        "",
        "## Limitations",
        "",
        "- Pitch tracking uses Parselmouth (Praat PSOLA); voiced frames only.",
        "- RMS is computed over the full region including inter-word silences.",
        "- Silence share uses 5% of 95th-percentile RMS as threshold.",
        "- Duration ratio for missing_pause reflects overall shortening.",
        "- This report does **not** replace listening.",
    ]

    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nWrote {a.out}  ({n_pass} PASS / {n_fail} FAIL / {n_meas} MEASURED)")


if __name__ == "__main__":
    main()
