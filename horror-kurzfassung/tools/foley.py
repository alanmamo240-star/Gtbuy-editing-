# python3 tools/foley.py      (after `node tools/snap.mjs info`)
# The story's own sound effects that the kit's audio.py does not know (it skips them as "unknown sfx"):
# running feet, a distant explosion and air-raid siren, the door latch, the warm hum of the carriage, panting, wind,
# the coupling chain, paper, the conductor's whistle, far door slams, a coupling clank, a gasp; plus a fog/wind ambience.
# Writes audio/foley.wav (48 kHz mono) at the same level scale audio.py uses for voices (one line ~ RMS 0.12).
import json, wave, os
import numpy as np
SR = 48000; TL = json.load(open(os.environ.get('TIMELINE', 'timeline.json'))); DUR = TL['duration'] + 0.3; N = int(DUR * SR); rs = np.random.RandomState(31)
tt = lambda d: np.arange(int(d * SR)) / SR
def noise(d): return rs.randn(int(d * SR)).astype(np.float32)
def filt(a, lo=None, hi=None, slope=3.0):
    n = len(a); A = np.fft.rfft(a); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo: m *= 1 - 1 / (1 + (f / lo) ** (2 * slope))
    return np.fft.irfft(A * m, n).astype(np.float32)
def env(n, a=0.005, r=0.3): return (np.minimum(1, np.arange(n) / (a * SR + 1)) * np.exp(-np.arange(n) / (r * SR))).astype(np.float32)
def verb(a, t=0.9, mix=0.35, lo=150, hi=3000):
    n = int(SR * t); ir = rs.randn(n).astype(np.float32) * np.exp(-np.linspace(0, 6, n)); ir = filt(ir, lo, hi); ir /= np.sqrt((ir ** 2).sum())
    L = len(a) + n; wet = np.fft.irfft(np.fft.rfft(a, L) * np.fft.rfft(ir, L), L).astype(np.float32); out = np.zeros(L, np.float32); out[:len(a)] = a * (1 - mix * 0.4); return out + wet * mix
out = np.zeros(N + SR * 4, np.float32)
def put(a, t, g=1.0):
    i = int(max(0, t) * SR); a = a[:max(0, len(out) - i)]; out[i:i + len(a)] += a * g

# ---- cue builders
def step(dist):          # one footfall on stone, quieter and duller with distance
    n = int(0.12 * SR); thud = filt(noise(0.12), 50, 520) * env(n, 0.001, 0.028) * 1.4; grit = filt(noise(0.12), 1200, 5200) * env(n, 0.0005, 0.012) * 0.5
    a = thud + grit
    if dist > 6: a = filt(a, None, max(900, 5000 - dist * 220))
    return a
def breath(d, lo, hi, g, shape=1.0):
    n = int(d * SR); x = filt(noise(d), lo, hi, 2.0); e = np.sin(np.pi * np.arange(n) / n) ** shape; return x * e * g
def pant(t0, dur, period, voices, gain):   # in-out breathing of one or more people
    for v, (off, pitch) in enumerate(voices):
        t = t0 + off; k = 0
        while t < t0 + dur:
            fade = 1 - max(0, (t - t0) / dur) ** 2
            put(breath(period * 0.38, 900 * pitch, 3400 * pitch, 0.06, 1.3), t, gain * fade)                       # in
            put(breath(period * 0.52, 420 * pitch, 1900 * pitch, 0.075, 0.8), t + period * 0.42, gain * fade)        # out
            t += period * (0.94 + 0.12 * rs.rand()); k += 1
def siren(t0, d=9.0):      # distant air-raid siren: one slow wail
    t = tt(d); f = 330 + 190 * np.sin(np.pi * np.clip(t / (d * 0.85), 0, 1)) ** 1.5; ph = 2 * np.pi * np.cumsum(f) / SR
    a = (np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)) * np.minimum(1, t / 1.2) * np.clip((d - t) / 2.5, 0, 1)
    a = filt(a.astype(np.float32), 200, 1300, 2.0); put(verb(a, 1.8, 0.6, 150, 1500), t0, 0.022)
def explosion(t0):
    d = 4.0; t = tt(d); n = len(t)
    sub = np.sin(2 * np.pi * (52 * t - 9 * t * t / 2)) * env(n, 0.004, 0.9) * 0.9
    rumble = filt(noise(d), 25, 260, 2.0) * env(n, 0.02, 1.2) * (1 + 0.5 * np.sin(2 * np.pi * 3.1 * t)) * 0.9
    crack = filt(noise(d), 300, 2400, 2.0) * env(n, 0.002, 0.08) * 0.35
    debris = filt(noise(d) * (rs.rand(n) > 0.9985), 800, 4000) * np.clip(1 - t / 2.5, 0, 1) * 0.6
    a = (sub + rumble + crack + debris).astype(np.float32); put(verb(a, 2.5, 0.5, 40, 900), t0, 0.55)
def latch(t0):
    n = int(0.25 * SR); click = filt(noise(0.25), 1800, 7000) * env(n, 0.0003, 0.006) * 0.7; ping = np.sin(2 * np.pi * 920 * tt(0.25)) * env(n, 0.001, 0.05) * 0.18
    clunk = filt(noise(0.25), 90, 600) * env(n, 0.001, 0.03) * 0.8
    a = np.zeros(int(0.5 * SR), np.float32); a[:n] += click + ping; a[int(0.12 * SR):int(0.12 * SR) + n] += clunk + click * 0.4; put(verb(a, 0.6, 0.25), t0, 0.9)
