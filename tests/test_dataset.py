import hashlib
import os
import subprocess
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "dataset"))
sys.path.insert(0, os.path.join(ROOT, "src", "eval"))

from flaws import wsola, volume_drop, long_pause, missing_pause, level_value, SEVERITY  # noqa: E402
from generate import apply_flaws  # noqa: E402
from evaluate import iou, match  # noqa: E402
from validate import f0_track  # noqa: E402

SR = 16000


def tone(f, dur=3.0):
    t = np.arange(int(dur * SR)) / SR
    return (0.3 * np.sin(2 * np.pi * f * t)).astype(np.float32)


def peak_hz(x):
    sp = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    return np.argmax(sp) * SR / len(x)


@pytest.mark.parametrize("rate", [0.5, 1.25, 1.8])
def test_wsola_length_and_pitch(rate):
    x = tone(200)
    y = wsola(x, rate)
    assert abs(len(y) / SR - len(x) / SR / rate) < 0.05
    assert abs(peak_hz(y) - 200) < 5            # pitch preserved


def test_wsola_deterministic():
    x = tone(150)
    assert np.array_equal(wsola(x, 1.4), wsola(x, 1.4))


def test_volume_drop_db():
    x = tone(200)
    y = volume_drop(x, SR, -12, None)
    mid = slice(SR, 2 * SR)
    ratio = np.sqrt(np.mean(y[mid] ** 2) / np.mean(x[mid] ** 2))
    assert abs(20 * np.log10(ratio) + 12) < 0.1


def test_long_pause_length():
    assert len(long_pause(np.zeros(0), SR, 1.5, None)) == int(1.5 * SR)


def test_missing_pause_shortens():
    x = np.concatenate([tone(200, 1), np.zeros(SR // 2), tone(200, 1)])
    y = missing_pause(x, SR, 1.0, None)
    assert len(x) - len(y) > 0.4 * SR


def test_f0_track_finds_pitch():
    f = f0_track(tone(180, 1.0), SR)
    assert abs(np.median(f[f > 0]) - 180) < 5


def test_time_map_and_labels():
    x = tone(200, 10.0)
    y, lab, tm = apply_flaws(x, SR, [
        {"type": "too_fast", "level": 5, "start": 2.0, "end": 4.0},
        {"type": "long_pause", "level": 3, "at": 6.0}], seed=1)
    assert abs(lab[0]["start"] - 2.0) < 1e-3 and abs(lab[0]["end"] - 3.1111) < 0.01   # 2 s / 1.8
    assert abs(lab[1]["start"] - 6.0 + 0.8889) < 0.01 and abs(lab[1]["end"] - lab[1]["start"] - 1.0) < 1e-3
    assert abs(len(y) / SR - tm[-1][1]) < 1e-3


def test_overlap_rejected():
    with pytest.raises(ValueError):
        apply_flaws(tone(200, 6), SR, [{"type": "too_fast", "level": 1, "start": 1, "end": 3},
                                       {"type": "volume_drop", "level": 1, "start": 2, "end": 4}], 0)


def test_severity_tables_complete():
    assert all(len(v) == 5 for v in SEVERITY.values())
    assert level_value("monotone", 5) == 0.0


def test_iou_and_match():
    assert iou((0, 2), (1, 3)) == pytest.approx(1 / 3)
    truth = [{"type": "a", "start": 0, "end": 2}]
    pred = [{"type": "a", "start": 0.1, "end": 2.2}, {"type": "a", "start": 10, "end": 12}]
    assert len(match(truth, pred, 0.3)) == 1


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def test_regeneration_is_identical(tmp_path):
    """Run the generator twice; every output file must be byte-identical."""
    cfg = os.path.join(ROOT, "configs", "demo_regions.yaml")
    if not os.path.exists(cfg):
        pytest.skip("run make_demo_audio.py first")
    hashes = []
    for run in range(2):
        out, lab = tmp_path / f"bad{run}", tmp_path / f"lab{run}"
        subprocess.run([sys.executable, os.path.join(ROOT, "src/dataset/generate.py"), cfg,
                        "--out-dir", str(out), "--label-dir", str(lab), "--skip-pitch"],
                       cwd=ROOT, check=True, capture_output=True)
        hashes.append({p.name: sha(p) for p in sorted(out.iterdir())})
        hashes[-1].update({p.name: sha(p) for p in sorted(lab.iterdir())})
    assert hashes[0] == hashes[1] and len(hashes[0]) > 5


def test_monotone_reduces_pitch_spread():
    """Needs Parselmouth. Uses a voiced signal with a moving pitch."""
    parselmouth = pytest.importorskip("parselmouth")
    from flaws import monotone
    t = np.arange(int(3 * SR)) / SR
    f0 = 150 * 2 ** (3 * np.sin(2 * np.pi * 0.7 * t) / 12)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    x = (0.2 * sum(np.sin(k * ph) / k for k in range(1, 12))).astype(np.float32)
    y = monotone(x, SR, 0.0, np.random.default_rng(0))

    def spread(s):
        snd = parselmouth.Sound(s.astype(np.float64), sampling_frequency=SR)
        p = snd.to_pitch(time_step=0.01, pitch_floor=75, pitch_ceiling=400)
        f = p.selected_array["frequency"]
        f = f[f > 0]
        return np.std(12 * np.log2(f))
    assert spread(y) < 0.5 * spread(x)
