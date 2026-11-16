# python3 tools/audio.py     (after voice.py and a fresh `node tools/snap.mjs info`)
#   timeline.json + audio/lines/L###.wav [+ audio/music.(mp3|wav) from nixly_music]  ->  audio/final_audio.wav  (48 kHz stereo, -14 LUFS)
# Voices get a per-speaker treatment (fx: door = muffled behind a door, far = further away, phone = small speaker, radio, whisper).
# The bed is the measured reference recipe: 55 Hz drone, a soft pulse every 0.53 s, slow siren-like swells; plus cues on every camera whip,
# phone event and the final boom. All synthesised here, so the pipeline works offline.
import json, wave, os, subprocess, sys
import numpy as np
SR = 48000; TL = json.load(open('timeline.json')); DUR = TL['duration'] + 0.3; N = int(DUR * SR); rs = np.random.RandomState(7)
def rd(path):
    w = wave.open(path); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    return a
def filt(a, lo=None, hi=None, slope=3.0):   # zero-phase FFT filter with soft shoulders
    n = len(a); A = np.fft.rfft(a); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if hi: m *= 1 / (1 + (f / hi) ** (2 * slope))
    if lo: m *= 1 - 1 / (1 + (f / lo) ** (2 * slope))
    return np.fft.irfft(A * m, n).astype(np.float32)
def verb(a, t=0.35, mix=0.3):
    n = int(SR * t); ir = rs.randn(n).astype(np.float32) * np.exp(-np.linspace(0, 6, n)); ir = filt(ir, 200, 3500); ir /= np.sqrt((ir ** 2).sum())
    L = len(a) + n; wet = np.fft.irfft(np.fft.rfft(a, L) * np.fft.rfft(ir, L), L)[:len(a) + n].astype(np.float32); out = np.zeros(len(a) + n, np.float32); out[:len(a)] = a * (1 - mix * 0.4); return out + wet * mix
env = lambda n, a=0.005, r=0.3: np.minimum(1, np.arange(n) / (a * SR + 1)) * np.exp(-np.arange(n) / (r * SR))
tt = lambda d: np.arange(int(d * SR)) / SR
def noise(d): return rs.randn(int(d * SR)).astype(np.float32)
def sweep(d, f0, f1): t = tt(d); return np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t * t / (2 * d)))
def bandnoise(d, f0, f1, q=0.5):   # noise through a moving band: the classic whoosh
    n = int(d * SR); x = noise(d); out = np.zeros(n, np.float32); K = 12
    for k in range(K):
        fc = f0 * (f1 / f0) ** ((k + 0.5) / K); seg = filt(x, fc * (1 - q), fc * (1 + q)); w = np.exp(-0.5 * ((np.arange(n) / n - (k + 0.5) / K) / (0.9 / K)) ** 2); out += seg * w
    return out
