import numpy as np, wave
SR = 48000; DUR = 482 / 30 + 1.0; n = int(DUR * SR); rng = np.random.default_rng(6)
def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, np.float64), x.shape); a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def st(m): return np.stack([m, m], 1)
def whoosh(dur=0.6, peak=0.62, f0=300, f1=4200):
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); x = rng.standard_normal(m_)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    y = lp(x, np.clip(sw, 120, 9000)); y = y - lp(y, 180.0)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5)); y = y * env; y /= np.abs(y).max()
    pan = np.clip(t * 1.2 - 0.1, 0, 1); return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.3
def impact(dur=1.2, f_lo=44):
    m_ = int(dur * SR); t = np.arange(m_) / SR; f = f_lo + 55 * np.exp(-t * 18)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.8) + lp(rng.standard_normal(m_), 2600.0) * np.exp(-t * 90) * 0.55
    return st(y / np.abs(y).max())
def tick(f=2900, dur=0.08):
    m_ = int(dur * SR); t = np.arange(m_) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 85) + 0.5 * np.sin(2 * np.pi * f / 2 * t) * np.exp(-t * 60); return st(y / np.abs(y).max())
def tape_stop(dur=0.5):  # pitch-down swoosh for the slow-motion ramp
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); y = lp(rng.standard_normal(m_), 3000 * (1 - t) ** 2 + 150); y = y - lp(y, 120.0)
    y *= np.sin(np.pi * t) ** 0.8; return st(y / np.abs(y).max())
out = np.zeros((n, 2))
def place(sig, t, db, align=0.0):
    s = int((t - align) * SR); g = 10 ** (db / 20); a, b = max(s, 0), min(s + len(sig), n)
    if b > a: out[a:b] += sig[a - s:b - s] * g
place(whoosh(0.45, 0.45, 500, 6000), 0.0, -21)            # opening whip zoom
place(whoosh(0.4, 0.6, 600, 5000), 0.65, -24, 0.24); place(impact(), 0.70, -13)   # FIT CHECK lands on beat
place(whoosh(0.5, 0.5, 300, 4000), 1.87, -22, 0.25)       # text flies behind the head across the cut
for t in [2.32, 4.32, 6.33, 7.95]: place(tick(2800), t, -24)   # product tags
place(tape_stop(), 4.9, -27)                              # into slow motion
for c in [6.267, 9.633, 14.667]: place(whoosh(0.5, 0.55, 400, 5000), c, -24, 0.27)   # light-leak cuts
place(whoosh(0.35, 0.5, 900, 7000), 10.567, -21, 0.17)     # whip pan
place(whoosh(0.4, 0.6, 500, 5000), 12.967, -22, 0.24)      # zoom-through
for i, t in enumerate([13.2, 13.45, 13.96, 14.33]): place(tick(2300 + 200 * i, 0.06), t, -27)   # recap rows
place(impact(1.0, 55), 14.72, -16)                         # RATE DEN FIT
place(impact(1.4, 40), 482 / 30, -15); place(whoosh(0.6, 0.3, 300, 3000), 482 / 30, -25, 0.18)  # freeze
out = np.clip(out, -1, 1)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
print("sfx ok")
