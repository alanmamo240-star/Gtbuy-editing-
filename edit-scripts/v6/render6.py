"""v6 outfit edit: FIT CHECK carried across a cut, tracked product tags, speed ramp, beat-synced transitions,
recap card, CTA + freeze frame.  usage: render6.py chunk K N | preview t1,t2,..."""
import subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw
import typo as T

W, H, FPS = 1080, 1920, 30
N_SRC = 482
FREEZE = 1.0
N_OUT = N_SRC + int(FREEZE * FPS)
ENH = "hqdn3d=1.5:1.1:3:3,cas=0.42:planes=1,eq=contrast=1.04:brightness=0.01:saturation=1.05:gamma=1.03"
CUTS = [0.0, 1.867, 4.0, 6.267, 7.6, 9.633, 10.567, 12.967, 14.667, N_SRC / FPS]
GOLD, WHITE, INK = (255, 200, 80), (255, 255, 255), (16, 16, 18)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def ei(x): x = clamp(x); return x ** 3
def eio(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x, s=1.7): x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def over_full(base, L, m=None):
    a = L[..., 3:4] if m is None else L[..., 3:4] * m
    return base * (1 - a) + L[..., :3] * a

# ---------------------------------------------------------------- time remap (speed ramp on the walk-away shot)
RAMP = (4.0, 6.267, 0.2)
def src_time(to):
    a, b, A = RAMP
    if a <= to < b:
        u = (to - a) / (b - a); return a + (b - a) * (u + A * np.sin(np.pi * u))
    return to
# NOTE f(u)=u+A*sin(pi u): speed 1+A*pi -> 1-A*pi (fast, then slow motion), endpoints preserved

