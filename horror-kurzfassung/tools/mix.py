# python3 tools/mix.py        (after voice.py and a fresh `node tools/snap.mjs info`)
# 1. drops the kit's camera whoosh where a beat keeps the same shot, and at the hard cut (a hit there instead)
# 2. runs the kit's audio.py (voices, drone bed, kit cues)  3. runs foley.py (this story's own effects)
# 4. lays the foley under the kit mix at the voices' level and normalises everything to -14 LUFS -> audio/mix.wav
import json, os, shutil, subprocess, sys, wave
import numpy as np
SR = 48000
TL = json.load(open('timeline.json')); shutil.copy('timeline.json', 'timeline.full.json')
CUTS = [e[1] for e in TL['events'] if e[0] == 'cut']          # beats that start with a hard cut (lib.js marks cut: true)
B = TL['beats']; drop = set()
for i in range(1, len(B)):
    a, b = B[i - 1], B[i]
    if a['look'] == b['look'] and abs(a['zoom'] - b['zoom']) / max(1, a['zoom']) < 0.12: drop.add(round(b['cam'], 3))
ev = []
for e in TL['events']:
    if e[0] == 'cut': continue
    if e[0] in ('whoosh', 'zoom') and (round(e[1], 3) in drop or any(abs(e[1] - c) < 0.08 for c in CUTS)): continue
    ev.append(e)
ev += [['punch', c, 1.3] for c in CUTS]
TL['events'] = sorted(ev, key=lambda e: e[1]); json.dump(TL, open('timeline.json', 'w'))
print(f'cues kept {len(ev)} of {len(json.load(open("timeline.full.json"))["events"])}')
try:
    subprocess.run([sys.executable, 'tools/audio.py'], check=True)
    subprocess.run([sys.executable, 'tools/foley.py'], check=True)
finally:
    shutil.move('timeline.full.json', 'timeline.json')
def rd(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a.reshape(-1, w.getnchannels()).mean(1)
kit, fol = rd('audio/final_audio.wav'), rd('audio/foley.wav'); n = min(len(kit), len(fol)); kit, fol = kit[:n], fol[:n]
# the voices were levelled to RMS 0.12 before audio.py normalised the mix: measure what that became, scale the foley the same way
win = np.zeros(n, bool)
for l in TL['lines']: win[int(l['t0'] * SR):int((l['t0'] + l['dur']) * SR)] = True
k = np.sqrt((kit[win] ** 2).mean()) / 0.12 if win.any() and os.path.exists('audio/lines/L000.wav') else 2.0
full = kit + fol * k; full = np.tanh(full * 1.25) / 1.25
st = np.stack([full, full], 1); w = wave.open('audio/_mix.wav', 'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', 'audio/_mix.wav', '-af', 'loudnorm=I=-14:TP=-1.2:LRA=9', '-ar', str(SR), 'audio/mix.wav'], check=True); os.remove('audio/_mix.wav')
print(f'audio/mix.wav  {n / SR:.1f}s  foley x{k:.2f}')
