"""Edit decision list: tightened cuts (intro filler + dead air removed) and source<->output time mapping."""
FPS = 30
SEGS = [(0.92, 5.24), (7.1333, 16.47), (17.2, 72.9), (73.2, 92.0)]   # kept source ranges (s)
FREEZE = 1.4                                                         # freeze-frame tail (s)

FRAMES = []      # output frame -> source frame index
SEG_OF = []      # output frame -> segment index
for k, (a, b) in enumerate(SEGS):
    for f in range(round(a * FPS), round(b * FPS)):
        FRAMES.append(f); SEG_OF.append(k)
N_MAIN = len(FRAMES)
N_FREEZE = round(FREEZE * FPS)
N_OUT = N_MAIN + N_FREEZE
OUT_START = []   # output start time (s) of each segment
acc = 0
for a, b in SEGS:
    OUT_START.append(acc / FPS); acc += round(b * FPS) - round(a * FPS)
CUTS_OUT = OUT_START[1:]                     # output times of the edit points
DUR_MAIN = N_MAIN / FPS
DUR = N_OUT / FPS

def s2o(ts):
    """source time -> output time (None if cut away)"""
    for k, (a, b) in enumerate(SEGS):
        if a <= ts < b + 1e-6: return OUT_START[k] + (round(ts * FPS) - round(a * FPS)) / FPS
    return None

def o2s(to):
    i = min(max(int(round(to * FPS)), 0), N_MAIN - 1); return FRAMES[i] / FPS
