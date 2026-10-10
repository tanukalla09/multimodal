"""Make FAKE detector output from the labels (noise added) so you can test
evaluate.py before Member C's detector exists. Results are meaningless as science.

Usage: python src/eval/make_fake_preds.py [--labels data/labels] [--out data/preds_fake]
"""
import argparse
import glob
import json
import os

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--labels", default="data/labels")
ap.add_argument("--out", default="data/preds_fake")
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()
rng = np.random.default_rng(a.seed)
os.makedirs(a.out, exist_ok=True)
for lf in sorted(glob.glob(os.path.join(a.labels, "*.json"))):
    lab = json.load(open(lf))
    flaws = []
    for f in lab["flaws"]:
        if rng.random() < 0.85:                        # miss 15 % of flaws
            flaws.append({"type": f["type"],
                          "start": f["start"] + float(rng.normal(0, 0.15)),
                          "end": f["end"] + float(rng.normal(0, 0.15))})
    if rng.random() < 0.3:                             # one false alarm
        s = float(rng.uniform(0, max(lab["duration"] - 3, 1)))
        flaws.append({"type": "monotone", "start": s, "end": s + 2.0})
    score = 100 - 15 * lab["overall_severity"] + float(rng.normal(0, 4))
    stem = os.path.splitext(os.path.basename(lf))[0]
    json.dump({"flaws": flaws, "scores": {"overall": round(score, 1)}},
              open(os.path.join(a.out, stem + ".json"), "w"), indent=2)
print("fake predictions written to", a.out)
