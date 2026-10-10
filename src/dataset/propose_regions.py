"""Region proposal tool for new speeches (e.g. speeches 3 and 4).

Finds pauses via silence detection, builds speech segments, and writes
a draft YAML in the exact schema of configs/sp01_regions.yaml.

Rules enforced:
  - Each range region is 3 to 5 s long
  - Starting and ending at natural pause boundaries (inside speech)
  - No overlap inside a file
  - At least 1 s apart between any pair of regions (including long_pause)
  - missing_pause contains a natural pause > 0.15 s
  - No region within 6 s of the clip end
  - Single flaw regions spread across different parts of the clip

Usage:
  python src/dataset/propose_regions.py data/raw/sp03_ideal.wav sp03 [--seed 42] [--out configs/sp03_regions.draft.yaml]
"""
import argparse
import os
import sys

import numpy as np
import yaml

sys.path.insert(0, os.path.dirname(__file__))
from common import read_wav


def detect_silence(x, sr, hop_s=0.01, win_s=0.03, min_silence_s=0.20):
    """Detect silence runs in an audio array using RMS thresholding."""
    hop = int(hop_s * sr)
    win = int(win_s * sr)
    n = (len(x) - win) // hop
    if n < 5:
        return []
    frames = np.lib.stride_tricks.sliding_window_view(x[:n * hop + win], win)[::hop]
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    p95 = np.percentile(rms, 95)
    thr = max(1e-4, 0.08 * p95)
    is_silent = rms < thr

    runs = []
    in_sil = False
    start_f = 0
    for i, s in enumerate(is_silent):
        if s and not in_sil:
            in_sil = True
            start_f = i
        elif not s and in_sil:
            in_sil = False
            dur = (i - start_f) * hop_s
            if dur >= min_silence_s:
                runs.append((round(start_f * hop_s, 2), round(i * hop_s, 2)))
    if in_sil:
        dur = (len(is_silent) - start_f) * hop_s
        if dur >= min_silence_s:
            runs.append((round(start_f * hop_s, 2), round(len(is_silent) * hop_s, 2)))
    return runs


def get_candidate_regions(silences, total_dur):
    """Find all valid 3-5 s candidate speech segments between detected silences."""
    candidates = []
    max_t = total_dur - 6.0
    for i in range(len(silences)):
        t_start = silences[i][1]
        for j in range(i + 1, len(silences)):
            t_end = silences[j][0]
            dur = t_end - t_start
            if 3.0 <= dur <= 5.0 and t_end <= max_t:
                internal_pauses = [p for p in silences[i + 1:j] if (p[1] - p[0]) >= 0.15]
                candidates.append({
                    "start": round(t_start, 2),
                    "end": round(t_end, 2),
                    "dur": round(dur, 2),
                    "has_pause": len(internal_pauses) > 0,
                    "pause_dur": max([p[1] - p[0] for p in internal_pauses], default=0.0),
                })
            elif dur > 5.0:
                break
    return candidates


def check_separation(regions, item, min_gap=1.0):
    """Check if item is at least min_gap seconds away from all existing regions."""
    for r in regions:
        if "at" in r and "at" in item:
            if abs(r["at"] - item["at"]) < min_gap:
                return False
        elif "at" in r:
            if (item["start"] - min_gap < r["at"] < item["end"] + min_gap):
                return False
        elif "at" in item:
            if (r["start"] - min_gap < item["at"] < r["end"] + min_gap):
                return False
        else:
            if not (item["end"] + min_gap <= r["start"] or item["start"] >= r["end"] + min_gap):
                return False
    return True