# ---------------------------------------------------------------- tracking
TR = np.load("track.npy")
def _sm(x, k):
    p = np.pad(x, k // 2, mode="edge"); med = np.median(np.lib.stride_tricks.sliding_window_view(p, k), 1)
    p2 = np.pad(med, k // 2, mode="edge"); return np.convolve(p2, np.ones(k) / k, "valid")
# smooth within shots only
for a, b in zip(CUTS[:-1], CUTS[1:]):
    i0, i1 = int(round(a * FPS)), min(int(round(b * FPS)), N_SRC)
    if i1 - i0 > 9:
        for j in range(TR.shape[1]): TR[i0:i1, j] = _sm(TR[i0:i1, j], 9)
def trk(ts):
    f = ts * FPS; i = int(np.clip(np.floor(f), 0, N_SRC - 1)); j = min(i + 1, N_SRC - 1); w = f - np.floor(f)
    return TR[i] * (1 - w) + TR[j] * w
def shot(ts):
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        if a <= ts < b: return a, b
    return CUTS[-2], CUTS[-1]

# ---------------------------------------------------------------- sprites
FIT = T.shadow(T.extrude(T.chrome(T.text_mask("FIT CHECK", "unb", 150, 0.02)), 18, 0.5, 1.0, (26, 26, 32)), 22, 0, 24, 0.45)
CTA = T.shadow(T.over(T.solid(T.text_mask("RATE DEN FIT", "anton", 160, 0.03), WHITE, pad=8), T.outline(T.text_mask("RATE DEN FIT", "anton", 160, 0.03), 4, INK, pad=8)), 20, 0, 16, 0.5)
CTA_S = T.shadow(T.solid(T.text_mask("1–10 IN DIE KOMMENTARE", "grotesk", 38, 0.18), GOLD), 10, 0, 6, 0.6)
LEAKS = []
for p in ("img/leak_a.png", "img/leak_b.png"):
    im = np.asarray(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    LEAKS.append(cv2.GaussianBlur(np.clip((im - np.percentile(im, 30, axis=(0, 1))) / 0.9, 0, 1), (0, 0), 6))

# tags: (category, brand, extra, start, end, track-key, side)
TAGS = [("T-SHIRT", "Zara", None, 2.32, 3.95, "tee", +1),
        ("HOSE", "Gallery Dept", "via GTBuy", 4.32, 6.2, "legs", -1),
        ("CAP", "New York Yankees", None, 6.33, 7.55, "cap", -1),
        ("SCHUHE", "Dior", None, 7.95, 9.58, "feet", +1)]
def tag_point(key, ts):
    top, bot, hx, tx, ty, lx, ly, fx, fy = trk(ts)
    return {"tee": (tx + 20, ty + 10), "legs": (lx - 10, ly), "cap": (hx, top + 150), "feet": (fx, fy - 34)}[key]
_tagcache = {}
def tag_pill(cat, brand, extra):
    k = (cat, brand, extra)
    if k in _tagcache: return _tagcache[k]
    fc, fb, fe = T.font("grotesk", 24), T.font("serifi", 70), T.font("grotesk", 24)
    cw = sum(fc.getlength(c) + 5 for c in cat); bw = fb.getlength(brand); ew = fe.getlength(extra) + 30 if extra else 0
    w = int(max(cw, bw, ew) + 56); h = 150 if extra else 120
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 26, fill=(12, 12, 14, 190), outline=(255, 255, 255, 60), width=2)
    x = 28
    for c in cat: d.text((x, 18), c, font=fc, fill=(255, 255, 255, 170)); x += fc.getlength(c) + 5
    d.text((28, 102), brand, font=fb, fill=(255, 255, 255, 255), anchor="ls")
    if extra:
        d.rounded_rectangle([26, 112, 26 + ew, 140], 14, fill=GOLD + (255,)); d.text((26 + ew / 2, 126), extra, font=fe, fill=INK + (255,), anchor="mm")
    _tagcache[k] = im; return im

def draw_tags(ts, canvas):
    d = ImageDraw.Draw(canvas)
    for cat, brand, extra, t0, t1, key, side in TAGS:
        if not (t0 <= ts <= t1): continue
        out = eio((t1 - ts) / 0.22); x, y = tag_point(key, ts)
        kd = eo((ts - t0) / 0.2); kl = eo((ts - t0 - 0.08) / 0.25); kp = eo((ts - t0 - 0.2) / 0.3)
        rr = 18 * kd * (1 + 0.15 * np.sin((ts - t0) * 8))
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=(255, 255, 255, int(170 * kd * out)), width=3)
        r0 = 9 * kd; d.ellipse([x - r0, y - r0, x + r0, y + r0], fill=(255, 255, 255, int(255 * kd * out)))
        pill = tag_pill(cat, brand, extra); pw, ph = pill.size
        py = min(max(y, 330), 1720)                                     # elbow when the dot is near an edge
        L = 120; ex = x + side * 24
        pts = [(ex, y), (ex + side * 30, py), (ex + side * (30 + L), py)]
        # draw line progressively
        seg = [np.hypot(pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]), np.hypot(pts[2][0] - pts[1][0], 0)]
        Lp = sum(seg) * kl; drawn = [pts[0]]
        for i_, sl in enumerate(seg):
            if Lp <= 0: break
            f = min(1, Lp / max(sl, 1e-3)); drawn.append((pts[i_][0] + (pts[i_ + 1][0] - pts[i_][0]) * f, pts[i_][1] + (pts[i_ + 1][1] - pts[i_][1]) * f)); Lp -= sl
        if len(drawn) > 1: d.line(drawn, fill=(255, 255, 255, int(235 * out)), width=3, joint="curve")
        if kp > 0:
            px = pts[2][0] + (0 if side > 0 else -pw) + side * (1 - kp) * 20
            px = min(max(px, 20), W - pw - 20)
            p2 = pill.copy(); a_ = np.asarray(p2).copy(); a_[..., 3] = (a_[..., 3] * kp * out).astype(np.uint8)
            canvas.alpha_composite(Image.fromarray(a_), (int(px), int(py - ph / 2)))

ROWS = [("CAP", "New York Yankees", None), ("T-SHIRT", "Zara", None), ("HOSE", "Gallery Dept", "via GTBuy"), ("SCHUHE", "Dior", None)]
ROW_T = [13.2, 13.45, 13.96, 14.33]
def recap(ts, canvas):
    t0, t1 = 13.0, 14.62
    if not (t0 <= ts <= t1): return
    a = min(eo((ts - t0) / 0.3), eio((t1 - ts) / 0.2)); pw, ph = 520, 470
    x0 = W - pw - 36 + (1 - eo((ts - t0) / 0.35)) * 80; y0 = 330
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], 34, fill=(12, 12, 14, int(205 * a)), outline=(255, 255, 255, int(50 * a)), width=2)
    d.text((34, 34), "THE FIT", font=T.font("unb", 34), fill=GOLD + (int(255 * a),))
    for i, ((cat, brand, extra), rt) in enumerate(zip(ROWS, ROW_T)):
        if ts < rt: continue
        k = eo((ts - rt) / 0.3); y = 112 + i * 88; xo = (1 - k) * 30
        d.line([(34, y - 12), (pw - 34, y - 12)], fill=(255, 255, 255, int(40 * a * k)), width=2)
        d.text((34 + xo, y + 22), cat, font=T.font("grotesk", 22), fill=(255, 255, 255, int(150 * a * k)), anchor="lm")
        d.text((pw - 34 + xo, y + 26), brand, font=T.font("serifi", 50), fill=(255, 255, 255, int(255 * a * k)), anchor="rm")
        if extra: d.text((pw - 34 + xo, y + 62), extra.upper(), font=T.font("grotesk", 18), fill=GOLD + (int(255 * a * k),), anchor="rm")
    canvas.alpha_composite(im, (int(x0), y0))

