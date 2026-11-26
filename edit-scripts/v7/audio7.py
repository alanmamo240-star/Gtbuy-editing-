"""Cut voice track (12 ms crossfades), synthesized lo-fi groove and SFX timed to the output timeline (tl.py)."""
import numpy as np, wave, subprocess
from tl import SEGS, OUT_START, DUR, DUR_MAIN, CUTS_OUT, s2o
SR = 48000; rng = np.random.default_rng(27)
def save(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(name, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "input_cfr.mov", "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2)
n = int(DUR * SR); voice = np.zeros((n, 2), np.float32); xf = int(0.012 * SR)
for k, (a, b) in enumerate(SEGS):
    seg = src[int(a * SR):int(b * SR)].copy(); r = np.linspace(0, 1, xf)[:, None]; seg[:xf] *= r; seg[-xf:] *= r[::-1]
    o = int(OUT_START[k] * SR); m = max(0, min(len(seg), n - o)); voice[o:o + m] += seg[:m]
save("voice_cut.wav", voice)

def lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, np.float64), x.shape); a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def st(m, pan=0.5): return np.stack([m * np.cos(pan * np.pi / 2), m * np.sin(pan * np.pi / 2)], 1)
def whoosh(dur=0.6, peak=0.62, f0=300, f1=4200):
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); x = rng.standard_normal(m_)
    sw = np.where(t < peak, f0 + (f1 - f0) * (t / peak) ** 2, f1 * np.exp(-(t - peak) * 5))
    y = lp(x, np.clip(sw, 120, 9000)); y = y - lp(y, 180.0)
    env = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 4.5)); y = y * env; y /= np.abs(y).max()
    pan = np.clip(t * 1.2 - 0.1, 0, 1); return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.3
def impact(dur=1.2, f_lo=44):
    m_ = int(dur * SR); t = np.arange(m_) / SR; f = f_lo + 55 * np.exp(-t * 18)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.8) + lp(rng.standard_normal(m_), 2600.0) * np.exp(-t * 90) * 0.55 \
        + lp(rng.standard_normal(m_), 900.0) * np.exp(-t * 3.2) * 0.09
    return st(y / np.abs(y).max())
def tick(f=2900, dur=0.08):
    m_ = int(dur * SR); t = np.arange(m_) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 85) + 0.5 * np.sin(2 * np.pi * f / 2 * t) * np.exp(-t * 60); return st(y / np.abs(y).max())
def pop(f=520):
    m_ = int(0.18 * SR); t = np.arange(m_) / SR; fr = f * (1 + 1.4 * np.exp(-t * 40))
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 22); return st(y / np.abs(y).max())
def riser(dur=1.2):
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); y = lp(rng.standard_normal(m_), 300 + 7000 * t ** 2.5); y = y - lp(y, 250.0)
    y = (y / np.abs(y).max() + np.sin(2 * np.pi * np.cumsum(220 + 660 * t ** 2) / SR) * 0.25) * t ** 2.4; y /= np.abs(y).max()
    return np.stack([y, np.roll(y, 300)], 1)
def scratch(dur=0.22):
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); y = lp(rng.standard_normal(m_), 1500 + 5000 * t); y *= np.sin(np.pi * t) ** 0.7
    return st(y / np.abs(y).max(), 0.6)
def chime():
    m_ = int(0.9 * SR); t = np.arange(m_) / SR; y = np.zeros(m_)
    for f0, s0 in [(1318.5, 0.0), (1975.5, 0.09)]:
        tt = np.clip(t - s0, 0, None); y += (np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 6) + 0.3 * np.sin(4 * np.pi * f0 * tt) * np.exp(-tt * 9)) * (t >= s0)
    return st(y / np.abs(y).max())
def stamp():
    y = impact(0.5, 70)[:, 0] * 0.8; t = np.arange(len(y)) / SR; y += lp(rng.standard_normal(len(y)), 1800.0) * np.exp(-t * 40) * 0.6
    return st(y / np.abs(y).max())
def hiss(dur=0.9):  # vacuum suck
    m_ = int(dur * SR); t = np.linspace(0, 1, m_); y = lp(rng.standard_normal(m_), 6000 - 4500 * t); y = y - lp(y, 500.0)
    y *= np.sin(np.pi * t ** 0.6) * (1 - t) ** 0.5; return st(y / np.abs(y).max())
def coin():
    m_ = int(0.5 * SR); t = np.arange(m_) / SR; y = np.zeros(m_)
    for f0, s0 in [(1976, 0), (2637, 0.07)]:
        tt = np.clip(t - s0, 0, None); y += np.sign(np.sin(2 * np.pi * f0 * tt)) * 0.3 * np.exp(-tt * 12) * (t >= s0)
    y = lp(y, 7000.0); return st(y / np.abs(y).max())

sfx = np.zeros((n, 2))
def place(sig, t_src, db, align=0.0, out=False):
    t_out = t_src if out else s2o(t_src)
    s = int((t_out - align) * SR); g = 10 ** (db / 20); a, b = max(s, 0), min(s + len(sig), n)
    if b > a: sfx[a:b] += sig[a - s:b - s] * g
