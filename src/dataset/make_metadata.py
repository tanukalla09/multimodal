"""Build data/metadata.csv with one row per audio file (skip demo_*).

Columns (semicolons for list fields):
  sample_id, audio_path, label_path, speech_id, ideal_file,
  sr, duration_s, overall_severity, flaw_types, flaw_severities,
  flaw_start_s, flaw_end_s, src_start_s, src_end_s

List columns use semicolon separation, same order as flaws[].
Times are seconds from start of that file.
"""
import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dataset'))
from common import read_wav  # noqa: E402

COLUMNS = [
    "sample_id", "audio_path", "label_path", "speech_id", "ideal_file",
    "sr", "duration_s", "overall_severity",
    "flaw_types", "flaw_severities",
    "flaw_start_s", "flaw_end_s",
    "src_start_s", "src_end_s",
]

LABELS_DIR = "data/labels"
BAD_DIR = "data/bad"
RAW_DIR = "data/raw"
OUT_CSV = "data/metadata.csv"


def join(lst):
    return ";".join(str(x) for x in lst)


def main():
    label_files = sorted(glob.glob(os.path.join(LABELS_DIR, "*.json")))
    label_files = [f for f in label_files
                   if not os.path.basename(f).startswith("demo_")]

    rows = []
    for lf in label_files:
        lab = json.load(open(lf))
        fname = lab["file"]
        stem = os.path.splitext(fname)[0]

        # audio path
        if fname.endswith("_ideal.wav"):
            audio_path = os.path.join(RAW_DIR, fname)
        else:
            audio_path = os.path.join(BAD_DIR, fname)

        # measure actual duration from file
        if os.path.exists(audio_path):
            x, sr = read_wav(audio_path)
            duration_s = round(len(x) / sr, 4)
        else:
            sr = lab["sr"]
            duration_s = lab["duration"]

        flaws = lab["flaws"]
        row = {
            "sample_id":        stem,
            "audio_path":       audio_path.replace("\\", "/"),
            "label_path":       lf.replace("\\", "/"),
            "speech_id":        lab["speech_id"],
            "ideal_file":       lab["ideal_file"],
            "sr":               sr,
            "duration_s":       duration_s,
            "overall_severity": lab["overall_severity"],
            "flaw_types":       join(f["type"] for f in flaws),
            "flaw_severities":  join(f["severity"] for f in flaws),
            "flaw_start_s":     join(f["start"] for f in flaws),
            "flaw_end_s":       join(f["end"] for f in flaws),
            "src_start_s":      join(f["src_start"] for f in flaws),
            "src_end_s":        join(f["src_end"] for f in flaws),
        }
        rows.append(row)
        print(f"  {stem:40s}  flaws={len(flaws)}  dur={duration_s:.2f}s")

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {OUT_CSV} with {len(rows)} rows.")


if __name__ == "__main__":
    main()
