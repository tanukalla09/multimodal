"""Convert any recording into the dataset format: 16 kHz, mono, RMS-normalised WAV.

Usage:
  python src/dataset/prepare.py INPUT.wav OUTPUT.wav [--start S] [--end E] [--target-db -20]
"""
import argparse
from math import gcd

import numpy as np
from scipy.signal import resample_poly

from common import SR, read_wav, write_wav, rms_db


def prepare(x, sr, start=None, end=None, target_db=-20.0, peak=0.97):
    if start is not None or end is not None:
        a = int(round((start or 0.0) * sr))
        b = int(round(end * sr)) if end is not None else len(x)
        x = x[a:b]
    if sr != SR:
        g = gcd(int(sr), SR)
        x = resample_poly(x, SR // g, int(sr) // g)
    x = x - np.mean(x)                      # remove DC offset
    gain = 10 ** ((target_db - rms_db(x)) / 20.0)
    x = x * gain
    m = np.max(np.abs(x))
    if m > peak:                            # keep headroom, never clip
        x = x * (peak / m)
    return x.astype(np.float32)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--target-db", type=float, default=-20.0)
    a = ap.parse_args()
    x, sr = read_wav(a.inp)
    y = prepare(x, sr, a.start, a.end, a.target_db)
    write_wav(a.out, y, SR)
    print(f"wrote {a.out}: {len(y)/SR:.2f} s, {SR} Hz, mono, RMS {rms_db(y):.1f} dBFS")
