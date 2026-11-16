# Thin wrapper around Piper (local German TTS). Voices live in ../voices_piper/de_DE-<name>.onnx
import io, os, wave
import numpy as np
from piper import PiperVoice, SynthesisConfig
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'voices_piper'); _V = {}
def voice(name):
    if name not in _V: _V[name] = PiperVoice.load(os.path.join(DIR, f'de_DE-{name}.onnx'))
    return _V[name]
def synth(text, vname, speaker=None, length=1.0, noise=0.667, noise_w=0.8):
    """-> (float32 mono, sample rate)"""
    v = voice(vname); cfg = SynthesisConfig(speaker_id=speaker, length_scale=length, noise_scale=noise, noise_w_scale=noise_w)
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as w: v.synthesize_wav(text, w, syn_config=cfg)
    buf.seek(0)
    with wave.open(buf) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, sr
def f0(a, sr):
    n = 2048; fs = []
    for i in range(0, len(a) - n, n // 2):
        x = a[i:i + n] * np.hanning(n)
        if np.sqrt((x ** 2).mean()) < 0.02: continue
        ac = np.correlate(x, x, 'full')[n - 1:]; lo, hi = int(sr / 400), int(sr / 60); k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.4 * ac[0]: fs.append(sr / k)
    return float(np.median(fs)) if fs else 0.0
