# python3 tools/tts.py       (after `node tools/snap.mjs info`)
# Local German voices (Piper) for every spoken line: synthesise, trim, shift pitch/tempo per character with rubberband,
# optional doubled "wrong" voice for doppelgangers -> audio/lines/L###.wav + timings.json (same format as the kit's voice.py).
# The kit's audio.py then adds the room/phone/door effects named in each speaker's fx.
import json, os, re, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import ttslib as L
SR = 48000
# speaker id -> (piper voice, speaker id, semitones, length scale, extra)
VOICES = {
    'paul': ('thorsten-high', None, 3.5, 0.95, {}), 'emil': ('thorsten_emotional-medium', 6, 4.5, 0.92, {}), 'lena': ('kerstin-low', None, 2.0, 0.95, {}),
    'schaffner': ('karlsson-low', None, -1.0, 1.15, {}),
    'ben': ('pavoque-low', None, 2.5, 0.9, {}), 'nina': ('ramona-low', None, 1.5, 0.95, {}), 'max': ('karlsson-low', None, 6.0, 0.92, {}),
    'durchsage': ('eva_k-x_low', None, 0.0, 1.0, {}),
    'ben2': ('pavoque-low', None, 2.2, 1.08, {'double': True}), 'nina2': ('ramona-low', None, 1.2, 1.12, {'double': True}),
}
TL = json.load(open('timeline.json')); says = [b for b in TL['beats'] if b['type'] == 'say']
os.makedirs('audio/lines', exist_ok=True); os.makedirs('tts', exist_ok=True)
def syl(w): w = re.sub(r'[^a-zäöüß]', '', w.lower()); return max(1, len(re.findall(r'(?:au|äu|eu|ei|ie|ai|[aeiouyäöü])', w)))
def save(p, a, sr=SR):
    w = wave.open(p, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def shift(a, sr, st, tempo):
    save('tts/_in.wav', a, sr)
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'tts/_in.wav', '-af', f'aresample={SR},rubberband=pitch={2 ** (st / 12):.4f}:tempo={tempo:.3f}', '-ac', '1', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32).copy()
def trim(a, thr=0.006):
    e = np.where(np.abs(a) > thr)[0]
    if not len(e): return a
    return a[max(0, e[0] - int(0.03 * SR)):min(len(a), e[-1] + int(0.08 * SR))]
def envelope_db(a):
    hop = SR // 100; e = np.sqrt(np.convolve(a * a, np.ones(hop * 2) / (hop * 2), 'same'))[::hop]; return 20 * np.log10(e + 1e-7)
result = {}
for l in TL['lines']:
    who = l['who']; b = says[l['n']]; text = b['text'].replace('|', ' '); text = re.sub(r'\s+', ' ', text).strip()
    v, sid, st, ln, ex = VOICES.get(who, VOICES.get(l['voice'], ('thorsten-high', None, 0, 1.0, {})))
    speak = text.replace('„', '').replace('“', '').replace('…', '.').replace('...', '.')
    a, sr = L.synth(speak, v, sid, length=ln * (1.15 if len(speak.split()) <= 2 else 1.0))
    a = trim(shift(a, sr, st, 1.0))
    if ex.get('double'):   # a second, slightly lower copy a few milliseconds late: the voice is almost right
        b2 = trim(shift(a, SR, -0.45, 1.0)); d = int(0.028 * SR); n = max(len(a), len(b2) + d); m = np.zeros(n, np.float32); m[:len(a)] += a * 0.75; m[d:d + len(b2)] += b2 * 0.55; a = m
    f = int(SR * 0.008); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    rms = np.sqrt((a ** 2).mean()) + 1e-6; a *= min(4.0, 0.12 / rms)
    save(f"audio/lines/L{l['n']:03d}.wav", a)
    # word times by syllables over the voiced part; a word after . ! ? , starts at the nearest pause
    db = envelope_db(a); thr = np.percentile(db, 95) - 30; vb = np.where(db > thr)[0]; v0, v1 = (vb[0] / 100, vb[-1] / 100) if len(vb) else (0, len(a) / SR)
    words = text.split(); ws = np.array([syl(w) + 0.35 for w in words]); edges = v0 + np.concatenate([[0], np.cumsum(ws)]) / ws.sum() * (v1 - v0); quiet = db < thr + 4
    for k in range(1, len(words)):
        if words[k - 1][-1:] not in '.!?,…:': continue
        c = int(edges[k] * 100); lo = max(0, c - 20); seg = quiet[lo:c + 20]
        if seg.any(): idx = np.where(seg)[0]; edges[k] = (lo + idx[np.argmin(np.abs(idx - (c - lo)))]) / 100
    hop = SR // 30; env = np.array([np.sqrt((a[i:i + hop] ** 2).mean()) for i in range(0, len(a), hop)]); env = np.clip(env / (np.percentile(env, 92) + 1e-6), 0, 1)
    result[l['n']] = {'dur': round(len(a) / SR, 3), 'words': [[round(float(edges[k]), 3), round(float(edges[k + 1]), 3)] for k in range(len(words))], 'env': [round(float(x), 2) for x in env]}
    print(f"L{l['n']:03d} {who:10s} {result[l['n']]['dur']:.2f}s  {text}")
json.dump({'lines': [result[n] for n in range(len(TL['lines']))]}, open('timings.json', 'w'))
