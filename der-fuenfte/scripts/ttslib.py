import wave, numpy as np, io
from piper import PiperVoice
try:
    from piper import SynthesisConfig
except Exception:
    from piper.config import SynthesisConfig
_V = {}
def voice(name):
    if name not in _V: _V[name] = PiperVoice.load(f"voices/de_DE-{name}.onnx")
    return _V[name]
def synth(text, vname, speaker=None, length=1.0, noise=0.667, noise_w=0.8):
    """returns (float32 mono, sr)"""
    v = voice(vname); cfg = SynthesisConfig(speaker_id=speaker, length_scale=length, noise_scale=noise, noise_w_scale=noise_w)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w: v.synthesize_wav(text, w, syn_config=cfg)
    buf.seek(0)
    with wave.open(buf) as w:
        sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, sr
def f0(a, sr):
    n = 2048; fs = []
    for i in range(0, len(a) - n, n):
        x = a[i:i + n] * np.hanning(n)
        if np.sqrt((x ** 2).mean()) < 0.03: continue
        ac = np.correlate(x, x, "full")[n - 1:]; lo, hi = int(sr / 400), int(sr / 60)
        k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.4 * ac[0]: fs.append(sr / k)
    return float(np.median(fs)) if fs else 0.0