def propose_regions(x, sr, speech_id, ideal_path, seed=42):
    """Build a draft regions config conforming to all hackathon dataset rules."""
    rng = np.random.default_rng(seed)
    total_dur = len(x) / sr
    max_t = total_dur - 6.0
    silences = detect_silence(x, sr)
    candidates = get_candidate_regions(silences, total_dur)

    if len(candidates) < 6:
        raise ValueError(f"Not enough candidate speech regions found in {ideal_path} ({len(candidates)})")

    # Select candidate pauses for long_pause (prefer middle or later half of the clip, <= max_t)
    valid_pauses = [p for p in silences if p[0] >= 5.0 and p[1] <= max_t and (p[1] - p[0]) >= 0.20]
    if not valid_pauses:
        valid_pauses = [p for p in silences if p[1] <= max_t and (p[1] - p[0]) >= 0.20]

    # Partition the timeline into early, middle, late buckets for spreading
    n_buckets = 6
    edges = np.linspace(0, max_t, n_buckets + 1)
    bucket_cands = [[] for _ in range(n_buckets)]
    for c in candidates:
        mid = (c["start"] + c["end"]) / 2.0
        for b_idx in range(n_buckets):
            if edges[b_idx] <= mid < edges[b_idx + 1] or (b_idx == n_buckets - 1 and mid <= max_t):
                bucket_cands[b_idx].append(c)
                break

    # Search for valid single region set: 6 ranges spread across buckets + 1 long_pause
    single_ranges = None
    long_pause_pt = None

    for attempt in range(500):
        chosen = []
        # Try picking one from each bucket or sequential scan
        bucket_order = list(range(n_buckets))
        for b_idx in bucket_order:
            b_list = list(bucket_cands[b_idx])
            rng.shuffle(b_list)
            for cand in b_list:
                if check_separation(chosen, cand):
                    chosen.append(cand)
                    break

        if len(chosen) < 6:
            # Fall back to greedy selection from all candidates
            all_shuffled = list(candidates)
            rng.shuffle(all_shuffled)
            chosen = []
            for cand in all_shuffled:
                if check_separation(chosen, cand):
                    chosen.append(cand)
                    if len(chosen) == 6:
                        break

        if len(chosen) == 6 and any(c["has_pause"] for c in chosen):
            # Sort chosen ranges by start time
            chosen.sort(key=lambda c: c["start"])
            # Now find a long_pause point at least 1s away from all chosen
            shuffled_pauses = list(valid_pauses)
            rng.shuffle(shuffled_pauses)
            found_lp = None
            for p in shuffled_pauses:
                pt = round((p[0] + p[1]) / 2.0, 2)
                lp_cand = {"at": pt}
                if check_separation(chosen, lp_cand):
                    found_lp = pt
                    break
            if found_lp is not None:
                single_ranges = chosen
                long_pause_pt = found_lp
                break

    if single_ranges is None:
        raise RuntimeError(f"Could not find a valid non-overlapping set of 7 single flaws for seed {seed}")

    # Assign single flaw types
    # Identify which candidate has a pause for missing_pause
    pause_cand_indices = [i for i, c in enumerate(single_ranges) if c["has_pause"]]
    # Pick one for missing_pause
    mp_idx = rng.choice(pause_cand_indices)

    range_types = ["too_fast", "monotone", "volume_drop", "erratic_pitch", "too_slow"]
    rng.shuffle(range_types)

    single_dict = {}
    type_idx = 0
    for i, c in enumerate(single_ranges):
        if i == mp_idx:
            single_dict["missing_pause"] = {"start": c["start"], "end": c["end"]}
        else:
            ft = range_types[type_idx]
            type_idx += 1
            single_dict[ft] = {"start": c["start"], "end": c["end"]}
    single_dict["long_pause"] = {"at": long_pause_pt}

    # Search for combined regions: 3 distinct ranges at least 1s apart, <= max_t
    combined_chosen = None
    for attempt in range(200):
        shuffled_c = list(candidates)
        rng.shuffle(shuffled_c)
        comb = []
        for c in shuffled_c:
            if check_separation(comb, c):
                comb.append(c)
                if len(comb) == 3:
                    break
        if len(comb) == 3:
            comb.sort(key=lambda c: c["start"])
            combined_chosen = comb
            break

    if combined_chosen is None:
        raise RuntimeError("Could not find a valid set of 3 combined regions")

    comb_types = ["monotone", "too_fast", "volume_drop"]
    rng.shuffle(comb_types)
    combined_list = [
        {"type": comb_types[i], "start": combined_chosen[i]["start"], "end": combined_chosen[i]["end"]}
        for i in range(3)
    ]

    config_data = {
        "speech_id": speech_id,
        "ideal": ideal_path.replace("\\", "/"),
        "seed": int(seed),
        "single_levels": [2, 4],
        "single": single_dict,
        "combined": combined_list,
    }
    return config_data


