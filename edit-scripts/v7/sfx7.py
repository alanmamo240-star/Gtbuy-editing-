"""Audio for v7: the creator's own song (kept in sync) + 2-beat outro tail + light SFX/cut sounds under it."""
import numpy as np, wave, subprocess, sys
SR = 48000; DUR = 15.3; N = int(DUR * SR)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "input.mov", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
song = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
out = np.zeros((N, 2), np.float32)
e = int(14.06 * SR); out[:e] = song[:e]
tail = song[int(13.00 * SR):int(14.06 * SR)].copy()          # last two beats again, filtered and faded
y = np.zeros_like(tail); a = np.exp(-2 * np.pi * 1200 / SR); s_ = np.zeros(2)
for i in range(len(tail)): s_ = (1 - a) * tail[i] + a * s_; y[i] = s_
env = np.linspace(1, 0, len(y))[:, None] ** 1.5
xf = int(0.03 * SR); out[e - xf:e] *= np.linspace(1, 0, xf)[:, None]; y[:xf] *= np.linspace(0, 1, xf)[:, None]
out[e - xf:e - xf + len(y)] += y * env * 1.1
rng = np.random.default_rng(7)
def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape); yy = np.empty_like(x); al = np.exp(-2 * np.pi * fc / SR); s = 0.0
    for i in range(len(x)): s = (1 - al[i]) * x[i] + al[i] * s; yy[i] = s
    return yy
def hp(x, fc): return x - lp(x, fc)
def norm(m): return m / (np.abs(m).max() + 1e-9)
def st(m): return np.stack([m, m], 1)
def whoosh(dur=0.5, peak=0.6, f0=300, f1=4500):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    x = hp(lp(rng.standard_normal(n), np.clip(sw, 120, 9000)), 180)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5)); return st(norm(x * env))
def tick(f=2900):
    n = int(0.07 * SR); t = np.arange(n) / SR; return st(norm(np.sin(2 * np.pi * f * t) * np.exp(-t * 90)))
def cut_snd():
    n = int(0.35 * SR); t = np.arange(n) / SR
    burst = hp(lp(rng.standard_normal(n), 9000.0), 2500) * np.exp(-t * 22)
    click = np.sin(2 * np.pi * 3100 * t) * np.exp(-t * 140)
    thump = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 35)) / SR) * np.exp(-t * 14)
    return st(norm(burst) * 0.55 + norm(click) * 0.5 + norm(thump) * 0.8)
def glitch(dur=0.2):
    n = int(dur * SR); x = np.repeat(np.round(rng.standard_normal(n // 6 + 1) * 3) / 3, 6)[:n]
    return st(norm(hp(x, 1500) * (np.sin(np.linspace(0, 40 * np.pi, n)) > 0) * np.hanning(n)))
sfx = np.zeros_like(out)
def put(sig, at, db):
    s = int(at * SR); g = 10 ** (db / 20); e2 = min(s + len(sig), N)
    if e2 > s >= 0: sfx[s:e2] += sig[:e2 - s] * g
def at_peak(sig, t, db, peak=0.6, dur=0.5): put(sig, t - peak * dur, db)
CS = cut_snd()
for c in (0.0, 2.03, 3.43, 4.53, 7.00, 8.53, 10.03, 11.93, 12.77): put(CS, c, -15)
at_peak(whoosh(0.5, .6, 200, 6000), 2.03, -20); at_peak(whoosh(0.6, .65, 300, 5000), 3.43, -20, .65, .6)
put(glitch(), 4.45, -22); at_peak(whoosh(0.5, .55, 300, 5000), 5.64, -20, .55, .5)
at_peak(whoosh(0.45, .5, 500, 6000), 8.53, -20, .5, .45); at_peak(whoosh(0.4, .75, 4000, 400), 11.93, -21, .75, .4)
for tt in (2.30, 2.62, 4.70, 5.13): put(tick(), tt + 0.32, -24)
for tt in (7.15, 7.55, 9.15, 9.35): put(tick(3300), tt + 0.1, -25)
for k, tt in enumerate((13.25, 13.43, 13.61, 13.79)): put(tick(2600 + k * 300), tt, -24)
put(tick(3800), 14.05, -22)
np.save("sfx7.npy", sfx); np.save("song7.npy", out); print("ok")
