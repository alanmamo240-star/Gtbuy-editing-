"""Sound design for v8 (synthesised): whooshes/pops/ticks on graphics, stamp impact, cut accents, soft pad under the end card."""
import numpy as np, wave
SR = 48000; DUR = 29.0; N = int(DUR * SR); rng = np.random.default_rng(8)
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
put(impact(), 0.0, -14); at_peak(whoosh(0.45, .3, 4000, 300), 0.05, -20, .3, .45); put(pop(), 0.25, -25)
put(riser(0.9), 0.40, -27); at_peak(whoosh(0.5, .55, 300, 5000), 1.30, -20, .55, .5)
for k in range(7): put(tick(2200 + 130 * k), 1.45 + k * 0.285, -29)
put(impact(0.9, 48), 2.20, -15); put(shimmer(), 2.5, -28)
at_peak(whoosh(0.5, .5, 200, 6000), 4.33, -18, .5, .5); put(cut_snd(), 4.33, -20)
put(impact(0.8, 52), 4.45, -19); put(shimmer(0.7), 4.7, -30)
at_peak(whoosh(0.5, .6, 300, 4000), 5.55, -24); put(tap(), 6.35, -20); at_peak(whoosh(0.4, .6, 3000, 600), 6.8, -26, .6, .4); put(pop(), 6.85, -24); put(tap(), 7.40, -20)
at_peak(whoosh(0.4, .6, 600, 4000), 7.9, -27, .6, .4)
put(pop(), 8.70, -22); put(pop(1000, 470), 9.66, -22); put(tick(), 10.44, -28)
put(cut_snd(), 11.10, -20); put(impact(0.8, 52), 11.15, -19)
at_peak(whoosh(0.5, .6, 300, 4000), 11.95, -25); put(pop(), 12.1, -25)
put(impact(0.9, 46), 14.40, -16); put(impact(0.8, 54), 14.80, -17); put(shimmer(0.7), 14.9, -29)
put(cut_snd(), 15.93, -22); at_peak(whoosh(0.5, .6, 300, 4500), 16.2, -24)
put(pop(800, 400), 16.26, -23); put(pop(900, 420), 16.40, -23); put(impact(0.7, 60), 16.92, -18); at_peak(whoosh(0.3, .6, 2000, 6000), 17.2, -25, .6, .3)
put(pop(), 18.05, -24)
for k in range(12): put(tick(1700 if k % 2 else 1400), 18.15 + k * 0.28, -31)
put(pop(1000, 470), 19.16, -24); put(impact(0.8, 50), 20.02, -19)
put(cut_snd(), 21.60, -17); put(impact(0.9, 46), 21.90, -17); put(shimmer(), 22.2, -29)
at_peak(whoosh(0.4, .6, 400, 4000), 22.3, -26, .6, .4); put(riser(1.6), 23.4, -30)
put(pad(3.1), 25.90, -26); put(impact(0.9, 46), 26.0, -18); put(shimmer(1.0), 26.5, -27)
for k in range(3): put(pop(850 + 70 * k, 420), 26.45 + k * 0.18, -24)
put(tap(), 27.8, -20); put(tick(3800), 28.0, -22)
out = out[:N]
with wave.open("sfx12.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print("peak dB", round(20 * np.log10(np.abs(out).max() + 1e-9), 1))
