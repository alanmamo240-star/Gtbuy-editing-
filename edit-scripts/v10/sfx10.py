"""Sound design for v8 (synthesised): whooshes/pops/ticks on graphics, stamp impact, cut accents, soft pad under the end card."""
import numpy as np, wave
SR = 48000; DUR = 38.9; N = int(DUR * SR); rng = np.random.default_rng(8)
def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape); y = np.empty_like(x); a = np.exp(-2 * np.pi * fc / SR); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def hp(x, fc): return x - lp(x, fc)
def norm(m): return m / (np.abs(m).max() + 1e-9)
def st(m, pan=0.5): return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def whoosh(dur=0.5, peak=0.6, f0=300, f1=4500):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    x = hp(lp(rng.standard_normal(n), np.clip(sw, 120, 9000)), 180)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5)); m = norm(x * env)
    pan = np.clip(t * 1.2 - .1, 0, 1); return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def impact(dur=1.1, f=44):
    n = int(dur * SR); t = np.arange(n) / SR
    return st(norm(np.sin(2 * np.pi * np.cumsum(f + 55 * np.exp(-t * 16)) / SR) * np.exp(-t * 3.8) + lp(rng.standard_normal(n), 2400.0) * np.exp(-t * 80) * .5))
def tick(f=2900):
    n = int(0.07 * SR); t = np.arange(n) / SR; return st(norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 90)), .55)
def pop(f0=900, f1=420):
    n = int(0.12 * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t * 40)
    return st(norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * np.clip(t / .002, 0, 1)))
def tap():
    n = int(0.09 * SR); t = np.arange(n) / SR
    return st(norm(np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 70) + lp(rng.standard_normal(n), 3000.0) * np.exp(-t * 200) * .4))
def shimmer(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(3520, 1), (5274, .6), (7040, .35)]) * np.exp(-t * 4.5) * np.clip(t / .03, 0, 1)
    return np.stack([m, np.roll(m, 300)], 1) / 2
def pad(dur, freqs=(146.8, 220.0, 293.7, 370.0)):
    n = int(dur * SR); t = np.arange(n) / SR
    m = lp(sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.004 * t + 1) for f in freqs), 900.0)
    return st(norm(m * np.clip(t / 0.4, 0, 1) * np.clip((dur - t) / 0.6, 0, 1)))
def cut_snd():
    n = int(0.35 * SR); t = np.arange(n) / SR
    b = hp(lp(rng.standard_normal(n), 9000.0), 2500) * np.exp(-t * 22); c = np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 140)
    th = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 35)) / SR) * np.exp(-t * 14)
    return st(norm(b) * .55 + norm(c) * .5 + norm(th) * .8)
def riser(dur=0.7):
    n = int(dur * SR); t = np.linspace(0, 1, n); return st(norm(hp(lp(rng.standard_normal(n), 400 + 6000 * t ** 2), 250) * t ** 2.5))
out = np.zeros((N + SR, 2))
def put(sig, at, db):
    s = int(at * SR); g = 10 ** (db / 20); e = min(s + len(sig), len(out))
    if e > s >= 0: out[s:e] += sig[:e - s] * g
def at_peak(sig, t, db, peak=0.6, dur=0.5): put(sig, t - peak * dur, db)
put(impact(), 0.0, -14); at_peak(whoosh(0.45, .3, 4000, 300), 0.05, -20, .3, .45); put(shimmer(1.4), 0.1, -30)
at_peak(whoosh(0.4, .6, 500, 4000), 0.80, -25, .6, .4); put(impact(0.9, 50), 1.05, -15); put(shimmer(), 1.3, -28); put(pop(), 1.75, -22)
for k in range(8): put(tick(2000 + 90 * k), 4.55 + k * 0.05, -32)
for k in range(6): put(tick(2700 + 120 * k), 5.26 + k * 0.05, -31)
put(impact(0.7, 56), 5.30, -19)
at_peak(whoosh(0.4, .5, 300, 5000), 6.05, -21, .5, .4); at_peak(whoosh(0.4, .6, 4000, 500), 7.0, -25, .6, .4)
put(pop(), 9.20, -23); put(tick(), 9.95, -28); put(pop(1000, 470), 10.20, -23)
at_peak(whoosh(0.5, .5, 200, 6000), 10.78, -19, .5, .5); put(cut_snd(), 10.78, -21)
put(pop(700, 380), 11.10, -24); put(pop(800, 400), 11.60, -23); put(pop(900, 420), 12.30, -22); put(tick(), 12.3, -28)
at_peak(whoosh(0.5, .6, 300, 4000), 14.30, -25); put(pop(), 15.35, -25)
put(riser(0.5), 15.6, -27); put(impact(0.9, 48), 16.10, -16); put(shimmer(), 16.3, -29)
put(impact(1.0, 46), 18.40, -15); put(shimmer(1.0), 18.85, -24)
at_peak(whoosh(0.5, .6, 300, 4000), 19.60, -24); put(tap(), 20.5, -20); at_peak(whoosh(0.4, .6, 3000, 600), 20.95, -26, .6, .4); put(tap(), 21.6, -20)
put(pop(), 21.55, -22); at_peak(whoosh(0.4, .6, 600, 4000), 22.25, -27, .6, .4); put(pop(1000, 470), 22.90, -22)
put(pop(), 24.55, -23); at_peak(whoosh(0.3, .6, 2000, 7000), 25.05, -24, .6, .3); put(impact(0.8, 52), 25.88, -17); put(shimmer(0.7), 26.0, -29)
at_peak(whoosh(0.5, .6, 400, 4000), 26.5, -26); put(tick(), 27.15, -27)
put(impact(1.0, 40), 27.80, -12); put(tick(1800), 27.80, -18)
at_peak(whoosh(0.4, .5, 300, 5000), 28.55, -21, .5, .4); at_peak(whoosh(0.4, .6, 4000, 500), 30.2, -25, .6, .4)
put(pop(), 30.5, -25); put(impact(0.7, 60), 31.30, -18); put(pop(1000, 470), 31.96, -23); put(impact(0.9, 46), 33.62, -16); put(shimmer(), 33.8, -28)
put(pad(3.2), 35.80, -26); put(impact(0.9, 46), 35.85, -18); put(shimmer(1.0), 36.3, -26)
put(tap(), 37.4, -20); put(tick(3800), 37.5, -22)
out = out[:N]
with wave.open("sfx10.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print("peak dB", round(20 * np.log10(np.abs(out).max() + 1e-9), 1))
