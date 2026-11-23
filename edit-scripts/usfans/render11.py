"""v11 monochrome fit-check, built from v7 by build11.py. Original v7 doc:
v7 Fit-Check (Jacke Maison Margiela via USFans / T-Shirt Zara / Hose Zara / Schuhe Dior via USFans).
Keeps the creator's own song and cut timing (117.5 BPM), 'crazy' red/chrome/white look: beat-pulsed kinetic type,
red/black duotone strobe scene, invert frame, VIA USFANS ticker bands behind the body, label card, red studio.
Usage: python render7.py <out_start_frame> <out_end_frame> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib5 import *
import lib5

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
DUR = 14.0
NSRC = 359
RED = np.array([0.05, 0.05, 0.06], np.float32)   # monochrome: accent is ink black
WHITE = np.array([250, 250, 246], np.float32) / 255
BEATS = [0.09, 1.0, 2.0, 3.0, 3.99, 4.99, 5.8, 6.78, 7.78, 8.75, 9.8, 10.75, 11.75]
def pulse(t, tau=0.13):
    d = [t - b for b in BEATS if t >= b]
    return math.exp(-min(d) / tau) if d else 0.0

SC = [
    (1, 0.00, 1.20, [(0.00, 0.00), (1.20, 1.18)], (0, 35)),
    (2, 1.20, 2.57, [(1.20, 1.21), (1.55, 1.38), (2.57, 2.40)], (36, 76)),       # short 0.5x ramp, tail trimmed
    (3, 2.57, 4.40, [(2.57, 2.58), (4.40, 4.38)], (77, 131)),
    (4, 4.40, 6.03, [(4.40, 4.41), (6.03, 6.01)], (132, 180)),
    (5, 6.03, 7.93, [(6.03, 6.04), (7.93, 7.91)], (181, 237)),
    (6, 7.93, 9.03, [(7.93, 7.94), (9.03, 9.01)], (238, 270)),
    (7, 9.03, 11.13, [(9.03, 9.04), (11.13, 11.11)], (271, 333)),
    (8, 11.13, 14.00, [(11.13, 11.14), (11.30, 11.31), (14.00, 11.31)], (334, 358)),
]
def scene_at(t):
    for sc in SC:
        if sc[1] <= t < sc[2]: return sc
    return SC[-1]
def src_frame(sc, t):
    xs, ys = zip(*sc[3]); return float(np.clip(np.interp(t, xs, ys) * FPS, sc[4][0], sc[4][1]))

# ---- pose
P = json.load(open("pose.json"))
LM = np.full((NSRC, 33, 3), np.nan, np.float32)
for i, p in enumerate(P[:NSRC]):
    if p is not None: LM[i] = np.array(p, np.float32)
CL = [0, 36, 77, 132, 181, 238, 271, 334, NSRC]
for a, b in zip(CL[:-1], CL[1:]):
    seg = LM[a:b]
    for k in range(33):
        for c in range(2):
            v = seg[:, k, c]; ok = ~np.isnan(v)
            if ok.sum() == 0: continue
            v = np.interp(np.arange(len(v)), np.where(ok)[0], v[ok])
            ker = np.exp(-0.5 * (np.arange(-9, 10) / 3.0) ** 2); ker /= ker.sum()
            seg[:, k, c] = np.convolve(np.pad(v, 9, mode="edge"), ker, "valid")
    LM[a:b] = seg
def lm(f, k):
    i = int(f); fr = f - i; j = min(i + 1, NSRC - 1); return LM[i, k, :2] * (1 - fr) + LM[j, k, :2] * fr
def mid(f, a, b): return (lm(f, a) + lm(f, b)) / 2
def anchor(kind, f):
    if kind == "chest": sh = mid(f, 11, 12); hp = mid(f, 23, 24); return sh + 0.30 * (hp - sh)
    if kind == "back": sh = mid(f, 11, 12); hp = mid(f, 23, 24); return sh + 0.22 * (hp - sh)
    if kind == "thigh":
        h, k = (23, 25) if lm(f, 23)[0] > lm(f, 24)[0] else (24, 26); return lm(f, h) * 0.45 + lm(f, k) * 0.55
    if kind == "foot":
        a, fi = (27, 31) if lm(f, 27)[0] > lm(f, 28)[0] else (28, 32); return (lm(f, a) + lm(f, fi)) / 2
    if kind == "feet": return (lm(f, 27) + lm(f, 28) + lm(f, 31) + lm(f, 32)) / 4

# ---- camera
def cam(sc, t, f):
    sid, o0, o1 = sc[0], sc[1], sc[2]; u = clamp((t - o0) / (o1 - o0)); rot = 0.0; oob = False
    bp = 1 + 0.02 * pulse(t)
    if sid == 1:      # close lean-in (tee), hook
        s = (1.06 + 0.34 * (1 - ease_out(t / 0.5)) + 0.03 * u) * bp
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.52 * H)
    elif sid == 2:    # full front, jacket
        s = 1.12 + 0.06 * ease_io(u)
        if t > 2.43: s *= 1 + 0.45 * ease_in((t - 2.43) / 0.14)
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
    elif sid == 3:    # back close, jacket
        s = 1.05 + 0.06 * ease_io(u)
        if t < 2.92: s *= 1 + 0.42 * (1 - ease_out((t - 2.57) / 0.35))
        n = mid(f, 11, 12); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1] - 100); sp = (W / 2, 0.45 * H)
        if t > 4.27: rot = 14 * ease_in((t - 4.27) / 0.13)
    elif sid == 4:    # back/side full, tee
        s = 1.10 + 0.06 * ease_io(u)
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
        if t < 4.57: rot = -14 * (1 - ease_out((t - 4.40) / 0.17))
    elif sid == 5:    # side, looking at shoes -> white studio
        h = mid(f, 23, 24); c = (h[0], h[1] - 40)
        s = 1.08 + 0.08 * ease_io(u)
        k = ease_io((t - 6.30) / 0.5)
        sx = W / 2 + (min(W - W / (2 * s), max(W / (2 * s), c[0])) - c[0]) * s * (1 - k)
        sp = (sx, 0.52 * H); oob = t > 6.15
    elif sid == 6:    # back walking, B/W strobe
        s = (1.10 + 0.08 * ease_io(u)) * bp
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
    elif sid == 7:    # close lean, jacket
        s = (1.06 + 0.30 * (1 - ease_out((t - 9.03) / 0.3)) + 0.04 * u) * bp
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.50 * H)
    else:
        s = 1.08 + 0.06 * ease_io(clamp((t - 11.13) / 1.0))
        h = mid(f, 11, 12); c = (W / 2 + (h[0] - W / 2) * 0.5, h[1] + 200); sp = (W / 2, 0.5 * H)
    return s, c, sp, oob, rot
def cam_M(s, c, sp, oob, rot):
    x0 = c[0] - sp[0] / s; y0 = c[1] - sp[1] / s
    if not oob: x0 = clamp(x0, 0, W - W / s); y0 = clamp(y0, 0, H - H / s)
    M = np.float32([[s, 0, -s * x0], [0, s, -s * y0]])
    if abs(rot) > 0.01:
        R = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1 + abs(rot) / 40)
        M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return M
def apply(M, p): return np.array([M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2], M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2]])

# ---- source frames
need = set()
for j in range(A, B):
    t = j / FPS; sc = scene_at(t); f = src_frame(sc, t); need.update({int(f), min(int(f) + 1, sc[4][1])})
lo, hi = min(need), max(need)
def load(path, fmt, ch):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select='between(n\\,{lo}\\,{hi})'", "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", fmt, "-"], stdout=subprocess.PIPE)
    out = {}
    for i in range(lo, hi + 1):
        b = p.stdout.read(W * H * ch)
        if len(b) < W * H * ch: break
        if i in need: out[i] = np.frombuffer(b, np.uint8).reshape((H, W, ch) if ch > 1 else (H, W))
    p.stdout.close(); p.wait(); return out
FR = load("enh.mov", "rgb24", 3); MK = load("mask.mkv", "gray", 1)
_flow = {}
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def flows(i):
    if i not in _flow:
        for k_ in [k for k in _flow if k < i - 1]: del _flow[k_]
        g0 = cv2.cvtColor(cv2.resize(FR[i], (540, 960)), cv2.COLOR_RGB2GRAY); g1 = cv2.cvtColor(cv2.resize(FR[i + 1], (540, 960)), cv2.COLOR_RGB2GRAY)
        _flow[i] = (cv2.resize(DIS.calc(g0, g1, None), (W, H)) * 2, cv2.resize(DIS.calc(g1, g0, None), (W, H)) * 2)
    return _flow[i]
def frame_at(sc, f):
    i = int(f); fr = f - i
    if fr < 0.04 or i + 1 > sc[4][1] or (i + 1) not in FR: return FR[i].astype(np.float32) / 255, MK[i].astype(np.float32) / 255
    if fr > 0.96: return FR[i + 1].astype(np.float32) / 255, MK[i + 1].astype(np.float32) / 255
    f01, f10 = flows(i)
    m0 = (GX - fr * f01[..., 0], GY - fr * f01[..., 1]); m1 = (GX - (1 - fr) * f10[..., 0], GY - (1 - fr) * f10[..., 1])
    a0 = cv2.remap(FR[i], *m0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    a1 = cv2.remap(FR[i + 1], *m1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k0 = cv2.remap(MK[i], *m0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k1 = cv2.remap(MK[i + 1], *m1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    return (a0 * (1 - fr) + a1 * fr) / 255, (k0 * (1 - fr) + k1 * fr) / 255

# ---- typography (red / chrome / white)
_cache = {}
def chrome_cached(key, M_, depth, sw):
    k = (key, None if sw is None else round(round(sw / 0.05) * 0.05, 2))
    if k not in _cache: _cache[k] = sprite_chrome(M_, depth=depth, sweep=k[1])
    return _cache[k]
def solid3d(M_, face_top, face_bot, ext_col, depth=20):
    P_ = depth + 40; Mp = np.pad(M_, ((P_ // 2, P_), (P_ // 2, P_))); hh, ww = Mp.shape
    ext = np.zeros_like(Mp)
    for k in range(1, depth + 1): ext = np.maximum(ext, np.roll(np.roll(Mp, int(k * 0.6), 1), k, 0))
    shadow = cv2.GaussianBlur(np.roll(np.roll(Mp, depth + 14, 0), 10, 1), (0, 0), 18) * 0.55
    ys = np.where(Mp.max(1) > .5)[0]; y0, y1 = ys[0], ys[-1]
    g = np.clip((np.arange(hh) - y0) / max(y1 - y0, 1), 0, 1)[:, None, None]
    face = np.array(face_top, np.float32) / 255 * (1 - g) + np.array(face_bot, np.float32) / 255 * g
    face = face + np.clip(Mp - np.roll(Mp, 3, 0), 0, 1)[..., None] * 0.35
    rgb = np.zeros((hh, ww, 3), np.float32); a = shadow * (1 - ext); ec = np.array(ext_col, np.float32) / 255
    rgb = rgb * (1 - ext[..., None]) + ec * ext[..., None]; a = a * (1 - ext) + ext
    rgb = rgb * (1 - Mp[..., None]) + np.clip(face, 0, 1) * Mp[..., None]; a = a * (1 - Mp) + Mp
    return rgb, a, (P_ // 2, P_ // 2)

S = {}
def tag_sprite(item, brand, gt):
    fi, fb, fg = font("SpaceGrotesk", 26, 700), font("Archivo", 46, 900, 112), font("SpaceGrotesk", 24, 700)
    wb = fb.getlength(brand); pw = int(max(wb, 200) + 52); ph = 128 + (52 if gt else 0); pad = 40
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 8, fill=(250, 250, 246, 245))
    d.rectangle([pad, pad, pad + pw, pad + 8], fill=(20, 20, 22, 255))
    x = pad + 24
    for ch_ in item: d.text((x, pad + 38), ch_, font=fi, fill=(20, 20, 22, 255), anchor="lm"); x += fi.getlength(ch_) + 3
    d.text((pad + 22, pad + 88), brand, font=fb, fill=(12, 12, 14, 255), anchor="lm")
    if gt:
        gw = fg.getlength("via USFans") + 44
        d.rounded_rectangle([pad + 22, pad + 124, pad + 22 + gw, pad + 164], 6, fill=(12, 12, 14, 255))
        d.text((pad + 22 + gw / 2, pad + 144), "via USFans", font=fg, fill=(250, 250, 246, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 14) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
def label_card():
    """numbered label motif (0-23, one circled) with four corner stitches"""
    w, h, pad = 600, 200, 40
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([pad, pad, pad + w, pad + h], fill=(250, 250, 246, 245))
    for cx_, cy_ in [(pad + 18, pad + 18), (pad + w - 18, pad + 18), (pad + 18, pad + h - 18), (pad + w - 18, pad + h - 18)]:
        d.line([(cx_ - 7, cy_), (cx_ + 7, cy_)], fill=(40, 40, 44, 255), width=3)
    f = font("SpaceGrotesk", 27, 500)
    for n in range(24):
        r, c = divmod(n, 12); x = pad + 40 + c * 47; y = pad + 72 + r * 64
        d.text((x, y), str(n), font=f, fill=(20, 20, 22, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 16) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
S["label"] = label_card()
ROWS = [("Jacke", "Maison Margiela", True), ("T-Shirt", "Zara", False), ("Hose", "Zara", False), ("Schuhe", "Dior", True)]
def row_sprite(item, brand, gt):
    f1, f2, fg = font("Archivo", 50, 800, 110), font("InstrumentSerif-Italic", 60), font("SpaceGrotesk", 24, 700)
    pad = 30; w = 800; im = Image.new("RGBA", (w + 2 * pad, 84 + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((pad, pad + 42), item, font=f1, fill=(250, 250, 246, 255), anchor="lm")
    d.text((pad + f1.getlength(item) + 20, pad + 44), "— " + brand, font=f2, fill=(250, 250, 246, 215), anchor="lm")
    if gt:
        gw = fg.getlength("USFans") + 30; gx = pad + w - gw
        d.rounded_rectangle([gx, pad + 22, gx + gw, pad + 62], 6, fill=(20, 20, 22, 255))
        d.text((gx + gw / 2, pad + 42), "USFans", font=fg, fill=(255, 255, 255, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3], (pad, pad)
ROW_S = [row_sprite(*r) for r in ROWS]

def ticker_band(text, bg, fg, h, offset):
    f = font("Archivo", int(h * 0.62), 900, 125)
    unit = Image.new("RGB", (int(f.getlength(text)) + 60, h), tuple(int(c * 255) for c in bg))
    ImageDraw.Draw(unit).text((30, h / 2), text, font=f, fill=tuple(int(c * 255) for c in fg), anchor="lm")
    u = np.asarray(unit).astype(np.float32) / 255
    reps = int(np.ceil((W * 1.6) / u.shape[1])) + 2
    strip = np.concatenate([u] * reps, 1)
    x0 = int(offset) % u.shape[1]
    return strip[:, x0:x0 + int(W * 1.5)]

def draw_line(L, p0, p1, alpha, col=WHITE, w=3, dot=True):
    m = np.zeros((H, W), np.float32)
    cv2.line(m, tuple(int(v) for v in p0), tuple(int(v) for v in p1), 1.0, w, cv2.LINE_AA)
    if dot: cv2.circle(m, tuple(int(v) for v in p1), 10, 1.0, -1, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += col * m[..., None]; L[1] *= (1 - m); L[1] += m
def scribble_circle(L, c, rx, ry, prog, alpha, col=RED, w=7, seed=0):
    if prog <= 0: return
    r_ = np.random.default_rng(seed); m = np.zeros((H, W), np.float32); pts = []
    for k in range(80):
        u = k / 79 * prog * 1.12; a_ = -math.pi / 2 + u * 2 * math.pi
        jit = 1 + 0.04 * math.sin(u * 9 + seed)
        pts.append((c[0] + rx * jit * math.cos(a_), c[1] + ry * jit * math.sin(a_)))
    cv2.polylines(m, [np.int32(pts)], False, 1.0, w, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += col * m[..., None]; L[1] *= (1 - m); L[1] += m

def tags(t, f, M, front, TL, t_end):
    for it, br, gt, t0, kind, side, ty in TL:
        a = win(t, t0, t_end, 0.22, 0.1)
        if a <= 0: continue
        p = apply(M, anchor(kind, f)); sp = S["tag_" + it + br]; tw = sp[1].shape[1] - 80
        k = ease_out((t - t0) / 0.35)
        if side == "L":
            place(front, sp, 50 - (1 - k) * 60, ty, anchor=(40 / sp[1].shape[1], 0.5), alpha=a, rot=-2); e = (50 + tw + 6, ty - 10)
        else:
            place(front, sp, W - 50 + (1 - k) * 60, ty, anchor=(1 - 40 / sp[1].shape[1], 0.5), alpha=a, rot=2); e = (W - 50 - tw - 6, ty - 10)
        prog = ease_io((t - t0 - 0.05) / 0.3)
        draw_line(front, e, (e[0] + (p[0] - e[0]) * prog, e[1] + (p[1] - e[1]) * prog), a, col=RED, dot=prog > .95)

# ---- per-scene graphics (monochrome: black / white / chrome)
INKC = np.array([0.05, 0.05, 0.06], np.float32)
FIT_M = tmask("FIT", font("Unbounded", 330, 900), 8)[0]
S["fit_echo"] = sprite_outline(FIT_M, WHITE, 3)
S["check"] = sprite_fill(tmask("CHECK", font("Archivo", 120, 900, 125), 26)[0], WHITE, shadow=0.6, sblur=10, stroke=(INKC, 5))
MAI_M = tmask("MAISON", font("Anton-Regular", 200), 16)[0]; MAR_M = tmask("MARGIELA", font("Anton-Regular", 200), 16)[0]
S["c_jacke"] = chip("Jacke  ·  via USFans", bg=WHITE, fg=INKC, size=44)
S["zara_o"] = sprite_outline(tmask("ZARA", font("Archivo", 260, 900, 125), 10)[0], WHITE, 4)
S["teehose"] = chip("T-Shirt  &  Hose  ·  Zara", bg=WHITE, fg=INKC, size=42)
S["dior"] = sprite_fill(tmask("Dior", font("InstrumentSerif-Regular", 380), 4)[0], INKC, shadow=0.25, sblur=24, soff=(20, 10))
S["c_schuhe"] = chip("Schuhe  ·  via USFans", bg=INKC, fg=WHITE, size=44)
AB_M = tmask("ALL BLACK", font("Unbounded", 118, 900), 6)[0]
S["every"] = sprite_outline(tmask("EVERYTHING", font("Archivo", 86, 900, 118), 10)[0], WHITE, 3)
S["best"] = sprite_fill(tmask("BESTELLT  ÜBER", font("SpaceGrotesk", 36, 700), 9)[0], WHITE, shadow=0.0)
GTB_M = tmask("USFans", font("Unbounded", 170, 900), 2)[0]
S["link"] = link_card(size=50)
STUDIO = load_img("img/studio.png"); POOL_Y = 0.80
TAGS2 = [("JACKE", "MAISON MARGIELA", True, 1.35, "chest", "L", 640), ("HOSE", "ZARA", False, 1.65, "thigh", "R", 1230),
         ("SCHUHE", "DIOR", True, 1.95, "foot", "L", 1520)]
for it, br, gt, *_ in TAGS2: S["tag_" + it + br] = tag_sprite(it, br, gt)

def graphics(t, sc, f, M, back, front):
    sid = sc[0]; bp = pulse(t)
    if sid == 1:
        a = win(t, 0.05, 1.17, 0.2, 0.08)
        k = back_out((t - 0.05) / 0.4, 1.8)
        for dy, al in ((150, 0.35), (80, 0.6)):
            place(back, S["fit_echo"], W / 2, 170 + dy * (0.6 + 0.4 * bp), s=1.0 + 0.04 * bp, alpha=a * al * clamp((t - 0.2) / 0.2))
        sw = (t - 0.3) / 0.8 if 0.3 <= t <= 1.1 else None
        place(back, chrome_cached("fit", FIT_M, 22, sw), W / 2, 170, s=(1.5 - 0.5 * k) * (1 + 0.04 * bp), alpha=clamp(t / 0.06) * a, blur=max(0, 1 - t / 0.2) * 8)
        k2 = ease_out((t - 0.3) / 0.45)
        place(back, S["check"], W / 2, 350, s=(1.25 - 0.25 * k2) * 0.85, alpha=a * k2)
    if sid == 2: tags(t, f, M, front, TAGS2, 2.50)
    if sid == 3:
        a = win(t, 2.75, 4.30, 0.3, 0.1); k = ease_out((t - 2.75) / 0.5)
        sw = (t - 3.0) / 0.9 if 3.0 <= t <= 3.9 else None
        place(back, chrome_cached("mai", MAI_M, 14, sw), W / 2 - (1 - k) * 250, 230, alpha=a)
        place(back, chrome_cached("mar", MAR_M, 14, sw), W / 2 + (1 - k) * 250, 440, alpha=a)
        a2 = win(t, 3.05, 4.30, 0.25, 0.1); k2 = ease_out((t - 3.05) / 0.45)
        place(back, S["label"], 345, 700 - (1 - k2) * 60, alpha=a2, rot=-3)
        scribble_circle(back, (345 - 340 + 40 + 40 + 10 * 47, 700 - 140 + 40 + 72 + 6), 32, 30, ease_io((t - 3.35) / 0.3), a2, col=INKC, w=5, seed=3)
        a3 = win(t, 3.55, 4.30, 0.2, 0.1)
        if a3: place(front, S["c_jacke"], W / 2, 1300, s=back_out((t - 3.55) / 0.3, 2.0), alpha=a3)
    if sid == 4:
        a = win(t, 4.50, 5.95, 0.3, 0.1)
        for r in range(3):
            y = 380 + r * 330; dx = ((t - 4.4) * (90 if r % 2 == 0 else -90)) + (r - 1) * 140
            place(back, S["zara_o"], W / 2 + dx, y, alpha=a * (0.9 - 0.2 * r), s=1.0 + 0.03 * bp)
        a2 = win(t, 4.85, 5.95, 0.2, 0.1)
        if a2: place(front, S["teehose"], W / 2, 1560, s=back_out((t - 4.85) / 0.3, 2.0), alpha=a2)
    if sid == 5:
        a = win(t, 6.35, 7.88, 0.35, 0.1); k = ease_out((t - 6.35) / 0.55)
        place(back, S["dior"], W / 2, 640 + (1 - k) * 80, s=0.9 + 0.1 * k, alpha=a)
        p = apply(M, anchor("feet", f))
        scribble_circle(front, p + np.array([0, -10.0]), 190, 90, ease_io((t - 6.75) / 0.4), a, col=INKC, w=7, seed=4)
        a2 = win(t, 7.05, 7.88, 0.2, 0.1)
        if a2: place(front, S["c_schuhe"], W / 2, min(p[1] + 190, 1640), s=back_out((t - 7.05) / 0.3, 2.0), alpha=a2)
    if sid == 7:
        a = win(t, 9.20, 11.05, 0.35, 0.15); k = ease_out((t - 9.20) / 0.55)
        sw = (t - 9.5) / 0.9 if 9.5 <= t <= 10.4 else None
        place(back, chrome_cached("ab", AB_M, 16, sw), W / 2, 210, rx=-70 * (1 - k), alpha=a, s=1 + 0.03 * bp)
        a2 = win(t, 9.75, 11.05, 0.3, 0.15)
        if a2: place(back, S["every"], W / 2, 380, alpha=a2, s=1.1 - 0.1 * ease_out((t - 9.75) / 0.4))

def tickers(t, back):
    a = win(t, 7.96, 9.00, 0.2, 0.1)
    if a <= 0: return
    k = ease_out((t - 7.96) / 0.3)
    for text, bg, fg, y, speed, ang in (("VIA USFANS   •   MAISON MARGIELA   •   DIOR   •   ", WHITE, INKC, 760, 560, -7),
                                        ("ALL BLACK   •   ALL BLACK   •   ", INKC, WHITE, 1050, -460, 5)):
        band = ticker_band(text, bg, fg, 130, (t - 7.9) * speed + 2000)
        hh, ww = band.shape[:2]
        place(back, (band, np.ones((hh, ww), np.float32), (0, 0)), W / 2 + (1 - k) * (W if speed > 0 else -W), y, rot=ang, alpha=a)

def endcard(t, comp):
    if t < 11.30: return comp
    L = new_layer()
    k0 = ease_out((t - 11.30) / 0.5)
    k = ease_out((t - 11.45) / 0.4); place(L, S["best"], W / 2, 300 - (1 - k) * 20, alpha=k)
    k2 = ease_out((t - 11.55) / 0.5)
    place(L, chrome_cached("gtb", GTB_M, 14, (t - 12.0) / 0.9 if 12.0 <= t <= 12.9 else None), W / 2, 440, s=0.9 + 0.1 * k2, rx=-60 * (1 - k2), alpha=clamp((t - 11.55) / .1))
    for n, sp in enumerate(ROW_S):
        t0 = 11.85 + n * 0.17; kk = ease_out((t - t0) / 0.3)
        if kk <= 0: continue
        y = 760 + n * 100
        place(L, check_sprite(26, clamp((t - t0) / 0.22)), 140, y, s=back_out((t - t0) / 0.3, 2.0), alpha=kk)
        place(L, sp, 190 + (1 - kk) * 30, y, anchor=(30 / sp[1].shape[1], 0.5), alpha=kk)
    k4 = ease_out((t - 12.6) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1260, s=back_out((t - 12.6) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

# ---- compositing
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.26 * np.clip(np.sqrt(((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .46) / (H * .72)) ** 2) - .45, 0, 1) ** 1.5)[..., None]
def refine(frame, m):
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)
    return np.clip(cv2.resize(guided(gs, ms), (W, H)), 0, 1)
def studio(t, comp, cm, M, f):
    feet = apply(M, (lm(f, 27) + lm(f, 28)) / 2); s = M[0, 0]
    z = 1.22 * (1 + (s - 1) * 0.45)
    oy = (feet[1] + 30 - (H / 2 + (POOL_Y - 0.5) * H * z)) / H; ox = (feet[0] - W / 2) / W * 0.8
    bg = np.clip(cover(STUDIO, W, H, z, ox, oy) * 1.02, 0, 1)
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(feet[0]), int(feet[1] + 20)), (int(150 * s), int(26 * s)), 0, 0, 360, 1.0, -1)
    bg = bg * (1 - cv2.GaussianBlur(sh, (0, 0), 18 * s)[..., None] * 0.6)
    r = ease_out((t - 6.03) / 0.40) * 2400
    d = np.sqrt((XX - feet[0]) ** 2 + ((YY - feet[1]) * 1.6) ** 2)
    circ = np.clip((r - d) / 40, 0, 1); ring = np.exp(-((d - r) / 14) ** 2) * (r < 2300) * 0.9
    cmc = cv2.GaussianBlur(np.clip((cv2.erode(cm, np.ones((5, 5), np.uint8)) - 0.25) / 0.6, 0, 1), (0, 0), 1.2)
    band = np.clip(cm - cmc, 0, 1) * circ
    comp = comp * (1 - 0.65 * band[..., None])
    cm2 = cmc * circ + cm * (1 - circ)
    bm = ((1 - cm2) * circ)[..., None]
    comp = comp * (1 - bm) + bg * bm
    # red rim light on the person's edge, as if lit by the red room
    rim = np.clip(cv2.GaussianBlur(1 - cm2, (0, 0), 6) * cm2 * 2.2, 0, 1) * circ * 0.35
    comp = comp * (1 - rim[..., None] * 0.4) + WHITE * rim[..., None] * 0.4
    return comp * (1 - ring[..., None] * 0.8) + INK * ring[..., None] * 0.8, cm2

def duotone(img, amt):
    g = img @ np.array([0.3, 0.59, 0.11], np.float32)
    g = np.clip((g - 0.08) / 0.75, 0, 1) ** 0.9
    dark = np.array([0.04, 0.0, 0.01], np.float32); lite = np.array([1.0, 0.22, 0.24], np.float32)
    d = dark + (lite - dark) * g[..., None]
    d = np.where(g[..., None] > 0.82, d + (g[..., None] - 0.82) * 4.0, d)  # highlights burn to white
    return img * (1 - amt) + np.clip(d, 0, 1) * amt

def render_shot(t, sc):
    f = src_frame(sc, t)
    frame, m = frame_at(sc, f); m = refine(frame, m)
    s, c, sp, oob, rot = cam(sc, t, f)
    M = cam_M(s, c, sp, oob, rot)
    zb = 0.0
    if t < 0.3: zb = 1 - t / 0.3
    if 2.43 <= t < 2.57: zb = ease_in((t - 2.43) / 0.14)
    if 2.57 <= t < 2.82: zb = 1 - ease_out((t - 2.57) / 0.25)
    if 9.03 <= t < 9.25: zb = 1 - ease_out((t - 9.03) / 0.22)
    dx = 0.0
    if 1.08 <= t < 1.20: dx = -ease_in((t - 1.08) / 0.12) * W * 0.6
    if 1.20 <= t < 1.34: dx = (1 - ease_out((t - 1.20) / 0.14)) * W * 0.6
    M[0, 2] += dx
    if zb > 0.02:
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(6):
            sk = 1 + zb * 0.07 * k / 5
            Mk = M.copy(); Mk[:, :2] *= sk; Mk[0, 2] = M[0, 2] * sk + W / 2 * (1 - sk); Mk[1, 2] = M[1, 2] * sk + H * .45 * (1 - sk)
            acc += cv2.warpAffine(frame, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cf = acc / 6
    else:
        cf = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    if abs(rot) > 2:
        acc = np.zeros_like(cf)
        for k in range(5):
            acc += cv2.warpAffine(cf, cv2.getRotationMatrix2D((W / 2, H / 2), (k - 2) * rot * 0.12, 1), (W, H), borderMode=cv2.BORDER_REFLECT)
        cf = acc / 5
    cm = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT if oob else cv2.BORDER_REFLECT)
    if abs(dx) > 1:
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    comp = cf
    if sc[0] == 5: comp, cm = studio(t, comp, cm, M, f)
    if sc[0] == 6: g_ = comp @ np.array([0.3, 0.59, 0.11], np.float32); g_ = np.clip((g_ - 0.06) / 0.8, 0, 1) ** 1.1; comp = np.repeat(g_[..., None], 3, 2)
    back, front = new_layer(), new_layer()
    if sc[0] == 6: tickers(t, back)
    graphics(t, sc, f, M, back, front)
    comp = comp * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = comp * (1 - front[1][..., None]) + front[0]
    return comp

def rgb_split(img, amt, seed):
    r = np.random.default_rng(seed); sh = int(26 * amt); dy = int(r.normal(0, 10 * amt))
    out = img.copy(); out[..., 0] = np.roll(np.roll(img[..., 0], sh, 1), dy, 0); out[..., 2] = np.roll(img[..., 2], -sh, 1)
    return out

rng = np.random.default_rng(A + 21)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
for j in range(A, B):
    t = j / FPS
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    sc = scene_at(t)
    comp = render_shot(t, sc)
    if 4.32 <= t < 4.62:  # RGB split shake on the 4.40 cut (kept neutral: luminance split)
        comp = rgb_split(comp, clamp(1 - abs(t - 4.42) / 0.2), j)
    if sc[0] == 6:  # beat strobe in the B/W shot
        p_ = pulse(t, 0.05)
        if p_ > 0.05: comp = comp * (1 - 0.55 * p_) + WHITE * 0.55 * p_
    if 7.93 <= t < 7.966: comp = 1 - comp           # one inverted frame into the B/W shot
    if t >= 11.15:
        k = ease_io((t - 11.15) / 0.5); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.55 * k)
    comp = endcard(t, comp)
    comp = comp * VIGN
    comp += rng.normal(0, 0.012, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.3: comp *= ease_io((DUR - t) / 0.3)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if PREVIEW is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=88)
    else:
        enc.stdin.write(out.tobytes())
        if (j - A) % 30 == 0: print(A, "frame", j, flush=True)
if PREVIEW is None: enc.stdin.close(); enc.wait()
print("done", A, B)
