"""Synthesised sound design + soft ambient pad (no samples). Writes sfx.wav and pad.wav (48 kHz stereo)."""
import numpy as np, wave
SR = 48000; DUR = 27.6
rng = np.random.default_rng(11)

def lp(x, fc):
    fc = np.broadcast_to(fc, x.shape); a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

def whoosh(dur=0.6, peak=0.62, f0=300, f1=4200):
    n = int(dur * SR); t = np.linspace(0, 1, n); x = rng.standard_normal(n)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    y = lp(x, np.clip(sw, 120, 9000)); y = y - lp(y, 180.0)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    y = y * env; y /= np.abs(y).max(); pan = np.clip(t * 1.2 - 0.1, 0, 1)
    return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.3

def impact(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 46 + 50 * np.exp(-t * 18); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
    click = lp(rng.standard_normal(n), 2500.0) * np.exp(-t * 90) * 0.5
    tail = lp(rng.standard_normal(n), 900.0) * np.exp(-t * 3.5) * 0.08
    m = body + click + tail; m /= np.abs(m).max(); return np.stack([m, m], 1)

def tick(f=2900):
    n = int(0.08 * SR); t = np.arange(n) / SR
    m = np.sin(2 * np.pi * f * t) * np.exp(-t * 85) + np.sin(2 * np.pi * f / 2 * t) * np.exp(-t * 60) * 0.5
    m /= np.abs(m).max(); return np.stack([m * 0.9, m], 1)

def swish(dur=0.35):        # short airy swish for cards
    return whoosh(dur, 0.55, 800, 6000)

def chime():                # soft two-note "saved" confirmation
    n = int(0.9 * SR); t = np.arange(n) / SR; m = np.zeros(n)
    for f0, st in [(1318.5, 0.0), (1975.5, 0.09)]:
        tt = np.clip(t - st, 0, None); m += np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 6) * (t >= st)
        m += 0.3 * np.sin(2 * np.pi * f0 * 2 * tt) * np.exp(-tt * 9) * (t >= st)
    m /= np.abs(m).max(); return np.stack([m, m * 0.95], 1)

out = np.zeros((int(DUR * SR), 2))
def place(sig, at, db, align=0.0):
    s = int((at - align) * SR); g = 10 ** (db / 20); a, b = max(s, 0), min(s + len(sig), len(out))
    out[a:b] += sig[a - s:b - s] * g

# --- timeline (seconds), synced to the visual events in render4.py
place(whoosh(0.5, 0.7), 0.42, -26, 0.35)    # hook headline sweep
place(impact(), 0.46, -16)                  # hook headline lands
place(swish(), 4.30, -28, 0.19)             # gifts card in
place(whoosh(0.5, 0.7), 8.48, -26, 0.35)    # "Delays" headline
place(impact(), 8.50, -18)
place(swish(), 9.75, -28, 0.19)             # warehouse card
place(tick(2400), 14.65, -30)               # chart card appears
place(tick(3200), 15.95, -27)               # chart peaks on "Shippingpreise"
place(swish(), 19.60, -28, 0.19)            # coupon card
place(whoosh(0.5, 0.7), 24.42, -25, 0.35)   # "4 Coupons"
place(impact(), 24.44, -15)
place(tick(2600), 26.00, -27)               # save badge pops
place(chime(), 26.62, -27)                  # badge fills = saved
for c in [3.67, 6.13, 8.9, 11.37, 16.47, 25.93]:
    place(whoosh(0.45, 0.6, 500, 3500), c, -33, 0.27)   # barely-there air on cuts

def save(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
save("sfx.wav", out)

# --- ambient pad: Fmaj9 - Am7 - Dm9 - Cmaj7, soft detuned triangles, low-passed, slow swells
def tri(f, t): return 2 * np.abs(2 * ((t * f) % 1) - 1) - 1
chords = [[174.6, 220.0, 261.6, 329.6, 392.0], [220.0, 261.6, 329.6, 392.0, 196.0],
          [146.8, 220.0, 261.6, 349.2, 329.6], [130.8, 196.0, 246.9, 329.6, 392.0]]
n = int(DUR * SR); t = np.arange(n) / SR; pad = np.zeros((n, 2)); bar = 3.5
for k in range(int(DUR / bar) + 1):
    ch = chords[k % 4]; t0 = k * bar
    seg = (t >= t0) & (t < t0 + bar + 1.5); tt = t[seg] - t0
    env = np.clip(tt / 1.2, 0, 1) * np.clip((bar + 1.5 - tt) / 1.5, 0, 1)
    for j, f in enumerate(ch):
        for det, side in [(-0.12, 0), (0.12, 1)]:
            pad[seg, side] += tri(f * (1 + det / 100), tt) * env * (0.5 if j == 0 else 0.32)
for c in range(2): pad[:, c] = lp(lp(pad[:, c], 900.0), 1400.0)
lfo = 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t)
pad *= lfo[:, None]
# cheap stereo "room": a few decaying delays
for d, g in [(0.031, 0.35), (0.047, 0.3), (0.089, 0.22), (0.131, 0.15)]:
    s = int(d * SR); pad[s:, 0] += pad[:-s, 1] * g; pad[s:, 1] += pad[:-s, 0] * g
pad /= np.abs(pad).max(); pad *= np.clip(t / 1.5, 0, 1)[:, None] * np.clip((DUR - t) / 1.2, 0, 1)[:, None]
save("pad.wav", pad * 0.9)
print("ok")
