"""Synthesised 120 BPM fashion beat + SFX for the v5 fit-check, aligned to render5.py's cuts (every cut on a beat)."""
import numpy as np, wave, sys
sys.path.insert(0, "../../v4")
SR = 48000
DUR = 16.5
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
CHORDS = [([52, 55, 59], 28), ([48, 52, 55], 36), ([55, 59, 62], 31), ([50, 54, 57], 26)]  # Em C G D (+ bass)
K, C, HC, HO = kick(), clap(), hat(), hat(True)

# ---- arrangement: groove 0-10.5, break 10.5-12.0 (split-screen freeze), groove 12.0-13.5, outro 13.5-16.5
def in_break(t): return 10.5 <= t < 12.0
for b in range(int(DUR / BEAT)):
    t = b * BEAT
    outro = t >= 13.5
    if not in_break(t) and t < 16.0:
        put(music, K, t, -4 if not outro else -7)
        if b % 2 == 1 and not outro: put(music, C, t, -10)
        for h in range(2):
            ht = t + h * 0.25 + (0.03 if h else 0)
            if not in_break(ht) and ht < 16.0: put(music, HO if (h == 1 and b % 4 == 3) else HC, ht, -20 if not outro else -24)
    if b % 4 == 0 and t < 16.0:
        ch, bass = CHORDS[(b // 4) % 4]
        put(music, pad([NOTE(n) for n in ch], min(2.0, 16.5 - t), 1100 if not (outro or in_break(t)) else 750), t, -21 if not in_break(t) else -19)
        for k_ in range(4):
            bt = t + k_ * BEAT
            if not in_break(bt) and bt < 16.0: put(music, sub(NOTE(bass), 0.42), bt, -11 if not outro else -14)
for tt, nn in [(2.35, 76), (2.85, 71), (3.35, 79), (10.62, 76), (10.80, 71), (10.98, 79), (14.65, 71), (14.85, 76), (15.05, 79)]:
    put(music, pluck(NOTE(nn)), tt, -19)
for k_, tt in enumerate([3.5, 3.625, 3.75, 3.875]): put(music, C, tt, -16 + k_ * 1.5)
n = int(1.0 * SR); tt = np.linspace(0, 1, n)
riser = hp(lp(rng.standard_normal(n), 400 + 7000 * tt ** 2), 300) * tt ** 2.4
put(music, st(norm(riser)), 11.0, -17)
put(music, K, 16.0, -6)
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
put(sfx, impact(), 0.0, -9); at_peak(whoosh(0.45, .3, 4000, 300), 0.05, -16, .3, .45)
put(sfx, impact(0.8), 0.06, -14)
at_peak(whoosh(0.5, .6, 200, 6000), 2.0, -14)
for tt in (2.35, 2.85, 3.35): put(sfx, tick(), tt + 0.32, -22)
at_peak(whoosh(0.6, .65, 300, 5000), 4.0, -15, .65, .6)
put(sfx, shimmer(), 4.4, -25); at_peak(whoosh(0.4, .6, 600, 4000), 4.35, -23, .6, .4)
at_peak(whoosh(0.45, .5, 500, 6000), 5.5, -14, .5, .45)          # spin
put(sfx, impact(0.8), 5.62, -16); put(sfx, tick(3200), 6.42, -22)
put(sfx, glitch_burst(), 7.39, -17)
at_peak(whoosh(0.4, .6, 600, 4000), 7.85, -23, .6, .4); put(sfx, tick(), 8.1, -22)
at_peak(whoosh(0.5, .55, 300, 5000), 9.0, -15, .55, .5); put(sfx, shimmer(1.0), 9.05, -22)
put(sfx, shutter(), 10.5, -14); put(sfx, impact(1.2), 10.5, -11)
for tt in (10.62, 10.80, 10.98): at_peak(whoosh(0.3, .6, 800, 5000), tt + 0.12, -24, .6, .3)
at_peak(whoosh(0.4, .75, 4000, 400), 12.0, -16, .75, .4)
at_peak(whoosh(0.5, .6, 4000, 500), 13.5, -20)
at_peak(whoosh(0.5, .6, 300, 3500), 14.05, -22)
for k_, tt in enumerate((14.65, 14.85, 15.05)): put(sfx, tick(2600 + k_ * 350), tt, -22)
put(sfx, tick(3800), 15.35, -20)
def cut_snd():
    n = int(0.35 * SR); t = np.arange(n) / SR
    burst = hp(lp(rng.standard_normal(n), 9000.0), 2500) * np.exp(-t * 22) * np.clip(t / 0.002, 0, 1)
    click = np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 140) + np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 110) * 0.6
    thump = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 35)) / SR) * np.exp(-t * 14)
    l = norm(burst) * 0.55 + norm(click) * 0.5 + norm(thump) * 0.9; r = norm(np.roll(burst, 70)) * 0.55 + norm(click) * 0.5 + norm(thump) * 0.9
    return np.stack([l, r], 1)
CS = cut_snd()
for tt, db in [(0.0, -9), (2.0, -10), (4.0, -10), (5.5, -10), (7.5, -11), (9.0, -10), (10.5, -9), (12.0, -10), (13.5, -15)]:
    put(sfx, CS, tt, db)
mix = music[:N] * 0.9 + sfx[:N]
peak = np.abs(mix).max(); mix = mix / peak * 0.8
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("ok, pre-norm peak", round(peak, 2))
