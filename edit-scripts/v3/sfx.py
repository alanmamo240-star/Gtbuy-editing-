"""Synthesised sound design (no samples): soft whooshes into cuts, low impacts on headline landings, a subtle tick."""
import numpy as np, wave
SR = 48000
DUR = 13.52
rng = np.random.default_rng(7)

def onepole_lp(x, fc):
    """time-varying one-pole lowpass; fc array (Hz) per sample"""
    y = np.zeros_like(x); a = np.exp(-2 * np.pi * fc / SR); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

def whoosh(dur=0.6, peak=0.62, f0=300, f1=4200):
    n = int(dur * SR); t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    sweep = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    lp = onepole_lp(noise, np.clip(sweep, 120, 9000))
    hp = lp - onepole_lp(lp, np.full(n, 180.0))
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5))
    mono = hp * env; mono /= np.abs(mono).max() + 1e-9
    pan = np.clip(t * 1.2 - 0.1, 0, 1)               # gentle L->R movement
    return np.stack([mono * np.cos(pan * np.pi / 2), mono * np.sin(pan * np.pi / 2)], 1) * 1.3

def impact(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 46 + 50 * np.exp(-t * 18)                      # pitch drop
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.2)
    click = onepole_lp(rng.standard_normal(n), np.full(n, 2500.0)) * np.exp(-t * 90) * 0.5
    tail = onepole_lp(rng.standard_normal(n), np.full(n, 900.0)) * np.exp(-t * 3.5) * 0.08
    m = body + click + tail; m /= np.abs(m).max()
    return np.stack([m, m], 1)

def tick():
    n = int(0.08 * SR); t = np.arange(n) / SR
    m = np.sin(2 * np.pi * 2900 * t) * np.exp(-t * 85) + np.sin(2 * np.pi * 1450 * t) * np.exp(-t * 60) * 0.5
    m /= np.abs(m).max(); return np.stack([m * 0.9, m], 1)

out = np.zeros((int(DUR * SR), 2))
def place(sig, at, gain_db, align=0.0):
    """align: seconds into sig that should land at 'at'"""
    s = int((at - align) * SR); g = 10 ** (gain_db / 20)
    a, b = max(s, 0), min(s + len(sig), len(out))
    out[a:b] += sig[a - s:b - s] * g

W = whoosh(); WP = 0.6 * 0.62
place(whoosh(0.5, 0.7), 2.05, -25, 0.35)            # headline sweep-in
place(impact(), 2.32, -15)                           # "Fit Check" lands (on beat)
for c, g in [(1.60, -23), (5.73, -25), (6.67, -25), (12.00, -21)]:
    place(whoosh(), c, g, WP)                        # whoosh peaks exactly on the cut
place(impact(), 12.47, -14)                          # final headline lands (on beat)
place(tick(), 2.56, -27)                             # T-Shirt tag
place(tick(), 2.79, -27)                             # Hose tag
place(tick(), 12.78, -26)                            # label appears
place(tick(), 12.86, -30)
out = np.clip(out, -1, 1)
with wave.open("sfx.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print("sfx peak dBFS", round(20 * np.log10(np.abs(out).max() + 1e-9), 1))