def warm(t0, t1):          # the carriage's warm interior: a soft hum and air, until the door slams shut
    d = t1 - t0 + 0.05; t = tt(d); hum = np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 150 * t) * 0.25 + np.sin(2 * np.pi * 50 * t) * 0.6
    air = filt(noise(d), 200, 1400) * 0.5; a = (hum * 0.02 + air * 0.02) * np.minimum(1, t / 0.8)
    a[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR)); put(a.astype(np.float32), t0, 1.0)
def wind(t0, d=3.6):
    t = tt(d); a = filt(noise(d), 180, 1100, 2.0) * (0.5 + 0.5 * np.sin(np.pi * t / d)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.7 * t))
    whistle = filt(noise(d), 640, 760, 6.0) * np.sin(np.pi * t / d) ** 2 * 1.4; put((a * 0.05 + whistle * 0.05).astype(np.float32), t0, 1.0)
def chain(t0):
    for k, dt in enumerate([0.0, 0.31, 0.52, 0.9]):
        n = int(0.3 * SR); f = 2400 + 900 * rs.rand(); a = (np.sin(2 * np.pi * f * tt(0.3)) + 0.6 * np.sin(2 * np.pi * f * 1.47 * tt(0.3))) * env(n, 0.0005, 0.04)
        put(verb(a.astype(np.float32), 0.5, 0.3), t0 + dt, 0.05 * (1 - 0.15 * k))
def paper(t0):
    d = 0.45; n = int(d * SR); a = filt(noise(d), 2000, 9000) * (rs.rand(n) > 0.55) * np.sin(np.pi * np.arange(n) / n) ** 0.6; put(a.astype(np.float32), t0, 0.07)
def whistle(t0):           # conductor's pea whistle: one long shrill blast
    d = 1.05; t = tt(d); n = len(t); f = 2950 + 40 * np.sin(2 * np.pi * 5 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    trill = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 34 * t)) * 0.6 + 0.2 * np.sin(2 * np.pi * 34 * t)
    tone = (np.sin(ph) + 0.25 * np.sin(2 * ph)) * trill
    e = np.minimum(1, t / 0.025) * np.clip((d - t) / 0.12, 0, 1); a = (tone * e + filt(noise(d), 2500, 6000) * e * 0.15).astype(np.float32)
    put(verb(a, 1.6, 0.45, 600, 6000), t0, 0.16)
def slam_far(t0, g=1.0):
    n = int(0.6 * SR); a = (np.sin(2 * np.pi * 78 * tt(0.6)) * env(n, 0.001, 0.08) + filt(noise(0.6), 150, 1800) * env(n, 0.001, 0.035)).astype(np.float32)
    put(verb(filt(a, None, 1500), 1.4, 0.55, 100, 2000), t0, 0.5 * g)
def clank(t0):             # the couplings take up slack: a deep metallic clunk and a long groan
    d = 2.8; t = tt(d); n = len(t)
    clunk = sum(np.sin(2 * np.pi * f * t) * env(n, 0.001, r) for f, r in ((118, 0.5), (177, 0.35), (263, 0.25), (419, 0.15))) * 0.3 + filt(noise(d), 100, 1500) * env(n, 0.001, 0.05) * 0.5
    fg = 60 + 25 * np.sin(np.pi * np.clip((t - 0.4) / 2.2, 0, 1)); groan = np.sin(2 * np.pi * np.cumsum(fg) / SR) * np.sin(np.pi * np.clip((t - 0.4) / 2.3, 0, 1)) ** 2 * 0.35
    groan = filt(groan.astype(np.float32) + filt(noise(d), 300, 900) * 0.04 * np.sin(np.pi * np.clip((t - 0.4) / 2.3, 0, 1)), None, 1200)
    put(verb((clunk + groan).astype(np.float32), 1.5, 0.45, 60, 1800), t0, 0.32)
def heart(t0, g):          # two low thumps: lub-dub
    for o, k in ((0, 1.0), (0.24, 0.7)):
        n = int(0.3 * SR); put((np.sin(2 * np.pi * 52 * tt(0.3)) * env(n, 0.004, 0.07)).astype(np.float32), t0 + o, 0.5 * k * g)
def gasp(t0):
    d = 0.3; n = int(d * SR); a = filt(noise(d), 900, 3600) * np.linspace(0.2, 1, n) ** 1.5 * np.minimum(1, (n - np.arange(n)) / (0.03 * SR)); put(a.astype(np.float32), t0, 0.14)

# ---- more cues (train interior, town)
def train(t0, t1):        # moving train: wheel clatter over the rail joints and a low rumble
    d = max(0.5, t1 - t0); n = int(d * SR); t = np.arange(n) / SR
    rum = filt(rs.randn(n).astype(np.float32), 25, 170, 2.0) * 0.06 * (0.85 + 0.15 * np.sin(2 * np.pi * 0.3 * t))
    a = rum.copy(); k = 0
    while k * 1.05 < d:
        for o, g in ((0, 1.0), (0.14, 0.8)):
            i = int((k * 1.05 + o) * SR); m = int(0.12 * SR)
            if i + m < n: a[i:i + m] += (filt(rs.randn(m).astype(np.float32), 70, 900) * env(m, 0.001, 0.035) * 0.22 * g).astype(np.float32)
        k += 1
    f = int(0.3 * SR); a[-f:] *= np.linspace(1, 0, f); put(a, t0, 1.0)
