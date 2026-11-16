# python3 tools/mix2.py      (replaces mix.py: voices in front, a quiet dark bed instead of the pulsing drone)
#   timeline.json + audio/lines/L###.wav -> audio/mix.wav (48 kHz stereo, -14 LUFS)
# 1. voices: each line with its speaker effect (door, far, phone, radio, whisper), a presence lift and gentle compression
# 2. effects: foley.py renders the story's own cues and the kit's cues (camera whooshes much quieter than before)
# 3. bed: a dark, slow ambience (sub rumble, a dissonant breathing pad, a thin glassy whine, distant groans), no pulse
# 4. everything that is not a voice ducks about 10 dB while someone speaks; 'silence' events cut the whole mix
import json, os, shutil, subprocess, sys, wave
import numpy as np
SR = 48000; HERE = os.path.dirname(os.path.abspath(__file__)); rs = np.random.RandomState(5)
TL = json.load(open('timeline.json')); DUR = TL['duration'] + 0.3; N = int(DUR * SR)
def rd(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    return a
def filt(a, lo=None, hi=None, slope=3.0):
    n = len(a); A = np.fft.rfft(a); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo: m *= 1 - 1 / (1 + (f / lo) ** (2 * slope))
    return np.fft.irfft(A * m, n).astype(np.float32)
def peak_eq(a, fc, gain_db, q=1.0):   # broad bell boost in the frequency domain
    n = len(a); A = np.fft.rfft(a); f = np.fft.rfftfreq(n, 1 / SR); g = 10 ** (gain_db / 20)
    m = 1 + (g - 1) * np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) * 2 * q) ** 2); return np.fft.irfft(A * m, n).astype(np.float32)
def verb(a, t=0.35, mix=0.3, lo=200, hi=3500):
    n = int(SR * t); ir = rs.randn(n).astype(np.float32) * np.exp(-np.linspace(0, 6, n)); ir = filt(ir, lo, hi); ir /= np.sqrt((ir ** 2).sum())
    L = len(a) + n; wet = np.fft.irfft(np.fft.rfft(a, L) * np.fft.rfft(ir, L), L).astype(np.float32); out = np.zeros(L, np.float32); out[:len(a)] = a * (1 - mix * 0.4); return out + wet * mix
def comp(a, thr=0.18, ratio=3.0):     # simple peak compressor with a smoothed envelope
    e = np.sqrt(np.convolve(a * a, np.ones(480) / 480, 'same')) + 1e-6; g = np.where(e > thr, (thr + (e - thr) / ratio) / e, 1.0); return (a * g).astype(np.float32)
def put(buf, a, t, g=1.0):
    i = int(max(0, t) * SR); a = a[:max(0, N - i)]; buf[i:i + len(a)] += a.astype(np.float32) * g

# ---- 1. voices
voice = np.zeros(N, np.float32)
for l in TL['lines']:
    p = f"audio/lines/L{l['n']:03d}.wav"
    if not os.path.exists(p): print('missing', p); continue
    a = rd(p); fx = l.get('fx'); g = 1.0
    if fx == 'door': a = verb(filt(a, 160, 2300, 2.0), 0.3, 0.3); g = 1.15
    elif fx == 'far': a = verb(filt(a, 220, 2000, 2.0), 0.7, 0.45); g = 1.05
    elif fx == 'phone': a = filt(a, 450, 3400, 3.0); g = 1.0
    elif fx == 'radio': a = np.tanh(filt(a, 500, 3000, 3.0) * 3) * 0.5 + filt(rs.randn(len(a)).astype(np.float32), 2000, 6000) * 0.008
    elif fx == 'whisper': a = filt(a, 300, None) * 0.9
    else: a = filt(a, 80, None)
    a = peak_eq(a, 2800, 4.0, 0.8); a = comp(a)
    a *= 0.13 / (np.sqrt((a[np.abs(a) > 0.01] ** 2).mean()) + 1e-6)   # every line equally loud while it sounds
    put(voice, a, l['t0'], g)
# ---- 2. effects (story cues + kit cues; camera whooshes only where the shot changes, never at a hard cut)
B = TL['beats']; drop = set()
for i in range(1, len(B)):
    a, b = B[i - 1], B[i]
    if a['look'] == b['look'] and abs(a['zoom'] - b['zoom']) / max(1, a['zoom']) < 0.12: drop.add(round(b['cam'], 3))