SFX = {
    'whoosh': lambda: bandnoise(0.34, 300, 3200) * np.sin(np.pi * np.arange(int(0.34 * SR)) / int(0.34 * SR)) ** 1.5 * 0.5,
    'whoosh_long': lambda: bandnoise(0.6, 180, 2600) * np.sin(np.pi * np.arange(int(0.6 * SR)) / int(0.6 * SR)) ** 1.3 * 0.55,
    'zoom': lambda: bandnoise(0.3, 220, 900) * np.sin(np.pi * np.arange(int(0.3 * SR)) / int(0.3 * SR)) ** 2 * 0.3,
    'rustle': lambda: filt(noise(0.4), 500, 5000) * np.sin(np.pi * np.arange(int(0.4 * SR)) / int(0.4 * SR)) ** 2 * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt(0.4))) * 0.16,
    'punch': lambda: (np.sin(2 * np.pi * 62 * tt(0.4)) * env(int(0.4 * SR), 0.003, 0.11) * 0.8 + filt(noise(0.4), 900, 5000) * env(int(0.4 * SR), 0.001, 0.02) * 0.2),
    'notify': lambda: sum(np.pad(np.sin(2 * np.pi * f * tt(0.5)) * env(int(0.5 * SR), 0.002, 0.12) * 0.32, (int(o * SR), int((0.2 - o) * SR))) for f, o in ((1046.5, 0), (1396.9, 0.11))),
    'key': lambda: filt(noise(0.03), 1800, 7000) * env(int(0.03 * SR), 0.0005, 0.006) * 0.25,
    'send': lambda: sweep(0.16, 500, 1500) * env(int(0.16 * SR), 0.004, 0.07) * 0.3,
    'pop': lambda: sweep(0.09, 320, 780) * env(int(0.09 * SR), 0.002, 0.03) * 0.4,
    'knock': lambda: (np.sin(2 * np.pi * 150 * tt(0.3)) * env(int(0.3 * SR), 0.001, 0.045) + filt(noise(0.3), 300, 1500) * env(int(0.3 * SR), 0.001, 0.02) * 0.6) * 0.75,
    'sting': lambda: (sweep(1.4, 70, 38) * env(int(1.4 * SR), 0.004, 0.45) * 0.9 + sum(np.sin(2 * np.pi * f * tt(1.4)) for f in (622, 659, 932, 988)) * env(int(1.4 * SR), 0.01, 0.5) * 0.06 + filt(noise(1.4), 2000, 9000) * env(int(1.4 * SR), 0.002, 0.08) * 0.2),
    'steps': lambda: sum(np.pad(filt(noise(0.2), 80, 500) * env(int(0.2 * SR), 0.002, 0.05) * (0.5 - 0.09 * i), (int(i * 0.42 * SR), int((4 - i) * 0.42 * SR))) for i in range(5)),
    'riser': lambda: (bandnoise(1.6, 200, 5000) * 0.3 + sweep(1.6, 110, 440) * 0.14) * (np.arange(int(1.6 * SR)) / int(1.6 * SR)) ** 2.2,
    'boom': lambda: (sweep(2.2, 62, 30) * env(int(2.2 * SR), 0.003, 0.7) * 1.25 + filt(noise(2.2), 60, 700) * env(int(2.2 * SR), 0.002, 0.25) * 0.5),
    'heartbeat': lambda: sum(np.pad(np.sin(2 * np.pi * 52 * tt(0.25)) * env(int(0.25 * SR), 0.004, 0.06) * g, (int(o * SR), int((0.25 - o) * SR))) for o, g in ((0, 0.8), (0.23, 0.55))),
    'buzz': lambda: np.sign(np.sin(2 * np.pi * 150 * tt(0.45))) * (np.sin(2 * np.pi * 3.2 * tt(0.45)) > -0.3) * 0.07,
    'glitch': lambda: filt(noise(0.25), 1500, 9000) * (rs.rand(int(0.25 * SR)) > 0.6) * 0.2,
    'creak': lambda: np.sin(2 * np.pi * (180 + 60 * np.sin(2 * np.pi * 2.2 * tt(0.9))) * tt(0.9)) * np.sin(np.pi * np.arange(int(0.9 * SR)) / int(0.9 * SR)) ** 2 * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 37 * tt(0.9)))) * 0.14,
    'slam': lambda: (np.sin(2 * np.pi * 85 * tt(0.6)) * env(int(0.6 * SR), 0.001, 0.09) + filt(noise(0.6), 200, 3000) * env(int(0.6 * SR), 0.001, 0.04)) * 0.9,
    'scream_far': lambda: filt(np.sin(2 * np.pi * (700 + 250 * np.sin(2 * np.pi * 5 * tt(0.9))) * tt(0.9)) * np.sin(np.pi * np.arange(int(0.9 * SR)) / int(0.9 * SR)), 300, 1400) * 0.12,
}
mix = np.zeros(N, np.float32); voice = np.zeros(N, np.float32)
def put(buf, a, t, g=1.0):
    i = int(max(0, t) * SR); a = a[:max(0, N - i)]; buf[i:i + len(a)] += a.astype(np.float32) * g
