"""Sanity-check the generated dataset and print before/after numbers per flaw.

Usage: python src/dataset/validate.py [--plots]
Checks: sample rate, duration vs label, regions inside file, time map ordering,
clipping, and region statistics (loudness, tempo ratio, pitch spread).
"""
import argparse
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import read_wav, rms_db


def f0_track(x, sr, hop=0.01, win=0.04, fmin=75, fmax=400):
    """Crude autocorrelation F0 (Hz, 0 = unvoiced). Only for validation, not for scoring."""
    h, w = int(hop * sr), int(win * sr)
    lo, hi = int(sr / fmax), int(sr / fmin)
    thr = 0.05 * (np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-9)
    out = []
    for i in range(0, len(x) - w - hi, h):
        fr = x[i:i + w + hi].astype(np.float64)
        a = fr[:w]
        if np.sqrt(np.mean(a ** 2)) < thr:
            out.append(0.0)
            continue
        ac = np.array([np.dot(a, fr[l:l + w]) for l in range(lo, hi)])
        l0 = np.dot(a, a) + 1e-12
        k = int(np.argmax(ac))
        out.append(sr / (lo + k) if ac[k] / l0 > 0.5 else 0.0)
    return np.array(out)


def region_stats(x, sr, s, e):
    seg = x[int(s * sr):int(e * sr)]
    if len(seg) < sr * 0.1:
        return {"rms_db": rms_db(seg), "f0_std_st": float("nan")}
    f0 = f0_track(seg, sr)
    f0 = f0[f0 > 0]
    spread = float(np.std(12 * np.log2(f0))) if len(f0) > 5 else float("nan")
    return {"rms_db": rms_db(seg), "f0_std_st": spread}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="data/labels")
    ap.add_argument("--bad", default="data/bad")
    ap.add_argument("--raw", default="data/raw")
    ap.add_argument("--plots", action="store_true")
    a = ap.parse_args()
    problems = 0
    files = sorted(glob.glob(os.path.join(a.labels, "*.json")))
    if not files:
        print("no label files found")
        sys.exit(1)
    cache = {}
    for lf in files:
        lab = json.load(open(lf))
        name = lab["file"]
        path = os.path.join(a.raw if name.endswith("_ideal.wav") else a.bad, name)
        if not os.path.exists(path):
            print(f"[MISSING] {name}")
            problems += 1
            continue
        x, sr = read_wav(path)
        errs = []
        if sr != 16000:
            errs.append(f"sr={sr}")
        if abs(len(x) / sr - lab["duration"]) > 0.002:
            errs.append(f"duration {len(x)/sr:.3f} != label {lab['duration']}")
        if np.max(np.abs(x)) >= 0.999:
            errs.append("clipping")
        tm = lab["time_map"]
        if any(b[0] < a_[0] or b[1] < a_[1] for a_, b in zip(tm, tm[1:])):
            errs.append("time_map not non-decreasing")
        for f in lab["flaws"]:
            if not (0 <= f["start"] <= f["end"] <= lab["duration"] + 1e-6):
                errs.append(f"{f['type']} region outside file")
            if f["type"] != "long_pause" and f["end"] - f["start"] < 0.2 and f["type"] != "missing_pause":
                errs.append(f"{f['type']} region too short")
        print(f"[{'FAIL' if errs else ' OK '}] {name:32s} {len(x)/sr:6.2f}s  flaws={len(lab['flaws'])}  {'; '.join(errs)}")
        problems += bool(errs)
        # before/after statistics
        ideal_path = os.path.join(a.raw, lab["ideal_file"])
        if lab["flaws"] and os.path.exists(ideal_path):
            if ideal_path not in cache:
                cache[ideal_path] = read_wav(ideal_path)[0]
            xi = cache[ideal_path]
            for f in lab["flaws"]:
                b = region_stats(x, sr, f["start"], f["end"])
                if f["type"] == "long_pause":
                    print(f"        long_pause  inserted {f['end']-f['start']:.2f}s of silence at {f['start']:.2f}s")
                    continue
                i = region_stats(xi, sr, f["src_start"], f["src_end"])
                ratio = (f["src_end"] - f["src_start"]) / max(f["end"] - f["start"], 1e-9)
                print(f"        {f['type']:13s} sev{f['severity']} {f['start']:6.2f}-{f['end']:6.2f}s "
                      f"loudness {i['rms_db']:6.1f}->{b['rms_db']:6.1f} dB  "
                      f"tempo x{ratio:4.2f}  pitch-spread {i['f0_std_st']:4.2f}->{b['f0_std_st']:4.2f} st")
        if a.plots:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            os.makedirs("data/plots", exist_ok=True)
            fig, ax = plt.subplots(figsize=(10, 2.5))
            ax.plot(np.arange(len(x)) / sr, x, lw=0.4)
            for f in lab["flaws"]:
                ax.axvspan(f["start"], f["end"], color="red", alpha=0.25)
            ax.set_title(name)
            ax.set_xlabel("time (s)")
            fig.tight_layout()
            fig.savefig(f"data/plots/{name.replace('.wav', '.png')}", dpi=100)
            plt.close(fig)
    print("\nPROBLEMS:", problems)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
