"""Edit decision list: dead air removed (jump cuts) + per-shot framing, source<->output time mapping."""
FPS = 30
SIL = [(5.48, 6.09), (20.97, 21.64), (26.63, 27.27), (30.68, 31.11), (33.08, 33.75), (38.22, 38.83), (40.28, 40.74),
       (42.71, 43.31), (48.05, 48.78), (51.72, 52.40), (56.89, 57.38), (58.15, 58.71), (61.96, 62.58), (68.15, 68.76)]
END = 69.6
SEGS = []; a = 0.0
for s, e in SIL:
    SEGS.append((a, s + 0.1)); a = e - 0.1
SEGS.append((a, END))
SEGS = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in SEGS]
# framing per shot: zoom (1 = full body) ; dx = horizontal offset of the person on screen
ZOOM = [1.0, 1.28, 1.0, 1.36, 1.14, 1.32, 1.0, 1.3, 1.12, 1.36, 1.0, 1.26, 1.12, 1.36, 1.0]
FREEZE = 1.3
FRAMES, SEG_OF = [], []
for k, (a, b) in enumerate(SEGS):
    for f in range(round(a * FPS), round(b * FPS)): FRAMES.append(f); SEG_OF.append(k)
N_MAIN = len(FRAMES); N_FREEZE = round(FREEZE * FPS); N_OUT = N_MAIN + N_FREEZE
OUT_START = []; acc = 0
for a, b in SEGS: OUT_START.append(acc / FPS); acc += round(b * FPS) - round(a * FPS)
CUTS_OUT = OUT_START[1:]; DUR_MAIN = N_MAIN / FPS; DUR = N_OUT / FPS
def s2o(ts):
    for k, (a, b) in enumerate(SEGS):
        if a - 1e-6 <= ts < b + 1e-6: return OUT_START[k] + (ts - a)
    # inside a removed gap -> snap to next segment start
    for k, (a, b) in enumerate(SEGS):
        if ts < a: return OUT_START[k]
    return DUR_MAIN
def o2s(to):
    i = min(max(int(round(to * FPS)), 0), N_MAIN - 1); return FRAMES[i] / FPS
if __name__ == "__main__":
    print(len(SEGS), len(ZOOM), "main", round(DUR_MAIN, 2), "total", round(DUR, 2))
    for k, (a, b) in enumerate(SEGS): print(k, a, b, round(OUT_START[k], 2), ZOOM[k])
