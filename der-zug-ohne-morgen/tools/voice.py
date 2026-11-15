# python3 tools/voice.py
#   reads timeline.json + voices.json (from `node tools/snap.mjs info`) and audio/vo_<Voice>.mp3 (one Nixly voiceover per voice)
#   -> audio/lines/L000.wav ... (one clean clip per spoken line, 48 kHz mono) and timings.json (line length, word times, mouth envelope)
# Word timing = forced alignment of the known script with pocketsphinx (pip install pocketsphinx; offline). Fallback: pause detection.
import sys, re, json, wave, subprocess, os, difflib
import numpy as np
SR = 48000
os.makedirs('audio/lines', exist_ok=True)
TL = json.load(open('timeline.json')); V = json.load(open('voices.json')); LINES = {l['n']: l for l in TL['lines']}
norm = lambda w: re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'"))
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split(); TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()
def num(n):
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if n < 1000: return [ONES[n // 100], 'hundred'] + (num(n % 100) if n % 100 else [])
    return num(n // 1000) + ['thousand'] + (num(n % 1000) if n % 1000 else [])
def spoken(tok):  # caption word -> plain words the aligner knows ("9:13" -> nine thirteen)
    out = []
    for part in re.split(r"[-:/]", tok):
        m = re.fullmatch(r"(\d+)(st|nd|rd|th|s)?", part)
        if m: out += num(int(m.group(1)))
        else:
            p = re.sub(r"(.)\1{2,}", r"\1", part)   # "pleeease" -> "please"
            if re.sub(r"[^a-z']", '', p): out.append(re.sub(r"[^a-z']", '', p))
    return out
def syl(w): return max(1, len(re.findall(r'[aeiouy]+', re.sub(r'e$', '', w) if len(w) > 3 else w)))
run = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
TEMPO = float(os.environ.get('TEMPO', '0.94'))   # a touch slower than the TTS reads: tension needs room
def load(path, sr):
    run('-i', path, '-af', f'atempo={TEMPO}', '-ar', str(sr), '-ac', '1', '-f', 's16le', 'audio/_tmp.raw'); a = np.fromfile('audio/_tmp.raw', dtype=np.int16).astype(np.float32) / 32768; os.remove('audio/_tmp.raw'); return a
def save(path, a):
    w = wave.open(path, 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

def forced(a16, toks):
    from pocketsphinx import Decoder
    d = Decoder(samprate=16000, loglevel='FATAL', beam=1e-300, wbeam=1e-200, pbeam=1e-300, maxhmmpf=-1, maxwpf=-1)
    L = dict(a='AE', b='B', c='K', d='D', e='EH', f='F', g='G', h='HH', i='IH', j='JH', k='K', l='L', m='M', n='N', o='OW', p='P', q='K', r='R', s='S', t='T', u='AH', v='V', w='W', x='K S', y='Y', z='Z')
    DG = dict(sh='SH', ch='CH', th='TH', ph='F', ck='K', ng='NG', ee='IY', oo='UW', ou='AW', ow='OW', ai='EY', ay='EY', ea='IY', oa='OW', oi='OY', oy='OY', qu='K W')
    def g2p(w):
        w = re.sub(r'[^a-z]', '', w); o = []; i = 0
        while i < len(w):
            if w[i:i + 2] in DG: o.append(DG[w[i:i + 2]]); i += 2
            else:
                if not (w[i] == 'e' and i == len(w) - 1 and len(w) > 3): o.append(L[w[i]])
                i += 1
        return ' '.join(o) or 'AH'
    seq = []
    for i, t in enumerate(toks):
        for p in spoken(t):
            if d.lookup_word(p) is None:
                q = re.sub(r"[^a-z]", '', p)
                if q and d.lookup_word(q) is None: d.add_word(q, g2p(q), True)
                p = q
            if p: seq.append((i, p))
    d.set_align_text(' '.join(p for _, p in seq)); d.start_utt(); d.process_raw((a16 * 32767).astype(np.int16).tobytes(), full_utt=True); d.end_utt()
    segs = [(re.sub(r'\(\d+\)$', '', s.word), s.start_frame / 100, s.end_frame / 100) for s in (d.seg() or []) if not s.word.startswith('<') and s.word != '(NULL)']
    if len(segs) < 0.8 * len(seq): raise RuntimeError(f'aligner returned {len(segs)} of {len(seq)} words')
    T = [None] * len(toks); sm = difflib.SequenceMatcher(None, [p for _, p in seq], [s[0] for s in segs], autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            ti = seq[i + k][0]; s, e = segs[j + k][1], segs[j + k][2]; T[ti] = [s, e] if T[ti] is None else [T[ti][0], e]
    return T

def speech_chunks(a, sr, gap=0.22):
    hop = int(sr * 0.01); env = np.sqrt(np.convolve(a * a, np.ones(hop * 2) / (hop * 2), 'same'))[::hop]; db = 20 * np.log10(env + 1e-7); sp = db > np.percentile(db, 95) - 32; iv = []; s = None
    for i, v in enumerate(np.append(sp, False)):
        if v and s is None: s = i
        if not v and s is not None: iv.append([s * 0.01, i * 0.01]); s = None
    mg = []
    for x in iv:
        if mg and x[0] - mg[-1][1] < gap: mg[-1][1] = x[1]
        else: mg.append(x)
    return [x for x in mg if x[1] - x[0] > 0.07], db

def by_pauses(a, sr, lines_toks):   # fallback: split at the longest pauses, one group of chunks per line, sized by syllables
    mg, _ = speech_chunks(a, sr); P = len(lines_toks); M = len(mg)
    if M < P: raise RuntimeError(f'only {M} spoken chunks for {P} lines')
    wt = np.array([sum(syl(p) for t in lt for p in spoken(t)) + 1.0 for lt in lines_toks]); rate = sum(x[1] - x[0] for x in mg) / wt.sum(); D = np.full((P + 1, M + 1), 1e18); Bk = np.zeros((P + 1, M + 1), int); D[0, 0] = 0
    cum = np.concatenate([[0], np.cumsum([x[1] - x[0] for x in mg])])
    for p in range(1, P + 1):
        for m in range(p, M - (P - p) + 1):
            for q in range(p - 1, m):
                c = D[p - 1, q] + abs((cum[m] - cum[q]) - wt[p - 1] * rate)
                if c < D[p, m]: D[p, m] = c; Bk[p, m] = q
    out = []; m = M
    for p in range(P, 0, -1): q = Bk[p, m]; out.append((mg[q][0], mg[m - 1][1])); m = q
    out.reverse(); T = []
    for (s, e), lt in zip(out, lines_toks):
        ww = np.array([sum(syl(p) for p in spoken(t)) + 0.3 for t in lt]); t0 = s
        for w in ww: dd = (e - s) * w / ww.sum(); T.append([t0, t0 + dd]); t0 += dd
    return T

result = {}; report = []
for voice, info in V.items():
    path = info['file']
    if not os.path.exists(path):
        alt = [p for p in (path.replace('.mp3', '.wav'), path.replace('.mp3', '.m4a')) if os.path.exists(p)]
        if not alt: print(f'MISSING {path}  (generate it with nixly_voiceover, voice "{voice}", script = {info["script"]})'); sys.exit(1)
        path = alt[0]
    a = load(path, SR); a16 = load(path, 16000); dur = len(a) / SR
    ltoks = [[w for w in LINES[n]['text'].split() if norm(w)] for n in info['lines']]; toks = [norm(w) for lt in ltoks for w in lt]
    method = 'forced'
    try:
        T = forced(a16, toks)
        i = 0
        while i < len(T):   # fill words the aligner skipped
            if T[i]: i += 1; continue
            j = i
            while j < len(T) and not T[j]: j += 1
            s = T[i - 1][1] if i else 0.0; e = T[j][0] if j < len(T) else dur; n = j - i
            for k in range(i, j): T[k] = [s + (e - s) * (k - i) / n, s + (e - s) * (k - i + 1) / n]
            i = j
    except Exception as ex:
        print(f'{voice}: forced alignment unavailable ({repr(ex)[:120]}), using pauses'); method = 'pauses'; T = by_pauses(a, SR, ltoks)
    _, db = speech_chunks(a, SR); thr = np.percentile(db, 95) - 34; quiet = lambda t: db[min(len(db) - 1, max(0, int(t * 100)))] < thr
    k = 0; bounds = []
    for lt in ltoks: bounds.append((T[k][0], T[k + len(lt) - 1][1], k, len(lt))); k += len(lt)
    for li, (s, e, k0, n) in enumerate(bounds):
        lo = bounds[li - 1][1] + 0.03 if li else 0.0; hi = bounds[li + 1][0] - 0.03 if li + 1 < len(bounds) else dur
        s2 = s
        while s2 > lo and not quiet(s2 - 0.01) and s - s2 < 0.25: s2 -= 0.01      # grow outwards to the nearest silence so no consonant is clipped
        e2 = e
        while e2 < hi and not quiet(e2 + 0.01) and e2 - e < 0.5: e2 += 0.01
        s2 = max(lo, s2 - 0.04); e2 = min(hi, e2 + 0.09); clip = a[int(s2 * SR):int(e2 * SR)].copy(); f = int(SR * 0.008)
        if len(clip) > 2 * f: clip[:f] *= np.linspace(0, 1, f); clip[-f:] *= np.linspace(1, 0, f)
        n_line = info['lines'][li]; L = LINES[n_line]; wt = [[round(max(0, T[k0 + j][0] - s2), 3), round(T[k0 + j][1] - s2, 3)] for j in range(n)]
        if L.get('stretch'):   # the voice drags and drops in pitch, like a tape running down, over the last 60% of the line
            N = len(clip); pos = []; x = 0.0; i0 = int(N * 0.4)
            while x < N - 1: pos.append(x); x += 1.0 if x < i0 else max(0.38, 1.0 - 0.62 * (x - i0) / (N - i0))
            pos = np.array(pos); clip = np.interp(pos, np.arange(N), clip).astype(np.float32); m = lambda t: float(np.searchsorted(pos, t * SR) / SR); wt = [[round(m(w0), 3), round(m(w1), 3)] for w0, w1 in wt]
            fo = int(SR * 0.5); clip[-fo:] *= np.linspace(1, 0, fo) ** 1.5
        rms = np.sqrt((clip ** 2).mean()) + 1e-6; clip *= min(4.0, 0.12 / rms)            # level every line the same
        save(f'audio/lines/L{n_line:03d}.wav', clip)
        hop = SR // 30; env = np.array([np.sqrt((clip[i:i + hop] ** 2).mean()) for i in range(0, len(clip), hop)]); env = np.clip(env / (np.percentile(env, 92) + 1e-6), 0, 1)
        result[n_line] = {'dur': round(len(clip) / SR, 3), 'words': wt, 'env': [round(float(v), 2) for v in env]}
    report.append(f'{voice}: {method}, {len(bounds)} lines, {dur:.1f}s raw')
N = len(TL['lines']); missing = [n for n in range(N) if n not in result]
if missing: print('lines without audio:', missing); sys.exit(1)
json.dump({'lines': [result[n] for n in range(N)]}, open('timings.json', 'w'))
print(' | '.join(report)); print('spoken seconds:', round(sum(result[n]['dur'] for n in range(N)), 1), ' words/s while speaking:', round(sum(len(result[n]['words']) for n in range(N)) / sum(result[n]['dur'] for n in range(N)), 2))
print('next: node tools/snap.mjs info   (real timings)  ->  python3 tools/audio.py')