def validate_config(cfg, total_dur, silences):
    """Verify that a proposed config satisfies every rule."""
    errors = []
    max_t = total_dur - 6.0

    # 1. Single checks
    single = cfg["single"]
    single_items = []
    for k, v in single.items():
        if k == "long_pause":
            at = v.get("at")
            if at is None:
                errors.append("long_pause missing 'at'")
            elif at > max_t:
                errors.append(f"long_pause at={at} exceeds max_t={max_t:.2f}")
            single_items.append({"name": k, "at": at})
        else:
            s, e = v.get("start"), v.get("end")
            dur = e - s
            if not (3.0 <= dur <= 5.0):
                errors.append(f"{k} duration {dur:.2f}s outside [3.0, 5.0]s")
            if e > max_t:
                errors.append(f"{k} end={e} exceeds max_t={max_t:.2f}")
            if k == "missing_pause":
                internal_pauses = [p for p in silences if p[0] >= s and p[1] <= e and (p[1] - p[0]) >= 0.15]
                if not internal_pauses:
                    errors.append(f"missing_pause ({s}-{e}) contains no natural pause >= 0.15s")
            single_items.append({"name": k, "start": s, "end": e})

    # Check pairwise separation in single
    for i in range(len(single_items)):
        for j in range(i + 1, len(single_items)):
            if not check_separation([single_items[i]], single_items[j]):
                errors.append(f"single overlap or <1s gap between {single_items[i]['name']} and {single_items[j]['name']}")

    # 2. Combined checks
    comb = cfg["combined"]
    if len(comb) != 3:
        errors.append(f"combined has {len(comb)} items instead of 3")
    for i, c in enumerate(comb):
        s, e = c.get("start"), c.get("end")
        dur = e - s
        if not (3.0 <= dur <= 5.0):
            errors.append(f"combined[{i}] duration {dur:.2f}s outside [3.0, 5.0]s")
        if e > max_t:
            errors.append(f"combined[{i}] end={e} exceeds max_t={max_t:.2f}")
        for j in range(i + 1, len(comb)):
            if not check_separation([c], comb[j]):
                errors.append(f"combined overlap or <1s gap between item {i} and {j}")

    return errors


def main():
    ap = argparse.ArgumentParser(description="Propose flaw regions YAML for a speech recording.")
    ap.add_argument("wav", help="Path to ideal WAV file (e.g. data/raw/sp03_ideal.wav)")
    ap.add_argument("speech_id", help="Speech ID (e.g. sp03)")
    ap.add_argument("--seed", type=int, default=42, help="Random seed")
    ap.add_argument("--out", default=None, help="Output YAML path")
    args = ap.parse_args()

    if not os.path.exists(args.wav):
        sys.exit(f"File not found: {args.wav}")

    x, sr = read_wav(args.wav)
    total_dur = len(x) / sr
    silences = detect_silence(x, sr)

    out_path = args.out or f"configs/{args.speech_id}_regions.draft.yaml"

    cfg = propose_regions(x, sr, args.speech_id, args.wav, seed=args.seed)
    errors = validate_config(cfg, total_dur, silences)

    if errors:
        print(f"Validation FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="ascii") as fh:
        yaml.dump(cfg, fh, sort_keys=False)

    print(f"Proposed regions YAML written to {out_path} (ALL RULES PASSED)")
    print(f"  Single regions ({len(cfg['single'])}):")
    for k, v in cfg["single"].items():
        if k == "long_pause":
            print(f"    {k:15s}: at={v['at']:.2f}s")
        else:
            print(f"    {k:15s}: {v['start']:.2f} - {v['end']:.2f}s ({v['end'] - v['start']:.2f}s)")
    print(f"  Combined regions ({len(cfg['combined'])}):")
    for item in cfg["combined"]:
        print(f"    {item['type']:15s}: {item['start']:.2f} - {item['end']:.2f}s ({item['end'] - item['start']:.2f}s)")


if __name__ == "__main__":
    main()
