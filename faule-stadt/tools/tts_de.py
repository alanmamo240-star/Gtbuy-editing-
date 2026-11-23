# python3 tools/tts_de.py [voice] [length_scale]
# Free German voice: Piper (de_DE-thorsten) per sentence -> audio/vo.wav, with the // and /// holds from script.txt,
# then word timings (timings.json, one [start,end] per caption word) from faster-whisper run on each sentence clip.
import sys, re, json, wave, io, difflib, subprocess, os
import numpy as np
from piper import PiperVoice
try: from piper import SynthesisConfig
except Exception: from piper.config import SynthesisConfig
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'thorsten-high'; LS = float(sys.argv[2]) if len(sys.argv) > 2 else 0.82
SR = 48000; GAP = 0.09
cap = lambda w: re.sub(r"[^a-z0-9äöüß'\-$%]", '', w.lower().replace('’', "'"))
toks = open('script.txt').read().split()
sents, cur = [], []                      # sentence = (list of raw tokens, hold seconds after it)
for t in toks:
    if re.fullmatch(r'/{2,}', t): sents[-1] = (sents[-1][0], 0.6 if len(t) == 2 else 1.0); continue
    cur.append(t)
    if re.search(r'[.!?:]["“”]*$', t) or re.search(r'\.“$', t): sents.append((cur, 0.0)); cur = []
if cur: sents.append((cur, 0.0))
v = PiperVoice.load(f'voices/de_DE-{VOICE}.onnx'); cfg = SynthesisConfig(length_scale=LS, noise_scale=0.6, noise_w_scale=0.7)
def synth(text):
    b = io.BytesIO()
    with wave.open(b, 'wb') as w: v.synthesize_wav(text, w, syn_config=cfg)
    b.seek(0)
    with wave.open(b) as w: sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    open('audio/_s.raw', 'wb').write((a * 32767).astype(np.int16).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(sr), '-ac', '1', '-i', 'audio/_s.raw', '-ar', str(SR), 'audio/_s.wav'], check=True)
    with wave.open('audio/_s.wav') as w: a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    e = np.abs(a) > 0.01; i0 = max(0, np.argmax(e) - int(0.02 * SR)); i1 = len(a) - np.argmax(e[::-1]) + int(0.04 * SR)
    return a[i0:i1]
from faster_whisper import WhisperModel
wm = WhisperModel('small', device='cpu', compute_type='int8')
out, T, t0 = [], [], 0.0
for raw, hold in sents:
    text = ' '.join(x.replace('*', '') for x in raw); a = synth(text); d = len(a) / SR
    words = [(i, cap(x)) for i, x in enumerate(raw) if cap(x)]
    w16 = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-ar', '16000', '-f', 'f32le', '-'], input=a.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    segs, _ = wm.transcribe(np.frombuffer(w16, np.float32), language='de', word_timestamps=True, beam_size=5, initial_prompt=text)
    hyp = [(cap(w.word), w.start, w.end) for s in segs for w in s.words if cap(w.word)]
    tm = [None] * len(words); sm = difflib.SequenceMatcher(None, [w for _, w in words], [h[0] for h in hyp], autojunk=False)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n): tm[i + k] = [hyp[j + k][1], hyp[j + k][2]]
    # fill unmatched words by letter count between known neighbours
    k = 0
    while k < len(words):
        if tm[k]: k += 1; continue
        j = k
        while j < len(words) and not tm[j]: j += 1
        s = tm[k - 1][1] if k else 0.0; e = tm[j][0] if j < len(words) else d; L = [len(words[q][1]) + 1 for q in range(k, j)]; acc = s
        for q, l in zip(range(k, j), L): dd = (e - s) * l / sum(L); tm[q] = [acc, acc + dd]; acc += dd
        k = j
    for q in range(len(tm)): tm[q][0] = max(tm[q][0], tm[q - 1][0] + 0.034) if q else max(0.0, tm[q][0])
    T += [[round(t0 + s, 3), round(t0 + e, 3)] for s, e in tm]
    out += [a, np.zeros(int((GAP + hold) * SR), np.float32)]; t0 += d + GAP + hold
    print(f'{t0:6.2f}s  {len(hyp):2d}/{len(words):2d} matched  {text}')
a = np.concatenate(out)
with wave.open('audio/vo.wav', 'w') as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(T, open('timings.json', 'w')); [os.remove(f) for f in ('audio/_s.raw', 'audio/_s.wav')]
print(json.dumps({'words': len(T), 'seconds': round(len(a) / SR, 2), 'wps': round(len(T) / (len(a) / SR), 2)}))
