"""Sound design for v8 (synthesised): whooshes/pops/ticks on graphics, stamp impact, cut accents, soft pad under the end card."""
import numpy as np, wave
SR = 48000; DUR = 36.4; N = int(DUR * SR); rng = np.random.default_rng(8)
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
put(impact(), 0.0, -14); at_peak(whoosh(0.45, .3, 4000, 300), 0.05, -20, .3, .45)
put(impact(0.9, 50), 0.40, -16); put(shimmer(), 0.8, -28); at_peak(whoosh(0.4, .6, 500, 4000), 0.62, -26, .6, .4); put(pop(), 1.45, -24)
put(tick(), 2.2, -30); at_peak(whoosh(0.5, .5, 200, 6000), 2.82, -18, .5, .5); put(cut_snd(), 2.82, -20)
at_peak(whoosh(0.5, .6, 300, 4000), 3.75, -24); put(tap(), 4.55, -20); at_peak(whoosh(0.4, .6, 3000, 600), 5.0, -26, .6, .4); put(tap(), 5.75, -20)
at_peak(whoosh(0.4, .6, 600, 4000), 6.35, -27, .6, .4)
put(pop(), 6.62, -22); put(pop(1000, 470), 7.56, -22); put(tick(), 8.40, -28)
put(pop(), 9.95, -23); at_peak(whoosh(0.3, .6, 2000, 7000), 10.42, -24, .6, .3); put(impact(0.8, 52), 10.80, -17); put(shimmer(0.7), 11.0, -29)
at_peak(whoosh(0.5, .6, 400, 4000), 11.4, -26); put(pop(820, 400), 11.84, -24)
put(cut_snd(), 13.30, -22)
put(impact(1.0, 40), 14.38, -12); put(tick(1800), 14.38, -18)
put(cut_snd(), 15.70, -20); at_peak(whoosh(0.5, .6, 300, 5000), 15.72, -22); put(shimmer(), 16.0, -29)
at_peak(whoosh(0.5, .6, 400, 4000), 16.3, -26)
for k, tt in enumerate((17.26, 18.14, 19.10, 20.44)): put(pop(900 + k * 60, 420 + k * 20), tt, -23)
put(cut_snd(), 22.0, -20); at_peak(whoosh(0.4, .8, 500, 7000), 22.30, -19, .8, .4)
put(riser(0.6), 24.85, -26); at_peak(whoosh(0.4, .5, 300, 5000), 25.45, -20, .5, .4)
at_peak(whoosh(0.4, .6, 4000, 500), 27.05, -24, .6, .4); put(impact(0.9, 48), 27.30, -16); put(shimmer(), 27.5, -29)
for k in range(4): put(tick(2400 + k * 300), 27.6 + k * 0.2, -28)
put(pop(), 29.40, -25)
at_peak(whoosh(0.4, .6, 300, 4500), 30.40, -22, .6, .4); at_peak(whoosh(0.4, .6, 4500, 300), 31.92, -24, .6, .4)
put(impact(0.9, 48), 31.94, -17); put(pop(), 32.5, -26)
put(pad(3.0), 33.40, -26); at_peak(whoosh(0.5, .6, 300, 3500), 33.5, -22)
put(tap(), 34.9, -20); put(tick(3800), 35.2, -22)
out = out[:N]
with wave.open("sfx8.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
print("peak dB", round(20 * np.log10(np.abs(out).max() + 1e-9), 1))
