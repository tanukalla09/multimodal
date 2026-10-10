"""Score a detector against the ground-truth labels.

Prediction files: <pred_dir>/<file stem>.json, same shape as the team's JSON contract:
  {"flaws": [{"start": 12.0, "end": 14.3, "type": "monotone", ...}],
   "scores": {"overall": 59}}

Usage:
  python src/eval/evaluate.py --labels data/labels --preds data/preds [--iou 0.3] [--strict-type]
Outputs: console table + data/eval_results.json
"""
import argparse
import glob
import json
import os

import numpy as np
from scipy.stats import spearmanr


def iou(a, b):
    inter = max(0.0, min(a[1], b[1]) - max(a[0], b[0]))
    union = (a[1] - a[0]) + (b[1] - b[0]) - inter
    return inter / union if union > 0 else 0.0


def match(truth, pred, thr=0.3, strict_type=False):
    """Greedy one-to-one matching by IoU. Returns list of (truth_i, pred_j, iou)."""
    cand = []
    for i, t in enumerate(truth):
        for j, p in enumerate(pred):
            if strict_type and t["type"] != p.get("type"):
                continue
            v = iou((t["start"], t["end"]), (p["start"], p["end"]))
            if v >= thr:
                cand.append((v, i, j))
    cand.sort(reverse=True)
    used_t, used_p, out = set(), set(), []
    for v, i, j in cand:
        if i in used_t or j in used_p:
            continue
        used_t.add(i)
        used_p.add(j)
        out.append((i, j, v))
    return out


def evaluate(labels_dir, preds_dir, thr=0.3, strict_type=False):
    tp = fp = fn = 0
    start_err, end_err, type_ok, type_n = [], [], 0, 0
    sev, score = [], []
    per_file = []
    for lf in sorted(glob.glob(os.path.join(labels_dir, "*.json"))):
        lab = json.load(open(lf))
        stem = os.path.splitext(os.path.basename(lf))[0]
        pf = os.path.join(preds_dir, stem + ".json")
        if not os.path.exists(pf):
            continue
        pred = json.load(open(pf))
        truth, det = lab["flaws"], pred.get("flaws", [])
        m = match(truth, det, thr, strict_type)
        tp += len(m)
        fn += len(truth) - len(m)
        fp += len(det) - len(m)
        for i, j, _ in m:
            start_err.append(abs(truth[i]["start"] - det[j]["start"]))
            end_err.append(abs(truth[i]["end"] - det[j]["end"]))
            type_n += 1
            type_ok += truth[i]["type"] == det[j].get("type")
        if "overall" in pred.get("scores", {}):
            sev.append(lab["overall_severity"])
            score.append(pred["scores"]["overall"])
        per_file.append({"file": stem, "truth": len(truth), "detected": len(det), "matched": len(m)})
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    rho = None
    if len(set(sev)) > 1 and len(set(score)) > 1:
        rho = float(spearmanr(sev, score)[0])
    return {
        "files_evaluated": len(per_file), "iou_threshold": thr, "strict_type": strict_type,
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
        "mean_start_error_s": round(float(np.mean(start_err)), 3) if start_err else None,
        "mean_end_error_s": round(float(np.mean(end_err)), 3) if end_err else None,
        "type_accuracy_on_matched": round(type_ok / type_n, 3) if type_n else None,
        "spearman_severity_vs_score": None if rho is None else round(rho, 3),
        "per_file": per_file,
        "_sev": sev, "_score": score,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default="data/labels")
    ap.add_argument("--preds", default="data/preds")
    ap.add_argument("--iou", type=float, default=0.3)
    ap.add_argument("--strict-type", action="store_true")
    ap.add_argument("--out", default="data/eval_results.json")
    ap.add_argument("--plot", default="data/plots/score_vs_severity.png")
    a = ap.parse_args()
    r = evaluate(a.labels, a.preds, a.iou, a.strict_type)
    for k, v in r.items():
        if k not in ("per_file", "_sev", "_score"):
            print(f"{k:28s} {v}")
    if r["_sev"]:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        os.makedirs(os.path.dirname(a.plot), exist_ok=True)
        plt.figure(figsize=(4.5, 3.2))
        plt.scatter(r["_sev"], r["_score"])
        plt.xlabel("injected severity (0 = ideal)")
        plt.ylabel("overall score")
        plt.title(f"Spearman = {r['spearman_severity_vs_score']}")
        plt.tight_layout()
        plt.savefig(a.plot, dpi=120)
        print("plot:", a.plot)
    out = {k: v for k, v in r.items() if not k.startswith("_")}
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print("saved:", a.out)


if __name__ == "__main__":
    main()
