"""Synthesised 120 BPM fashion beat + SFX for the v5 fit-check, aligned to render5.py's cuts (every cut on a beat)."""
import numpy as np, wave, sys
sys.path.insert(0, "../../v4")
SR = 48000
DUR = 12.5
BEAT = 0.5
rng = np.random.default_rng(12)
N = int(DUR * SR)
music = np.zeros((N + SR, 2)); sfx = np.zeros((N + SR, 2))

def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape); y = np.empty_like(x); a = np.exp(-2 * np.pi * fc / SR); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def hp(x, fc): return x - lp(x, fc)
def st(m, pan=0.5): return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def norm(m): return m / (np.abs(m).max() + 1e-9)
def put(buf, sig, at, db):
    s = int(at * SR); g = 10 ** (db / 20); e = min(s + len(sig), len(buf))
    if e > s >= 0: buf[s:e] += sig[:e - s] * g

# ---- instruments
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7) + lp(rng.standard_normal(n), 4000.0) * np.exp(-t * 160) * 0.35
    return st(np.tanh(norm(m) * 1.6))
def clap():
    n = int(0.3 * SR); t = np.arange(n) / SR
    env = sum(np.exp(-np.clip(t - d, 0, None) * 120) * (t >= d) for d in (0, .011, .022)) + np.exp(-t * 18) * 0.5
    m = hp(lp(rng.standard_normal(n), 3200.0), 900) * env
    return np.stack([norm(m), norm(np.roll(m, 90))], 1) * 0.9
def hat(open_=False):
    n = int((0.22 if open_ else 0.06) * SR); t = np.arange(n) / SR
    m = hp(rng.standard_normal(n), 7000) * np.exp(-t * (14 if open_ else 70))
    return st(norm(m), 0.62)