# ---------------------------------------------------------------- camera
def camera(ts, to, s_extra=1.0, dx=0.0):
    a, b = shot(ts); top, bot, hx = trk(ts)[:3]
    close = top < 400
    s = (1.0 + 0.035 * eio((to - a) / max(b - a, 0.1))) * (1 + 0.05 * (1 - eo((to - a) / 0.35))) * s_extra
    cx, cy = hx, (top + 260 if close else top + 300)
    M = cv2.getRotationMatrix2D((cx, cy), 0, s)
    M[0, 2] = np.clip(M[0, 2], -(s - 1) * W, 0) if s >= 1 else M[0, 2]; M[1, 2] = np.clip(M[1, 2], -(s - 1) * H, 0) if s >= 1 else M[1, 2]
    M[0, 2] += dx; return M

def transition(to):
    zf, zb, dx, leak = 1.0, 0.0, 0.0, None
    if to < 0.4: k = eo(to / 0.4); zf = 1 + 0.35 * (1 - k); zb = 0.1 * (1 - k)            # opening whip-zoom
    for c, li in [(6.267, 0), (9.633, 1), (14.667, 0)]:                                     # light leaks
        dt = to - c
        if -0.25 < dt < 0.4: leak = (li, (eo((dt + 0.25) / 0.25) if dt < 0 else 1 - eio(dt / 0.4)) * 0.75, dt)
    c = 10.567                                                                              # whip pan
    if c - 0.14 <= to < c: p = ei((to - (c - 0.14)) / 0.14); dx = -W * 0.11 * p; zf *= 1 + 0.24 * p
    if c <= to < c + 0.2: p = 1 - eo((to - c) / 0.2); dx = W * 0.11 * p; zf *= 1 + 0.24 * p
    c = 12.967                                                                              # zoom-through
    if c - 0.16 <= to < c: p = ei((to - (c - 0.16)) / 0.16); zf *= 1 + 0.25 * p; zb = 0.09 * p
    if c <= to < c + 0.22: p = 1 - eo((to - c) / 0.22); zf *= 1 + 0.25 * p; zb = 0.09 * p
    return zf, zb, dx, leak

def zoom_blur(img, cx, cy, amount, n=6):
    acc = np.zeros_like(img)
    for k in range(n):
        M = cv2.getRotationMatrix2D((cx, cy), 0, 1 + amount * k / (n - 1)); acc += cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
    return acc / n
def box_(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=10, eps=2e-3):
    mI, mp = box_(I, r), box_(p, r); a = (box_(I * p, r) - mI * mp) / (box_(I * I, r) - mI * mI + eps); b = mp - a * mI
    return box_(a, r) * I + box_(b, r)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.16 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.46) / (H * 0.62)) ** 2, 0, 1.6) ** 1.3)[..., None]
rng = np.random.default_rng(4)

