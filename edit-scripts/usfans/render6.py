"""v6 Fit-Check (Gallery Dept via USFans / Genluv / Timberland), yellow + white type.
Beat-synced re-cut of 9 of 12 clips (120 BPM), optical-flow slow-mo, split-screen freeze breakdown,
pose-tracked tags/circles, head-masked headlines, Higgsfield concrete studio + parcel end card.
Usage: python render6.py <out_start_frame> <out_end_frame> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib5 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
DUR = 16.5
NSRC = 754
YEL = np.array([255, 214, 10], np.float32) / 255
WHITE = np.array([250, 250, 246], np.float32) / 255
FREEZE_SRC = 339 / 30

# ------------------------------------------------------------------ timeline
SC = [  # id, out0, out1, [(out_t, src_t)], (first, last) src frame of the clip
    (1, 0.0, 2.0, [(0.0, 8.92), (2.0, 10.60)], (267, 318)),
    (2, 2.0, 4.0, [(2.0, 4.66), (2.5, 4.90), (4.0, 6.40)], (139, 200)),
    (3, 4.0, 5.5, [(4.0, 6.80), (5.5, 8.30)], (201, 266)),
    (4, 5.5, 7.5, [(5.5, 2.00), (7.5, 4.00)], (55, 138)),
    (5, 7.5, 9.0, [(7.5, 14.00), (9.0, 15.50)], (417, 499)),
    (6, 9.0, 10.5, [(9.0, 10.66), (10.5, FREEZE_SRC)], (319, 359)),
    (7, 10.5, 12.0, [(10.5, FREEZE_SRC), (12.0, FREEZE_SRC)], (319, 359)),
    (8, 12.0, 13.5, [(12.0, 21.50), (13.5, 23.00)], (642, 721)),
    (9, 13.5, 16.5, [(13.5, 18.75), (15.3, 20.40), (16.5, 20.40)], (560, 641)),
]
def scene_at(t):
    for sc in SC:
        if sc[1] <= t < sc[2]: return sc
    return SC[-1]
def src_frame(sc, t):
    xs, ys = zip(*sc[3]); return float(np.clip(np.interp(t, xs, ys) * FPS, sc[4][0], sc[4][1]))

# ------------------------------------------------------------------ pose (smoothed within each clip)
P = json.load(open("pose.json"))
LM = np.full((NSRC, 33, 3), np.nan, np.float32)
for i, p in enumerate(P[:NSRC]):
    if p is not None: LM[i] = np.array(p, np.float32)
CLIPS = [0, 55, 139, 201, 267, 319, 360, 417, 500, 560, 642, 722, NSRC]
for a, b in zip(CLIPS[:-1], CLIPS[1:]):
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
    i = int(f); fr = f - i; j = min(i + 1, NSRC - 1)
    return LM[i, k, :2] * (1 - fr) + LM[j, k, :2] * fr
def mid(f, a, b): return (lm(f, a) + lm(f, b)) / 2
def anchor(kind, f):
    if kind == "chest": sh = mid(f, 11, 12); hp = mid(f, 23, 24); return sh + 0.30 * (hp - sh)
    if kind == "thigh":
        h, k = (23, 25) if lm(f, 23)[0] > lm(f, 24)[0] else (24, 26); return lm(f, h) * 0.45 + lm(f, k) * 0.55
    if kind == "foot":
        a, fi = (27, 31) if lm(f, 27)[0] < lm(f, 28)[0] else (28, 32); return (lm(f, a) + lm(f, fi)) / 2
    if kind == "feet": return (lm(f, 27) + lm(f, 28) + lm(f, 31) + lm(f, 32)) / 4
    if kind == "label":  # back view: waistband label sits right of the right-hand hip
        h = 23 if lm(f, 23)[0] > lm(f, 24)[0] else 24; return lm(f, h) + np.array([70.0, -5.0])

# ------------------------------------------------------------------ camera
def cam(sc, t, f):
    sid, o0, o1 = sc[0], sc[1], sc[2]; u = clamp((t - o0) / (o1 - o0))
    rot = 0.0
    if sid == 1:
        s = 1.06 + 0.30 * (1 - ease_out(t / 0.45)) + 0.03 * u
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.53 * H)
    elif sid == 2:
        s = 1.10 + 0.06 * ease_io(u)
        if t > 3.86: s *= 1 + 0.45 * ease_in((t - 3.86) / 0.14)
        h = mid(f, 23, 24); c = (h[0], h[1] - 30); sp = (0.45 * W, 0.56 * H)
    elif sid == 3:
        s = 1.18 + 0.06 * ease_io(u)
        if t < 4.35: s *= 1 + 0.42 * (1 - ease_out((t - 4.0) / 0.35))
        h = mid(f, 23, 24); c = (h[0], h[1] + 80); sp = (W / 2, 0.52 * H)
        if t > 5.36: rot = 14 * ease_in((t - 5.36) / 0.14)
    elif sid == 4:
        s = 1.12 + 0.10 * ease_io(u)
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.55 * H)
        if t < 5.66: rot = -14 * (1 - ease_out((t - 5.5) / 0.16))
    elif sid == 5:
        s = 1.06 + 0.07 * ease_io(u)
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1] + 150); sp = (W / 2, 0.45 * H)
    elif sid in (6, 7):
        h = mid(f, 23, 24); c = (h[0], h[1] - 70)
        k = ease_io((t - 9.25) / 0.5)
        s = 1.12 + 0.05 * ease_io(clamp((t - 9.0) / 1.5))
        sx = W / 2 + (min(W - W / (2 * s), max(W / (2 * s), c[0])) - c[0]) * s * (1 - k)
        sp = (sx, 0.53 * H)
        if sid == 7: sp = (sx + (0.29 * W - sx) * ease_io((t - 10.5) / 0.38), sp[1])
        return s, c, sp, t > 9.05, 0.0
    elif sid == 8:
        s = 1.04 + 0.09 * ease_io(u)
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.44 * H)
    else:
        s = 1.06 + 0.10 * ease_io(u)
        h = mid(f, 11, 12); c = (W / 2 + (h[0] - W / 2) * 0.5, h[1] + 250); sp = (W / 2, 0.47 * H)
    return s, c, sp, False, rot
def cam_M(s, c, sp, oob, rot):
    x0 = c[0] - sp[0] / s; y0 = c[1] - sp[1] / s
    if not oob:
        x0 = clamp(x0, 0, W - W / s); y0 = clamp(y0, 0, H - H / s)
    M = np.float32([[s, 0, -s * x0], [0, s, -s * y0]])
    if abs(rot) > 0.01:
        R = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1 + abs(rot) / 40)
        M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return M
def apply(M, p): return np.array([M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2], M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2]])

# ------------------------------------------------------------------ source frames for this chunk
def scenes_for(t):
    out = [scene_at(t)]
    if 13.36 <= t < 13.64: out = [SC[7], SC[8]]
    if 11.86 <= t < 12.18: out = [SC[6], SC[7]]
    return out
need = {339, 230}
for j in range(A, B):
    t = j / FPS
    for sc in scenes_for(t):
        f = src_frame(sc, t); need.update({int(f), min(int(f) + 1, sc[4][1])})
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
    if fr < 0.04 or i + 1 > sc[4][1] or (i + 1) not in FR:
        return FR[i].astype(np.float32) / 255, MK[i].astype(np.float32) / 255
    if fr > 0.96: return FR[i + 1].astype(np.float32) / 255, MK[i + 1].astype(np.float32) / 255
    f01, f10 = flows(i)
    m0 = (GX - fr * f01[..., 0], GY - fr * f01[..., 1]); m1 = (GX - (1 - fr) * f10[..., 0], GY - (1 - fr) * f10[..., 1])
    a0 = cv2.remap(FR[i], *m0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    a1 = cv2.remap(FR[i + 1], *m1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k0 = cv2.remap(MK[i], *m0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k1 = cv2.remap(MK[i + 1], *m1, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    return (a0 * (1 - fr) + a1 * fr) / 255, (k0 * (1 - fr) + k1 * fr) / 255

# ------------------------------------------------------------------ typography assets (yellow + white)
GOLD = [(0, (255, 251, 222)), (.36, (255, 214, 10)), (.49, (176, 120, 0)), (.53, (110, 70, 0)), (.72, (255, 200, 40)), (1, (255, 246, 200))]
import lib5
def chrome_with(stops, M_, depth, sw):
    old = lib5.CHROME; lib5.CHROME = stops
    try: return sprite_chrome(M_, depth=depth, sweep=sw)
    finally: lib5.CHROME = old
_cache = {}
def chrome_cached(key, M_, depth, sw, stops=None):
    k = (key, None if sw is None else round(round(sw / 0.05) * 0.05, 2))
    if k not in _cache: _cache[k] = chrome_with(stops or lib5.CHROME, M_, depth, k[1])
    return _cache[k]

def solid3d(M_, face_top, face_bot, ext_col, depth=20):
    """flat-colour face with gradient + hard 3D extrusion + soft shadow"""
    h, w = M_.shape; P_ = depth + 40
    Mp = np.pad(M_, ((P_ // 2, P_), (P_ // 2, P_))); hh, ww = Mp.shape
    ext = np.zeros_like(Mp)
    for k in range(1, depth + 1): ext = np.maximum(ext, np.roll(np.roll(Mp, int(k * 0.6), 1), k, 0))
    shadow = cv2.GaussianBlur(np.roll(np.roll(Mp, depth + 14, 0), 10, 1), (0, 0), 18) * 0.55
    ys = np.where(Mp.max(1) > .5)[0]; y0, y1 = ys[0], ys[-1]
    g = np.clip((np.arange(hh) - y0) / max(y1 - y0, 1), 0, 1)[:, None, None]
    face = np.array(face_top, np.float32) / 255 * (1 - g) + np.array(face_bot, np.float32) / 255 * g
    face = face + np.clip(Mp - np.roll(Mp, 3, 0), 0, 1)[..., None] * 0.35
    rgb = np.zeros((hh, ww, 3), np.float32); a = shadow * (1 - ext)
    ec = np.array(ext_col, np.float32) / 255
    rgb = rgb * (1 - ext[..., None]) + ec * ext[..., None]; a = a * (1 - ext) + ext
    rgb = rgb * (1 - Mp[..., None]) + np.clip(face, 0, 1) * Mp[..., None]; a = a * (1 - Mp) + Mp
    return rgb, a, (P_ // 2, P_ // 2)

S = {}
S["ootd"] = sprite_fill(tmask("OUTFIT  OF  THE  DAY", font("SpaceGrotesk", 30, 700), 8)[0], WHITE, shadow=0.6, sblur=6, soff=(3, 2))
S["fit"] = solid3d(tmask("FIT", font("Archivo", 320, 900, 125), 4)[0], (255, 236, 120), (255, 196, 0), (92, 62, 0), 24)
S["check"] = sprite_fill(tmask("CHECK", font("Unbounded", 150, 900), 10)[0], WHITE, shadow=0.6, sblur=12, stroke=(INK, 5))
TIMB_M = tmask("TIMBERLAND", font("Anton-Regular", 210), 10)[0]
S["c_schuhe"] = chip("Schuhe  ·  Timberland", tick=True, size=42)
GD_M = tmask("GALLERY DEPT.", font("Archivo", 88, 900, 118), 2)[0]
S["gd_white"] = sprite_fill(GD_M, WHITE, shadow=0.6, sblur=14)
S["via"] = chip("Hose  ·  via USFans", bg=YEL, fg=INK, size=46)
S["genluv"] = sprite_fill(tmask("Genluv", font("InstrumentSerif-Italic", 300))[0], WHITE, shadow=0.55, sblur=18)
S["c_pulli"] = chip("Pulli", bg=YEL, fg=INK, size=42)
LOOK_M = tmask("LOOK", font("Unbounded", 210, 900), 8)[0]
S["best"] = sprite_fill(tmask("BESTELLT  ÜBER", font("SpaceGrotesk", 36, 700), 9)[0], WHITE, shadow=0.0)
GTB_M = tmask("USFans", font("Unbounded", 190, 900), 2)[0]
S["parcel"] = card_sprite(load_img("img/parcel.png"), 520, 600, 1.03)
S["link"] = link_card(size=50)
STUDIO = load_img("img/studio.png"); POOL_Y = 0.855

def tag_sprite(item, brand, gt):
    fi, fb, fg = font("SpaceGrotesk", 26, 700), font("Archivo", 48, 900, 112), font("SpaceGrotesk", 24, 700)
    wb = fb.getlength(brand); pw = int(max(wb, 200) + 52); ph = 128 + (52 if gt else 0); pad = 40
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 24, fill=(12, 12, 14, 228))
    d.rectangle([pad, pad + 22, pad + 5, pad + 106], fill=(255, 214, 10, 255))
    x = pad + 26
    for ch_ in item: d.text((x, pad + 34), ch_, font=fi, fill=(255, 214, 10, 255), anchor="lm"); x += fi.getlength(ch_) + 3
    d.text((pad + 24, pad + 86), brand, font=fb, fill=(250, 250, 246, 255), anchor="lm")
    if gt:
        gw = fg.getlength("via USFans") + 44
        d.rounded_rectangle([pad + 24, pad + 124, pad + 24 + gw, pad + 164], 20, fill=(255, 214, 10, 255))
        d.text((pad + 24 + gw / 2, pad + 144), "via USFans", font=fg, fill=(12, 12, 14, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 14) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
TAGS = [("PULLI", "GENLUV", False, 2.35, "chest", "L", 640), ("HOSE", "GALLERY DEPT.", True, 2.85, "thigh", "R", 1060),
        ("SCHUHE", "TIMBERLAND", False, 3.35, "foot", "L", 1450)]
for it, br, gt, *_ in TAGS: S["tag_" + br] = tag_sprite(it, br, gt)

PANELS = [("chest", "Pulli", "Genluv", False, 10.62, 300, 1.9), ("thigh", "Hose", "Gallery Dept.", True, 10.80, 260, 1.7),
          ("feet", "Schuhe", "Timberland", False, 10.98, 330, 1.25)]
def panel_label(item, brand, gt):
    fi, fb, fg = font("SpaceGrotesk", 22, 700), font("Archivo", 40, 900, 112), font("SpaceGrotesk", 20, 700)
    w = int(max(fb.getlength(brand), 150) + (fg.getlength("via USFans") + 40 if gt else 0) + 40); pad = 30
    im = Image.new("RGBA", (w + 2 * pad, 96 + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + w, pad + 96], 20, fill=(12, 12, 14, 232))
    x = pad + 20
    for ch_ in item.upper(): d.text((x, pad + 26), ch_, font=fi, fill=(255, 214, 10, 255), anchor="lm"); x += fi.getlength(ch_) + 3
    d.text((pad + 20, pad + 66), brand, font=fb, fill=(250, 250, 246, 255), anchor="lm")
    if gt:
        gw = fg.getlength("via USFans") + 26; gx = pad + w - gw - 16
        d.rounded_rectangle([gx, pad + 48, gx + gw, pad + 84], 18, fill=(255, 214, 10, 255))
        d.text((gx + gw / 2, pad + 66), "via USFans", font=fg, fill=(12, 12, 14, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3], (pad, pad)
PANEL_L = [panel_label(it, br, gt) for _, it, br, gt, *_ in PANELS]
ROWS = [("Hose", "Gallery Dept.", True), ("Pulli", "Genluv", False), ("Schuhe", "Timberland", False)]
def row_sprite(item, brand, gt):
    f1, f2, fg = font("Archivo", 54, 800, 110), font("InstrumentSerif-Italic", 64), font("SpaceGrotesk", 24, 700)
    pad = 30; w = 780; im = Image.new("RGBA", (w + 2 * pad, 90 + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((pad, pad + 45), item, font=f1, fill=(250, 250, 246, 255), anchor="lm")
    d.text((pad + f1.getlength(item) + 22, pad + 47), "— " + brand, font=f2, fill=(250, 250, 246, 215), anchor="lm")
    if gt:
        gw = fg.getlength("USFans") + 30; gx = pad + w - gw
        d.rounded_rectangle([gx, pad + 25, gx + gw, pad + 67], 21, fill=(255, 214, 10, 255))
        d.text((gx + gw / 2, pad + 46), "USFans", font=fg, fill=(12, 12, 14, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3], (pad, pad)
ROW_S = [row_sprite(*r) for r in ROWS]

def draw_line(L, p0, p1, alpha, col=WHITE, w=3, dot=True, pulse=0.0):
    m = np.zeros((H, W), np.float32)
    cv2.line(m, tuple(int(v) for v in p0), tuple(int(v) for v in p1), 1.0, w, cv2.LINE_AA)
    if dot:
        cv2.circle(m, tuple(int(v) for v in p1), 9, 1.0, -1, cv2.LINE_AA)
        if pulse > 0: cv2.circle(m, tuple(int(v) for v in p1), int(12 + 26 * pulse), 1.0 - pulse, 2, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += col * m[..., None]; L[1] *= (1 - m); L[1] += m
def circle_draw(L, c, rx, ry, prog, alpha, col=YEL):
    m = np.zeros((H, W), np.float32)
    if prog > 0: cv2.ellipse(m, (int(c[0]), int(c[1])), (int(rx), int(ry)), -10, -90, -90 + 360 * prog, 1.0, 6, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += col * m[..., None]; L[1] *= (1 - m); L[1] += m
def underline(L, x0, x1, y, prog, alpha):
    if prog <= 0: return
    m = np.zeros((H, W), np.float32); pts = []
    for k in range(41):
        u = k / 40 * prog; pts.append((x0 + (x1 - x0) * u, y + 10 * math.sin(u * math.pi * 1.2)))
    cv2.polylines(m, [np.int32(pts)], False, 1.0, 12, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += YEL * m[..., None]; L[1] *= (1 - m); L[1] += m

# ------------------------------------------------------------------ per-scene graphics
def graphics(t, sc, f, M, back, front):
    sid = sc[0]
    if sid == 1:
        a = win(t, 0.08, 1.92, 0.3, 0.12)
        place(front, S["ootd"], W / 2, 56, alpha=a, s=1 + 0.2 * (1 - ease_out((t - .08) / .5)))
        k = back_out((t - 0.06) / 0.45, 1.8)
        place(back, S["fit"], W / 2, 205, s=(1.55 - 0.55 * k) * (1 + 0.025 * t), alpha=clamp(t / 0.06) * a, blur=max(0, 1 - t / 0.2) * 8)
        k2 = ease_out((t - 0.40) / 0.5)
        place(back, S["check"], W / 2, 395, s=0.82 + 0.08 * k2, alpha=k2 * a, rx=-60 * (1 - k2))
    if sid == 2:
        for it, br, gt, t0, kind, side, ty in TAGS:
            a = win(t, t0, 3.9, 0.22, 0.1)
            if a <= 0: continue
            p = apply(M, anchor(kind, f)); sp = S["tag_" + br]; tw = sp[1].shape[1] - 80
            k = ease_out((t - t0) / 0.35); sc_ = 1.0
            if side == "L":
                place(front, sp, 50 - (1 - k) * 60, ty, s=sc_, anchor=(40 / sp[1].shape[1], 0.5), alpha=a); e = (50 + tw * sc_ + 6, ty - 20)
            else:
                place(front, sp, W - 50 + (1 - k) * 60, ty, s=sc_, anchor=(1 - 40 / sp[1].shape[1], 0.5), alpha=a); e = (W - 50 - tw * sc_ - 6, ty - 20)
            prog = ease_io((t - t0 - 0.05) / 0.3)
            draw_line(front, e, (e[0] + (p[0] - e[0]) * prog, e[1] + (p[1] - e[1]) * prog), a, dot=prog > .95,
                      pulse=clamp((t - t0 - .35) / .5) if t - t0 < 0.85 else 0)
    if sid == 3:
        a = win(t, 4.12, 5.42, 0.35, 0.1); k = ease_out((t - 4.12) / 0.6)
        sw = (t - 4.4) / 0.9 if 4.4 <= t <= 5.3 else None
        place(back, chrome_cached("timb", TIMB_M, 14, sw, GOLD), 150, 900 + (1 - k) * 200, rot=90, alpha=a, s=0.95)
        p = apply(M, anchor("feet", f))
        circle_draw(front, p + np.array([0, -10.0]), 200, 95, ease_io((t - 4.35) / 0.4), a)
        a2 = win(t, 4.7, 5.42, 0.2, 0.1)
        if a2: place(front, S["c_schuhe"], W / 2 + 120, min(p[1] + 215, 1660), s=back_out((t - 4.7) / 0.3, 2.0), alpha=a2)
    if sid == 4:
        a = win(t, 5.62, 7.42, 0.35, 0.1); k = ease_out((t - 5.62) / 0.55)
        sw = (t - 5.9) / 0.9 if 5.9 <= t <= 6.8 else None
        place(back, chrome_cached("gd", GD_M, 12, sw), W / 2, 420 - (1 - k) * 50, s=0.92 + 0.08 * k, alpha=a)
        p = apply(M, anchor("label", f))
        circle_draw(front, p, 62, 50, ease_io((t - 6.1) / 0.35), a)
        a2 = win(t, 6.35, 7.42, 0.2, 0.1)
        if a2:
            e = (p[0] - 230, p[1] - 230)
            draw_line(front, (p[0] - 45, p[1] - 45), e, a2, col=YEL, dot=False)
            place(front, S["via"], max(e[0], 250), e[1] - 30, s=back_out((t - 6.35) / 0.3, 2.0), alpha=a2)
    if sid == 5:
        a = win(t, 7.6, 8.92, 0.3, 0.1); k = ease_out((t - 7.6) / 0.55)
        place(back, S["genluv"], W / 2 + (1 - k) * 120, 330, alpha=a)
        underline(back, W / 2 - 330, W / 2 + 330, 440, ease_io((t - 7.85) / 0.35), a)
        a2 = win(t, 8.1, 8.92, 0.2, 0.1)
        if a2:
            p = apply(M, anchor("chest", f))
            place(front, S["c_pulli"], p[0] + 230, p[1] + 60, s=back_out((t - 8.1) / 0.3, 2.0), alpha=a2)
            draw_line(front, (p[0] + 170, p[1] + 60), p, a2, col=YEL, dot=True)
    if sid == 6:
        a = win(t, 9.18, 10.45, 0.4, 0.15); k = ease_out((t - 9.18) / 0.6)
        sw = (t - 9.5) / 0.9 if 9.5 <= t <= 10.4 else None
        place(back, chrome_cached("look", LOOK_M, 16, sw, GOLD), W / 2, 330, rx=-70 * (1 - k), alpha=a)

def split_panels(t, comp, frame339, M):
    """freeze breakdown: three detail crops of the real outfit slide in on the right, linked to the body"""
    L = new_layer()
    for n, ((kind, it, br, gt, t0, half, z), lab) in enumerate(zip(PANELS, PANEL_L)):
        k = ease_out((t - t0) / 0.4)
        if k <= 0: continue
        src_img = frame339 if kind != "feet" else FR[230].astype(np.float32) / 255  # boots fully in frame in the side shot
        c = anchor(kind, 339) if kind != "feet" else np.array([585.0, 1680.0])  # measured boot centre in frame 230
        pw, ph = 380, 400
        tile = cv2.getRectSubPix(src_img, (int(pw / z * 1.0), int(ph / z)), (float(c[0]), float(c[1])))
        tile = cv2.resize(tile, (pw, ph), interpolation=cv2.INTER_CUBIC)
        tile = np.clip(tile * 1.3 - cv2.GaussianBlur(tile, (0, 0), 2) * 0.3, 0, 1)
        rm = rounded(pw, ph, 30); pad = 60
        rgb = np.zeros((ph + 2 * pad, pw + 2 * pad, 3), np.float32); al = np.zeros((ph + 2 * pad, pw + 2 * pad), np.float32)
        sh = np.zeros_like(al); sh[pad + 24:pad + ph + 20, pad + 14:pad + pw - 14] = 1; sh = cv2.GaussianBlur(sh, (0, 0), 22) * 0.55
        al[:] = sh; rgb[pad:pad + ph, pad:pad + pw] = tile * rm[..., None]
        al[pad:pad + ph, pad:pad + pw] = np.maximum(sh[pad:pad + ph, pad:pad + pw] * (1 - rm), rm)
        br_ = np.zeros((ph, pw), np.uint8); cv2.rectangle(br_, (1, 1), (pw - 2, ph - 2), 255, 3)
        brm = (br_.astype(np.float32) / 255 * rm)[..., None]
        rgb[pad:pad + ph, pad:pad + pw] = rgb[pad:pad + ph, pad:pad + pw] * (1 - brm) + YEL * brm
        cy = 470 + n * 430; cx = 790 + (1 - k) * 500
        place(L, (rgb, al, (pad, pad)), cx, cy, s=0.94 + 0.06 * k, alpha=k)
        place(L, lab, cx + 190, cy + 200 - 6, anchor=(1 - 30 / lab[1].shape[1], 0.5), alpha=k)
        lk = ease_io((t - t0 - 0.2) / 0.3)
        if lk > 0:
            p = apply(M, anchor(kind, 339)); e = (cx - 190 - 8, cy)
            draw_line(L, e, (e[0] + (p[0] - e[0]) * lk, e[1] + (p[1] - e[1]) * lk), k, col=YEL, w=2, dot=lk > .95)
    return comp * (1 - L[1][..., None]) + L[0]

def endcard(t, comp):
    if t < 13.95: return comp
    L = new_layer()
    k = ease_out((t - 13.95) / 0.5); place(L, S["best"], W / 2, 175 - (1 - k) * 20, alpha=k)
    k2 = ease_out((t - 14.05) / 0.55)
    sw = (t - 14.5) / 0.9 if 14.5 <= t <= 15.4 else None
    place(L, chrome_cached("gtb", GTB_M, 14, sw, GOLD), W / 2, 315, s=0.9 + 0.1 * k2, rx=-60 * (1 - k2), alpha=clamp((t - 14.05) / .1))
    k3 = ease_out((t - 14.3) / 0.55)
    place(L, S["parcel"], W / 2, 750 + (1 - k3) * 120, s=0.94 + 0.06 * k3 + 0.006 * (t - 14.3), rot=-2.5 * (1 - k3) - 1.2, alpha=k3)
    for n, sp in enumerate(ROW_S):
        t0 = 14.65 + n * 0.2; kk = ease_out((t - t0) / 0.35)
        if kk <= 0: continue
        y = 1130 + n * 86
        place(L, check_sprite(26, clamp((t - t0) / 0.25)), 150, y, s=back_out((t - t0) / 0.3, 2.0), alpha=kk)
        place(L, sp, 200 + (1 - kk) * 30, y, anchor=(30 / sp[1].shape[1], 0.5), alpha=kk)
    k4 = ease_out((t - 15.35) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1420, s=back_out((t - 15.35) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

# ------------------------------------------------------------------ compositing
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.24 * np.clip(np.sqrt(((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .46) / (H * .72)) ** 2) - .45, 0, 1) ** 1.5)[..., None]
def refine(frame, m):
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)
    return np.clip(cv2.resize(guided(gs, ms), (W, H)), 0, 1)
def studio(t, comp, cm, M, f):
    feet = apply(M, (lm(f, 27) + lm(f, 28)) / 2); s = M[0, 0]
    z = 1.22 * (1 + (s - 1) * 0.45)
    oy = (feet[1] + 30 - (H / 2 + (POOL_Y - 0.5) * H * z)) / H; ox = (feet[0] - W / 2) / W * 0.8
    bg = np.clip(cover(STUDIO, W, H, z, ox, oy) * 1.1, 0, 1)
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(feet[0]), int(feet[1] + 20)), (int(150 * s), int(26 * s)), 0, 0, 360, 1.0, -1)
    bg = bg * (1 - cv2.GaussianBlur(sh, (0, 0), 18 * s)[..., None] * 0.55)
    r = ease_out((t - 9.0) / 0.42) * 2400
    d = np.sqrt((XX - feet[0]) ** 2 + ((YY - feet[1]) * 1.6) ** 2)
    circ = np.clip((r - d) / 40, 0, 1); ring = np.exp(-((d - r) / 14) ** 2) * (r < 2300) * 0.9
    cmc = cv2.GaussianBlur(np.clip((cv2.erode(cm, np.ones((5, 5), np.uint8)) - 0.25) / 0.6, 0, 1), (0, 0), 1.2)
    band = np.clip(cm - cmc, 0, 1) * circ
    comp = comp * (1 - 0.65 * band[..., None])
    cm2 = cmc * circ + cm * (1 - circ)
    bm = ((1 - cm2) * circ)[..., None]
    comp = comp * (1 - bm) + bg * bm
    return comp + ring[..., None] * YEL * 0.7, cm2

def render_shot(t, sc):
    f = src_frame(sc, t)
    frame, m = frame_at(sc, f); m = refine(frame, m)
    s, c, sp, oob, rot = cam(sc, t, f)
    M = cam_M(s, c, sp, oob, rot)
    zb = 0.0
    if t < 0.3: zb = 1 - t / 0.3
    if 3.86 <= t < 4.0: zb = ease_in((t - 3.86) / 0.14)
    if 4.0 <= t < 4.25: zb = 1 - ease_out((t - 4.0) / 0.25)
    dx = 0.0
    if 1.88 <= t < 2.0: dx = -ease_in((t - 1.88) / 0.12) * W * 0.6
    if 2.0 <= t < 2.14: dx = (1 - ease_out((t - 2.0) / 0.14)) * W * 0.6
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
    if abs(rot) > 2:  # spin transition: rotational smear
        acc = np.zeros_like(cf)
        for k in range(5):
            R = cv2.getRotationMatrix2D((W / 2, H / 2), (k - 2) * rot * 0.12, 1)
            acc += cv2.warpAffine(cf, R, (W, H), borderMode=cv2.BORDER_REFLECT)
        cf = acc / 5
    cm = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_CONSTANT if oob else cv2.BORDER_REFLECT)
    if abs(dx) > 1:
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    comp = cf
    if sc[0] in (6, 7): comp, cm = studio(t, comp, cm, M, f)
    back, front = new_layer(), new_layer()
    graphics(t, sc, f, M, back, front)
    comp = comp * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = comp * (1 - front[1][..., None]) + front[0]
    if sc[0] == 7: comp = split_panels(t, comp, FR[339].astype(np.float32) / 255, M)
    return comp

def glitch(img, amt, seed):
    r = np.random.default_rng(seed); out = img.copy(); y = 0
    while y < H:
        h = int(r.integers(20, 140)); out[y:y + h] = np.roll(img[y:y + h], int(r.normal(0, 90 * amt)), 1); y += h
    sh = int(18 * amt); out[..., 0] = np.roll(out[..., 0], sh, 1); out[..., 2] = np.roll(out[..., 2], -sh, 1)
    return out

rng = np.random.default_rng(A + 9)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
for j in range(A, B):
    t = j / FPS
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    sc = scene_at(t)
    comp = render_shot(t, sc)
    if 11.86 <= t < 12.18:  # vertical push 7 -> 8
        u = ease_io((t - 11.86) / 0.32)
        a_ = render_shot(t, SC[6]) if t >= 12.0 else comp
        b_ = comp if t >= 12.0 else render_shot(t, SC[7])
        dy = int(u * H); k_ = int(5 + math.sin(math.pi * u) * 70) | 1
        out_ = np.empty_like(a_)
        out_[:H - dy] = a_[dy:]; out_[H - dy:] = b_[:dy]
        comp = cv2.blur(out_, (1, k_))
    if 13.36 <= t < 13.64:  # defocus dissolve 8 -> 9
        u = ease_io((t - 13.36) / 0.28)
        o_ = render_shot(t, SC[8] if t < 13.5 else SC[7])
        a_, b_ = (comp, o_) if t < 13.5 else (o_, comp)
        bl = math.sin(math.pi * u) * 18
        if bl > 0.5: a_ = cv2.GaussianBlur(a_, (0, 0), bl); b_ = cv2.GaussianBlur(b_, (0, 0), bl)
        comp = a_ * (1 - u) + b_ * u
    if 7.40 <= t < 7.62:
        amt = 1 - abs(t - 7.5) / 0.12
        if amt > 0: comp = glitch(comp, clamp(amt), j)
    if t >= 13.8:
        k = ease_io((t - 13.8) / 0.6); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.5 * k)
    comp = endcard(t, comp)
    comp = comp * VIGN
    comp += rng.normal(0, 0.011, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.35: comp *= ease_io((DUR - t) / 0.35)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if PREVIEW is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=88)
    else:
        enc.stdin.write(out.tobytes())
        if (j - A) % 30 == 0: print(A, "frame", j, flush=True)
if PREVIEW is None: enc.stdin.close(); enc.wait()
print("done", A, B)
