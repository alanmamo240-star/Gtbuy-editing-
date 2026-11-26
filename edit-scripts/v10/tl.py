"""Edit decision list for v10 (Top Schuhe): dead air removed, source<->output time mapping."""
FPS = 30
SIL = [(1.03, 1.70), (3.65, 4.07), (5.00, 5.49)]
END = 7.05
SEGS = []; a = 0.2
for s, e in SIL:
    SEGS.append((a, s + 0.1)); a = e - 0.1
SEGS.append((a, END))
SEGS = [(round(a * FPS) / FPS, round(b * FPS) / FPS) for a, b in SEGS]
FREEZE = 1.8
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
    for k, (a, b) in enumerate(SEGS):
        if ts < a: return OUT_START[k]
    return DUR_MAIN
def o2s(to):
    i = min(max(int(round(to * FPS)), 0), N_MAIN - 1); return FRAMES[i] / FPS
if __name__ == "__main__":
    print("main", round(DUR_MAIN, 2), "total", round(DUR, 2))
    for k, (a, b) in enumerate(SEGS): print(k, a, b, round(OUT_START[k], 2))
