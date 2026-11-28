"""Synthesize + process every line. writes build/vo_<key>.wav (48k mono) and build/lines.json {key:{dur, env[30fps]}}"""
import os, sys, json, io, wave, subprocess, numpy as np
from piper import PiperVoice
try: from piper import SynthesisConfig
except Exception: from piper.config import SynthesisConfig
from lines import LINES
VD = os.environ.get("VOICES", "voices"); SR = 48000; os.makedirs("build", exist_ok=True)
COMP = "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3"
# speaker -> voice, length_scale, pitch semitones, tempo, ffmpeg fx chain, gain dB
SP = {
    "narr":    ("kerstin-low", 1.08, -0.6, 1.0, f"highpass=f=70,{COMP},aecho=0.8:0.4:30:0.08", 0),
    "mom":     ("eva_k-x_low", 1.02, 0.0, 1.0, f"highpass=f=90,{COMP},aecho=0.8:0.5:28|55:0.14|0.08", -1),
    "mia":     ("ramona-low", 1.05, 1.6, 1.0, f"highpass=f=110,{COMP},aecho=0.8:0.5:24:0.1", 0),
    "whisper": ("ramona-low", 1.25, 1.6, 0.92, f"highpass=f=300,lowpass=f=6000,{COMP},aecho=0.8:0.5:24:0.1", -5),
    "door":    ("ramona-low", 1.2, 1.6, 0.95, "lowpass=f=1100,highpass=f=150,aecho=0.8:0.7:40|85|140:0.4|0.28|0.18", -2),
    "future":  ("ramona-low", 1.15, 0.6, 0.97, f"highpass=f=350,lowpass=f=3600,{COMP},aecho=0.8:0.85:70|150|260:0.35|0.25|0.15", -3),
    "creepy":  ("eva_k-x_low", 1.3, -5.0, 0.9, "aecho=0.8:0.85:55|120|210:0.45|0.3|0.2,lowpass=f=5000", 1),
}
_V = {}
def synth(text, vname, ln):
    if vname not in _V: _V[vname] = PiperVoice.load(f"{VD}/de_DE-{vname}.onnx")
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w: _V[vname].synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=ln, noise_scale=0.6, noise_w_scale=0.8))
    buf.seek(0)
    with wave.open(buf) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return a, sr
def ff(a, sr, af):
    p = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-af", af, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], input=a.tobytes(), capture_output=True)
    return np.frombuffer(p.stdout, np.float32).copy()
meta = {}
for key, (sp, text, cap) in LINES.items():
    v, ln, st, tempo, chain, db = SP[sp]
    a, sr = synth(text, v, ln)
    af = f"aresample={SR},rubberband=pitch={2 ** (st / 12):.4f}:tempo={tempo},{chain},silenceremove=start_periods=1:start_threshold=-48dB"
    y = ff(a, sr, af)
    if sp == "creepy":  # double with an octave-down whisper layer for the "fremde Stimme"
        y2 = ff(a, sr, f"aresample={SR},rubberband=pitch={2 ** (-12 / 12):.4f}:tempo={tempo},lowpass=f=1800,silenceremove=start_periods=1:start_threshold=-48dB")
        n = min(len(y), len(y2)); y = y[:n] * 0.85 + y2[:n] * 0.55
    if sp == "whisper": y = y + np.random.default_rng(3).normal(0, 0.004, len(y)).astype(np.float32) * (np.abs(y) > 0.01)
    e = np.where(np.abs(y) > 0.004)[0]; y = y[: e[-1] + int(0.3 * SR)] if len(e) else y
    y *= 0.72 / (np.abs(y).max() + 1e-6) * 10 ** (db / 20)
    with wave.open(f"build/vo_{key}.wav", "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    hop = SR // 30; env = [float(np.sqrt((y[i:i + hop] ** 2).mean())) for i in range(0, len(y), hop)]; mx = max(env) + 1e-6
    # speech end = last frame above threshold
    meta[key] = dict(dur=round(len(y) / SR, 3), env=[round(min(1.0, x / mx * 1.6), 2) for x in env])
    print(key, sp, meta[key]["dur"])
json.dump(meta, open("build/lines.json", "w"))