def render(o, get):
    to = o / FPS; freeze = o >= N_SRC; fz = (o - N_SRC) / FPS if freeze else 0.0
    ts = src_time(to) if not freeze else (N_SRC - 1) / FPS
    f8, m8 = get(ts)
    frame = f8.astype(np.float32) / 255; m = m8.astype(np.float32) / 255
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    m = np.clip(cv2.resize(guided(gs, cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    zf, zb, dx, leak = transition(to) if not freeze else (1 + 0.04 * eo(fz / 0.35), 0, 0, None)
    tcam = to if not freeze else (N_SRC - 1) / FPS
    M = camera(ts, tcam, zf, dx)
    frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    m = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if dx != 0:
        k = int(9 + abs(dx) * 1.1) | 1; ker = np.zeros((1, k), np.float32); ker[0] = 1 / k
        frame = cv2.filter2D(frame, -1, ker); m = cv2.filter2D(m, -1, ker)
    if zb > 0.005:
        top, _, hx = trk(ts)[:3]; frame = zoom_blur(frame, hx, top + 260, zb); m = zoom_blur(np.dstack([m] * 3), hx, top + 260, zb)[..., 0]
    bgk = (1 - m)[..., None]; comp = frame
    if freeze:
        k = eo(fz / 0.3); g = comp.mean(2, keepdims=True); bg = (comp * (1 - 0.75 * k) + g * 0.75 * k) * (1 - 0.3 * k)
        comp = comp * (1 - bgk) + bg * bgk
    # FIT CHECK: slams onto the T-shirt in the close-up, flies up behind the head across the cut
    if 0.12 <= to <= 3.95:
        k = back((to - 0.15) / 0.5, 1.4); move = eio((to - 1.62) / 0.5); out = eio((3.95 - to) / 0.3)
        cy = 1430 + (770 - 1430) * move; sc = (1.6 - 0.6 * clamp(k)) * (1 - 0.18 * move) * (1 + 0.06 * (1 - out))
        L = T.place_canvas(FIT, W, H, 540, cy, sc, rot_x=10 - 4 * move, rot_y=-10 + 14 * eio(to / 3.9), alpha=clamp(eo((to - 0.12) / 0.18)) * out,
                           blur=(1 - clamp(k)) * 8 + 10 * np.sin(np.pi * clamp((to - 1.62) / 0.5)) * 0.6)
        comp = over_full(comp, L, None if to < 1.867 else bgk)
    if freeze:
        k = eo(fz / 0.3); mb = (m > 0.5).astype(np.uint8)
        ring = cv2.GaussianBlur(cv2.dilate(mb, np.ones((23, 23), np.uint8)).astype(np.float32) - mb, (0, 0), 1.2)[..., None] * k
        comp = comp * (1 - ring) + ring
    if leak is not None:
        li, a, dt = leak; comp = 1 - (1 - comp) * (1 - np.roll(LEAKS[li], int(dt * 500 * (1 if li == 0 else -1)), axis=1) * a)
    comp = comp * VIG
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not freeze: draw_tags(ts, canvas); recap(ts, canvas)
    U = np.asarray(canvas).astype(np.float32) / 255
    if U[..., 3].max() > 0: comp = over_full(comp, U)
    if to >= 14.7:                                                         # CTA on the torso + freeze frame
        tc = to; k = back((tc - 14.72) / 0.45, 1.4)
        comp = over_full(comp, T.place_canvas(CTA, W, H, 540, 1400, 1.3 - 0.3 * clamp(k), rot_x=(1 - clamp(k)) * 40, alpha=clamp(eo((tc - 14.7) / 0.2))))
        if tc > 15.05: k2 = eo((tc - 15.05) / 0.35); comp = over_full(comp, T.place_canvas(CTA_S, W, H, 540, 1530 + (1 - k2) * 12, 1.0, alpha=k2))
    comp = comp + rng.normal(0, 0.01, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if freeze and fz > FREEZE - 0.35: comp *= clamp((FREEZE - fz) / 0.35)
    return (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)

def loader(i0, i1):
    """preload enhanced source frames + mattes [i0, i1) and return a getter with frame blending for slow motion"""
    n = i1 - i0
    dv = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i0 / FPS:.4f}", "-i", "input_cfr.mov", "-vf", ENH, "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    dm = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{i0 / FPS:.4f}", "-i", "mask.mkv", "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    F = np.frombuffer(dv, np.uint8).reshape(-1, H, W, 3); Mk = np.frombuffer(dm, np.uint8).reshape(-1, H, W)
    def get(ts):
        f = ts * FPS - i0; a = int(np.clip(np.floor(f), 0, len(F) - 1)); b = min(a + 1, len(F) - 1); w = f - np.floor(f)
        if w < 0.08 or a == b: return F[a], Mk[a]
        if w > 0.92: return F[b], Mk[b]
        return (F[a] * (1 - w) + F[b] * w).astype(np.uint8), (Mk[a] * (1 - w) + Mk[b] * w).astype(np.uint8)
    return get

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        get = loader(0, N_SRC)
        for to in [float(x) for x in sys.argv[2].split(",")]:
            Image.fromarray(render(int(round(to * FPS)), get)).save(f"frames/p_{to:05.2f}.jpg", quality=92)
        print("preview done")
    else:
        K, NC = int(sys.argv[2]), int(sys.argv[3]); a, b = K * N_OUT // NC, (K + 1) * N_OUT // NC
        srcs = [src_time(o / FPS) if o < N_SRC else (N_SRC - 1) / FPS for o in range(a, b)]
        i0 = max(int(np.floor(min(srcs) * FPS)) - 1, 0); i1 = min(int(np.ceil(max(srcs) * FPS)) + 2, N_SRC)
        get = loader(i0, i1)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "13", "-pix_fmt", "yuv420p", f"chunk_{K}.mp4"], stdin=subprocess.PIPE)
        for o in range(a, b):
            enc.stdin.write(render(o, get).tobytes())
            if (o - a) % 30 == 0: print(f"chunk {K}: {o - a}/{b - a}", flush=True)
        enc.stdin.close(); enc.wait(); print(f"chunk {K} done")
