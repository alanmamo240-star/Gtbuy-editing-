"""Sound design + final mix -> build/audio.wav (48k stereo)"""
import wave, math, numpy as np
from story import START, KNOCKS, BUZZ, LIGHT_ON, END_BLACK, CARD, DUR, CUTS
SR = 48000; N = int(DUR * SR); rng = np.random.default_rng(13)
def rd(p):
    with wave.open(p) as w: return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def lp(x, fc):
    from scipy.signal import lfilter
    a = math.exp(-2 * math.pi * fc / SR); return lfilter([1 - a], [1, -a], x)
def env(n, a=0.002, d=8.0): t = np.arange(n) / SR; return np.clip(t / a, 0, 1) * np.exp(-t * d)
def tone(f, dur, d=8.0, a=0.002): n = int(dur * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * f * t) * env(n, a, d)
def noise(dur, fc, d=20.0): n = int(dur * SR); return lp(rng.standard_normal(n), fc) * env(n, 0.001, d)
def pad(*xs):
    o = np.zeros(max(len(x) for x in xs))
    for x in xs: o[:len(x)] += x
    return o
BUS = dict(m=np.zeros((N, 2)), v=np.zeros((N, 2)))
def put(x, t, g=1.0, pan=0.0, bus="m"):
    i = int(t * SR); x = np.asarray(x)[:max(0, N - i)] * g; B = BUS[bus]
    B[i:i + len(x), 0] += x * math.sqrt(0.5 * (1 - pan)) * 1.41; B[i:i + len(x), 1] += x * math.sqrt(0.5 * (1 + pan)) * 1.41
def db(x): return 10 ** (x / 20)
def knock(): return pad(tone(105, 0.25, 18), noise(0.14, 900, 40) * 0.9, tone(240, 0.1, 40) * 0.4) * 0.9
def buzz():
    n = int(0.42 * SR); t = np.arange(n) / SR; b = lp(np.sign(np.sin(2 * np.pi * 150 * t)), 600) * np.clip(t / 0.01, 0, 1) * np.clip((0.42 - t) / 0.03, 0, 1)
    o = np.zeros(int(1.0 * SR)); o[:n] += b; o[int(0.55 * SR):int(0.55 * SR) + n] += b; return o * 0.5
def heart(dur):
    o = np.zeros(int(dur * SR)); t = 0.0
    while t < dur - 0.4:
        g = 0.6 + 0.4 * t / dur
        for dt, f in ((0, 52), (0.17, 46)):
            x = pad(tone(f, 0.22, 20), noise(0.12, 180, 30) * 0.4) * g; i = int((t + dt) * SR); o[i:i + len(x)] += x[:len(o) - i]
        t += 0.86 - 0.25 * t / dur
    return o
def creak(dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR; f = 330 - 80 * t / dur + 20 * np.sin(2 * np.pi * 8 * t)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sign(np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR)) * 0.1) * np.clip(t / 0.2, 0, 1) * np.clip((dur - t) / 0.3, 0, 1) * (0.6 + 0.4 * np.sin(2 * np.pi * 5.3 * t)) * 0.3
def whoosh(dur=0.6):
    n = int(dur * SR); t = np.linspace(0, 1, n); x = lp(rng.standard_normal(n), 2500); return x * np.sin(np.pi * t) ** 2 * 0.8
def sting():
    n = int(3.0 * SR); t = np.arange(n) / SR; y = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((207.6, 220, 311.1, 329.6, 110, 55))) / 6
    scr = lp(rng.standard_normal(n), 4000) * np.exp(-t * 3) * 0.5
    return (y * np.exp(-t * 1.1) * np.clip(t / 0.01, 0, 1) + scr) * 0.9
def boom():
    n = int(3.0 * SR); t = np.arange(n) / SR; return pad(np.sin(2 * np.pi * np.cumsum(32 + 50 * np.exp(-t * 6)) / SR) * np.exp(-t * 1.3), noise(0.5, 1200, 9) * 0.6)
def powerdown():
    n = int(0.9 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(180 * np.exp(-t * 3) + 25) / SR) * np.exp(-t * 2.5) * 0.7
def hum(dur):
    n = int(dur * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t)) * 0.05
