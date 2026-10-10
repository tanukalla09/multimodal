"""Shared helpers: WAV I/O and small utilities (numpy + scipy only)."""
import numpy as np
from scipy.io import wavfile

SR = 16000


def read_wav(path):
    """Return (float32 mono samples in [-1, 1], sample_rate)."""
    sr, x = wavfile.read(path)
    if x.dtype == np.int16:
        x = x.astype(np.float32) / 32768.0
    elif x.dtype == np.int32:
        x = x.astype(np.float32) / 2147483648.0
    elif x.dtype == np.uint8:
        x = (x.astype(np.float32) - 128.0) / 128.0
    else:
        x = x.astype(np.float32)
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x, sr


def write_wav(path, x, sr=SR):
    """Write 16-bit PCM. Rounding is deterministic, so output is reproducible."""
    x = np.clip(np.asarray(x, dtype=np.float64), -1.0, 1.0)
    wavfile.write(str(path), sr, np.round(x * 32767.0).astype(np.int16))


def rms_db(x):
    """RMS level in dB relative to full scale."""
    x = np.asarray(x, dtype=np.float64)
    if x.size == 0:
        return -120.0
    return 20.0 * np.log10(max(np.sqrt(np.mean(x ** 2)), 1e-9))
