"""Voices (Piper TTS + ffmpeg FX), synthesized SFX, ambience and final mix per episode. usage: audio7.py N"""
import sys, os, re, json, wave, hashlib, subprocess, math, numpy as np
import ttslib as L
SR = 48000
SP = dict(alan=dict(v="thorsten-high", sid=None, st=2.0, ln=0.96), zizo=dict(v="thorsten_emotional-medium", sid=0, st=4.6, ln=1.0),
          hame=dict(v="thorsten_emotional-medium", sid=6, st=0.4, ln=1.0), shiar=dict(v="thorsten_emotional-medium", sid=4, st=3.2, ln=0.94))
COMP = "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4"
FX = dict(near=(f"highpass=f=90,{COMP},aecho=0.8:0.5:22:0.12", 0), quiet=(f"highpass=f=120,lowpass=f=5200,{COMP}", -5),
          door=("lowpass=f=1300,highpass=f=140,aecho=0.8:0.6:34|67:0.32|0.2", -3), peep=("lowpass=f=2300,highpass=f=140,aecho=0.8:0.65:40|83:0.34|0.22", -2),
          icom=("highpass=f=500,lowpass=f=2400,acrusher=bits=7:mode=log:aa=1:mix=0.6", -1), phone=(f"highpass=f=380,lowpass=f=3000,{COMP}", -1),
          room=("aecho=0.8:0.8:60|120|190:0.45|0.3|0.2,lowpass=f=3800", -1))
def tts_text(x):
    x = x.replace("Zizo", "Siso").replace("Shiar", "Schiar").replace("…", "").replace("'s", " es").replace("Hä?", "Hä?")
    return re.sub(r"\b[A-ZÄÖÜ]{2,}\b", lambda m: m.group(0).lower(), x).strip()