def knips(t0, g):         # a conductor's punch, somewhere in the dark: click-clack and a small metal ring
    m = int(0.4 * SR); a = np.zeros(m, np.float32)
    for o, q in ((0, 1.0), (0.07, 0.7)):
        i = int(o * SR); c = filt(rs.randn(int(0.05 * SR)).astype(np.float32), 2000, 7000) * env(int(0.05 * SR), 0.0003, 0.004); a[i:i + len(c)] += c * q
    a += (np.sin(2 * np.pi * 1850 * np.arange(m) / SR) * env(m, 0.001, 0.05) * 0.08).astype(np.float32)
    put(verb(a, 1.1, 0.45, 400, 6000), t0, 0.22 * g)
def rattle(t0):
    m = int(0.35 * SR); a = np.zeros(m, np.float32)
    for o in (0, 0.05, 0.11, 0.16, 0.24):
        i = int(o * SR); c = filt(rs.randn(int(0.04 * SR)).astype(np.float32), 900, 5000) * env(int(0.04 * SR), 0.0005, 0.008); a[i:i + len(c)] += c
    a += (filt(rs.randn(m).astype(np.float32), 60, 400) * env(m, 0.002, 0.05) * 0.8).astype(np.float32); put(verb(a, 0.5, 0.25), t0, 0.35)
def chime(t0):            # loudspeaker gong through a small speaker
    d = 1.4; t = tt(d); n = len(t); a = np.zeros(n, np.float32)
    for o, f in ((0, 880), (0.45, 660)):
        i = int(o * SR); m = n - i; x = (np.sin(2 * np.pi * f * t[:m]) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t[:m]) + 0.2 * np.sin(2 * np.pi * f * 3.0 * t[:m])) * env(m, 0.003, 0.5); a[i:] += x.astype(np.float32)
    a = np.tanh(filt(a, 450, 2800, 3.0) * 2.5) * 0.4 + filt(rs.randn(n).astype(np.float32), 2000, 6000) * 0.01; put(a.astype(np.float32), t0, 0.35)
def stumble(t0):
    for o, g in ((0, 0.8), (0.18, 0.9), (0.33, 0.7)): put(verb(step(3.0), 0.4, 0.2), t0 + o, 0.5 * g)
    n = int(0.5 * SR); put((np.sin(2 * np.pi * 95 * tt(0.5)) * env(n, 0.002, 0.07) + filt(rs.randn(n).astype(np.float32), 120, 900) * env(n, 0.001, 0.03)).astype(np.float32), t0 + 0.4, 0.5)
def lightsout(t0):
    n = int(0.8 * SR); a = (np.sin(2 * np.pi * 70 * tt(0.8)) * env(n, 0.001, 0.06) + filt(rs.randn(n).astype(np.float32), 1500, 8000) * env(n, 0.0005, 0.01) * 0.6).astype(np.float32); put(verb(a, 0.9, 0.35), t0, 0.5)
def alarmhum(t0, t1):     # emergency light: a low electric hum with a slow throb
    d = max(0.5, t1 - t0); t = tt(d); a = (np.sin(2 * np.pi * 100 * t) * 0.5 + np.sin(2 * np.pi * 200 * t) * 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 1.6) ** 2) * 0.018
    put(a.astype(np.float32), t0, 1.0)
def lever(t0):
    n = int(0.7 * SR); a = (np.sin(2 * np.pi * 180 * tt(0.7)) * env(n, 0.001, 0.12) * 0.5 + np.sin(2 * np.pi * 267 * tt(0.7)) * env(n, 0.001, 0.08) * 0.3 + filt(rs.randn(n).astype(np.float32), 600, 4000) * env(n, 0.0005, 0.02)).astype(np.float32)
    put(verb(a, 0.8, 0.3), t0, 0.5)
def jolt(t0):             # the whole carriage bangs into the brake
    d = 1.6; n = int(d * SR); a = (np.sin(2 * np.pi * (60 - 25 * tt(d)) * tt(d)) * env(n, 0.002, 0.35) + filt(rs.randn(n).astype(np.float32), 80, 2500) * env(n, 0.001, 0.12) * 0.9).astype(np.float32)
    for o in (0.05, 0.11, 0.2, 0.31): i = int(o * SR); m = int(0.08 * SR); a[i:i + m] += (filt(rs.randn(m).astype(np.float32), 1500, 6000) * env(m, 0.0005, 0.015) * 0.5).astype(np.float32)
    put(verb(a, 1.0, 0.3), t0, 0.8)
def brake(t0):            # metal squeal dying away
    d = 1.8; t = tt(d); f = 2400 - 600 * t / d; a = np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - t / d) ** 1.5 * (0.7 + 0.3 * np.sin(2 * np.pi * 23 * t)); a = filt(a.astype(np.float32), 1200, 5000) * 0.25
    put(verb(a, 1.2, 0.35, 800, 6000), t0, 0.35)
