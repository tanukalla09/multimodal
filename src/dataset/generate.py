"""Build every flawed file + labels.json for one speech from its regions YAML.

Usage:
  python src/dataset/generate.py configs/demo_regions.yaml
  python src/dataset/generate.py configs/sp01_regions.yaml --skip-pitch   # no Parselmouth
"""
import argparse
import json
import os
import sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import read_wav, write_wav
from flaws import FUNCS, PARAM_NAME, NEEDS_PARSELMOUTH, level_value


def apply_flaws(x, sr, flaws, seed):
    """flaws: list of dicts {type, level, start, end} (pause: use 'at').
    Returns (audio, label_flaws, time_map). Times in label_flaws are in the NEW file."""
    items = []
    for f in flaws:
        s = f.get("at", f.get("start"))
        e = f.get("at", f.get("end"))
        items.append(dict(f, s=int(round(s * sr)), e=int(round(e * sr))))
    items.sort(key=lambda d: d["s"])
    for a, b in zip(items, items[1:]):
        if b["s"] < a["e"]:
            raise ValueError(f"flaw regions overlap: {a['type']} and {b['type']}")
    out, pos, out_len = [], 0, 0
    time_map = [[0.0, 0.0]]
    labels = []
    for i, it in enumerate(items):
        keep = x[pos:it["s"]]
        out.append(keep)
        out_len += len(keep)
        rng = np.random.default_rng([seed, i])
        value = level_value(it["type"], it["level"])
        new = FUNCS[it["type"]](x[it["s"]:it["e"]], sr, value, rng)
        ns = out_len / sr
        out.append(new)
        out_len += len(new)
        ne = out_len / sr
        time_map += [[round(it["s"] / sr, 4), round(ns, 4)],
                     [round(it["e"] / sr, 4), round(ne, 4)]]
        labels.append({
            "type": it["type"], "severity": int(it["level"]),
            "start": round(ns, 4), "end": round(ne, 4),
            "src_start": round(it["s"] / sr, 4), "src_end": round(it["e"] / sr, 4),
            "params": {PARAM_NAME[it["type"]]: value},
        })
        pos = it["e"]
    out.append(x[pos:])
    out_len += len(x) - pos
    time_map.append([round(len(x) / sr, 4), round(out_len / sr, 4)])
    return np.concatenate(out).astype(np.float32), labels, time_map


def write_label(path, name, cfg, sr, audio, overall, labels, time_map):
    doc = {
        "file": name, "speech_id": cfg["speech_id"],
        "ideal_file": os.path.basename(cfg["ideal"]),
        "sr": sr, "duration": round(len(audio) / sr, 4), "seed": cfg["seed"],
        "overall_severity": overall, "flaws": labels, "time_map": time_map,
    }
    with open(path, "w") as fh:
        json.dump(doc, fh, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--out-dir", default="data/bad")
    ap.add_argument("--label-dir", default="data/labels")
    ap.add_argument("--skip-pitch", action="store_true",
                    help="drop monotone/erratic_pitch (use only if Parselmouth is not installed)")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config))
    x, sr = read_wav(cfg["ideal"])
    os.makedirs(a.out_dir, exist_ok=True)
    os.makedirs(a.label_dir, exist_ok=True)
    sid, seed = cfg["speech_id"], cfg["seed"]

    def ok(t):
        if a.skip_pitch and t in NEEDS_PARSELMOUTH:
            print(f"  [skip] {t} (--skip-pitch)")
            return False
        return True

    # ideal: label with no flaws
    write_label(os.path.join(a.label_dir, f"{sid}_ideal.json"),
                f"{sid}_ideal.wav", cfg, sr, x, 0, [], [[0.0, 0.0], [len(x) / sr, len(x) / sr]])
    n = 1
    # single-flaw files
    for ftype, reg in cfg["single"].items():
        if not ok(ftype):
            continue
        for lvl in cfg["single_levels"]:
            f = dict(reg, type=ftype, level=lvl)
            y, lab, tm = apply_flaws(x, sr, [f], seed)
            name = f"{sid}_{ftype}_s{lvl}.wav"
            write_wav(os.path.join(a.out_dir, name), y, sr)
            write_label(os.path.join(a.label_dir, name.replace(".wav", ".json")),
                        name, cfg, sr, y, lvl, lab, tm)
            n += 1
    # combined gradient s1..s5
    for lvl in range(1, 6):
        fl = [dict(r, level=lvl) for r in cfg["combined"] if ok(r["type"])]
        y, lab, tm = apply_flaws(x, sr, fl, seed)
        name = f"{sid}_combined_s{lvl}.wav"
        write_wav(os.path.join(a.out_dir, name), y, sr)
        write_label(os.path.join(a.label_dir, name.replace(".wav", ".json")),
                    name, cfg, sr, y, lvl, lab, tm)
        n += 1
    print(f"{sid}: wrote {n} label files; audio in {a.out_dir}, labels in {a.label_dir}")


if __name__ == "__main__":
    main()
