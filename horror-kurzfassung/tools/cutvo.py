# python3 tools/cutvo.py     (German replacement for the kit's voice.py; its English aligner cannot follow German)
#   timeline.json + voices.json + audio/vo_<Voice>.(mp3|wav) (one recording per voice, lines in order)
#   -> audio/lines/L###.wav and timings.json (line length, word times, mouth envelope), same format as voice.py.
# Lines are separated at pauses; if two lines run together, at the deepest dip near where the syllable count expects the break.
# Word times inside a line follow the syllables; phrase changes snap to the nearest short pause.
import json, os, re, subprocess, sys, wave
import numpy as np
SR = 48000; TEMPO = float(os.environ.get('TEMPO', '0.94'))
TL = json.load(open('timeline.json')); V = json.load(open('voices.json')); LINES = {l['n']: l for l in TL['lines']}
os.makedirs('audio/lines', exist_ok=True)
def syl(w):
    w = re.sub(r'[^a-zäöüß]', '', w.lower())
    return max(1, len(re.findall(r'(?:au|äu|eu|ei|ie|ai|[aeiouyäöü])', w)))
def load(path):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-af', f'atempo={TEMPO}', '-ar', str(SR), '-ac', '1', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(np.float32) / 32768
def save(p, a):
    w = wave.open(p, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def envelope(a):
    hop = SR // 100; e = np.sqrt(np.convolve(a * a, np.ones(hop * 2) / (hop * 2), 'same'))[::hop]; return 20 * np.log10(e + 1e-7)
def chunks(db, gap):
    thr = np.percentile(db, 95) - 32; sp = db > thr; iv = []; s = None
    for i, v in enumerate(np.append(sp, False)):
        if v and s is None: s = i
        if not v and s is not None: iv.append([s, i]); s = None
    mg = []
    for x in iv:
        if mg and x[0] - mg[-1][1] < gap * 100: mg[-1][1] = x[1]
        else: mg.append(x)
    return [x for x in mg if x[1] - x[0] > 6], thr
def split_lines(a, words_per_line):
    db = envelope(a); sm = np.convolve(db, np.ones(5) / 5, 'same'); mg, thr = chunks(db, 0.16)
    if not mg: raise RuntimeError('no speech found')
    s0, s1 = mg[0][0], mg[-1][1]; P = len(words_per_line)
    wts = np.array([sum(syl(w) for w in ws) + 0.6 for ws in words_per_line]); cut = []
    groups = [[x] for x in mg]
    while len(groups) > P:   # merge the closest neighbours
        gaps = [groups[i + 1][0][0] - groups[i][-1][1] for i in range(len(groups) - 1)]; i = int(np.argmin(gaps)); groups[i] += groups.pop(i + 1)
    bounds = [[g[0][0], g[-1][1]] for g in groups]
    while len(bounds) < P:   # lines ran together: split the longest span at its deepest dip near the expected place
        k = int(np.argmax([b[1] - b[0] for b in bounds])); b = bounds[k]; i = len(bounds) - 1 - k if False else k
        before = sum(wts[:k]); here = wts[k] + wts[k + 1] if k + 1 < len(wts) else wts[k]; frac = wts[k] / here
        lo, hi = int(b[0] + (b[1] - b[0]) * (frac - 0.25)), int(b[0] + (b[1] - b[0]) * (frac + 0.25)); lo = max(b[0] + 5, lo); hi = min(b[1] - 5, hi)
        m = lo + int(np.argmin(sm[lo:hi])) if hi > lo else (b[0] + b[1]) // 2; bounds[k:k + 1] = [[b[0], m], [m + 1, b[1]]]
    return bounds, db, thr
result = {}; report = []
for voice, info in V.items():
    path = next((p for p in (info['file'], info['file'].replace('.mp3', '.wav')) if os.path.exists(p)), None)
    if not path: print('MISSING', info['file']); sys.exit(1)
    a = load(path); wl = [[w for w in LINES[n]['text'].split()] for n in info['lines']]
    bounds, db, thr = split_lines(a, wl)
    for li, (b0, b1) in enumerate(bounds):
        s2 = max(0, b0 / 100 - 0.04); e2 = min(len(a) / SR, b1 / 100 + 0.1); clip = a[int(s2 * SR):int(e2 * SR)].copy(); f = int(SR * 0.008); clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
        n = info['lines'][li]; L = LINES[n]; words = L['text'].split(); text = TL['beats'][[b['type'] == 'say' for b in TL['beats']].index(True)]  # unused
        # word times by syllables over the voiced part, then snap phrase starts to short pauses
        sdb = envelope(clip); vb = np.where(sdb > thr)[0]; v0 = (vb[0] if len(vb) else 0) / 100; v1 = (vb[-1] if len(vb) else len(sdb)) / 100
        ws = np.array([syl(w) + 0.35 for w in words]); edges = v0 + np.concatenate([[0], np.cumsum(ws)]) / ws.sum() * (v1 - v0)
        quiet = sdb < thr + 4
        for k in range(1, len(words)):
            c = int(edges[k] * 100); w = 18; seg = quiet[max(0, c - w):c + w]
            if seg.any(): idx = np.where(seg)[0]; j = idx[np.argmin(np.abs(idx - (c - max(0, c - w))))]; edges[k] = (max(0, c - w) + j) / 100 if words[k - 1][-1:] in '.!?,…' else edges[k]
        wt = [[round(float(edges[k]), 3), round(float(edges[k + 1]), 3)] for k in range(len(words))]
        rms = np.sqrt((clip ** 2).mean()) + 1e-6; clip *= min(4.0, 0.12 / rms); save(f'audio/lines/L{n:03d}.wav', clip)
        hop = SR // 30; env = np.array([np.sqrt((clip[i:i + hop] ** 2).mean()) for i in range(0, len(clip), hop)]); env = np.clip(env / (np.percentile(env, 92) + 1e-6), 0, 1)
        result[n] = {'dur': round(len(clip) / SR, 3), 'words': wt, 'env': [round(float(v), 2) for v in env]}
    report.append(f'{voice}: {len(bounds)} lines, {len(a) / SR:.1f}s raw')
N = len(TL['lines']); missing = [n for n in range(N) if n not in result]
if missing: print('lines without audio:', missing); sys.exit(1)
json.dump({'lines': [result[n] for n in range(N)]}, open('timings.json', 'w'))
print(' | '.join(report)); print('lines:', ' '.join(f"{n}:{result[n]['dur']}s" for n in range(N)))