def windout(t0, d=6.0):
    t = tt(d); a = filt(noise(d), 200, 1300, 2.0) * np.minimum(1, t / 0.8) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t)) * np.clip((d - t) / 1.5, 0, 1); put((a * 0.05).astype(np.float32), t0, 1.0)
def spring(t0, g):        # the lever pushing back: a strained metal creak
    d = 1.2; t = tt(d); f = 140 + 40 * np.sin(2 * np.pi * 1.3 * t); a = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 29 * t))) * np.sin(np.pi * t / d) ** 2
    put(filt(a.astype(np.float32), 120, 1800) * 0.1, t0, g)
def land(t0):
    n = int(0.4 * SR); put(verb((np.sin(2 * np.pi * 80 * tt(0.4)) * env(n, 0.002, 0.05) + filt(rs.randn(n).astype(np.float32), 100, 1500) * env(n, 0.001, 0.03)).astype(np.float32), 0.6, 0.3), t0, 0.5)
def birds(t0, g, d=8.0):  # a few early birds far away
    for k in range(int(d * 1.6)):
        o = rs.rand() * d; f0 = 2600 + 1600 * rs.rand(); m = int(0.12 * SR); tt_ = np.arange(m) / SR
        a = np.sin(2 * np.pi * (f0 + 900 * np.sin(2 * np.pi * 18 * tt_)) * tt_) * np.sin(np.pi * tt_ / 0.12) ** 2; put(verb(a.astype(np.float32), 0.8, 0.5, 1500, 8000), t0 + o, 0.012 * g)
def crack(t0):            # wood splitting
    n = int(0.6 * SR); a = np.zeros(n, np.float32)
    for o, q in ((0, 1.0), (0.04, 0.7), (0.09, 0.9), (0.2, 0.5)): i = int(o * SR); m = int(0.06 * SR); a[i:i + m] += (filt(rs.randn(m).astype(np.float32), 400, 5000) * env(m, 0.0005, 0.012) * q).astype(np.float32)
    a += (np.sin(2 * np.pi * 150 * tt(0.6)) * env(n, 0.001, 0.04) * 0.4).astype(np.float32); put(verb(a, 0.6, 0.3), t0, 0.6)
def wood(t0):
    n = int(0.4 * SR); put(verb((np.sin(2 * np.pi * 210 * tt(0.4)) * env(n, 0.001, 0.05) + filt(rs.randn(n).astype(np.float32), 300, 3000) * env(n, 0.0005, 0.02)).astype(np.float32), 0.5, 0.3), t0, 0.5)
def whistle_long(t0):     # a steam whistle from a train with no engine: long, low, two notes
    d = 2.6; t = tt(d); a = np.zeros(len(t), np.float32)
    for f in (311, 370, 466): a += (np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 5 * t)) * 0.33).astype(np.float32)
    e = np.minimum(1, t / 0.15) * np.clip((d - t) / 0.5, 0, 1); a = (a * e + filt(noise(d), 800, 4000) * e * 0.12).astype(np.float32)
    put(verb(filt(a, 200, 3000), 2.2, 0.5, 200, 4000), t0, 0.12)
def alert(t0):            # emergency phone alert: harsh two-tone blasts from three phones at once
    d = 3.2; t = tt(d); a = np.zeros(len(t), np.float32)
    for k in range(4):
        i = int(k * 0.8 * SR); m = int(0.55 * SR); tm = np.arange(m) / SR; f = np.where((tm * 8).astype(int) % 2 == 0, 853, 960)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.003) / SR) * 0.4; x *= np.minimum(1, tm / 0.01) * np.clip((0.55 - tm) / 0.02, 0, 1)
        a[i:i + m] += filt(x.astype(np.float32), 500, 4000) * 0.11
    put(a, t0, 1.0)
def doorbell(t0):
    a = np.zeros(int(2.0 * SR), np.float32)
    for o, f in ((0, 784), (0.55, 622)):
        i = int(o * SR); m = int(1.4 * SR); tm = np.arange(m) / SR; a[i:i + m] += ((np.sin(2 * np.pi * f * tm) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tm)) * env(m, 0.002, 0.6) * 0.3).astype(np.float32)
    put(verb(a, 0.6, 0.25), t0, 0.6)
def handle(t0):           # a door handle pressed down slowly from outside, metal latch scraping
    d = 1.4; t = tt(d); a = filt(noise(d), 1500, 6000) * np.sin(np.pi * t / d) ** 2 * (rs.rand(len(t)) > 0.93) * 0.3
    n = int(0.3 * SR); a[:n] += (filt(rs.randn(n).astype(np.float32), 800, 5000) * env(n, 0.0005, 0.01) * 0.6).astype(np.float32)
    put(verb(a.astype(np.float32), 0.5, 0.3), t0, 0.6)
def chairscrape(t0):
    d = 0.7; t = tt(d); a = filt(noise(d), 300, 1500) * (0.6 + 0.4 * np.sin(2 * np.pi * 31 * t)) * np.sin(np.pi * t / d) ** 2 * 0.12; put(a.astype(np.float32), t0, 1.0)
