# python3 tools/foley.py      (after `node tools/snap.mjs info`)
# The story's own sound effects that the kit's audio.py does not know (it skips them as "unknown sfx"):
# running feet, a distant explosion and air-raid siren, the door latch, the warm hum of the carriage, panting, wind,
# the coupling chain, paper, the conductor's whistle, far door slams, a coupling clank, a gasp; plus a fog/wind ambience.
# Writes audio/foley.wav (48 kHz mono) at the same level scale audio.py uses for voices (one line ~ RMS 0.12).
import json, wave, os
import numpy as np
SR = 48000; TL = json.load(open('timeline.json')); DUR = TL['duration'] + 0.3; N = int(DUR * SR); rs = np.random.RandomState(31)
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
# ---- ambience: cold wind in the fog for the whole scene
t = np.arange(N) / SR
amb = filt(rs.randn(N).astype(np.float32), 90, 650, 2.0) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t) * np.sin(2 * np.pi * 0.037 * t + 1))
put(amb * 0.018, 0)

events = TL['events']; slam_t = next((e[1] for e in events if e[0] == 'slam'), TL['duration'])
B = {'step': lambda t0, g: put(verb(step(4.0), 0.5, 0.3), t0, 0.55 * g), 'stepw': lambda t0, g: put(verb(filt(step(4.0), None, 1800), 0.6, 0.35), t0, 0.45 * g), 'siren': lambda t0, g: siren(t0), 'explosion': lambda t0, g: explosion(t0), 'latch': lambda t0, g: latch(t0),
     'warm': lambda t0, g: warm(t0, slam_t + 0.02), 'pant': lambda t0, g: pant(t0, 2.5, 0.62, [(0, 1.0), (0.21, 1.12), (0.4, 1.25)], 0.9 * g),
     'pant_soft': lambda t0, g: pant(t0, 1.4, 0.9, [(0.1, 1.25)], 0.7 * g), 'pant_fast': lambda t0, g: pant(t0, 29.62 - t0, 0.46, [(0, 1.05)], 1.1 * g),
     'wind': lambda t0, g: wind(t0), 'chain': lambda t0, g: chain(t0), 'paper': lambda t0, g: paper(t0), 'whistle': lambda t0, g: whistle(t0),
     'slam_far': lambda t0, g: slam_far(t0, g), 'clank': lambda t0, g: clank(t0), 'gasp': lambda t0, g: gasp(t0), 'train': lambda t0, g: train(t0, next((e[1] for e in events if e[0] in ('trainstop', 'lightsout') and e[1] > t0), TL['duration'])), 'knips': lambda t0, g: knips(t0, g), 'rattle': lambda t0, g: rattle(t0), 'chime': lambda t0, g: chime(t0), 'stumble': lambda t0, g: stumble(t0), 'lightsout': lambda t0, g: lightsout(t0), 'heart': lambda t0, g: heart(t0, g)}
used = []
for e in events:
    name, at = e[0], e[1]; g = e[2] if len(e) > 2 else 1.0
    if name in B: B[name](at, g); used.append(name)
a = out[:N]
w = wave.open('audio/foley.wav', 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('audio/foley.wav', round(DUR, 1), 's  cues:', ' '.join(used))
