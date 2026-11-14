"""Synthesised sound design for v4, synced to render4.py animation times. No samples."""
import numpy as np, wave
SR = 48000
DUR = 1087 / 30
rng = np.random.default_rng(4)

def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    y = np.empty_like(x); a = np.exp(-2 * np.pi * fc / SR); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def hp(x, fc): return x - lp(x, fc)
def st(m, pan=0.5): return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def norm(m): return m / (np.abs(m).max() + 1e-9)

def whoosh(dur=0.6, peak=0.62, f0=300, f1=4200, pan_move=True):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    sweep = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    x = hp(lp(rng.standard_normal(n), np.clip(sweep, 120, 9000)), 180)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    m = norm(x * env)
    if not pan_move: return st(m) * 1.3
    pan = np.clip(t * 1.2 - 0.1, 0, 1)
    return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1) * 1.3

def impact(dur=1.2, f_lo=44, punch=50, tail=0.08):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f_lo + punch * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.0)
    click = lp(rng.standard_normal(n), 2500.0) * np.exp(-t * 90) * 0.5
    tl = lp(rng.standard_normal(n), 900.0) * np.exp(-t * 3.2) * tail
    return st(norm(body + click + tl))

def sub_drop(dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 80 * np.exp(-t * 6)
    return st(norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4) * np.clip(t / 0.01, 0, 1)))

def tick(f=2900):
    n = int(0.08 * SR); t = np.arange(n) / SR
    m = np.sin(2 * np.pi * f * t) * np.exp(-t * 85) + np.sin(2 * np.pi * f / 2 * t) * np.exp(-t * 60) * 0.5
    return st(norm(m), 0.55)

def pop(f0=900, f1=420):
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 40)
    m = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 38) * np.clip(t / 0.002, 0, 1)
    return st(norm(m))

def shimmer(dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t + p) * a for f, a, p in [(3520, 1, 0), (5274, .6, 1), (7040, .35, 2), (4186, .5, 3)])
    m *= np.exp(-t * 4.5) * np.clip(t / 0.03, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 14 * t))
    return np.stack([m, np.roll(m, 300)], 1) / 2.5

def riser(dur=0.9):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    x = hp(lp(rng.standard_normal(n), 300 + 6000 * t ** 2), 250) * 0.6
    f = 180 + 900 * t ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return st(norm((x + tone) * t ** 2.5))

def scratch(dur=0.28):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    x = hp(lp(rng.standard_normal(n), 2500 + 3000 * t), 900)
    return st(norm(x * np.sin(np.pi * t) ** 1.5), 0.6)

def shutter():
    a = tick(1800); b = tick(2400)
    out = np.zeros((int(0.14 * SR), 2)); out[:len(a)] += a; out[int(0.05 * SR):int(0.05 * SR) + len(b)] += b * 0.8
    return out

def pad(dur, chord=(110, 164.81, 220, 277.18)):
    n = int(dur * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.004 * t + 1) for f in chord)
    m = lp(m, 900.0)
    env = np.clip(t / 0.35, 0, 1) * np.clip((dur - t) / 0.5, 0, 1)
    return st(norm(m * env))

out = np.zeros((int(DUR * SR) + SR, 2))
def place(sig, at, db, align=0.0):
    s = int((at - align) * SR); g = 10 ** (db / 20)
    a, b = max(s, 0), min(s + len(sig), len(out))
    if b > a: out[a:b] += sig[a - s:b - s] * g
WP = 0.6 * 0.62

# HOOK
place(sub_drop(), 0.0, -12)
place(whoosh(0.5, 0.15, 3000, 400), 0.0, -20)          # reverse-ish swoosh on the punch-out
place(tick(), 0.15, -30)
place(whoosh(0.45, 0.7, 500, 5000), 1.40, -27, 0.31)
place(impact(), 1.76, -12)                              # 0€ lands
place(shimmer(), 2.05, -28)                             # chrome sweep
# SAVE
place(whoosh(0.5, 0.5, 200, 6000), 4.70, -18, 0.25)     # whip pan
place(pop(), 5.78, -21); place(tick(3600), 5.80, -27)  # bookmark fills
place(pop(700, 380), 6.40, -27)
# ACCOUNT
place(whoosh(0.6, 0.65, 300, 5000, False), 7.27, -20, 0.39)  # zoom-through
place(impact(0.8, 52, 30, 0.04), 7.27, -22)
place(whoosh(0.4, 0.6, 600, 4500), 8.50, -28, 0.24)
place(tick(3200), 8.95, -30)                            # arrow head
place(pop(820, 400), 8.70, -24)                         # link card
place(impact(0.9, 50, 40), 9.90, -17)                   # GTBuy
place(shimmer(0.7), 10.05, -31)
place(whoosh(0.5, 0.6, 400, 4000), 11.05, -27, 0.3)     # coupon card
place(pop(), 11.42, -22); place(pop(1000, 470), 12.28, -22)
place(tick(), 12.97, -31)
# HAUL
place(riser(0.75), 13.12, -22)
place(sub_drop(1.4), 13.87, -13); place(impact(0.7, 60, 30, 0.02), 13.87, -21)
place(pad(3.0, (98, 146.83, 196, 246.94)), 13.87, -34)  # atmosphere under the haul flat-lay
place(whoosh(0.5, 0.6, 500, 4500), 14.75, -26, 0.3)    # perspective flip
# 01 CARDHOLDER
place(whoosh(0.35, 0.4, 2000, 7000, False), 17.00, -24, 0.14)
place(impact(0.9, 46, 40), 17.05, -19)
place(whoosh(0.6, 0.6, 400, 5000), 17.98, -26, 0.36)
place(shimmer(0.9), 18.25, -30)
place(whoosh(0.5, 0.6, 400, 4000), 19.30, -28, 0.3)
place(pop(), 19.70, -24); place(pop(950, 450), 20.94, -24); place(pop(1050, 480), 23.36, -24)
# 02 MÜTZEN
place(whoosh(0.5, 0.62, 300, 5000), 24.30, -18, 0.31)
place(impact(), 24.45, -14)
place(pad(1.6, (110, 164.81, 207.65, 277.18)), 24.30, -35)
place(whoosh(0.45, 0.75, 800, 5000), 25.62, -22, 0.34)
place(pop(), 27.30, -25)
place(whoosh(0.4, 0.6, 500, 4500), 29.30, -27, 0.24)
place(scratch(), 29.95, -25)
# 03 TEES
place(whoosh(0.4, 0.75, 4000, 400), 30.10, -18, 0.3)    # push down
place(impact(1.0, 42, 50), 30.40, -14)
place(pad(1.8, (98, 146.83, 196, 233.08)), 30.10, -35)
place(shimmer(0.9), 30.95, -29)
place(whoosh(0.5, 0.6, 3000, 600), 31.88, -26, 0.3)     # shrink into card
place(pop(), 32.30, -24); place(pop(980, 460), 33.10, -24)
place(whoosh(0.4, 0.6, 400, 4000), 33.80, -29, 0.24)
# RECAP + END
place(whoosh(0.5, 0.6, 300, 4000), 34.10, -25, 0.3)
for k, f in enumerate([2600, 2950, 3350]): place(tick(f), 34.32 + k * 0.25, -25)
place(pop(), 35.10, -22); place(tick(3800), 35.14, -28)  # end link card
place(shutter(), 35.73, -24)
place(sub_drop(1.2), 35.73, -18)

out = out[:int(DUR * SR)]
out = np.clip(out, -1, 1)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print("sfx peak dBFS", round(20 * np.log10(np.abs(out).max() + 1e-9), 1))