def sub(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    m = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    env = np.clip(t / 0.01, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
    return st(np.tanh(m * env * 1.4) * 0.8)
def pad(freqs, dur, cutoff=1400.0):
    n = int(dur * SR); t = np.arange(n) / SR
    m = sum(((t * f * d) % 1 * 2 - 1) for f in freqs for d in (1.0, 1.006, 0.995))
    m = lp(lp(m, cutoff), cutoff)
    env = np.clip(t / 0.25, 0, 1) * np.clip((dur - t) / 0.3, 0, 1)
    l = m * env; r = np.roll(l, int(0.012 * SR))
    return np.stack([norm(l), norm(r)], 1)
def pluck(freq, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    m = lp(((t * freq) % 1 * 2 - 1), 2600 * np.exp(-t * 12) + 300) * np.exp(-t * 9)
    return st(norm(m), 0.4)

NOTE = lambda midi: 440 * 2 ** ((midi - 69) / 12)
CHORDS = [([57, 60, 64], 33), ([53, 57, 60], 29), ([48, 52, 55], 36), ([55, 59, 62], 31)]  # Am F C G (+ bass)
K, C, HC, HO = kick(), clap(), hat(), hat(True)

# ---- arrangement: groove 0-8.4, break 8.4-9.0, outro 9.0-12.5
for b in range(int(DUR / BEAT)):
    t = b * BEAT
    in_break = 8.4 <= t < 9.0
    outro = t >= 9.0
    if not in_break and t < 12.0:
        put(music, K, t, -4 if not outro else -7)
        if b % 2 == 1 and not outro: put(music, C, t, -10)
        for h in range(2):
            ht = t + h * 0.25 + (0.03 if h else 0)  # light swing
            if not (8.4 <= ht < 9.0) and ht < 12.0:
                put(music, HO if (h == 1 and b % 4 == 3) else HC, ht, -20 if not outro else -24)
    if b % 4 == 0 and t < 12.0:
        ch, bass = CHORDS[(b // 4) % 4]
        if not in_break:
            put(music, pad([NOTE(n) for n in ch], 2.0 if t + 2 <= 12.5 else 12.5 - t, 1100 if not outro else 800), t, -21)
            for k_ in range(4):
                bt = t + k_ * BEAT
                if not (8.4 <= bt < 9.0) and bt < 12.0: put(music, sub(NOTE(bass), 0.42), bt, -11 if not outro else -14)
# small pluck motif on the tag beats
for tt, nn in [(2.0, 76), (2.5, 72), (3.0, 79), (7.5, 76), (7.75, 72), (8.0, 79), (10.15, 72), (10.35, 76), (10.55, 79)]:
    put(music, pluck(NOTE(nn)), tt, -19)
# drum fill into the zoom-through (3.5)
for k_, tt in enumerate([3.0, 3.125, 3.25, 3.375]): put(music, C, tt, -16 + k_ * 1.5)
# break: long pad + riser into 9.0
put(music, pad([NOTE(n) for n in (57, 64, 69)], 0.9, 2500.0), 8.4, -20)
n = int(0.6 * SR); tt = np.linspace(0, 1, n)
riser = hp(lp(rng.standard_normal(n), 400 + 7000 * tt ** 2), 300) * tt ** 2.4
put(music, st(norm(riser)), 8.4, -17)
put(music, K, 12.0, -6)
put(music, pad([NOTE(n) for n in (45, 57, 64)], 0.5, 600.0), 12.0, -18)

# ---- SFX
def whoosh(dur=0.5, peak=0.6, f0=300, f1=4500):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    x = hp(lp(rng.standard_normal(n), np.clip(sw, 120, 9000)), 180)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    pan = np.clip(t * 1.2 - .1, 0, 1); m = norm(x * env)
    return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def impact(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    m = np.sin(2 * np.pi * np.cumsum(42 + 60 * np.exp(-t * 16)) / SR) * np.exp(-t * 3.5) + lp(rng.standard_normal(n), 2400.0) * np.exp(-t * 80) * .5
    return st(norm(m))
def tick(f=2900):
    n = int(0.07 * SR); t = np.arange(n) / SR
    return st(norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 90)), 0.55)
def glitch_burst(dur=0.22):
    n = int(dur * SR); x = rng.standard_normal(n)
    x = np.round(x * 3) / 3  # bit-crush
    x = np.repeat(x[::6], 6)[:n]
    gate = (np.sin(np.linspace(0, 40 * np.pi, n)) > 0).astype(float)
    return st(norm(hp(x, 1500) * gate * np.hanning(n)))
def shutter():
    o = np.zeros((int(0.12 * SR), 2)); a = tick(1800); b = tick(2500)
    o[:len(a)] += a; o[int(.045 * SR):int(.045 * SR) + len(b)] += b * .8; return o
def shimmer(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(3520, 1), (5274, .6), (7040, .35)]) * np.exp(-t * 4.5) * np.clip(t / .03, 0, 1)
    return np.stack([m, np.roll(m, 300)], 1) / 2

def at_peak(sig, t, db, peak=0.6, dur=0.5): put(sfx, sig, t - peak * dur, db)
put(sfx, impact(), 0.0, -9)
at_peak(whoosh(0.45, .3, 4000, 300), 0.05, -16, .3, .45)
put(sfx, shimmer(), 0.35, -26)
at_peak(whoosh(0.5, .6, 200, 6000), 1.5, -14)            # whip
for tt in (2.0, 2.5, 3.0): put(sfx, tick(), tt + 0.3, -22)  # tag dots land
at_peak(whoosh(0.6, .65, 300, 5000), 3.5, -15, .65, .6)   # zoom-through
put(sfx, impact(0.8), 3.62, -15)                           # CB letters
put(sfx, glitch_burst(), 5.39, -17)                        # glitch slices
at_peak(whoosh(0.4, .6, 600, 4000), 5.85, -23, .6, .4)     # circle draw
at_peak(whoosh(0.5, .55, 300, 5000), 7.0, -15, .55, .5)    # studio reveal
put(sfx, shimmer(1.0), 7.05, -22)
for tt in (7.5, 7.75, 8.0): put(sfx, tick(3300), tt + 0.3, -23)
put(sfx, shutter(), 8.4, -14); put(sfx, impact(1.2), 8.4, -11)  # freeze
at_peak(whoosh(0.5, .6, 4000, 500), 9.0, -20)              # defocus dissolve
at_peak(whoosh(0.5, .6, 300, 3500), 9.55, -22)             # GTBuy flip
for k_, tt in enumerate((10.15, 10.35, 10.55)): put(sfx, tick(2600 + k_ * 350), tt, -22)
put(sfx, tick(3800), 10.85, -20)

mix = music[:N] * 0.9 + sfx[:N]
peak = np.abs(mix).max(); mix = mix / peak * 0.8
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok, pre-norm peak", round(peak, 2))