W1 = whoosh(0.5, 0.6, 400, 4200)
for c in CUTS_OUT: place(whoosh(0.4, 0.6, 500, 3500), c, -30, 0.24, out=True)       # air on jump cuts
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True)                          # whip zoom in
place(impact(), 0.35, -13)                                                            # MEIN NEUER PARTNER
place(tick(2500), 2.9, -25); place(scratch(), 3.35, -21)                              # GTBuy struck out
place(riser(0.9), 4.66, -25, 0.9); place(impact(1.0, 55), 4.66, -15); place(chime(), 4.72, -25)   # USFans
place(whoosh(0.45, 0.5, 500, 5000), 6.0, -22, 0.2)                                    # phone in
place(tick(2700), 6.55, -26); place(tick(3000), 6.98, -22)                            # bio link highlight / tap
place(whoosh(0.35, 0.55, 800, 6000), 7.22, -27, 0.19)                                 # -> beacons
place(tick(3000), 7.9, -22)                                                           # tap USFans button
place(whoosh(0.35, 0.55, 800, 6000), 8.2, -27, 0.19)                                  # -> app
place(pop(620), 8.76, -18); place(pop(780), 9.66, -18)                                # coupons
place(tick(3000), 11.6, -22); place(chime(), 11.7, -27)                               # get started
place(whoosh(0.4, 0.5, 600, 5000), 12.45, -25, 0.2)                                  # phone out
place(whoosh(0.5, 0.7), 13.78, -24, 0.35); place(impact(), 13.8, -16)                 # WAS IST USFANS
place(tick(2600), 15.98, -25)                                                         # all in one
for t_ in (17.04, 21.54, 33.64, 40.6, 52.3): place(pop(440), t_, -22)                 # section chips
place(whoosh(0.35, 0.55, 800, 6000), 17.4, -27, 0.19); place(tick(2400), 18.8, -26); place(tick(2700), 20.38, -26)
place(whoosh(0.6, 0.5, 300, 4500), 20.55, -23, 0.3)                                   # plane
place(whoosh(0.35, 0.55, 800, 6000), 23.54, -26, 0.19)                                # QC card
place(stamp(), 25.3, -17)                                                             # QC stamp
place(tick(2500), 31.42, -24); place(tick(2900), 32.8, -24); place(chime(), 32.95, -27)
place(whoosh(0.5, 0.7), 34.4, -24, 0.35); place(impact(1.0, 50), 34.42, -17)         # TRACKING headline
for t_ in (35.9, 36.5, 37.1, 39.7): place(tick(2300 + int(t_ * 10) % 700), t_, -25)  # tracker steps
place(whoosh(0.5, 0.7), 41.6, -24, 0.35); place(impact(1.0, 50), 41.62, -17)          # PACKING headline
place(scratch(), 44.15, -21)                                                          # boxes crossed
place(hiss(), 46.55, -20)                                                             # vacuum
place(coin(), 50.7, -22); place(coin(), 51.5, -24)                                    # money
place(whoosh(0.35, 0.55, 800, 6000), 53.5, -26, 0.19)
for t_ in np.arange(53.9, 58.0, 0.55): place(tick(2600, 0.05), float(t_), -30)       # language carousel
place(tick(2400), 59.7, -25); place(tick(2600), 61.5, -25)                            # language / currency
place(whoosh(0.5, 0.7), 63.58, -23, 0.35); place(impact(), 63.6, -14)                 # LINK IN BIO
place(pop(620), 65.34, -17); place(pop(780), 66.26, -17)
place(impact(1.4, 40), DUR_MAIN, -15, out=True); place(chime(), DUR_MAIN + 0.05, -24, out=True)
save("sfx.wav", sfx)

# lo-fi groove, 92 BPM
bpm = 92; beat = 60 / bpm; t = np.arange(n) / SR; mus = np.zeros((n, 2))
def add(sig, at, g=1.0, pan=0.5):
    s = int(at * SR); e = min(n, s + len(sig))
    if s < n: mus[s:e] += st(sig[:e - s], pan) * g
def kick():
    m_ = int(0.35 * SR); tt = np.arange(m_) / SR; f = 50 + 90 * np.exp(-tt * 30); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    m_ = int(0.06 * SR); tt = np.arange(m_) / SR; x = rng.standard_normal(m_); x = x - lp(x, 6000.0); return x * np.exp(-tt * 70) * 0.5
def snare():
    m_ = int(0.25 * SR); tt = np.arange(m_) / SR; x = lp(rng.standard_normal(m_), 3500.0); x = x - lp(x, 400.0)
    return (x * np.exp(-tt * 18) + 0.4 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 25)) * 0.8
def ep(freqs, dur):
    m_ = int(dur * SR); tt = np.arange(m_) / SR; y = np.zeros(m_)
    for f in freqs: y += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3)) * np.exp(-tt * 1.1)
    y *= np.clip(tt / 0.01, 0, 1) * (1 + 0.1 * np.sin(2 * np.pi * 4.5 * tt)); return y / len(freqs)
prog = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2]]
bass = [65.4, 55.0, 43.65, 49.0]
for b in range(int(DUR / (4 * beat)) + 1):
    t0 = b * 4 * beat; ch = prog[b % 4]; add(ep(ch, 4 * beat + 0.6), t0, 0.55, 0.45)
    bm = int(4 * beat * SR); tt = np.arange(bm) / SR
    add(np.sin(2 * np.pi * bass[b % 4] * tt) * np.clip(tt / 0.02, 0, 1) * np.exp(-tt * 0.6), t0, 0.5)
    if t0 < 0.3: continue
    for q in range(4):
        tb = t0 + q * beat
        if q in (0, 2): add(kick(), tb, 0.8)
        if q in (1, 3): add(snare(), tb + 0.01, 0.35, 0.55)
        add(hat(), tb + beat / 2 + 0.02 * (q % 2), 0.35, 0.65); add(hat(), tb, 0.22, 0.62)
for c in range(2): mus[:, c] = lp(mus[:, c], 5200.0)
mus += lp(rng.standard_normal(n), 3000.0)[:, None] * 0.004
mus /= np.abs(mus).max(); mus *= (np.clip(t / 0.6, 0, 1) * np.clip((DUR - t) / 1.2, 0, 1))[:, None]
save("music.wav", mus * 0.9); print("audio ok", round(DUR, 2))