def roomtone(t0, t1):
    d = max(0.5, t1 - t0); t = tt(d); a = filt(noise(d), 60, 300, 2.0) * 0.012 + np.sin(2 * np.pi * 50 * t) * 0.003; put(a.astype(np.float32), t0, 1.0)
def doorbang(t0):
    n = int(0.6 * SR); put(verb((np.sin(2 * np.pi * 95 * tt(0.6)) * env(n, 0.001, 0.08) + filt(rs.randn(n).astype(np.float32), 200, 3000) * env(n, 0.0005, 0.03) * 0.8).astype(np.float32), 0.7, 0.35), t0, 0.7)
def scrape(t0, d=2.0):    # a heavy metal container dragged over asphalt
    t = tt(d); a = filt(noise(d), 150, 2200, 2.0) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t))) * np.sin(np.pi * t / d) ** 0.5 * 0.16
    a += (np.sin(2 * np.pi * 70 * t) * 0.03 * np.sin(np.pi * t / d)).astype(np.float32); put(a.astype(np.float32), t0, 1.0)
def megaphone(t0):        # a crackle and a short feedback whine before the announcement
    d = 0.5; t = tt(d); a = filt(noise(d), 1500, 5000) * (rs.rand(len(t)) > 0.8) * 0.15 + np.sin(2 * np.pi * 2100 * t) * np.sin(np.pi * t / d) ** 2 * 0.05; put(a.astype(np.float32), t0, 1.0)
def doorshut(t0):
    n = int(1.0 * SR); a = (np.sin(2 * np.pi * 80 * tt(1.0)) * env(n, 0.001, 0.1) + filt(rs.randn(n).astype(np.float32), 100, 2500) * env(n, 0.0005, 0.04)).astype(np.float32); put(verb(a, 1.4, 0.5, 80, 2000), t0, 0.8)
def nightamb(t0, d=None):
    d = (TL['duration'] - t0) if d is None else d; t = tt(d); a = filt(noise(d), 120, 900, 2.0) * 0.012 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.11 * t)); put(a.astype(np.float32), t0, 1.0)
def drips(t0, d=None):    # a damp cellar: slow water drops and a low hum
    d = (TL['duration'] - t0) if d is None else d; k = 0.0
    while k < d:
        m = int(0.25 * SR); f = 1200 + 900 * rs.rand(); x = np.sin(2 * np.pi * (f + 600 * np.exp(-np.arange(m) / SR * 40)) * np.arange(m) / SR) * env(m, 0.001, 0.03); put(verb(x.astype(np.float32), 1.0, 0.5, 500, 5000), t0 + k, 0.035)
        k += 0.9 + 1.6 * rs.rand()
    t = tt(d); put((np.sin(2 * np.pi * 60 * t) * 0.006 + filt(noise(d), 40, 200) * 0.01).astype(np.float32), t0, 1.0)
def click(t0):
    m = int(0.08 * SR); put((filt(rs.randn(m).astype(np.float32), 2000, 8000) * env(m, 0.0003, 0.006)).astype(np.float32), t0, 0.35)
def ventoff(t0):
    n = int(0.9 * SR); a = (np.sin(2 * np.pi * 420 * tt(0.9)) * env(n, 0.001, 0.15) * 0.3 + np.sin(2 * np.pi * 633 * tt(0.9)) * env(n, 0.001, 0.1) * 0.2 + filt(rs.randn(n).astype(np.float32), 500, 5000) * env(n, 0.0005, 0.03)).astype(np.float32); put(verb(a, 0.8, 0.35), t0, 0.5)
def shuffle(t0, d=2.0):
    t = tt(d); a = filt(noise(d), 300, 2500) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 2.2 * t))) * 0.05; put(a.astype(np.float32), t0, 1.0)
def crawl(t0, d=3.6):     # knees and hands on a sheet-metal duct: hollow thumps
    k = 0.0
    while k < d:
        m = int(0.2 * SR); x = (np.sin(2 * np.pi * (140 + 60 * rs.rand()) * np.arange(m) / SR) * env(m, 0.001, 0.05) + filt(rs.randn(m).astype(np.float32), 300, 3000) * env(m, 0.0005, 0.02) * 0.6).astype(np.float32)
        put(verb(x, 0.5, 0.4, 200, 3000), t0 + k, 0.28); k += 0.17 + 0.12 * rs.rand()
def grate(t0):
    n = int(1.0 * SR); a = (np.sin(2 * np.pi * 310 * tt(1.0)) * env(n, 0.001, 0.2) * 0.4 + np.sin(2 * np.pi * 523 * tt(1.0)) * env(n, 0.001, 0.12) * 0.3 + filt(rs.randn(n).astype(np.float32), 400, 4000) * env(n, 0.0005, 0.03)).astype(np.float32); put(verb(a, 0.9, 0.4), t0, 0.6)
def river(t0, d=None):    # a slow river: broadband wash with gentle swells
    d = (TL['duration'] - t0) if d is None else d; t = tt(d); a = filt(noise(d), 200, 2500, 2.0) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.21 * t) * np.sin(2 * np.pi * 0.07 * t + 1)) * 0.035
    put(a.astype(np.float32), t0, 1.0)
