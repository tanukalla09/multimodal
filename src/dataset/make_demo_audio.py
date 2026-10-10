"""Create a synthetic ~29 s 'speech-like' WAV so you can test the whole pipeline
BEFORE you have real recordings. NOT part of the dataset. Also writes a matching
configs/demo_regions.yaml whose regions sit on phrase boundaries.

Usage: python src/dataset/make_demo_audio.py
"""
import os
import sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import SR, write_wav, rms_db

PHRASES = [3.6, 3.4, 3.8, 3.6, 3.5, 3.7, 3.4]   # seconds
PAUSE = 0.6
LEAD = 0.4


def synth(seed=0):
    rng = np.random.default_rng(seed)
    total = LEAD + sum(PHRASES) + PAUSE * len(PHRASES)
    n = int(total * SR)
    sig = np.zeros(n)
    starts, t = [], LEAD
    for dur in PHRASES:
        starts.append(round(t, 3))
        n_syl = int(dur / 0.22)
        syl_len = dur / n_syl
        centers = t + (np.arange(n_syl) + 0.5) * syl_len
        decl = np.linspace(3.0, -3.0, n_syl)              # declination in semitones
        accent = rng.normal(0, 2.0, n_syl)
        f0_c = 120.0 * 2 ** ((decl + accent) / 12.0)
        a = int(t * SR)
        b = int((t + dur) * SR)
        tt = np.arange(a, b) / SR
        f0 = np.interp(tt, centers, f0_c)
        phase = 2 * np.pi * np.cumsum(f0) / SR
        voice = sum(np.sin(k * phase) / k for k in range(1, 16))
        pos = ((tt - t) / syl_len) % 1.0
        env = np.sin(np.pi * pos) ** 2
        sig[a:b] = voice * env
        t += dur + PAUSE
    sig += rng.normal(0, 0.002, n)
    sig *= 10 ** ((-20 - rms_db(sig[sig != 0])) / 20)
    return sig.astype(np.float32), starts


if __name__ == "__main__":
    x, starts = synth()
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("configs", exist_ok=True)
    write_wav("data/raw/demo_ideal.wav", x)
    ends = [round(s + d, 3) for s, d in zip(starts, PHRASES)]
    cfg = {
        "speech_id": "demo", "ideal": "data/raw/demo_ideal.wav", "seed": 42,
        "single_levels": [2, 4],
        "single": {
            "too_fast":    {"start": starts[1], "end": ends[1]},
            "monotone":    {"start": starts[2], "end": ends[2]},
            "volume_drop": {"start": starts[3], "end": ends[3]},
            "long_pause":  {"at": ends[4]},
        },
        "combined": [
            {"type": "monotone",    "start": starts[0], "end": ends[0]},
            {"type": "too_fast",    "start": starts[2], "end": ends[2]},
            {"type": "volume_drop", "start": starts[4], "end": ends[4]},
        ],
    }
    yaml.safe_dump(cfg, open("configs/demo_regions.yaml", "w"), sort_keys=False)
    print(f"wrote data/raw/demo_ideal.wav ({len(x)/SR:.1f} s) and configs/demo_regions.yaml")