# ---- voices
for l in TL['lines']:
    p = f"audio/lines/L{l['n']:03d}.wav"
    if not os.path.exists(p): print('no voice file for line', l['n'], '- run tools/voice.py first'); break
    a = rd(p); fx = l.get('fx'); g = 1.0
    if fx == 'door': a = verb(filt(a, 140, 1150, 2.0), 0.28, 0.35); g = 1.25
    elif fx == 'far': a = verb(filt(a, 180, 820, 2.0), 0.6, 0.6); g = 1.0
    elif fx == 'phone': a = filt(a, 420, 3000, 3.0); g = 0.9
    elif fx == 'radio': a = np.tanh(filt(a, 500, 2600, 3.0) * 4) * 0.4 + filt(noise(len(a) / SR), 2000, 6000)[:len(a)] * 0.012
    elif fx == 'whisper': a = filt(a, 300, None) * 0.8
    elif fx == 'monster': a = verb(np.interp(np.arange(0, len(a), 0.8), np.arange(len(a)), a).astype(np.float32), 0.5, 0.4)   # slower and lower
    else: a = filt(a, 70, None)
    put(voice, a, l['t0'], g)
# ---- bed
t = np.arange(N) / SR; mood = TL.get('mood', 'tension'); music = next((p for p in ('audio/music.mp3', 'audio/music.wav', 'audio/music.m4a') if os.path.exists(p)), None)
if music:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-stream_loop', '-1', '-i', music, '-t', str(DUR), '-ar', str(SR), '-ac', '1', 'audio/_m.wav'], check=True); m = rd('audio/_m.wav')[:N]; os.remove('audio/_m.wav'); m = np.pad(m, (0, N - len(m))); bed = m / (np.sqrt((m ** 2).mean()) + 1e-6) * 0.045
else:
    drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110.4 * t) + 0.25 * np.sin(2 * np.pi * 164.6 * t)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.13 * t))
    period = 0.534; pulse = np.zeros(N, np.float32); thump = np.sin(2 * np.pi * 48 * tt(0.3)) * env(int(0.3 * SR), 0.004, 0.07)
    for k in range(int(DUR / period)): put(pulse, thump, 0.2 + k * period, 1.0 if k % 2 == 0 else 0.6)
    swell = np.sin(2 * np.pi * (296 + 22 * np.sin(2 * np.pi * 0.21 * t)) * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.085 * t - 1)) ** 3
    air = filt(noise(DUR)[:N], 2500, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
    bed = drone * 0.05 + pulse * (0.0 if mood == 'calm' else 0.13) + swell * 0.012 + air * 0.004
    ramp = 0.75 + 0.5 * np.clip(t / max(1, DUR - 4), 0, 1)       # tension climbs to the choice
    bed = (bed * ramp).astype(np.float32)
# duck the bed a little under speech
ve = np.sqrt(np.convolve(voice ** 2, np.ones(4800) / 4800, 'same')); duck = 1 - 0.45 * np.clip(ve / 0.05, 0, 1); bed = bed * duck
# ---- cues
G = {'whoosh': 0.5, 'whoosh_long': 0.55, 'zoom': 0.4, 'rustle': 0.7, 'punch': 0.55, 'notify': 0.8, 'key': 0.5, 'send': 0.7, 'pop': 0.6, 'riser': 0.8, 'boom': 0.95}
cho = next((b for b in TL['beats'] if b['type'] == 'choice'), None)
for e in TL['events']:
    name, at = e[0], e[1]; g = (e[2] if len(e) > 2 else 1.0) * G.get(name, 0.8)
    if name not in SFX: print('unknown sfx', name); continue
    put(mix, SFX[name](), at - (0.1 if name.startswith('whoosh') else 0), g)
if cho:   # everything but the boom's tail is cut at the choice card
    i = int(cho['t0'] * SR); fade = np.ones(N, np.float32); k = int(0.08 * SR); fade[i:i + k] = np.linspace(1, 0.25, k); fade[i + k:] = 0.25; bed *= fade
full = voice * 1.0 + bed + mix
full = np.tanh(full * 1.6) / 1.6
k = int(0.25 * SR); full[-k:] *= np.linspace(1, 0, k)
st = np.stack([full, full], 1); w = wave.open('audio/_mix.wav', 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/_mix.wav', '-af', 'loudnorm=I=-14:TP=-1.2:LRA=9', '-ar', str(SR), 'audio/final_audio.wav'], check=True); os.remove('audio/_mix.wav')
print(f'audio/final_audio.wav  {DUR:.1f}s  bed: {"nixly music" if music else "synth " + mood}  cues: {len(TL["events"])}')