def bandnoise(d, f0, f1, q=0.5):
    n = int(d * SR); x = noise(d); out_ = np.zeros(n, np.float32); K = 12
    for k in range(K):
        fc = f0 * (f1 / f0) ** ((k + 0.5) / K); seg = filt(x, fc * (1 - q), fc * (1 + q)); w_ = np.exp(-0.5 * ((np.arange(n) / n - (k + 0.5) / K) / (0.9 / K)) ** 2); out_ += seg * w_
    return out_
def sweep(d, f0, f1): t = tt(d); return np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * d))).astype(np.float32)
KIT = {
    'whoosh': lambda: bandnoise(0.34, 300, 3200) * np.sin(np.pi * np.arange(int(0.34 * SR)) / int(0.34 * SR)) ** 1.5 * 0.5,
    'whoosh_long': lambda: bandnoise(0.6, 180, 2600) * np.sin(np.pi * np.arange(int(0.6 * SR)) / int(0.6 * SR)) ** 1.3 * 0.55,
    'zoom': lambda: bandnoise(0.3, 220, 900) * np.sin(np.pi * np.arange(int(0.3 * SR)) / int(0.3 * SR)) ** 2 * 0.3,
    'punch': lambda: (np.sin(2 * np.pi * 62 * tt(0.4)) * env(int(0.4 * SR), 0.003, 0.11) * 0.8 + filt(noise(0.4), 900, 5000) * env(int(0.4 * SR), 0.001, 0.02) * 0.2),
    'notify': lambda: sum(np.pad(np.sin(2 * np.pi * f * tt(0.5)) * env(int(0.5 * SR), 0.002, 0.12) * 0.32, (int(o * SR), int(0.2 * SR) - int(o * SR))) for f, o in ((1046.5, 0), (1396.9, 0.11))),
    'knock': lambda: (np.sin(2 * np.pi * 150 * tt(0.3)) * env(int(0.3 * SR), 0.001, 0.045) + filt(noise(0.3), 300, 1500) * env(int(0.3 * SR), 0.001, 0.02) * 0.6) * 0.75,
    'sting': lambda: (sweep(1.4, 70, 38) * env(int(1.4 * SR), 0.004, 0.45) * 0.9 + sum(np.sin(2 * np.pi * f * tt(1.4)) for f in (622, 659, 932, 988)) * env(int(1.4 * SR), 0.01, 0.5) * 0.06 + filt(noise(1.4), 2000, 9000) * env(int(1.4 * SR), 0.002, 0.08) * 0.2),
    'steps': lambda: sum(np.pad(filt(noise(0.2), 80, 500) * env(int(0.2 * SR), 0.002, 0.05) * (0.5 - 0.09 * i), (int(i * 0.42 * SR), int(4 * 0.42 * SR) - int(i * 0.42 * SR))) for i in range(5)),
    'boom': lambda: (sweep(2.2, 62, 30) * env(int(2.2 * SR), 0.003, 0.7) * 1.25 + filt(noise(2.2), 60, 700) * env(int(2.2 * SR), 0.002, 0.25) * 0.5),
    'buzz': lambda: np.sign(np.sin(2 * np.pi * 150 * tt(0.45))) * (np.sin(2 * np.pi * 3.2 * tt(0.45)) > -0.3) * 0.07,
    'creak': lambda: np.sin(2 * np.pi * (180 + 60 * np.sin(2 * np.pi * 2.2 * tt(0.9))) * tt(0.9)) * np.sin(np.pi * np.arange(int(0.9 * SR)) / int(0.9 * SR)) ** 2 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 37 * tt(0.9)))) * 0.14,
    'slam': lambda: (np.sin(2 * np.pi * 85 * tt(0.6)) * env(int(0.6 * SR), 0.001, 0.09) + filt(noise(0.6), 200, 3000) * env(int(0.6 * SR), 0.001, 0.04)) * 0.9,
}
KITG = {'whoosh': 0.22, 'whoosh_long': 0.3, 'zoom': 0.15, 'punch': 0.55, 'notify': 0.8, 'boom': 0.95, 'sting': 0.7}
# ---- war city (Flucht aus Aschental): convoy, helicopters, distant impacts, water, a door knocked three times
def convoy(t0, d=19.0):    # tracked and wheeled vehicles rolling past: diesel rumble, track clatter, fading down the street
    t = tt(d); e = np.minimum(1, t / 0.6) * np.clip(1 - (t - 4.0) / (d - 4.0), 0.12, 1) ** 1.6
    eng = sum(np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.7 * t)) * a for f, a in ((31, 1.0), (62, 0.6), (93, 0.35), (47, 0.4)))
    eng = eng * (0.75 + 0.25 * np.sign(np.sin(2 * np.pi * 12.5 * t)))
    clat = np.zeros(len(t), np.float32); k = 0.0
    while k < d - 0.2: n = int(0.06 * SR); i = int(k * SR); clat[i:i + n] += filt(noise(0.06), 500, 4200) * env(n, 0.001, 0.015)[:len(clat[i:i + n])]; k += 0.16 + 0.03 * rs.rand()
    a = (filt(eng.astype(np.float32), 25, 300) * 0.16 + clat * 0.22 + filt(noise(d), 60, 500) * 0.05) * e
    put(verb(a.astype(np.float32), 1.2, 0.3, 40, 2500), t0, 0.6)
