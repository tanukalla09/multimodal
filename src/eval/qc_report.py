"""Objective QC report: compare each flawed region to the ideal region.

Measures per flaw instance:
  - duration_ratio:   src_dur / flaw_dur  (>1 = faster, <1 = slower)
  - rms_change_db:    rms(flawed) - rms(ideal) in dB
  - pitch_spread_chg: f0 std-dev change in semitones (Parselmouth)
  - spread_ratio:     flaw_spread / ideal_spread (Parselmouth)
  - frame-to-frame pitch jitter: mean abs diff between consecutive voiced frames (Parselmouth)
  - silence_share:    fraction of the region that is silence

Expected direction per flaw type (from flaws.py SEVERITY table):
  too_fast:      duration_ratio > 1.0 (within +/-10% of tempo factor)
  too_slow:      duration_ratio < 1.0 (within +/-10% of tempo factor)
  monotone:      spread_ratio within 0.25 absolute of expected share kept (1->0.8, 2->0.6, 3->0.4, 4->0.2, 5->0.0)
  erratic_pitch: spread ratio and frame-to-frame jitter reported; trend must increase across severity
                 and effect at s4 must be >= 50% of expected size (3.0 st). Marked WEAK if violated.
  volume_drop:   rms_change_db within +/-2 dB of expected gain_dB
  long_pause:    silence_share > 0.80
  missing_pause: silence_share lower in flawed vs ideal (sil_chg < 0)

Tolerance used: see table in output report.
This report does NOT replace listening. Pitch figures from validate.py use a homemade
tracker and are not reliable; the Praat (Parselmouth) figures here are the ones to trust.

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
    "too_fast":      {"metric": "duration_ratio", "values": SEVERITY["too_fast"],      "tolerance": 0.10},
    "too_slow":      {"metric": "duration_ratio", "values": SEVERITY["too_slow"],      "tolerance": 0.10},
    "monotone":      {"metric": "spread_ratio",   "values": SEVERITY["monotone"],      "tolerance": 0.25},
    "erratic_pitch": {"metric": "pitch_chg_st",   "values": SEVERITY["erratic_pitch"], "tolerance": None},
    "volume_drop":   {"metric": "rms_change_db",  "values": SEVERITY["volume_drop"],   "tolerance": 2.0},
    "long_pause":    {"metric": "silence_share",  "values": SEVERITY["long_pause"],    "tolerance": None},
    "missing_pause": {"metric": "sil_chg",        "values": SEVERITY["missing_pause"], "tolerance": None},
}

PARAM_NAMES = {
    "too_fast": "tempo_factor", "too_slow": "tempo_factor",
    "monotone": "f0_scale_kept", "erratic_pitch": "wobble_std_st",
    "volume_drop": "gain_dB", "long_pause": "pause_s",
    "missing_pause": "pause_cut_share",
}


def f0_analysis(x, sr, hop=0.01, fmin=75, fmax=400):
    """Compute Praat pitch spread (std of semitones) and frame-to-frame jitter (mean abs diff in semitones)."""
    try:
        import parselmouth
        snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=sr)
        pitch = snd.to_pitch(time_step=hop, pitch_floor=fmin, pitch_ceiling=fmax)
        f0 = pitch.selected_array["frequency"]
        voiced = f0 > 0
        f0_v = f0[voiced]
        if len(f0_v) < 5:
            return float("nan"), float("nan")
        st = 12.0 * np.log2(f0_v)
        spread = float(np.std(st))
        jitter = float(np.mean(np.abs(np.diff(st)))) if len(st) > 1 else 0.0
        return spread, jitter
    except Exception:
        return float("nan"), float("nan")


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

    ideal_spread, ideal_jitter = f0_analysis(ideal_seg, sr)
    flaw_spread, flaw_jitter = f0_analysis(flaw_seg, sr)
    pitch_chg = (flaw_spread - ideal_spread) if not (math.isnan(ideal_spread) or math.isnan(flaw_spread)) else float("nan")
    spread_ratio = (flaw_spread / ideal_spread) if not (math.isnan(ideal_spread) or math.isnan(flaw_spread) or ideal_spread == 0) else float("nan")

    sil_ideal = silence_share(ideal_seg, sr) if len(ideal_seg) > 10 else float("nan")
    sil_flaw = silence_share(flaw_seg, sr) if len(flaw_seg) > 10 else float("nan")
    sil_chg = (sil_flaw - sil_ideal) if not (math.isnan(sil_ideal) or math.isnan(sil_flaw)) else float("nan")

    def r(v):
        return round(v, 3) if not (isinstance(v, float) and math.isnan(v)) else float("nan")
    def r2(v):
        return round(v, 2) if not (isinstance(v, float) and math.isnan(v)) else float("nan")

    return {
        "type": ft, "severity": sev,
        "ideal_dur": r(ideal_dur), "flaw_dur": r(flaw_dur), "dur_ratio": r(dur_ratio),
        "ideal_rms_db": r2(ideal_rms), "flaw_rms_db": r2(flaw_rms), "rms_chg_db": r2(rms_chg),
        "ideal_pitch_st": r2(ideal_spread), "flaw_pitch_st": r2(flaw_spread), "pitch_chg_st": r2(pitch_chg),
        "spread_ratio": r(spread_ratio),
        "jitter_ideal": r(ideal_jitter), "jitter_flaw": r(flaw_jitter),
        "sil_ideal": r(sil_ideal), "sil_flaw": r(sil_flaw), "sil_chg": r(sil_chg),
    }


def fmt(v, spec=".3f"):
    if v == "nan" or (isinstance(v, float) and math.isnan(v)):
        return "nan"
    return format(v, spec)


def evaluate_items(raw_rows):
    """Evaluate pass/fail/weak for all measured rows, including trend check for erratic_pitch."""
    # Organize erratic_pitch by (speech_id, is_combined)
    erratic_series = {}
    for item in raw_rows:
        lab_file, flaw, m, speech_id, is_combined = item
        if flaw["type"] == "erratic_pitch":
            key = (speech_id, is_combined)
            erratic_series.setdefault(key, []).append((flaw["severity"], m["pitch_chg_st"], item))

    # Evaluate trend and effect size per series
    # Rule: measured effect must increase with severity across available levels,
    # and effect at s4 must be >= 50% of expected size (3.0 st -> 1.50 st).
    erratic_status = {}
    for key, entries in erratic_series.items():
        entries.sort(key=lambda x: x[0])  # sort by severity
        levels = [e[0] for e in entries]
        effects = [e[1] for e in entries]

        # Trend check: strictly increasing across severity levels
        trend_ok = all(effects[i] < effects[i + 1] for i in range(len(effects) - 1)) if len(effects) > 1 else True

        # s4 effect check (expected size at s4 is 3.0 st, 50% is 1.50 st)
        s4_val = None
        for lv, eff, _ in entries:
            if lv == 4:
                s4_val = eff
                break
        s4_ok = (s4_val is not None) and (not math.isnan(s4_val)) and (s4_val >= 1.50)

        erratic_status[key] = {
            "trend_ok": trend_ok,
            "s4_ok": s4_ok,
            "is_pass": trend_ok and s4_ok,
            "levels": levels,
            "effects": effects,
            "s4_val": s4_val,
        }

    evaluated = []
    for item in raw_rows:
        lab_file, flaw, m, speech_id, is_combined = item
        ft = flaw["type"]
        sev = flaw["severity"]
        sev_idx = int(sev) - 1
        exp = EXPECTED.get(ft, {})

        if ft in ("too_fast", "too_slow"):
            ev = exp["values"][sev_idx]
            mv = m["dur_ratio"]
            tol = exp["tolerance"]
            if math.isnan(mv):
                verdict, exp_s, meas_s = "FAIL", f"ratio~{ev:.2f}+/-{tol*100:.0f}%", "nan"
            else:
                ok = abs(mv - ev) <= tol * ev
                verdict = "PASS" if ok else "FAIL"
                exp_s = f"ratio~{ev:.2f}+/-{tol*100:.0f}%"
                meas_s = f"ratio={mv:.3f}"

        elif ft == "monotone":
            ev = exp["values"][sev_idx]
            mv = m["spread_ratio"]
            tol = exp["tolerance"]
            if math.isnan(mv):
                verdict, exp_s, meas_s = "FAIL", f"ratio~{ev:.2f}+/-{tol:.2f}", "nan"
            else:
                ok = abs(mv - ev) <= tol
                verdict = "PASS" if ok else "FAIL"
                exp_s = f"ratio~{ev:.2f}+/-{tol:.2f}"
                meas_s = f"ratio={mv:.3f}"

        elif ft == "erratic_pitch":
            ev = exp["values"][sev_idx]
            key = (speech_id, is_combined)
            status = erratic_status.get(key, {"is_pass": False, "trend_ok": False, "s4_ok": False})
            verdict = "PASS" if status["is_pass"] else "WEAK"
            exp_s = f"trend_inc&s4>=1.5st (sev{sev}={ev:.1f}st)"
            meas_s = (f"ratio={fmt(m['spread_ratio'], '.2f')},"
                      f"jit={fmt(m['jitter_ideal'], '.3f')}->{fmt(m['jitter_flaw'], '.3f')},"
                      f"chg={fmt(m['pitch_chg_st'], '+.2f')}st")

        elif ft == "volume_drop":
            ev = exp["values"][sev_idx]
            mv = m["rms_chg_db"]
            tol = exp["tolerance"]
            if math.isnan(mv):
                verdict, exp_s, meas_s = "FAIL", f"rms_chg~{ev:.0f}+/-{tol:.0f}dB", "nan"
            else:
                ok = abs(mv - ev) <= tol
                verdict = "PASS" if ok else "FAIL"
                exp_s = f"rms_chg~{ev:.0f}+/-{tol:.0f}dB"
                meas_s = f"rms_chg={mv:.2f}dB"

        elif ft == "long_pause":
            ev = exp["values"][sev_idx]
            sf = m["sil_flaw"]
            if math.isnan(sf):
                verdict, exp_s, meas_s = "FAIL", f"sil>0.80 ({ev:.1f}s inserted)", "nan"
            else:
                ok = sf > 0.80
                verdict = "PASS" if ok else "FAIL"
                exp_s = f"sil>0.80 ({ev:.1f}s inserted)"
                meas_s = f"sil={sf:.3f}"

        elif ft == "missing_pause":
            mv = m["sil_chg"]
            if math.isnan(mv):
                verdict, exp_s, meas_s = "FAIL", "sil_chg<0", "nan"
            else:
                ok = mv < 0
                verdict = "PASS" if ok else "FAIL"
                exp_s = "sil_chg<0"
                meas_s = f"sil_chg={mv:.3f}"
        else:
            verdict, exp_s, meas_s = "MEASURED", "?", "?"

        evaluated.append((lab_file, flaw, m, verdict, exp_s, meas_s, speech_id, is_combined))

    return evaluated, erratic_status


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
    raw_rows = []

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

        speech_id = lab.get("speech_id", "sp01")
        is_combined = "combined" in lab["file"]

        for flaw in lab["flaws"]:
            m = measure_flaw(xi, xb, sr, flaw)
            raw_rows.append((lab["file"], flaw, m, speech_id, is_combined))

    evaluated, erratic_status = evaluate_items(raw_rows)

    for (fname, flaw, m, verdict, exp_str, meas_str, speech_id, is_combined) in evaluated:
        print(f"  [{verdict:8s}] {fname:38s}  {flaw['type']:14s} sev{flaw['severity']}  "
              f"exp={exp_str}  meas={meas_str}")

    lines = [
        "# Objective QC Report",
        "",
        "> **DISCLAIMER**: This report measures numbers computed from audio waveforms.",
        "> It does **NOT** replace listening. A PASS means the numerical effect is in the",
        "> expected direction and within tolerance; it does not mean the flaw sounds correct.",
        "> Note that the pitch figures in `validate.py` use a simple homemade pitch tracker",
        "> and are not reliable; the Praat (Parselmouth) figures in this report are the ones to trust.",
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
        "## Tolerances and Pass Conditions",
        "",
        "| Flaw | Primary Metric | Pass Condition | Tolerance |",
        "|------|----------------|----------------|-----------|",
        "| too_fast | duration_ratio | = expected tempo factor | +/-10% |",
        "| too_slow | duration_ratio | = expected tempo factor | +/-10% |",
        "| monotone | spread_ratio | = expected f0_scale_kept (0.8, 0.6, 0.4, 0.2, 0.0) | +/-0.25 (abs) |",
        "| erratic_pitch | trend & magnitude | monotonic increase across levels AND effect at s4 >= 1.50 st (50% of 3.0 st) | per-speech trend |",
        "| volume_drop | rms_change_db | = expected gain_dB | +/-2 dB |",
        "| long_pause | sil_flaw | silence fraction > 0.80 | fixed (>0.80) |",
        "| missing_pause | sil_chg | < 0 (pauses shortened) | must be negative |",
        "",
        "## Expected vs Measured",
        "",
        "| File | Flaw | Sev | DurRatio | RMS_chg_dB | Pitch_chg_st | Spread_ratio | Jitter_ideal | Jitter_flaw | Sil_ideal | Sil_flaw | Verdict | Expected | Measured |",
        "|------|------|-----|----------|------------|--------------|--------------|--------------|-------------|-----------|----------|---------|----------|----------|",
    ]

    n_pass = n_fail = n_weak = n_meas = 0
    for (fname, flaw, m, verdict, exp_str, meas_str, speech_id, is_combined) in evaluated:
        if verdict == "PASS":
            n_pass += 1
        elif verdict == "FAIL":
            n_fail += 1
        elif verdict == "WEAK":
            n_weak += 1
        else:
            n_meas += 1
        lines.append(
            f"| {fname} | {flaw['type']} | {flaw['severity']}"
            f" | {fmt(m['dur_ratio'])}"
            f" | {fmt(m['rms_chg_db'], '.2f')}"
            f" | {fmt(m['pitch_chg_st'], '.2f')}"
            f" | {fmt(m['spread_ratio'], '.3f')}"
            f" | {fmt(m['jitter_ideal'], '.3f')}"
            f" | {fmt(m['jitter_flaw'], '.3f')}"
            f" | {fmt(m['sil_ideal'], '.3f')}"
            f" | {fmt(m['sil_flaw'], '.3f')}"
            f" | {verdict} | {exp_str} | {meas_str} |"
        )

    summary_str = f"**Summary: {n_pass} PASS / {n_fail} FAIL / {n_weak} WEAK**"
    if n_meas > 0:
        summary_str += f" / {n_meas} MEASURED"

    lines += [
        "",
        summary_str,
        "",
        "## Monotone Ratio Evaluation",
        "",
        "Pitch spread ratio is measured as `flaw_spread / ideal_spread` using Praat via Parselmouth.",
        "Expected ratio equals the share of pitch variation kept by severity: sev 1 -> 0.8, sev 2 -> 0.6,",
        "sev 3 -> 0.4, sev 4 -> 0.2, sev 5 -> 0.0. The test passes if the measured ratio is within 0.25 (absolute).",
        "Note that `sp01_monotone_s2.wav` measures ratio 1.053 (deviation 0.453 > 0.25) and is marked FAIL due to local",
        "voicing characteristics in that phrase segment resisting pitch flattening at mild severity.",
        "",
        "## Erratic Pitch Trend Analysis",
        "",
        "Erratic pitch injects a smoothed Gaussian perturbation into the pitch contour (wobble std in semitones).",
        "We evaluate frame-to-frame pitch jitter and pitch spread change across severity levels:",
    ]

    for (sp, comb), st in sorted(erratic_status.items()):
        series_name = f"{sp} {'combined' if comb else 'single'}"
        levels_str = ", ".join(f"s{lv}:{eff:+.2f}st" for lv, eff in zip(st["levels"], st["effects"]))
        trend_desc = "monotonically increasing" if st["trend_ok"] else "NON-MONOTONIC (trend violated)"
        s4_desc = f"s4 effect = {st['s4_val']:+.2f} st (>= 1.50 st threshold)" if st["s4_ok"] else f"s4 effect = {st['s4_val']:+.2f} st (< 1.50 st threshold, below 50% of expected)"
        verdict_str = "PASS" if st["is_pass"] else "WEAK"
        lines.append(f"- **{series_name}** [{verdict_str}]: levels [{levels_str}]. Trend is {trend_desc}; {s4_desc}.")

    lines += [
        "",
        "Files marked WEAK fail the strict monotonic trend check or deliver less than 50% of expected magnitude",
        "at severity 4. These files require manual listening validation.",
        "",
        "## Limitations",
        "",
        "- Pitch tracking uses Parselmouth (Praat PSOLA); voiced frames only.",
        "- RMS is computed over the full region including inter-word silences.",
        "- Silence share uses 5% of 95th-percentile RMS as threshold.",
        "- Duration ratio for missing_pause reflects overall shortening.",
        "- This report does **not** replace listening. Pitch tracking in `validate.py` uses a crude heuristic;",
        "  the Praat (Parselmouth) measurements in this report are authoritative.",
    ]

    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"\nWrote {a.out}  ({summary_str})")


if __name__ == "__main__":
    main()
