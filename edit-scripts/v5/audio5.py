"""Builds the cut voice track (with micro-crossfades), a soft synthesized lo-fi groove and all SFX, timed to
the output timeline (tl.py). Writes voice_cut.wav, music.wav, sfx.wav (48 kHz)."""
import numpy as np, wave, subprocess
from tl import SEGS, OUT_START, DUR, DUR_MAIN, CUTS_OUT, s2o
SR = 48000
rng = np.random.default_rng(21)

def save(name, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    with wave.open(name, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- voice: cut + 12 ms crossfades
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", "input_cfr.mov", "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2)
n = int(DUR * SR); voice = np.zeros((n, 2), np.float32); xf = int(0.012 * SR)
for k, (a, b) in enumerate(SEGS):
    seg = src[int(a * SR):int(b * SR)].copy()
    ramp = np.linspace(0, 1, xf)[:, None]; seg[:xf] *= ramp; seg[-xf:] *= ramp[::-1]
    o = int(OUT_START[k] * SR); voice[o:o + len(seg)] += seg[:max(0, min(len(seg), n - o))]
save("voice_cut.wav", voice)

# ---------------------------------------------------------------- helpers
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
    pan = np.clip(t * 1.2 - 0.1, 0, 1)
    return np.stack([y * np.cos(pan * np.pi / 2), y * np.sin(pan * np.pi / 2)], 1) * 1.3
def impact(dur=1.2, f_lo=44):
    m_ = int(dur * SR); t = np.arange(m_) / SR
    f = f_lo + 55 * np.exp(-t * 18); body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.8)
    click = lp(rng.standard_normal(m_), 2600.0) * np.exp(-t * 90) * 0.55
    tail = lp(rng.standard_normal(m_), 900.0) * np.exp(-t * 3.2) * 0.09
    y = body + click + tail; return st(y / np.abs(y).max())
def sub_drop(dur=1.0):
    m_ = int(dur * SR); t = np.arange(m_) / SR; f = 70 * np.exp(-t * 2.2) + 32
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.6) * np.clip(t / 0.01, 0, 1); return st(y / np.abs(y).max())
def tick(f=2900, dur=0.08):
    m_ = int(dur * SR); t = np.arange(m_) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 85) + 0.5 * np.sin(2 * np.pi * f / 2 * t) * np.exp(-t * 60); return st(y / np.abs(y).max())
def riser(dur=1.4):
    m_ = int(dur * SR); t = np.linspace(0, 1, m_)
    y = lp(rng.standard_normal(m_), 300 + 7000 * t ** 2.5); y = y - lp(y, 250.0)
    tone = np.sin(2 * np.pi * np.cumsum(220 + 660 * t ** 2) / SR) * 0.25
    y = (y / np.abs(y).max() + tone) * t ** 2.4; y /= np.abs(y).max()
    return np.stack([y, np.roll(y, 300)], 1)
def scratch(dur=0.22):  # strike-through "ritsch"
    m_ = int(dur * SR); t = np.linspace(0, 1, m_)
    y = lp(rng.standard_normal(m_), 1500 + 5000 * t); y *= np.sin(np.pi * t) ** 0.7; return st(y / np.abs(y).max(), 0.6)
def stamp():
    y = impact(0.5, 70)[:, 0] * 0.8; m_ = len(y); t = np.arange(m_) / SR
    y += lp(rng.standard_normal(m_), 1800.0) * np.exp(-t * 40) * 0.6; return st(y / np.abs(y).max())
def chime():
    m_ = int(0.9 * SR); t = np.arange(m_) / SR; y = np.zeros(m_)
    for f0, s0 in [(1318.5, 0.0), (1975.5, 0.09)]:
        tt = np.clip(t - s0, 0, None); y += (np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 6) + 0.3 * np.sin(4 * np.pi * f0 * tt) * np.exp(-tt * 9)) * (t >= s0)
    return st(y / np.abs(y).max())