def heli(t0, d=10.0, peak=4.3, g=1.0):    # a helicopter passing: blade thumps, turbine whine, louder as it passes over
    t = tt(d); e = np.exp(-((t - peak) / (d * 0.28)) ** 2) * np.minimum(1, t / 0.5)
    rate = 4.7 + 0.25 * np.tanh((t - peak) / 1.5)   # a little doppler
    ph = np.cumsum(rate) / SR; chop = (0.5 + 0.5 * np.cos(2 * np.pi * ph)) ** 6
    a = filt(noise(d), 60, 900) * chop * 0.9 + np.sin(2 * np.pi * 1650 * (1 - 0.03 * np.tanh((t - peak) / 1.5)) * t) * 0.02 + filt(noise(d), 1500, 6000) * 0.04
    put((filt(a.astype(np.float32), 40, None) * e).astype(np.float32), t0, 0.42 * g)
def heli_far(t0, t1, g=1.0):    # helicopters somewhere over the city the whole time
    d = max(0.5, t1 - t0); t = tt(d); ph = np.cumsum(4.4 + 0.1 * np.sin(2 * np.pi * 0.05 * t)) / SR; chop = (0.5 + 0.5 * np.cos(2 * np.pi * ph)) ** 5
    a = filt(noise(d), 80, 600) * chop * (0.6 + 0.4 * np.sin(2 * np.pi * 0.03 * t + 1)) ** 2; f = int(0.5 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    put(verb(a.astype(np.float32), 2.0, 0.5, 60, 900), t0, 0.07 * g)
def boom_far(t0, g=1.0):   # an impact far away: felt more than heard
    d = 2.6; n = int(d * SR); a = np.sin(2 * np.pi * 38 * tt(d) * (1 - 0.2 * tt(d) / d)) * env(n, 0.01, 0.5) + filt(noise(d), 30, 260) * env(n, 0.005, 0.7) * 1.2
    put(verb(filt(a.astype(np.float32), None, 400), 3.0, 0.6, 30, 500), t0, 0.32 * g)
def cityamb(t0, t1, g=1.0):   # a city at war, in the distance: low wind, a far rumble, scattered impacts
    d = max(0.5, t1 - t0); t = tt(d); a = filt(noise(d), 70, 500, 2.0) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t) * np.sin(2 * np.pi * 0.031 * t + 1)) * 0.03
    f = int(0.6 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f); put(a.astype(np.float32), t0, g)
    k = t0 + 3.0 + 3 * rs.rand()
    while k < t1 - 2.5: boom_far(k, 0.5 + 0.5 * rs.rand()); k += 7 + 7 * rs.rand()
def knock3(t0, g=1.0):     # three slow knocks on a wooden door
    for o in (0, 0.42, 0.84): n = int(0.25 * SR); a = np.sin(2 * np.pi * 120 * tt(0.25)) * env(n, 0.001, 0.05) + filt(noise(0.25), 300, 2500) * env(n, 0.0005, 0.012) * 0.8; put(verb(a.astype(np.float32), 0.4, 0.25), t0 + o, 0.6 * g)
def water(t0, t1, g=1.0):  # river lapping against stone and wood
    d = max(0.5, t1 - t0); t = tt(d); a = filt(noise(d), 200, 1400, 2.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.35 * t) * np.sin(2 * np.pi * 0.13 * t + 2)) ** 2 * 0.05
    f = int(0.6 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f); put(a.astype(np.float32), t0, g)
def oars(t0, t1, g=1.0):   # oar strokes: the splash, the creak of the rowlock
    k = t0
    while k < t1: n = int(0.6 * SR); a = filt(noise(0.6), 300, 3000) * env(n, 0.05, 0.18) * 0.6 + np.sin(2 * np.pi * (300 + 80 * tt(0.6)) * tt(0.6)) * env(n, 0.002, 0.04) * 0.08; put(verb(a.astype(np.float32), 0.6, 0.25), k, 0.35 * g); k += 2.6
def crowd(t0, t1, g=1.0):  # people waiting in a line, murmuring, a cough, shuffling
    d = max(0.5, t1 - t0); t = tt(d); a = filt(noise(d), 250, 1100, 2.0) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 0.9 * t + np.sin(2 * np.pi * 0.23 * t) * 3))) * 0.025
    f = int(0.5 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f); put(verb(a.astype(np.float32), 1.0, 0.4), t0, g)
def drip(t0, t1, g=1.0):
    k = t0
    while k < t1: n = int(0.12 * SR); a = np.sin(2 * np.pi * (1400 + 600 * tt(0.12) * 8) * tt(0.12)) * env(n, 0.001, 0.02); put(verb(a.astype(np.float32), 0.8, 0.5), k, 0.08 * g); k += 0.9 + 1.4 * rs.rand()
def endof(name, t0, default):   # the time a looping cue stops: its 'stop_<name>' event, else the end
    return next((e[1] for e in TL['events'] if e[0] == 'stop_' + name and e[1] > t0), default)

# ---- ambience: cold wind in the fog for the whole scene
t = np.arange(N) / SR
amb = filt(rs.randn(N).astype(np.float32), 90, 650, 2.0) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t) * np.sin(2 * np.pi * 0.037 * t + 1))
put(amb * (0.0 if os.environ.get('WITH_KIT') == '1' else 0.018), 0)

