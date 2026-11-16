# python3 tools/mix2.py      (run in an episode folder; tools/ep.sh <ep> mix does that)
#   timeline.json + audio/lines/L###.wav + ../nixly/music.mp3 -> audio/mix.wav (48 kHz stereo, -14 LUFS)
# 1. voices: each line with its speaker effect (door, far, phone, radio, whisper) kept light so every word stays clear,
#    a presence lift and gentle compression, all lines equally loud
# 2. effects: foley.py renders the story's own cues (steps, doors, train, heart ...). No camera whooshes, zooms or cut
#    punches at all: shot changes are silent.
# 3. music: the Nixly horror track, tape-slowed (Zug a semitone down, Stadt almost two) so it drags darker, placed so
#    its build peaks right before the black at 29.6 s; under it a sub rumble, a thin glassy whine and distant groans
# 4. while someone speaks the music's mids/highs drop about 15 dB (the low end only 4 dB) and the effects about 7 dB;
#    'silence' events cut the whole mix
import json, os, subprocess, sys, wave
import numpy as np
SR = 48000; HERE = os.path.dirname(os.path.abspath(__file__)); rs = np.random.RandomState(5)
TL = json.load(open('timeline.json')); DUR = TL['duration'] + 0.3; N = int(DUR * SR); EP = os.path.basename(os.getcwd())
MUSIC = os.environ.get('MUSIC', os.path.join(HERE, '..', 'nixly', 'music.mp3'))
def rd(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    return a
def filt(a, lo=None, hi=None, slope=3.0):
    n = len(a); A = np.fft.rfft(a, axis=0); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo: m *= 1 - 1 / (1 + (f / lo) ** (2 * slope))
    if A.ndim == 2: m = m[:, None]
    return np.fft.irfft(A * m, n, axis=0).astype(np.float32)
def peak_eq(a, fc, gain_db, q=1.0):   # broad bell boost/cut in the frequency domain
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
    if fx == 'door': a = verb(filt(a, 150, 4500, 2.0), 0.28, 0.22); g = 1.1          # behind a door: a little boxy, still clear
    elif fx == 'far': a = verb(filt(a, 200, 4200, 2.0), 0.6, 0.3); g = 1.05
    elif fx == 'phone': a = filt(a, 350, 4200, 3.0)
    elif fx == 'radio': a = np.tanh(filt(a, 380, 4300, 3.0) * 1.6) / 1.6 + filt(rs.randn(len(a)).astype(np.float32), 2000, 6000) * 0.004
    elif fx == 'whisper': a = filt(a, 250, None)
    else: a = filt(a, 80, None)
    a = peak_eq(a, 300, -2.0, 1.0); a = peak_eq(a, 3000, 3.5, 0.8); a = comp(a)
    a *= 0.13 / (np.sqrt((a[np.abs(a) > 0.01] ** 2).mean()) + 1e-6)   # every line equally loud while it sounds
    put(voice, a, l['t0'], g)
# ---- 2. story effects only: every camera whoosh, zoom, punch and riser is gone
ev = [e for e in TL['events'] if e[0] not in ('whoosh', 'whoosh_long', 'zoom', 'punch', 'riser')]   # punch = the camera's punch-in
tl2 = dict(TL); tl2['events'] = sorted(ev, key=lambda e: e[1]); json.dump(tl2, open('audio/_tl.json', 'w'))
subprocess.run([sys.executable, os.path.join(HERE, 'foley.py')], check=True, env={**os.environ, 'TIMELINE': 'audio/_tl.json', 'FOLEY_OUT': 'audio/fx.wav', 'WITH_KIT': '1'}, stdout=subprocess.DEVNULL)
fx = rd('audio/fx.wav')[:N]; fx = np.pad(fx, (0, N - len(fx))); os.remove('audio/_tl.json')
SILENCE = [e[1] for e in TL['events'] if e[0] == 'silence']
# ---- 3. the music, slowed like a dying tape, and a quiet layer of dread under it
R = 0.94 if EP.startswith('zug') else 0.90; PEAK_AT = 30.6                       # music second that lands on 29.6 s
off = PEAK_AT / R - 29.6
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', MUSIC, '-af', f'asetrate={int(44100 * R)},aresample={SR},atrim=start={off:.3f}', '-ac', '2', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
mus = np.frombuffer(raw, np.float32).reshape(-1, 2)[:N].copy(); mus = np.pad(mus, ((0, N - len(mus)), (0, 0)))
fi = int(1.2 * SR); mus[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2
mus *= 0.05 / (np.sqrt((mus[:int(29.6 * SR)] ** 2).mean()) + 1e-6)              # average level ~ -26 dBFS, its own build kept
t = np.arange(N) / SR; T = DUR
rise = 0.75 + 0.25 * np.clip(t / max(1, T - 3), 0, 1) ** 1.5
sub = (np.sin(2 * np.pi * 36 * t) + 0.7 * np.sin(2 * np.pi * 36.35 * t) + 0.4 * np.sin(2 * np.pi * 54.2 * t)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.07 * t))
glass = (np.sin(2 * np.pi * 1760 * t) + np.sin(2 * np.pi * 1866 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t - 1.2)) ** 4
groans = np.zeros(N, np.float32); k = 4.5
while k < T - 2:                                                                   # a distant metallic groan now and then
    d = 2.6; tt_ = np.arange(int(d * SR)) / SR; f = 70 + 25 * np.sin(np.pi * tt_ / d); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt_ / d) ** 2
    x = filt(x.astype(np.float32) + filt(rs.randn(len(tt_)).astype(np.float32), 200, 700) * 0.05, None, 900); put(groans, verb(x, 1.6, 0.6, 60, 1200), k, 1.0); k += 7.5 + 3 * rs.rand()