def wsave(p, a, sr):
    with wave.open(p, "wb") as w: w.setnchannels(1 if a.ndim == 1 else 2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
def raw_clip(line):
    key = line.get("key") or hashlib.md5((line["sp"] + line["text"]).encode()).hexdigest()[:10]; p = f"tts/raw_{key}.wav"
    if not os.path.exists(p):
        c = SP[line["sp"]]; tx = tts_text(line["text"]); a, sr = L.synth(tx, c["v"], c["sid"], length=c["ln"] * (1.22 if len(tx.split()) <= 2 else 1.0)); wsave(p, a, sr)
    return p
def voice(line):
    c = SP[line["sp"]]; st = c["st"] - (1.3 if line.get("it") else 0); tempo = 0.93 if line.get("it") else 1.0; chain, db = FX[line["fx"]]
    af = f"aresample={SR},rubberband=pitch={2 ** (st / 12):.4f}:tempo={tempo},{chain},silenceremove=start_periods=1:start_threshold=-48dB"
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", raw_clip(line), "-af", af, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(out, np.float32).copy(); e = np.where(np.abs(a) > 0.004)[0]
    if len(e): a = a[:min(len(a), e[-1] + int(0.25 * SR))]
    a *= (0.7 / (np.abs(a).max() + 1e-6)) * 10 ** (db / 20)
    if line["fx"] == "icom": a += np.random.default_rng(1).normal(0, 0.012, len(a)).astype(np.float32)
    return a

rng = np.random.default_rng(13)
def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def env(n, a=0.002, d=8.0): t = np.arange(n) / SR; return np.clip(t / a, 0, 1) * np.exp(-t * d)
def tone(f, dur, d=8.0, a=0.002): n = int(dur * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * env(n, a, d)
def noise(dur, fc, d=20.0): n = int(dur * SR); return lp(rng.standard_normal(n), fc) * env(n, 0.001, d)
def pad(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n)
    for x in xs: o[:len(x)] += x
    return o
def at(parts, dur):
    o = np.zeros(int(dur * SR))
    for t, x in parts:
        i = int(t * SR); x = x[:max(0, len(o) - i)]; o[i:i + len(x)] += x
    return o
def thump(f=60, dur=0.3, d=14, nz=0.5, fc=500): return pad(tone(f, dur, d) , noise(dur, fc, 30) * nz)
def sfx(name, **kw):
    if name == "buzz": b = lp(np.sign(np.sin(2 * np.pi * 155 * np.arange(int(0.32 * SR)) / SR)), 700) * np.clip(np.arange(int(0.32 * SR)) / 300, 0, 1) ; b[-400:] *= np.linspace(1, 0, 400); return at([(0, b * 0.5), (0.48, b * 0.5)], 0.9)
    if name == "ring": b = lp(np.sign(np.sin(2 * np.pi * 150 * np.arange(int(0.6 * SR)) / SR)), 650) * 0.5; b[-600:] *= np.linspace(1, 0, 600); return at([(0, b), (1.0, b)], 2.0)
    if name == "ping": return at([(0, tone(880, 0.12, 22) * 0.5), (0.09, tone(1175, 0.2, 16) * 0.5)], 0.35)
    if name == "send": n = int(0.14 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(500 + 5200 * t) / SR) * env(n, 0.005, 16) * 0.4
    if name == "doorbell": return at([(0, pad(tone(659.3, 1.0, 3.2), tone(1318.5, 1.0, 6) * 0.3, tone(1977, 0.6, 9) * 0.12)), (0.62, pad(tone(523.3, 1.7, 2.3), tone(1046.5, 1.4, 4.5) * 0.3, tone(1569, 0.8, 8) * 0.12))], 2.4) * 0.5
    if name == "knock": return pad(tone(115, 0.22, 20), noise(0.12, 900, 45) * 0.8, tone(260, 0.1, 40) * 0.4) * 0.8
    if name == "bang": return pad(tone(62, 0.6, 7), noise(0.35, 700, 14) * 1.2, noise(0.9, 2500, 6) * 0.12) * 0.9
    if name == "slam": return pad(tone(70, 0.5, 9), noise(0.3, 900, 16) * 1.3, noise(1.2, 1800, 4) * 0.1) * 0.9
    if name == "thud": return pad(tone(52, 0.45, 9), noise(0.3, 300, 14) * 0.8) * 0.9
    if name == "step": return pad(noise(0.09, 500, 40) * 0.8, tone(85, 0.12, 30) * 0.5) * 0.6
    if name == "stairs": return at([(i * 0.44, thump(70, 0.2, 22, 0.6, 350) * (0.8 * 0.72 ** i)) for i in range(7)], 3.4)
    if name == "click": return pad(tone(2100, 0.03, 120) * 0.5, noise(0.04, 3500, 90) * 0.6, tone(180, 0.06, 50) * 0.5)
    if name == "lock": return at([(0, sfx("click")), (0.13, sfx("click") * 1.2), (0.13, tone(95, 0.12, 30) * 0.6)], 0.4)
    if name == "shutter": return at([(0, sfx("click") * 0.9), (0.07, noise(0.05, 5000, 70) * 0.7)], 0.2)
    if name == "creak":
        n = int(1.5 * SR); t = np.arange(n) / SR; f = 360 - 90 * t / 1.5 + 22 * np.sin(2 * np.pi * 9 * t)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sign(np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)) * 0.12) * np.clip(t / 0.2, 0, 1) * np.clip((1.5 - t) / 0.3, 0, 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 5.3 * t)) * 0.35
    if name == "whoosh":
        n = int(0.5 * SR); t = np.linspace(0, 1, n); x = rng.standard_normal(n); a = np.exp(-2 * np.pi * (300 + 3500 * np.sin(np.pi * t)) / SR); y = np.empty(n); s = 0.0
        for i in range(n): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
        return y * np.sin(np.pi * t) ** 1.5 * 1.6
    if name == "powerdown": n = int(1.1 * SR); t = np.arange(n) / SR; return pad(np.sin(2 * np.pi * np.cumsum(190 * np.exp(-t * 2.4) + 30) / SR) * np.exp(-t * 2.2) * 0.8, sfx("click"))
    if name == "sting":
        n = int(2.2 * SR); t = np.arange(n) / SR; y = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((207.6, 220, 311.1, 329.6, 110))) / 5
        return at([(0, noise(0.4, 3000, -6)[: int(0.4 * SR)] * 0.05), (0.4, y * np.exp(-t * 1.5) * np.clip(t / 0.01, 0, 1) * 0.9)], 2.7)
    if name == "boom": n = int(2.6 * SR); t = np.arange(n) / SR; return pad(np.sin(2 * np.pi * np.cumsum(34 + 50 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.6), noise(0.5, 1200, 9) * 0.7, noise(2.4, 250, 1.6) * 0.3)
    if name == "heart":
        dur = kw["t1"] - kw["t"]; parts = []; t = 0.0
        while t < dur - 0.4:
            g = 0.55 + 0.45 * t / dur; parts += [(t, thump(54, 0.16, 26, 0.25, 200) * g), (t + 0.17, thump(48, 0.18, 22, 0.2, 180) * g * 0.8)]
            t += 60.0 / (kw["b0"] + (kw["b1"] - kw["b0"]) * t / dur)
        return at(parts, dur)
    if name == "static": n = int((kw["t1"] - kw["t"]) * SR); x = rng.standard_normal(n); y = (lp(x, 4000) - lp(x, 900)) * 0.5; y *= 0.6 + 0.4 * (rng.random(n) > 0.9993).cumsum() % 2; y[:800] *= np.linspace(0, 1, 800); y[-800:] *= np.linspace(1, 0, 800); return y * 0.35
    if name == "flicker":
        n = int((kw["t1"] - kw["t"]) * SR); t = np.arange(n) / SR; g = (np.sin(t * 23.0) + np.sin(t * 61.7) > 1.2).astype(float)
        return lp(np.sign(np.sin(2 * np.pi * 100 * t)) * g, 2500) * 0.25
    raise KeyError(name)

def build(n):
    import story
    ep = story.EPS[n]; N = int(ep.dur * SR); V = np.zeros(N); X = np.zeros(N); times = []; prev = -9
    for l in ep.lines:
        a = voice(l); i = int(l["t"] * SR); a = a[:max(0, N - i)]; V[i:i + len(a)] += a; t1 = l["t"] + len(a) / SR - 0.2; times.append((l["t"], round(t1, 3)))
        if l["t"] < prev - 0.05: print(f"  !! overlap at {l['t']:.1f}s ({l['sp']}: {l['text'][:30]}) prev ends {prev:.2f}")
        prev = t1
    json.dump(times, open(f"ep{n}_lines.json", "w"))
    for s in ep.sfx:
        if s["t"] < 0: continue
        a = sfx(s["name"], **{k: v for k, v in s.items() if k not in ("name", "db")}) * 10 ** (s["db"] / 20); i = int(s["t"] * SR); a = a[:max(0, N - i)]; X[i:i + len(a)] += a
    t = np.arange(N) / SR
    amb = (np.sin(2 * np.pi * 48 * t) * 0.5 + np.sin(2 * np.pi * 72.3 * t + 1) * 0.35 + np.sin(2 * np.pi * 96.7 * t + 2) * 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    amb += lp(rng.standard_normal(N), 260) * 2.2 + np.sin(2 * np.pi * 1318 * t) * 0.012 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t))
    amb *= 0.05 * np.clip(t / 1.5, 0, 1) * np.clip((ep.t_black - t) / 0.05, 0, 1)
    mix = V * 1.0 + X * 0.8 + amb; wsave(f"ep{n}_premix.wav", np.stack([mix, mix], 1) * 0.7, SR)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", f"ep{n}_premix.wav", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1]); g = min(-15.0 - I, 14)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"ep{n}_premix.wav", "-af", f"volume={g:.2f}dB,alimiter=limit=0.8:level=disabled", f"ep{n}_audio.wav"], check=True)
    print(f"ep{n}: {len(ep.lines)} lines, dur {ep.dur:.1f}s, premix {I:.1f} LUFS, gain {g:+.1f} dB")

if __name__ == "__main__":
    for n in [int(x) for x in sys.argv[1:]]: build(n)
