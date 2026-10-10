"""A/B listening clip: IDEAL region, short gap, FLAWED region, for each flaw in a label.
Usage: python src/dataset/ab_clip.py data/labels/sp01_too_fast_s4.json [--pad 1.0]
Writes data/ab/<name>_AB.wav
"""
import argparse
import json
import os

import numpy as np

from common import SR, read_wav, write_wav

ap = argparse.ArgumentParser()
ap.add_argument("label")
ap.add_argument("--pad", type=float, default=1.0)
ap.add_argument("--raw", default="data/raw")
ap.add_argument("--bad", default="data/bad")
ap.add_argument("--out", default="data/ab")
a = ap.parse_args()

lab = json.load(open(a.label))
ideal, sr = read_wav(os.path.join(a.raw, lab["ideal_file"]))
flawed, _ = read_wav(os.path.join(a.bad, lab["file"]))
os.makedirs(a.out, exist_ok=True)


def cut(x, t0, t1):
    i0 = max(0, int(round(t0 * sr)))
    i1 = min(len(x), int(round(t1 * sr)))
    return x[i0:i1]


gap = np.zeros(int(0.8 * sr), dtype=np.float32)
parts = []
for fl in lab["flaws"]:
    A = cut(ideal, fl["src_start"] - a.pad, fl["src_end"] + a.pad)
    B = cut(flawed, fl["start"] - a.pad, fl["end"] + a.pad)
    parts += [A, gap, B, gap, gap]
    print(f'{fl["type"]} s{fl["severity"]}: ideal {fl["src_start"]:.2f}-{fl["src_end"]:.2f} s | '
          f'flawed {fl["start"]:.2f}-{fl["end"]:.2f} s')
if parts:
    out = os.path.join(a.out, os.path.splitext(lab["file"])[0] + "_AB.wav")
    write_wav(out, np.concatenate(parts).astype(np.float32), SR)
    print("wrote", out, "(first the IDEAL, then the FLAWED)")
