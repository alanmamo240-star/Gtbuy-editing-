"""Build a video's render/tl/audio/run scripts from the shared v7/v8 engine + a per-video config.
usage: python3 mk.py <video_dir>   (reads <video_dir>/cfg.py)"""
import sys, os, importlib.util
KIT = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1]
spec = importlib.util.spec_from_file_location("cfg", os.path.join(D, "cfg.py")); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)

s = open(os.path.join(KIT, "base_render.py")).read()
def R(a, b):
    global s
    assert a in s, a[:80]; s = s.replace(a, b)
def RB(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]
R('"""v8 USFans "5 Tipps für günstigen Versand" (built on the v7 engine):', f'"""{C.NAME} (shared v7/v8 engine, built by kit/mk.py):')
RB("SHOTS = [", "SHOT_END =", C.SHOTS.strip() + "\n")
if hasattr(C, "ENH"): R('ENH = "hqdn3d=1.4:1.1:3:3,cas=0.5,eq=contrast=1.06:saturation=1.08:gamma=1.02,colorbalance=rm=0.015:bm=-0.015:rh=0.01"', f'ENH = "{C.ENH}"')
R("    Y = 1000 - (z - 1) * 700", "    " + C.YFORM.strip())
RB("TITLE_P, TITLE_S = title_sprite(", "def headline(", C.TITLES.strip() + "\n")
R('        sm = T.text_mask(small, "montbi", 74, 0.04); S =',
  '        sm = T.text_mask(small, "montbi", 74, 0.04)\n        if sm.shape[1] > 900: sm = cv2.resize(sm, (900, int(sm.shape[0] * 900 / sm.shape[1])), interpolation=cv2.INTER_AREA)\n        S =')
if getattr(C, "WORDRULES", ""): R('    w = raw[i]; tok = w["w"]\n', '    w = raw[i]; tok = w["w"]\n' + C.WORDRULES.rstrip("\n") + "\n")
if hasattr(C, "REP"): R('REP = {', 'REP = {' + C.REP.strip().rstrip(",") + ", ")
RB("KEY = {", "def clean(", C.KEY.strip() + "\n")
RB("SECTIONS = [", "def chips(", C.SECTIONS.strip() + "\n")
RB("PH_MAP = (", "def phone_layer(", (getattr(C, "PH_MAP", None) or "PH_MAP = ([-9.0, -8.0], [6.0, 6.1])").strip() + "\n")
R("    if not (21.4 <= ts <= 27.55): return comp", "    if not (PH_MAP[0][0] <= ts <= PH_MAP[0][-1]): return comp")
RB("def parcel(", "def cards(", C.CARDS.strip() + "\n")
RB("def opening(comp, ts, bgk):", "def cta(comp, ts):", "def opening(comp, ts, bgk):\n" + (getattr(C, "OPENING", "") or "    return comp").rstrip() + "\n")
if getattr(C, "CARDS_FRONT", False):
    R("ry=-4 + 2 * np.sin(ts * 0.8)), bgk)", "ry=-4 + 2 * np.sin(ts * 0.8)))")
open(os.path.join(D, "render.py"), "w").write(s)

t = open(os.path.join(KIT, "base_tl.py")).read().split("\n")
out = []
for line in t:
    if line.startswith("SIL = "): line = f"SIL = {C.SIL!r}"
    elif line.startswith("END = "): line = f"END = {C.END}"
    elif line.startswith("FREEZE = "): line = f"FREEZE = {getattr(C, 'FREEZE', 1.8)}"
    elif line.startswith("SEGS = []; a = "): line = f"SEGS = []; a = {getattr(C, 'START', 0.0)}"
    elif line.startswith('"""'): line = f'"""Edit decision list for {C.NAME}: dead air removed, source<->output time mapping."""'
    out.append(line)
open(os.path.join(D, "tl.py"), "w").write("\n".join(out))

a = open(os.path.join(KIT, "base_audio.py")).read()
i = a.index("for c in CUTS_OUT:"); j = a.index('save("sfx.wav", sfx)')
a = a[:i] + "for c in CUTS_OUT: place(whoosh(0.4, 0.6, 500, 3500), c, -30, 0.24, out=True)\n" + C.SFX.strip() + \
    "\nplace(impact(1.4, 40), DUR_MAIN, -15, out=True); place(chime(), DUR_MAIN + 0.2, -24, out=True)\n" + a[j:]
open(os.path.join(D, "audio.py"), "w").write(a)

n = getattr(C, "NCH", 6); groups = [" ".join(str(k) for k in range(g, min(g + 3, n))) for g in range(0, n, 3)]
run = f"""#!/bin/bash
# render {n} chunks, 3 at a time (memory), then concat + mix voice/music/sfx
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python3 audio.py
for g in {' '.join('"' + g + '"' for g in groups)}; do
  for k in $g; do python3 render.py chunk $k {n} > log_$k.txt 2>&1 & done; wait
done
printf "file 'chunk_%d.mp4'\\n" {' '.join(str(k) for k in range(n))} > chunks.txt
ffmpeg -v error -y -f concat -safe 0 -i chunks.txt -c copy video_only.mp4
DUR=$(python3 -c "from tl import DUR;print(DUR)")
ffmpeg -v error -y -i video_only.mp4 -i voice_cut.wav -i music.wav -i sfx.wav -filter_complex \\
"[1:a]highpass=f=75,afftdn=nr=8:nf=-40:tn=1,equalizer=f=3500:t=q:w=1.2:g=2,acompressor=threshold=-20dB:ratio=2.8:attack=12:release=180:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=8,aresample=48000,asplit=2[v][vsc];\\
[2:a]volume=-19dB[mu];[mu][vsc]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=450[mud];\\
[3:a]volume=0dB[sx];[v][mud][sx]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9,afade=t=out:st=$(python3 -c "print($DUR-0.35)"):d=0.35[a]" \\
-map 0:v -map "[a]" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \\
-c:a aac -b:a 256k -movflags +faststart -shortest out.mp4
echo ALLDONE
"""
open(os.path.join(D, "run.sh"), "w").write(run); os.chmod(os.path.join(D, "run.sh"), 0o755)
print("built", D)