def shutter():
    y = tick(5200, 0.03)[:, 0]; y2 = tick(3000, 0.05)[:, 0]
    out = np.zeros(int(0.12 * SR)); out[:len(y)] += y; out[int(0.06 * SR):int(0.06 * SR) + len(y2)] += y2 * 0.8; return st(out)

sfx = np.zeros((n, 2))
def place(sig, t_out, db, align=0.0):
    if t_out is None: return
    s = int((t_out - align) * SR); g = 10 ** (db / 20); a, b = max(s, 0), min(s + len(sig), n)
    if b > a: sfx[a:b] += sig[a - s:b - s] * g
S = s2o
W1 = whoosh(); WP = 0.6 * 0.62
# --- hook
place(whoosh(0.55, 0.4, 600, 6000), 0.0, -20, 0.0)          # whip zoom in
place(impact(), S(1.35), -13)                                # GTBUY lands
place(tick(), S(2.05), -27)                                  # label
place(whoosh(0.4, 0.6, 500, 5000), S(4.2), -25, 0.24)        # HAUL
# --- cut transitions
for c in CUTS_OUT: place(W1, c, -19, WP)
# --- coupons section
place(tick(2600), S(7.92), -26); place(tick(2800), S(8.30), -24)        # link highlight + tap
place(whoosh(0.35, 0.55, 800, 6000), S(9.06), -26, 0.19)                # 2x40 tile
place(whoosh(0.35, 0.55, 800, 6000), S(10.46), -26, 0.19)               # 2x30 tile
place(tick(2400), S(13.3), -27)                                          # link chip
place(scratch(), S(14.9), -22)                                           # strike 3
place(riser(1.0), S(15.36), -24, 1.0)                                    # build into 4
place(impact(), S(15.36), -12)                                           # 4 COUPONS
# --- process
for ts in [17.35, 21.3, 28.7, 36.5, 44.1, 59.76]: place(tick(3100), S(ts), -27)   # tracker advances
place(tick(2800), S(18.6), -25)                                          # tap GTBuy button
place(whoosh(0.4, 0.6), S(22.42), -25, 0.24)                             # AGENT
place(whoosh(0.5, 0.5, 400, 5200), S(24.75), -22, 0.25); place(impact(), S(24.95), -15)  # 3-5 TAGE spin
place(whoosh(0.5, 0.45, 300, 5000), S(27.1), -20, 0.22)                  # card -> fullscreen
place(whoosh(0.45, 0.5, 600, 4500), S(28.45), -23, 0.22)                 # iris back
place(whoosh(0.35, 0.55, 800, 6000), S(29.3), -24, 0.19); place(shutter(), S(30.0), -22); place(shutter(), S(31.0), -25)
place(tick(2500), S(33.1), -26); place(tick(2700), S(35.25), -26)       # chips
place(whoosh(0.35, 0.55, 800, 6000), S(36.65), -27, 0.19)               # packing card
place(whoosh(0.3, 0.6, 700, 5000), S(38.32), -27, 0.18); place(whoosh(0.3, 0.6, 700, 5000), S(38.92), -27, 0.18)
place(tick(2200), S(39.44), -26)
place(sub_drop(), S(42.86), -14); place(impact(1.0, 60), S(42.86), -19)  # HOHE PREISE
place(riser(1.3), S(46.94), -22, 1.3); place(impact(), S(46.94), -12)   # REHEARSAL (key tip)
place(tick(2600), S(48.36), -25)
place(whoosh(0.35, 0.55, 800, 6000), S(50.0), -27, 0.19)                # scale card
place(tick(2300), S(53.15), -27); place(tick(2600), S(56.9), -27)
place(sub_drop(), S(57.84), -16); place(chime(), S(57.9), -27)          # WENIGER
place(whoosh(0.5, 0.45, 300, 6000), S(62.4), -18, 0.22); place(whoosh(0.5, 0.45, 300, 6000), S(63.7), -21, 0.22)  # plane cutaway
place(stamp(), S(64.95), -15); place(chime(), S(65.05), -26)            # ZUGESTELLT
place(whoosh(0.35, 0.55, 800, 6000), S(67.48), -26, 0.19); place(whoosh(0.35, 0.55, 800, 6000), S(68.5), -26, 0.19)
place(impact(0.8, 60), S(70.02), -19); place(chime(), S(70.1), -27)     # DHL favourite
place(whoosh(0.5, 0.5, 400, 5000), S(74.6), -22, 0.25); place(impact(), S(74.8), -15)    # 8-12
for d in range(8): place(tick(2000 + 120 * d, 0.06), S(77.5 + d * 0.2), -31)            # calendar fill
place(chime(), S(79.15), -27)
place(tick(2200), S(81.92), -25); place(tick(2400), S(83.04), -25); place(tick(1800), S(87.46), -23)
place(riser(1.0), S(90.64), -24, 1.0); place(impact(), S(90.64), -12)  # final 8 TAGE
place(impact(1.4, 40), DUR_MAIN, -14); place(whoosh(0.6, 0.3, 300, 3000), DUR_MAIN, -24, 0.18)  # freeze frame
save("sfx.wav", sfx)

