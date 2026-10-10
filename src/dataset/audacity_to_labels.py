"""Turn an Audacity label-track export into a labels JSON for an ACTED recording.

In Audacity: mark each flaw as a region label whose text is a flaw type
(monotone, too_fast, too_slow, erratic_pitch, volume_drop, long_pause, missing_pause),
then File > Export > Export Labels... (a .txt file with: start<TAB>end<TAB>text).

Usage:
  python src/dataset/audacity_to_labels.py labels.txt data/acted/sp01_acted_monotone.wav sp01 [--severity 3]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from common import read_wav

VALID = {"too_fast", "too_slow", "monotone", "erratic_pitch", "volume_drop", "long_pause", "missing_pause"}

ap = argparse.ArgumentParser()
ap.add_argument("txt")
ap.add_argument("wav")
ap.add_argument("speech_id")
ap.add_argument("--severity", type=int, default=3, help="your judgement 1-5 (acted recordings have no exact value)")
a = ap.parse_args()
x, sr = read_wav(a.wav)
flaws = []
for line in open(a.txt, encoding="utf-8"):
    parts = line.rstrip("\n").split("\t")
    if len(parts) < 3 or parts[0].startswith("\\"):
        continue
    s, e, t = float(parts[0]), float(parts[1]), parts[2].strip()
    if t not in VALID:
        sys.exit(f"unknown flaw type '{t}'. Allowed: {sorted(VALID)}")
    flaws.append({"type": t, "severity": a.severity, "start": round(s, 3), "end": round(e, 3), "params": {}})
name = os.path.basename(a.wav)
doc = {"file": name, "speech_id": a.speech_id, "ideal_file": f"{a.speech_id}_ideal.wav",
       "sr": sr, "duration": round(len(x) / sr, 3), "seed": None, "acted": True,
       "overall_severity": a.severity, "flaws": flaws, "time_map": []}
out = os.path.join("data", "acted", name.replace(".wav", ".json"))
os.makedirs("data/acted", exist_ok=True)
json.dump(doc, open(out, "w"), indent=2)
print(f"wrote {out} with {len(flaws)} flaw regions")