def drone(t0, t1, root=55.0, g=1.0, rise=0.0):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; u = t / max(t1 - t0, 0.1)
    f = root * (1 + rise * u ** 2)
    y = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.6 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t))
         + 0.35 * np.sin(2 * np.pi * np.cumsum(f * 2.02) / SR) + 0.25 * np.sin(2 * np.pi * np.cumsum(f * 1.189) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t + 1)))
    y += lp(rng.standard_normal(n), 300) * 0.8
    e = np.clip(t / 1.5, 0, 1) * np.clip((t1 - t0 - t) / 0.6, 0, 1)
    return y * e * 0.12 * g
def music_box(t0, notes, g=0.25):
    for i, (dt, f) in enumerate(notes):
        x = pad(tone(f, 1.6, 2.5), tone(f * 2, 1.0, 4) * 0.3, tone(f * 3.01, 0.6, 7) * 0.12); put(x, t0 + dt, g * 0.5, pan=0.25 * math.sin(i))

# ---- music / ambience
put(drone(0.0, 9.3, 55, 1.2), 0.0)
music_box(0.6, [(0, 659.3), (0.55, 622.3), (1.1, 659.3), (1.65, 493.9), (2.6, 523.3), (3.15, 440), (4.5, 659.3), (5.05, 622.3), (5.6, 659.3), (6.15, 493.9), (7.1, 587.3), (7.65, 392)], 0.35)
put(noise(9.0, 300, 0) * 0.0, 0)
# day: soft room tone + warm pad
n = int(12.4 * SR); tt = np.arange(n) / SR
pad_day = sum(np.sin(2 * np.pi * f * tt) for f in (220, 261.6, 329.6)) / 3 * np.clip(tt / 1.0, 0, 1) * np.clip((12.4 - tt) / 1.0, 0, 1) * 0.04
put(pad_day, 9.2); put(lp(rng.standard_normal(n), 400) * 0.02, 9.2)
put(drone(15.4, 21.8, 49, 0.7), 15.4)        # mother turns cold
put(drone(21.6, 33.8, 46.25, 1.0, 0.03), 21.6)
put(noise(12.0, 1500, 0)[:int(12 * SR)] * 0.0, 0)
put(lp(rng.standard_normal(int(12 * SR)), 900) * 0.025 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * np.arange(int(12 * SR)) / SR)), 21.6)  # night wind
put(drone(33.6, 52.4, 41.2, 1.1, 0.08), 33.6)
put(heart(8.8), 33.7, 0.9)
put(drone(52.2, END_BLACK + 0.1, 36.7, 1.3, 0.25), 52.2)
put(hum(10.8), 52.2)
put(drone(CARD - 0.6, DUR, 55, 0.8), CARD - 0.6); put(heart(DUR - CARD), CARD, 0.6)
music_box(CARD + 0.2, [(0, 659.3), (0.6, 622.3), (1.2, 659.3), (1.8, 493.9)], 0.3)

# ---- sfx
put(whoosh(0.7), 0.0, 0.25)
for k in KNOCKS: put(knock(), k, db(-1), pan=0.35)
put(creak(1.8), 28.0, 0.5)
put(creak(1.2), 33.9, 0.35, pan=-0.3)
for k in range(9): put(pad(noise(0.08, 500, 40) * 0.6, tone(80, 0.1, 30) * 0.4), 33.9 + k * 0.48, 0.35 * (1 - k * 0.05), pan=0.1)  # footsteps
put(noise(1.2, 5000, 4) * 0.08, 38.2)  # scratch
for k in range(10): put(noise(0.05, 6000, 60) * 0.5, 38.25 + k * 0.1 + rng.uniform(0, 0.04), 0.35)
for b in BUZZ: put(buzz(), b, db(-2))
put(sting(), LIGHT_ON, db(-1)); put(tone(1800, 0.05, 60) * 0.3, LIGHT_ON)
put(whoosh(0.5), 57.45, 0.35)
put(powerdown(), 62.55, 0.8); put(boom(), END_BLACK, 1.0)
for c in CUTS: put(whoosh(0.35), c - 0.15, 0.06)

# ---- voices (duck music under)
duck = np.ones(N)
for k, st in START.items():
    v = rd(f"build/vo_{k}.wav"); g = db(2.0)
    put(v, st, g, pan=0.0, bus="v")
    i0, i1 = int((st - 0.1) * SR), int((st + len(v) / SR + 0.2) * SR); duck[max(0, i0):min(N, i1)] = 0.6
from scipy.ndimage import uniform_filter1d
duck = uniform_filter1d(duck, int(0.15 * SR))
out = BUS["m"] * db(-3) * duck[:, None] + BUS["v"]
pk = np.abs(out).max(); out = out / pk * 0.89
with wave.open("build/audio_raw.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
print("peak", pk)