# ---------------------------------------------------------------- lo-fi groove, 88 BPM (kick, hat, rhodes-ish chords, bass)
bpm = 88; beat = 60 / bpm; t = np.arange(n) / SR; mus = np.zeros((n, 2))
def add(sig, at, g=1.0, pan=0.5):
    s = int(at * SR); e = min(n, s + len(sig))
    if s < n: mus[s:e] += st(sig[:e - s], pan) * g
def kick():
    m_ = int(0.35 * SR); tt = np.arange(m_) / SR; f = 50 + 90 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    m_ = int(0.06 * SR); tt = np.arange(m_) / SR; x = rng.standard_normal(m_); x = x - lp(x, 6000.0)
    return x * np.exp(-tt * 70) * 0.5
def snare():
    m_ = int(0.25 * SR); tt = np.arange(m_) / SR; x = lp(rng.standard_normal(m_), 3500.0); x = x - lp(x, 400.0)
    return (x * np.exp(-tt * 18) + 0.4 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 25)) * 0.8
def ep(freqs, dur):
    m_ = int(dur * SR); tt = np.arange(m_) / SR; y = np.zeros(m_)
    for f in freqs: y += (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 3)) * np.exp(-tt * 1.1)
    y *= np.clip(tt / 0.01, 0, 1) * (1 + 0.1 * np.sin(2 * np.pi * 4.5 * tt)); return y / len(freqs)
prog = [[220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [130.8, 164.8, 196.0, 246.9], [196.0, 246.9, 293.7, 349.2]]
bass = [55.0, 43.65, 65.4, 49.0]
bars = int(DUR / (4 * beat)) + 1
for b in range(bars):
    t0 = b * 4 * beat; ch = prog[b % 4]
    add(ep(ch, 4 * beat + 0.6), t0, 0.55, 0.45)
    bm = int(4 * beat * SR); tt = np.arange(bm) / SR
    add(np.sin(2 * np.pi * bass[b % 4] * tt) * np.clip(tt / 0.02, 0, 1) * np.exp(-tt * 0.6), t0, 0.5)
    if t0 < 1.4: continue                                         # let the hook breathe
    for q in range(4):
        tb = t0 + q * beat
        if q in (0, 2): add(kick(), tb, 0.8)
        if q in (1, 3): add(snare(), tb + 0.01, 0.35, 0.55)
        add(hat(), tb + beat / 2 + 0.02 * (q % 2), 0.35, 0.65); add(hat(), tb, 0.22, 0.62)
for c in range(2): mus[:, c] = lp(mus[:, c], 5200.0)                         # warm, dusty top end
mus += lp(rng.standard_normal(n), 3000.0)[:, None] * 0.004                    # vinyl air
mus /= np.abs(mus).max()
fade = np.clip(t / 1.0, 0, 1) * np.clip((DUR - t) / 1.6, 0, 1)
mus *= fade[:, None]
save("music.wav", mus * 0.9)
print("audio ok", round(DUR, 2))
