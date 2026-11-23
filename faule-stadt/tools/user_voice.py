# python3 tools/user_voice.py audio/user_raw.mp3 [tempo]
# Uses a self-recorded voiceover: whisper word times (audio/user_words.json) -> aligned to the script's caption words,
# long pauses tightened (story holds from holds.json kept), light tempo-up -> audio/vo.wav + timings.json
import sys, re, json, wave, subprocess, difflib, os
import numpy as np
src = sys.argv[1]; K = float(sys.argv[2]) if len(sys.argv) > 2 else 1.06; SR = 48000; GAP = 0.14
cap = lambda w: re.sub(r"[^a-z0-9äöüß'\-$%]", '', w.lower().replace('’', "'"))
toks = [cap(t) for t in open('script.txt').read().split() if cap(t)]
holds = {i: s for i, s in json.load(open('holds.json'))}
hyp = [(cap(w['w']), w['s'], w['e']) for w in json.load(open('audio/user_words.json')) if cap(w['w'])]
NUM = {'20': 'zwanzig', '12': 'zwölf', '6': 'sechs', '3': 'drei'}; hyp = [(NUM.get(w, w), s, e) for w, s, e in hyp]
T = [None] * len(toks); sm = difflib.SequenceMatcher(None, toks, [h[0] for h in hyp], autojunk=False)
for i, j, n in sm.get_matching_blocks():
    for k in range(n): T[i + k] = [hyp[j + k][1], hyp[j + k][2]]
miss = sum(t is None for t in T); k = 0
while k < len(T):
    if T[k]: k += 1; continue
    j = k
    while j < len(T) and not T[j]: j += 1
    s = T[k - 1][1]; e = T[j][0]; L = [len(toks[q]) + 1 for q in range(k, j)]; acc = s
    for q, l in zip(range(k, j), L): dd = (e - s) * l / sum(L); T[q] = [acc, acc + dd]; acc += dd
    k = j
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', 'highpass=f=80', '-ac', '1', '-ar', str(SR), 'audio/_u.wav'], check=True)
w = wave.open('audio/_u.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close()
# cut every gap between words down to GAP (or to the story hold), using the aligned word ends/starts
cuts = []
for i in range(len(T) - 1):
    g0, g1 = T[i][1] + 0.05, T[i + 1][0] - 0.03; want = holds.get(i, GAP)
    if g1 - g0 > want + 0.05: cuts.append((g0 + want / 2, g1 - want / 2))
def remap(t):
    off = 0.0
    for c0, c1 in cuts:
        if t >= c1: off += c1 - c0
        elif t > c0: return c0 - off
    return t - off
parts, pos, f = [], 0.0, int(0.006 * SR)
for c0, c1 in cuts + [(len(a) / SR, len(a) / SR)]:
    seg = a[int(pos * SR):int(c0 * SR)].copy()
    if len(seg) > 2 * f: seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    parts.append(seg); pos = c1
b = np.concatenate(parts); s0 = max(0.0, remap(T[0][0]) - 0.05); b = b[int(s0 * SR):]
w = wave.open('audio/_t.wav', 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(b, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/_t.wav', '-af', f'atempo={K}', '-ar', str(SR), '-ac', '1', 'audio/vo.wav'], check=True)
T2 = [[round((remap(s) - s0) / K, 3), round((remap(e) - s0) / K, 3)] for s, e in T]
for i in range(1, len(T2)): T2[i][0] = max(T2[i][0], round(T2[i - 1][0] + 0.034, 3))
json.dump(T2, open('timings.json', 'w')); [os.remove(x) for x in ('audio/_u.wav', 'audio/_t.wav')]
d = len(b) / SR / K; print(json.dumps({'words': len(T2), 'unmatched_filled': miss, 'raw_s': round(len(a) / SR, 2), 'final_s': round(d, 2), 'wps': round(len(T2) / d, 2)}))
