"""Flaw injectors. Every function has the signature

    fn(seg, sr, value, rng) -> new_seg

`seg` is the audio of ONE region (float array). Time-changing flaws return a
different length; generate.py keeps the time map. Everything here is
deterministic: no hidden randomness, `rng` is a seeded numpy Generator.
"""
import numpy as np
from scipy.signal import get_window

# severity level 1 (subtle) ... 5 (botched)
SEVERITY = {
    "too_fast":      [1.10, 1.25, 1.40, 1.60, 1.80],   # tempo factor
    "too_slow":      [0.90, 0.78, 0.65, 0.55, 0.45],   # tempo factor
    "monotone":      [0.8, 0.6, 0.4, 0.2, 0.0],        # share of pitch variation kept
    "erratic_pitch": [0.5, 1.0, 2.0, 3.0, 4.0],        # wobble std in semitones
    "volume_drop":   [-3, -6, -9, -12, -18],           # dB
    "long_pause":    [0.4, 0.7, 1.0, 1.5, 2.5],        # seconds of silence inserted
    "missing_pause": [0.2, 0.4, 0.6, 0.8, 1.0],        # share of each pause removed
}
PARAM_NAME = {
    "too_fast": "tempo", "too_slow": "tempo", "monotone": "f0_scale",
    "erratic_pitch": "wobble_semitones", "volume_drop": "gain_db",
    "long_pause": "pause_s", "missing_pause": "pause_cut",
}
NEEDS_PARSELMOUTH = {"monotone", "erratic_pitch"}


def wsola(x, rate, frame=1024, tol=256):
    """Pitch-preserving time-scale modification (WSOLA).
    rate > 1 -> faster (shorter), rate < 1 -> slower (longer). Deterministic."""
    x = np.asarray(x, dtype=np.float64)
    if len(x) < 4 * frame:
        return x.astype(np.float32)
    hs = frame // 2
    ha = hs * rate
    win = get_window("hann", frame, fftbins=True)
    n_out = int(round(len(x) / rate))
    n_frames = int(np.ceil(n_out / hs)) + 1
    xp = np.concatenate([np.zeros(tol), x, np.zeros(frame + 3 * tol)])
    y = np.zeros(n_out + 2 * frame)
    wsum = np.zeros_like(y)
    prev = None
    for k in range(n_frames):
        nominal = int(round(k * ha)) + tol
        if prev is None:
            pos = nominal
        else:
            target = xp[prev + hs: prev + hs + frame]
            lo = max(nominal - tol, 0)
            region = xp[lo: lo + 2 * tol + frame]
            if len(region) < frame + 1 or len(target) < frame:
                pos = nominal
            else:
                corr = np.correlate(region, target, mode="valid")
                pos = lo + int(np.argmax(corr))
        chunk = xp[pos: pos + frame]
        if len(chunk) < frame:
            chunk = np.pad(chunk, (0, frame - len(chunk)))
        y[k * hs: k * hs + frame] += chunk * win
        wsum[k * hs: k * hs + frame] += win
        prev = pos
    ok = wsum > 1e-3
    y[ok] /= wsum[ok]
    return y[:n_out].astype(np.float32)


def too_fast(seg, sr, value, rng):
    return wsola(seg, float(value))


def too_slow(seg, sr, value, rng):
    return wsola(seg, float(value))


def volume_drop(seg, sr, value, rng):
    gain = 10 ** (float(value) / 20.0)
    n = len(seg)
    ramp = min(int(0.05 * sr), n // 4)
    env = np.full(n, gain)
    if ramp > 0:
        env[:ramp] = np.linspace(1.0, gain, ramp)
        env[-ramp:] = np.linspace(gain, 1.0, ramp)
    return (seg * env).astype(np.float32)


def long_pause(seg, sr, value, rng):
    """Insert silence. `seg` is empty (zero-length region at a point)."""
    return np.zeros(int(round(float(value) * sr)), dtype=np.float32)


def missing_pause(seg, sr, value, rng, min_pause=0.15, hop=0.01):
    """Shorten every silent run longer than `min_pause` s by the share `value`."""
    h = int(hop * sr)
    n_fr = len(seg) // h
    if n_fr < 5:
        return seg
    fr = seg[: n_fr * h].reshape(n_fr, h)
    rms = np.sqrt(np.mean(fr.astype(np.float64) ** 2, axis=1))
    silent = rms < 0.1 * np.percentile(rms, 95)
    keep = np.ones(len(seg), dtype=bool)
    i = 0
    while i < n_fr:
        if silent[i]:
            j = i
            while j < n_fr and silent[j]:
                j += 1
            if (j - i) * hop >= min_pause:
                cut = int((j - i) * h * float(value))
                mid = (i * h + j * h) // 2
                keep[mid - cut // 2: mid - cut // 2 + cut] = False
            i = j
        else:
            i += 1
    return seg[keep].astype(np.float32)


def _resynth_with_f0(seg, sr, transform, floor=75, ceil=500):
    """Re-synthesise `seg` with a modified F0 contour (Praat PSOLA via Parselmouth)."""
    import parselmouth
    from parselmouth.praat import call
    snd = parselmouth.Sound(np.asarray(seg, dtype=np.float64), sampling_frequency=sr)
    pitch = snd.to_pitch(time_step=0.01, pitch_floor=floor, pitch_ceiling=ceil)
    t = pitch.xs()
    f0 = pitch.selected_array["frequency"]
    voiced = f0 > 0
    if voiced.sum() < 5:
        return seg
    new_f0 = transform(f0[voiced])
    manip = call(snd, "To Manipulation", 0.01, floor, ceil)
    tier = call("Create PitchTier", "new", snd.xmin, snd.xmax)
    for ti, fi in zip(t[voiced], new_f0):
        call(tier, "Add point", float(ti), float(fi))
    call([tier, manip], "Replace pitch tier")
    out = call(manip, "Get resynthesis (overlap-add)").values[0]
    out = out[: len(seg)]
    if len(out) < len(seg):
        out = np.pad(out, (0, len(seg) - len(out)))
    return out.astype(np.float32)


def monotone(seg, sr, value, rng):
    scale = float(value)

    def tr(f0):
        lf = np.log(f0)
        med = np.median(lf)
        return np.exp(med + scale * (lf - med))
    return _resynth_with_f0(seg, sr, tr)


def erratic_pitch(seg, sr, value, rng):
    std = float(value)

    def tr(f0):
        noise = rng.normal(size=len(f0))
        noise = np.convolve(noise, np.ones(5) / 5.0, mode="same")
        noise = noise / (np.std(noise) + 1e-9) * std
        return f0 * 2.0 ** (noise / 12.0)
    return _resynth_with_f0(seg, sr, tr)


FUNCS = {
    "too_fast": too_fast, "too_slow": too_slow, "monotone": monotone,
    "erratic_pitch": erratic_pitch, "volume_drop": volume_drop,
    "long_pause": long_pause, "missing_pause": missing_pause,
}


def level_value(flaw_type, level):
    """Severity level 1..5 -> numeric parameter."""
    return SEVERITY[flaw_type][int(level) - 1]