events = TL['events']; slam_t = next((e[1] for e in events if e[0] == 'slam'), TL['duration'])
B = {'step': lambda t0, g: put(verb(step(4.0), 0.5, 0.3), t0, 0.55 * g), 'stepw': lambda t0, g: put(verb(filt(step(4.0), None, 1800), 0.6, 0.35), t0, 0.45 * g), 'siren': lambda t0, g: siren(t0), 'explosion': lambda t0, g: explosion(t0), 'latch': lambda t0, g: latch(t0),
     'warm': lambda t0, g: warm(t0, slam_t + 0.02), 'pant': lambda t0, g: pant(t0, 2.5, 0.62, [(0, 1.0), (0.21, 1.12), (0.4, 1.25)], 0.9 * g),
     'pant_soft': lambda t0, g: pant(t0, 1.4, 0.9, [(0.1, 1.25)], 0.7 * g), 'pant_fast': lambda t0, g: pant(t0, (29.62 - t0) if TL['duration'] < 31 else 4.5, 0.46, [(0, 1.05)], 1.1 * g),
     'wind': lambda t0, g: wind(t0), 'chain': lambda t0, g: chain(t0), 'paper': lambda t0, g: paper(t0), 'whistle': lambda t0, g: whistle(t0),
     'slam_far': lambda t0, g: slam_far(t0, g), 'clank': lambda t0, g: clank(t0), 'gasp': lambda t0, g: gasp(t0), 'train': lambda t0, g: train(t0, next((e[1] for e in events if e[0] in ('trainstop', 'lightsout') and e[1] > t0), TL['duration'])), 'knips': lambda t0, g: knips(t0, g), 'rattle': lambda t0, g: rattle(t0), 'chime': lambda t0, g: chime(t0), 'stumble': lambda t0, g: stumble(t0), 'lightsout': lambda t0, g: lightsout(t0), 'alarmhum': lambda t0, g: alarmhum(t0, TL['duration'] - 0.4), 'lever': lambda t0, g: lever(t0), 'jolt': lambda t0, g: jolt(t0), 'brake': lambda t0, g: brake(t0), 'windout': lambda t0, g: windout(t0), 'spring': lambda t0, g: spring(t0, g), 'land': lambda t0, g: land(t0), 'birds': lambda t0, g: birds(t0, g), 'crack': lambda t0, g: crack(t0), 'wood': lambda t0, g: wood(t0), 'whistle_long': lambda t0, g: whistle_long(t0), 'alert': lambda t0, g: alert(t0), 'doorbell': lambda t0, g: doorbell(t0), 'handle': lambda t0, g: handle(t0), 'chairscrape': lambda t0, g: chairscrape(t0), 'doorbang': lambda t0, g: doorbang(t0), 'drips': lambda t0, g: drips(t0, next((e[1] for e in events if e[0] == 'cut' and e[1] > t0), TL['duration']) - t0), 'click': lambda t0, g: click(t0), 'river': lambda t0, g: river(t0), 'ventoff': lambda t0, g: ventoff(t0), 'shuffle': lambda t0, g: shuffle(t0), 'crawl': lambda t0, g: crawl(t0), 'grate': lambda t0, g: grate(t0), 'scrape': lambda t0, g: scrape(t0), 'megaphone': lambda t0, g: megaphone(t0), 'doorshut': lambda t0, g: doorshut(t0), 'nightamb': lambda t0, g: nightamb(t0, next((e[1] for e in events if e[0] == 'doorshut'), TL['duration']) - t0), 'roomtone': lambda t0, g: roomtone(t0, next((e[1] for e in events if e[0] == 'cut' and e[1] > t0), TL['duration'])), 'heart': lambda t0, g: heart(t0, g)}
B.update({'convoy': lambda t0, g: convoy(t0), 'heli': lambda t0, g: heli(t0, g=g), 'heli_far': lambda t0, g: heli_far(t0, endof('heli_far', t0, TL['duration']), g), 'boom_far': lambda t0, g: boom_far(t0, g),
          'cityamb': lambda t0, g: cityamb(t0, endof('cityamb', t0, TL['duration']), g), 'knock3': lambda t0, g: knock3(t0, g), 'water': lambda t0, g: water(t0, endof('water', t0, TL['duration']), g),
          'oars': lambda t0, g: oars(t0, endof('oars', t0, TL['duration']), g), 'crowd': lambda t0, g: crowd(t0, endof('crowd', t0, TL['duration']), g), 'drip': lambda t0, g: drip(t0, endof('drip', t0, TL['duration']), g)})
for k in list(B): B.setdefault('stop_' + k, lambda t0, g: None)
used = []
WITH_KIT = os.environ.get('WITH_KIT') == '1'
for e in events:
    name, at = e[0], e[1]; g = e[2] if len(e) > 2 else 1.0
    if name in B: B[name](at, g); used.append(name)
    elif WITH_KIT and name in KIT: put(KIT[name]().astype(np.float32), at - (0.1 if name.startswith('whoosh') else 0), g * KITG.get(name, 0.8)); used.append(name)
a = out[:N]
w = wave.open(os.environ.get('FOLEY_OUT', 'audio/foley.wav'), 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('audio/foley.wav', round(DUR, 1), 's  cues:', ' '.join(used))
