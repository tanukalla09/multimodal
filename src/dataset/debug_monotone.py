"""Measure pitch spread before/after monotone() using Praat's tracker."""
import numpy as np
import parselmouth
from flaws import monotone

SR = 16000

def praat_f0(x):
    snd = parselmouth.Sound(x.astype(np.float64), sampling_frequency=SR)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=400)
    f = pitch.selected_array["frequency"]
    return f[f > 0]

def report(name, x):
    f = praat_f0(x)
    st = 12 * np.log2(f)
    print(f"{name:14s} voiced={len(f):4d}  median={np.median(f):6.1f} Hz  "
          f"spread={np.std(st):5.2f} st  range={st.max()-st.min():5.2f} st")

t = np.arange(int(3 * SR)) / SR
f0 = 150 * 2 ** (3 * np.sin(2 * np.pi * 0.7 * t) / 12)
ph = 2 * np.pi * np.cumsum(f0) / SR
x = (0.2 * sum(np.sin(k * ph) / k for k in range(1, 12))).astype(np.float32)

report("original", x)
for s in (0.0, 0.5, 1.0):
    y = monotone(x, SR, s, np.random.default_rng(0))
    report(f"monotone {s}", y)