dread = ((sub * 0.03 + glass * 0.0012 + groans * 0.025) * rise).astype(np.float32)
mus_lo = filt(mus, None, 250, 2.0); mus_hi = mus - mus_lo
# ---- 4. ducking and the final mix
ve = np.sqrt(np.convolve(voice ** 2, np.ones(1440) / 1440, 'same')); dk = np.clip(ve / 0.04, 0, 1)
rel = np.zeros(N, np.float32); r = 0.0; a_ = np.exp(-1 / (0.04 * SR)); b_ = np.exp(-1 / (0.4 * SR))
for i in range(0, N, 48):                                                          # fast attack, slow release, at 1 ms steps
    x = dk[i]; r = (a_ ** 48) * r + (1 - a_ ** 48) * x if x > r else (b_ ** 48) * r + (1 - b_ ** 48) * x; rel[i:i + 48] = r
bg_mono = fx * 0.8 * (1 - 0.55 * rel) + dread * (1 - 0.5 * rel)
music = mus_hi * (1 - 0.82 * rel)[:, None] + mus_lo * (1 - 0.37 * rel)[:, None]
full = (voice + bg_mono)[:, None] + music
if os.environ.get('STEMS'):
    m_ = np.zeros(N, bool)
    for l in TL['lines']: m_[int(l['t0'] * SR):int((l['t0'] + l['dur']) * SR)] = True
    for name, x in (('voice', voice), ('bg', bg_mono + music.mean(1)), ('music', music.mean(1))):
        print(name, 'in lines', round(20 * np.log10(np.sqrt((x[m_] ** 2).mean()) + 1e-9), 1), 'dB, speech band', round(20 * np.log10(np.sqrt((filt(x, 300, 3400)[m_] ** 2).mean()) + 1e-9), 1), 'dB',
              '| outside lines', round(20 * np.log10(np.sqrt((x[~m_] ** 2).mean()) + 1e-9), 1), 'dB')
for s in SILENCE: i = int(s * SR); f = int(0.25 * SR); full[i:i + f] *= np.linspace(1, 0, len(full[i:i + f]))[:, None]; full[i + f:] = 0
k = int(0.3 * SR); full[-k:] *= np.linspace(1, 0, k)[:, None]
full = np.tanh(full * 1.2) / 1.2
w = wave.open('audio/_mix.wav', 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/_mix.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false', '-ar', str(SR), 'audio/mix.wav'], check=True); os.remove('audio/_mix.wav')
m = np.zeros(N, bool)
for l in TL['lines']: m[int(l['t0'] * SR):int((l['t0'] + l['dur']) * SR)] = True
spk = filt(full.mean(1), 300, 3400); db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f'{EP}: audio/mix.wav {DUR:.1f}s  speech band: lines {db(spk[m]):.1f} dB vs rest {db(spk[~m]):.1f} dB')