CUTS = [e[1] for e in TL['events'] if e[0] == 'cut']; SILENCE = [e[1] for e in TL['events'] if e[0] == 'silence']
ev = [e for e in TL['events'] if not (e[0] in ('whoosh', 'zoom') and (round(e[1], 3) in drop or any(abs(e[1] - c) < 0.08 for c in CUTS))) and e[0] not in ('cut', 'riser')]
ev += [['punch', c, 1.1] for c in CUTS]
tl2 = dict(TL); tl2['events'] = sorted(ev, key=lambda e: e[1]); json.dump(tl2, open('audio/_tl.json', 'w'))
subprocess.run([sys.executable, os.path.join(HERE, 'foley.py')], check=True, env={**os.environ, 'TIMELINE': 'audio/_tl.json', 'FOLEY_OUT': 'audio/fx.wav', 'WITH_KIT': '1'}, stdout=subprocess.DEVNULL)
fx = rd('audio/fx.wav')[:N]; fx = np.pad(fx, (0, N - len(fx))); os.remove('audio/_tl.json')
# ---- 3. the dark bed
t = np.arange(N) / SR; T = DUR
rise = 0.55 + 0.45 * np.clip(t / max(1, T - 3), 0, 1) ** 1.5                     # the dread climbs toward the end
sub = (np.sin(2 * np.pi * 36 * t) + 0.7 * np.sin(2 * np.pi * 36.35 * t) + 0.4 * np.sin(2 * np.pi * 54.2 * t)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
pad = np.zeros(N, np.float32)
for f, ph in ((110.0, 0.0), (116.5, 1.3), (155.6, 2.1), (164.8, 0.7)):         # A, B-flat, E-flat, E: minor seconds and a tritone
    pad += (np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.11 * t + ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.045 + ph * 0.01) * t + ph)) ** 2).astype(np.float32)
pad = filt(pad, 60, 900, 2.0)
glass = (np.sin(2 * np.pi * 1760 * t) + np.sin(2 * np.pi * 1866 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t - 1.2)) ** 4
air = filt(rs.randn(N).astype(np.float32), 300, 2500, 2.0) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.033 * t))
groans = np.zeros(N, np.float32); k = 4.5
while k < T - 2:                                                                   # a distant metallic groan now and then
    d = 2.6; tt_ = np.arange(int(d * SR)) / SR; f = 70 + 25 * np.sin(np.pi * tt_ / d); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt_ / d) ** 2
    x = filt(x.astype(np.float32) + filt(rs.randn(len(tt_)).astype(np.float32), 200, 700) * 0.05, None, 900); put(groans, verb(x, 1.6, 0.6, 60, 1200), k, 1.0); k += 7.5 + 3 * rs.rand()
bed = (sub * 0.035 + pad * 0.010 + glass * 0.0016 + air * 0.0035 + groans * 0.03) * rise
# ---- 4. ducking and the final mix
ve = np.sqrt(np.convolve(voice ** 2, np.ones(1440) / 1440, 'same')); dk = np.clip(ve / 0.04, 0, 1)
rel = np.zeros(N, np.float32); r = 0.0; a_ = np.exp(-1 / (0.04 * SR)); b_ = np.exp(-1 / (0.35 * SR))
for i in range(0, N, 48):                                                          # fast attack, slow release, at 1 ms steps
    x = dk[i]; r = (a_ ** 48) * r + (1 - a_ ** 48) * x if x > r else (b_ ** 48) * r + (1 - b_ ** 48) * x; rel[i:i + 48] = r
duck = 1 - 0.68 * rel
full = voice + (fx * 0.8 + bed) * duck
if os.environ.get('STEMS'):
    for name, x in (('voice', voice), ('bg', (fx * 0.8 + bed) * duck)):
        m_ = np.zeros(N, bool)
        for l in TL['lines']: m_[int(l['t0'] * SR):int((l['t0'] + l['dur']) * SR)] = True
        print(name, 'in lines', round(20 * np.log10(np.sqrt((x[m_] ** 2).mean()) + 1e-9), 1), 'dB, speech band', round(20 * np.log10(np.sqrt((filt(x, 300, 3400)[m_] ** 2).mean()) + 1e-9), 1), 'dB')
for s in SILENCE: i = int(s * SR); f = int(0.25 * SR); full[i:i + f] *= np.linspace(1, 0, len(full[i:i + f])); full[i + f:] = 0
k = int(0.3 * SR); full[-k:] *= np.linspace(1, 0, k)
full = np.tanh(full * 1.2) / 1.2
st = np.stack([full, full], 1); w = wave.open('audio/_mix.wav', 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/_mix.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false', '-ar', str(SR), 'audio/mix.wav'], check=True); os.remove('audio/_mix.wav')
m = np.zeros(N, bool)
for l in TL['lines']: m[int(l['t0'] * SR):int((l['t0'] + l['dur']) * SR)] = True
spk = filt(full, 300, 3400); db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f'audio/mix.wav {DUR:.1f}s  speech band: lines {db(spk[m]):.1f} dB vs rest {db(spk[~m]):.1f} dB')
