# python3 tools/splitall.py      (run in horror-kurzfassung/)
# One Nixly recording per voice holds that voice's lines from several episodes (voices_all.json says which, in order).
# Cut every recording into its lines and write each episode's audio/lines/L###.wav and timings.json (line length, word
# times, mouth envelope), the format core.js reads. With nixly/asr.json (word timestamps from a speech recognizer, see
# tools/asr.py) the break between two lines is the quietest spot around the recognizer's break and the caption word times
# are the recognized ones; without it, pauses and syllable counts decide. The doppelgangers get a slightly doubled voice.
import json, os, re, subprocess, sys, wave
import numpy as np
SR = 48000; TEMPO = float(os.environ.get('TEMPO', '0.97'))
G = json.load(open(os.environ.get('VOICES', 'voices_all.json'))); FILES = json.load(open(os.environ.get('VDIR', 'nixly/') + 'files.json'))
DOUBLE = {'doppel', 'draussen', 'nina2'}
def syl(w): w = re.sub(r'[^a-zäöüß]', '', w.lower()); return max(1, len(re.findall(r'(?:au|äu|eu|ei|ie|ai|[aeiouyäöü])', w)))
def load(path, af=f'atempo={TEMPO}'):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-af', af, '-ar', str(SR), '-ac', '1', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(np.float32) / 32768
def save(p, a):
    w = wave.open(p, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def envelope(a):
    hop = SR // 100; e = np.sqrt(np.convolve(a * a, np.ones(hop * 2) / (hop * 2), 'same'))[::hop]; return 20 * np.log10(e + 1e-7)
def chunks(db, gap):
    thr = np.percentile(db, 95) - 34; sp = db > thr; iv = []; s = None
    for i, v in enumerate(np.append(sp, False)):
        if v and s is None: s = i
        if not v and s is not None: iv.append([s, i]); s = None
    mg = []
    for x in iv:
        if mg and x[0] - mg[-1][1] < gap * 100: mg[-1][1] = x[1]
        else: mg.append(x)
    return [x for x in mg if x[1] - x[0] > 6], thr
def split(a, texts):
    db = envelope(a); sm = np.convolve(db, np.ones(5) / 5, 'same'); mg, thr = chunks(db, 0.16); P = len(texts)
    wts = np.array([sum(syl(w) for w in t.split()) + 0.6 for t in texts]); groups = [[x] for x in mg]
    while len(groups) > P:   # too many pieces: join the two closest neighbours (a pause inside a line)
        gaps = [groups[i + 1][0][0] - groups[i][-1][1] for i in range(len(groups) - 1)]; i = int(np.argmin(gaps)); groups[i] += groups.pop(i + 1)
    bounds = [[g[0][0], g[-1][1]] for g in groups]
    while len(bounds) < P:   # too few: split the span whose syllables say it holds two lines
        k = int(np.argmax([(b[1] - b[0]) / wts[min(i, P - 1)] for i, b in enumerate(bounds)])); b = bounds[k]; frac = wts[k] / (wts[k] + wts[min(k + 1, P - 1)])
        lo, hi = int(b[0] + (b[1] - b[0]) * (frac - 0.25)), int(b[0] + (b[1] - b[0]) * (frac + 0.25)); lo = max(b[0] + 5, lo); hi = min(b[1] - 5, hi)
        m = lo + int(np.argmin(sm[lo:hi])) if hi > lo else (b[0] + b[1]) // 2; bounds[k:k + 1] = [[b[0], m], [m + 1, b[1]]]
    return bounds, thr
def doubled(a):
    save('nixly/_in.wav', a)
    b = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', 'nixly/_in.wav', '-af', f'rubberband=pitch={2 ** (-0.5 / 12):.4f}', '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    d = int(0.026 * SR); n = max(len(a), len(b) + d); m = np.zeros(n, np.float32); m[:len(a)] += a * 0.86; m[d:d + len(b)] += b * 0.32; os.remove('nixly/_in.wav'); return m
_A = os.environ.get('VDIR', 'nixly/') + 'asr.json'; ASR = json.load(open(_A)) if os.path.exists(_A) else {}
def split_asr(a, lines, W):   # W: [[word, start, end], ...] in the raw recording's time
    db = envelope(a); sm = np.convolve(db, np.ones(5) / 5, 'same'); thr = np.percentile(db, 95) - 34; sp = db > thr
    A = np.fft.rfft(a); f = np.fft.rfftfreq(len(a), 1 / SR); hb = np.fft.irfft(A * (f > 3500), len(a)).astype(np.float32)
    fric = envelope(hb)[:len(db)] - db                                                    # near 0 dB where the sound is mostly hiss
    counts = [len(l['text'].split()) for l in lines]; assert sum(counts) == len(W), (sum(counts), len(W), [w[0] for w in W])
    first = np.cumsum([0] + counts[:-1]); cuts = []
    for k in first[1:]:
        c = int((W[k - 1][2] + W[k][1]) / 2 / TEMPO * 100); lo, hi = max(1, c - 14), min(len(sm) - 1, c + 14)
        q = np.where(~sp[lo:hi])[0]
        if len(q):   # the middle of the longest quiet run near the recognizer's break
            runs = np.split(q, np.where(np.diff(q) > 1)[0] + 1); r = max(runs, key=len); cuts.append(lo + int(r[len(r) // 2]))
        else: cuts.append(lo + int(np.argmin(sm[lo:hi])))
        pw, nw = (re.sub(r'[^a-zäöüß]', '', W[j][0].lower()) for j in (k - 1, k))   # '...raus' + 'Lauf': the hiss of the s is
        if re.search(r'(s|ß|z|f|ch|x)$', pw) and not re.match(r'(s|ß|z|f|c|x|t|p|k|h)', nw):    # quiet but still the
            while cuts[-1] < hi + 10 and fric[cuts[-1]] > -8: cuts[-1] += 1                      # old line: cut after it
    edges = [0] + cuts + [len(sp)]; bounds = []
    for i in range(len(lines)):
        v = np.where(sp[edges[i]:edges[i + 1]])[0]; bounds.append([edges[i] + int(v[0]), edges[i] + int(v[-1]) + 1] if len(v) else [edges[i], edges[i + 1]])
    words = [[[w[1] / TEMPO, w[2] / TEMPO] for w in W[k:k + n]] for k, n in zip(first, counts)]
    return bounds, thr, words
timings = {}
for voice, lines in G.items():
    a = load(FILES[voice]); texts = [l['text'] for l in lines]
    if voice in ASR: bounds, thr, awords = split_asr(a, lines, ASR[voice])
    else: (bounds, thr), awords = split(a, texts), [None] * len(lines)
    print(f'{voice}: {len(a) / SR:.1f}s raw, {len(bounds)} lines' + (' (word times from asr.json)' if voice in ASR else ''))
    for i, ((b0, b1), l) in enumerate(zip(bounds, lines)):
        s2 = max(0, b0 / 100 - 0.05, bounds[i - 1][1] / 100 + 0.02 if i else 0); e2 = min(len(a) / SR, b1 / 100 + 0.12, bounds[i + 1][0] / 100 - 0.02 if i + 1 < len(bounds) else 1e9)
        clip = a[int(s2 * SR):int(e2 * SR)].copy(); f = int(SR * 0.008); clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
        if l['who'] in DOUBLE: clip = doubled(clip)
        words = l['text'].split(); sdb = envelope(clip); vb = np.where(sdb > thr)[0]; v0 = (vb[0] if len(vb) else 0) / 100; v1 = (vb[-1] if len(vb) else len(sdb)) / 100
        if awords[i]:   # recognized word times, kept inside the clip and in order
            dur = len(clip) / SR; ed = [[min(dur, max(0, x - s2)) for x in w] for w in awords[i]]; ed[0][0] = min(ed[0][0], v0); ed[-1][1] = max(ed[-1][1], v1)
            edges = np.array([w[0] for w in ed] + [ed[-1][1]])
        else:
            ws = np.array([syl(w) + 0.35 for w in words]); edges = v0 + np.concatenate([[0], np.cumsum(ws)]) / ws.sum() * (v1 - v0); quiet = sdb < thr + 4
            for k in range(1, len(words)):
                if words[k - 1][-1:] not in '.!?,…:': continue
                c = int(edges[k] * 100); lo = max(0, c - 20); seg = quiet[lo:c + 20]
                if seg.any(): idx = np.where(seg)[0]; edges[k] = (lo + idx[np.argmin(np.abs(idx - (c - lo)))]) / 100
        # long pauses inside a line ("Raus! ... Sofort!") shrink to 0.32 s so the line keeps its pace
        ed = envelope(clip); q = ed < thr; vv = np.where(~q)[0]; cuts_ = []
        if len(vv):
            i = vv[0]
            while i < vv[-1]:
                if q[i]:
                    j = i
                    while j < vv[-1] and q[j]: j += 1
                    if j - i > 50: cuts_.append((i + 16, j - 16))
                    i = j
                else: i += 1
        for c0, c1 in reversed(cuts_):
            a0, a1 = int(c0 / 100 * SR), int(c1 / 100 * SR); f2 = int(0.01 * SR)
            clip = np.concatenate([clip[:a0], clip[a1:]]); clip[a0 - f2:a0 + f2] *= np.concatenate([np.linspace(1, 0.3, f2), np.linspace(0.3, 1, f2)])[:len(clip[a0 - f2:a0 + f2])]
            edges = np.where(edges >= c1 / 100, edges - (c1 - c0) / 100, np.minimum(edges, c0 / 100))
        if cuts_: print(f"      shortened {len(cuts_)} pause(s) by {sum(b - a for a, b in cuts_) / 100:.2f}s")
        rms = np.sqrt((clip ** 2).mean()) + 1e-6; clip *= min(4.0, 0.12 / rms)
        os.makedirs(f"{l['ep']}/audio/lines", exist_ok=True); save(f"{l['ep']}/audio/lines/L{l['n']:03d}.wav", clip)
        hop = SR // 30; env = np.array([np.sqrt((clip[i:i + hop] ** 2).mean()) for i in range(0, len(clip), hop)]); env = np.clip(env / (np.percentile(env, 92) + 1e-6), 0, 1)
        timings.setdefault(l['ep'], {})[l['n']] = {'dur': round(len(clip) / SR, 3), 'words': [[round(float(edges[k]), 3), round(float(edges[k + 1]), 3)] for k in range(len(words))], 'env': [round(float(x), 2) for x in env]}
        print(f"   {l['ep']} L{l['n']:03d} {len(clip) / SR:.2f}s  {l['text']}")
for ep, T in timings.items():
    json.dump({'lines': [T[n] for n in range(len(T))]}, open(f'{ep}/timings.json', 'w'))
print('timings written for', ', '.join(sorted(timings)))
