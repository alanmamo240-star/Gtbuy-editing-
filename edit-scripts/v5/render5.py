"""v5 Fit-Check edit (no speech): beat-synced re-cut at 120 BPM, optical-flow slow-mo, freeze-frame,
pose-tracked product tags, head/leg masked typography, Higgsfield studio backdrop + parcel end card.
Usage: python render5.py <out_start_frame> <out_end_frame> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib5 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
DUR = 12.5
NOUT = int(DUR * FPS)
NSRC = 292

# ------------------------------------------------------------------ timeline (output time -> source time)
SC = [  # id, out0, out1, piecewise map [(out_t, src_t)], src frame range
    (1, 0.0, 1.5, [(0.0, 0.00), (1.5, 1.37)], (0, 41)),
    (2, 1.5, 3.5, [(1.5, 1.40), (2.0, 1.62), (3.5, 3.13)], (42, 94)),       # 0.45x ramp -> 1.0x
    (3, 3.5, 5.5, [(3.5, 3.18), (5.5, 5.07)], (95, 152)),
    (4, 5.5, 7.0, [(5.5, 5.11), (7.0, 6.70)], (153, 201)),
    (5, 7.0, 9.0, [(7.0, 6.75), (8.4, 238 / 30), (9.0, 238 / 30)], (202, 257)),     # freeze 8.4-9.0
    (6, 9.0, 12.5, [(9.0, 8.62), (10.6, 9.68), (12.5, 9.68)], (258, 291)),  # 0.66x slow-mo, then hold
]
def scene_at(t):
    for sc in SC:
        if sc[1] <= t < sc[2]: return sc
    return SC[-1]
def src_time(sc, t):
    xs, ys = zip(*sc[3]); return float(np.interp(t, xs, ys))
def src_frame(sc, t):
    f = src_time(sc, t) * FPS
    return float(np.clip(f, sc[4][0], sc[4][1]))

# ------------------------------------------------------------------ pose tracking (smoothed within shots)
P = json.load(open("pose.json"))
LM = np.full((NSRC, 33, 3), np.nan, np.float32)
for i, p in enumerate(P[:NSRC]):
    if p is not None: LM[i] = np.array(p, np.float32)
for sc in SC:
    a, b = sc[4]
    seg = LM[a:b + 1]
    for k in range(33):
        for c in range(2):
            v = seg[:, k, c]; ok = ~np.isnan(v)
            if ok.sum() == 0: continue
            v = np.interp(np.arange(len(v)), np.where(ok)[0], v[ok])
            sig = 3.0; ker = np.exp(-0.5 * (np.arange(-9, 10) / sig) ** 2); ker /= ker.sum()
            seg[:, k, c] = np.convolve(np.pad(v, 9, mode="edge"), ker, "valid")
    LM[a:b + 1] = seg
def lm(f, k):
    i = int(f); fr = f - i; j = min(i + 1, NSRC - 1)
    return LM[i, k, :2] * (1 - fr) + LM[j, k, :2] * fr
def mid(f, a, b): return (lm(f, a) + lm(f, b)) / 2
def leftleg(f):  # the leg that is further left on screen (labels sit on the left)
    return (23, 25, 27, 31) if lm(f, 27)[0] < lm(f, 28)[0] else (24, 26, 28, 32)

# ------------------------------------------------------------------ camera
def cam(sc, t, f):
    """returns s, (cx,cy) source point, (sx,sy) screen point, allow_oob"""
    sid, o0, o1 = sc[0], sc[1], sc[2]
    u = (t - o0) / (o1 - o0)
    if sid == 1:
        s = 1.06 + 0.32 * (1 - ease_out((t - o0) / 0.45)) + 0.04 * u
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.42 * H)
        return s, c, sp, False
    if sid == 2:
        s = 1.22 + 0.08 * ease_io(u)
        if t > 3.36: s *= 1 + 0.45 * ease_in((t - 3.36) / 0.14)
        h = mid(f, 23, 24); c = (h[0], h[1] - 40); sp = (W / 2, 0.55 * H)
        return s, c, sp, False
    if sid == 3:
        s = 1.06 + 0.06 * ease_io(u)
        if t < 3.85: s *= 1 + 0.42 * (1 - ease_out((t - 3.5) / 0.35))
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.6, n[1]); sp = (W / 2, 0.40 * H)
        return s, c, sp, False
    if sid == 4:
        s = 1.12 + 0.05 * ease_io(u)
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1] + 120); sp = (W / 2 - 40, 0.36 * H)
        return s, c, sp, False
    if sid == 5:
        body = mid(f, 23, 24)
        k = ease_io((t - 7.25) / 0.6)                    # after the studio reveal: recentre the person
        s = 1.10 + 0.06 * ease_io(u)
        c0 = (body[0], body[1] - 60)
        sx = W / 2 + (min(W - W / (2 * s), max(W / (2 * s), c0[0])) - c0[0]) * s * (1 - k)  # clamped look before reveal
        sp = (sx, 0.52 * H)
        if t >= 8.4:  # freeze: punch into the shoes
            z = ease_io((t - 8.4) / 0.42)
            feet = (lm(f, 27) + lm(f, 28) + lm(f, 31) + lm(f, 32)) / 4
            s = s * (1 + 1.25 * z)
            c0 = (c0[0] + (feet[0] - c0[0]) * z, c0[1] + (feet[1] - c0[1]) * z)
            sp = (sp[0] + (0.66 * W - sp[0]) * z, sp[1] + (0.64 * H - sp[1]) * z)
        return s, c0, sp, t > 7.05
    # 6: back view, slow push
    s = 1.06 + 0.10 * ease_io(u)
    h = mid(f, 11, 12); c = (W / 2 + (h[0] - W / 2) * 0.5, h[1] + 200); sp = (W / 2, 0.45 * H)
    return s, c, sp, False

def cam_M(s, c, sp, oob):
    x0 = c[0] - sp[0] / s; y0 = c[1] - sp[1] / s
    if not oob:
        x0 = clamp(x0, 0, W - W / s); y0 = clamp(y0, 0, H - H / s)
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])
def apply(M, p): return np.array([M[0, 0] * p[0] + M[0, 2], M[1, 1] * p[1] + M[1, 2]])

# ------------------------------------------------------------------ source frames (only the range this chunk needs)
need = set()
for j in range(A, B):
    t = j / FPS
    scs = [scene_at(t)] + ([SC[4], SC[5]] if 8.85 <= t < 9.15 else [])
    for sc in scs:
        f = src_frame(sc, t); need.update({int(f), min(int(f) + 1, sc[4][1])})
lo, hi = min(need), max(need)
def load(path, fmt, ch):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select='between(n\\,{lo}\\,{hi})'", "-vsync", "0",
                          "-f", "rawvideo", "-pix_fmt", fmt, "-"], stdout=subprocess.PIPE)
    out = {}
    for i in range(lo, hi + 1):
        b = p.stdout.read(W * H * ch)
        if len(b) < W * H * ch: break
        if i in need: out[i] = np.frombuffer(b, np.uint8).reshape(H, W, ch) if ch > 1 else np.frombuffer(b, np.uint8).reshape(H, W)
    p.wait(); return out
FR = load("enh.mov", "rgb24", 3)
MK = load("mask.mkv", "gray", 1)
_flow = {}
DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def flows(i):
    if i not in _flow:
        for k_ in [k for k in _flow if k < i - 1]: del _flow[k_]
        g0 = cv2.cvtColor(cv2.resize(FR[i], (540, 960)), cv2.COLOR_RGB2GRAY)
        g1 = cv2.cvtColor(cv2.resize(FR[i + 1], (540, 960)), cv2.COLOR_RGB2GRAY)
        f01 = cv2.resize(DIS.calc(g0, g1, None), (W, H)) * 2; f10 = cv2.resize(DIS.calc(g1, g0, None), (W, H)) * 2
        _flow[i] = (f01, f10)
    return _flow[i]
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def frame_at(sc, f):
    """optical-flow interpolated frame + matte at fractional source frame f"""
    i = int(f); fr = f - i
    if fr < 0.04 or i + 1 > sc[4][1] or (i + 1) not in FR:
        k = i if fr < 0.5 or (i + 1) not in FR else i + 1
        return FR[k].astype(np.float32) / 255, MK[k].astype(np.float32) / 255
    if fr > 0.96: return FR[i + 1].astype(np.float32) / 255, MK[i + 1].astype(np.float32) / 255
    f01, f10 = flows(i)
    m0x, m0y = GX - fr * f01[..., 0], GY - fr * f01[..., 1]
    m1x, m1y = GX - (1 - fr) * f10[..., 0], GY - (1 - fr) * f10[..., 1]
    a0 = cv2.remap(FR[i], m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    a1 = cv2.remap(FR[i + 1], m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k0 = cv2.remap(MK[i], m0x, m0y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    k1 = cv2.remap(MK[i + 1], m1x, m1y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    return (a0 * (1 - fr) + a1 * fr) / 255, (k0 * (1 - fr) + k1 * fr) / 255

# ------------------------------------------------------------------ assets
STUDIO = load_img("img/studio.png")
PARCEL = load_img("img/parcel.png")
S = {}
S["ootd"] = sprite_fill(tmask("OUTFIT  OF  THE  DAY", font("SpaceGrotesk", 30, 700), 8)[0], CREAM, shadow=0.6, sblur=6, soff=(3, 2))
FIT_M = tmask("FIT", font("Unbounded", 330, 900), 6)[0]
S["check"] = sprite_fill(tmask("check", font("InstrumentSerif-Italic", 165))[0], LIME, shadow=0.55, sblur=14)
C_M = tmask("C", font("Unbounded", 560, 900))[0]; B_M = tmask("B", font("Unbounded", 560, 900))[0]
S["via"] = chip("Pulli  ·  via GTBuy", tick=True, size=44)
S["detail"] = sprite_fill(tmask("DETAIL", font("Anton-Regular", 250), 18)[0], CREAM, shadow=0.55, sblur=16)
S["cblogo"] = chip("CB Logo", bg=LIME, fg=INK, size=40)
S["thefit"] = sprite_fill(tmask("THE FIT", font("Archivo", 170, 900, 125), 2)[0], LIME, shadow=0.0, stroke=(INK, 6))
S["dior"] = sprite_fill(tmask("Dior", font("InstrumentSerif-Regular", 360), 4)[0], CREAM, shadow=0.6, sblur=20, soff=(16, 8))
S["dior_via"] = chip("Schuhe  ·  via GTBuy", bg=LIME, fg=INK, size=44)
S["best"] = sprite_fill(tmask("BESTELLT  ÜBER", font("SpaceGrotesk", 36, 700), 9)[0], CREAM, shadow=0.0)
GTB_M = tmask("GTBuy", font("Unbounded", 190, 900), 2)[0]
S["parcel"] = card_sprite(PARCEL, 520, 600, 1.03)
S["link"] = link_card(size=50)

def tag_sprite(item, brand, gt):
    """tracked tag: small item label + big brand + optional 'via GTBuy' pill"""
    fi, fb = font("SpaceGrotesk", 26, 700), font("Archivo", 58, 900, 125)
    fg = font("SpaceGrotesk", 24, 700)
    wb = fb.getlength(brand); wi = fi.getlength(item) + 3 * len(item)
    gw = fg.getlength("via GTBuy") + 28 if gt else 0
    pw, ph, pad = int(max(wb, wi) + (gw + 16 if gt else 0) + 52), 128, 40
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 24, fill=(12, 12, 14, 225))
    d.rectangle([pad, pad + 22, pad + 5, pad + ph - 22], fill=(196, 245, 62, 255))
    x = pad + 26
    for ch_ in item: d.text((x, pad + 34), ch_, font=fi, fill=(196, 245, 62, 255), anchor="lm"); x += fi.getlength(ch_) + 3
    d.text((pad + 24, pad + 86), brand, font=fb, fill=(246, 240, 228, 255), anchor="lm")
    if gt:
        gx = pad + 24 + wb + 16
        d.rounded_rectangle([gx, pad + 66, gx + gw, pad + 106], 20, fill=(196, 245, 62, 255))
        d.text((gx + gw / 2, pad + 86), "via GTBuy", font=fg, fill=(12, 12, 14, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 14) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
TAGS2 = [("PULLI", "CB", True, 2.0, "chest"), ("HOSE", "ZARA", False, 2.5, "thigh"), ("SCHUHE", "DIOR", True, 3.0, "foot")]
for it, br, gt, _, _ in TAGS2: S["tag_" + br] = tag_sprite(it, br, gt)

def spec_sprite(num, item, brand, gt, align_right=False):
    f1, f2, f3 = font("SpaceGrotesk", 26, 700), font("InstrumentSerif-Italic", 92), font("SpaceGrotesk", 22, 700)
    top = f"{num}  {item}" + ("   ·   VIA GTBUY" if gt else "")
    w = int(max(f1.getlength(top) + 4 * len(top), f2.getlength(brand))) + 20
    pad = 40; im = Image.new("RGBA", (w + 2 * pad, 150 + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x = pad if not align_right else pad + w - (f1.getlength(top) + 4 * len(top))
    for ch_ in top: d.text((x, pad + 22), ch_, font=f1, fill=(196, 245, 62, 255), anchor="lm"); x += f1.getlength(ch_) + 4
    d.text((pad + (w if align_right else 0), pad + 100), brand, font=f2, fill=(246, 240, 228, 255), anchor="rm" if align_right else "lm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 6, 0), (0, 0), 10) * 0.65; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
SPEC = [("01", "PULLI", "CB", True, 7.5, "chest", False), ("02", "HOSE", "Zara", False, 7.75, "thigh", True),
        ("03", "SCHUHE", "Dior", True, 8.0, "foot", False)]
for n_, it, br, gt, _, _, r in SPEC: S["spec_" + n_] = spec_sprite(n_, it, br, gt, r)
ROWS = [("Pulli", "CB", True), ("Schuhe", "Dior", True), ("Hose", "Zara", False)]
def row_sprite(item, brand, gt):
    f1, f2, fg = font("Archivo", 56, 800, 110), font("InstrumentSerif-Italic", 66), font("SpaceGrotesk", 24, 700)
    pad = 30; w = 760; im = Image.new("RGBA", (w + 2 * pad, 90 + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((pad, pad + 45), item, font=f1, fill=(246, 240, 228, 255), anchor="lm")
    x = pad + f1.getlength(item) + 22
    d.text((x, pad + 47), "— " + brand, font=f2, fill=(246, 240, 228, 210), anchor="lm")
    if gt:
        gw = fg.getlength("GTBuy") + 30; gx = pad + w - gw
        d.rounded_rectangle([gx, pad + 25, gx + gw, pad + 67], 21, fill=(196, 245, 62, 255))
        d.text((gx + gw / 2, pad + 46), "GTBuy", font=fg, fill=(12, 12, 14, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3], (pad, pad)
ROW_S = [row_sprite(*r) for r in ROWS]

def anchor(kind, f):
    if kind == "chest":
        sh = mid(f, 11, 12); hp = mid(f, 23, 24); return sh + 0.32 * (hp - sh)
    if kind == "thigh":
        h, k, _, _ = leftleg(f); return lm(f, h) * 0.45 + lm(f, k) * 0.55
    if kind == "foot":
        _, _, a, fi = leftleg(f); return (lm(f, a) + lm(f, fi)) / 2
    if kind == "sleeve":
        v11, v12 = LM[int(f), 11, 2], LM[int(f), 12, 2]
        s_, e_ = (11, 13) if v11 >= v12 else (12, 14)
        return lm(f, s_) * 0.55 + lm(f, e_) * 0.45

def draw_line(L, p0, p1, alpha, col=CREAM, w=3, dot=True, pulse=0.0):
    m = np.zeros((H, W), np.float32)
    cv2.line(m, tuple(int(v) for v in p0), tuple(int(v) for v in p1), 1.0, w, cv2.LINE_AA)
    if dot:
        cv2.circle(m, tuple(int(v) for v in p1), 9, 1.0, -1, cv2.LINE_AA)
        if pulse > 0: cv2.circle(m, tuple(int(v) for v in p1), int(12 + 26 * pulse), 1.0 - pulse, 2, cv2.LINE_AA)
    m *= alpha
    L[0] *= (1 - m[..., None]); L[0] += col * m[..., None]; L[1] *= (1 - m); L[1] += m

def circle_draw(L, c, r, prog, alpha):
    m = np.zeros((H, W), np.float32)
    if prog > 0:
        cv2.ellipse(m, (int(c[0]), int(c[1])), (int(r * 1.15), int(r)), -12, -90, -90 + 360 * prog, 1.0, 6, cv2.LINE_AA)
    m *= alpha
    L[0] *= (1 - m[..., None]); L[0] += LIME * m[..., None]; L[1] *= (1 - m); L[1] += m

# ------------------------------------------------------------------ per-scene graphics
_cache = {}
def chrome_cached(key, M_, depth, sw):
    k = (key, None if sw is None else round(round(sw / 0.05) * 0.05, 2))
    if k not in _cache: _cache[k] = sprite_chrome(M_, depth=depth, sweep=k[1])
    return _cache[k]

def graphics(t, sc, f, M, back, front):
    sid = sc[0]
    if sid == 1:
        a = win(t, 0.08, 1.42, 0.3, 0.12)
        place(front, S["ootd"], W / 2, 96, alpha=a, s=1 + 0.2 * (1 - ease_out((t - .08) / .5)))
        k = back_out((t - 0.05) / 0.45, 1.8)
        sw = (t - 0.35) / 0.8 if 0.35 <= t <= 1.2 else None
        place(back, chrome_cached("fit", FIT_M, 18, sw), W / 2 - 150, 290, s=(1.6 - 0.6 * k) * (1 + 0.03 * t),
              alpha=clamp(t / 0.06) * a, blur=max(0, 1 - t / 0.2) * 8)
        k2 = ease_out((t - 0.30) / 0.5)
        place(back, S["check"], W / 2 + 330, 330 - (1 - k2) * 40, alpha=k2 * a, rot=-8)
    if sid == 2:
        for n, (it, br, gt, t0, kind) in enumerate(TAGS2):
            a = win(t, t0, 3.42, 0.22, 0.12)
            if a <= 0: continue
            p = apply(M, anchor(kind, f))
            ty = {"chest": 560, "thigh": 1010, "foot": 1360}[kind]
            lx = 70
            sp = S["tag_" + br]; tw = sp[1].shape[1] - 80
            k = ease_out((t - t0) / 0.35)
            place(front, sp, lx - (1 - k) * 60, ty, s=1.3, anchor=(40 / sp[1].shape[1], 0.5), alpha=a)
            e = (lx + tw * 1.3 + 8, ty)
            prog = ease_io((t - t0 - 0.05) / 0.3)
            q = (e[0] + (p[0] - e[0]) * prog, e[1] + (p[1] - e[1]) * prog)
            draw_line(front, e, q, a, dot=prog > 0.95, pulse=clamp((t - t0 - .35) / .5) if t - t0 < 0.85 else 0)
    if sid == 3:
        k = ease_out((t - 3.62) / 0.55); a = win(t, 3.62, 5.42, 0.3, 0.12)
        spC = chrome_cached("C", C_M, 16, None); spB = chrome_cached("B", B_M, 16, None)
        place(back, spC, 250 - (1 - k) * 140, 380, alpha=a, s=0.95 + 0.05 * k)
        place(back, spB, 830 + (1 - k) * 140, 380, alpha=a, s=0.95 + 0.05 * k)
        a2 = win(t, 4.0, 5.42, 0.25, 0.12)
        if a2: place(front, S["via"], W / 2, 120, s=back_out((t - 4.0) / 0.35, 2.0), alpha=a2)
    if sid == 4:
        a = win(t, 5.62, 6.92, 0.35, 0.12)
        k = ease_out((t - 5.62) / 0.6)
        place(back, S["detail"], 950, 820 + (1 - k) * 160, rot=90, alpha=a * 0.95)
        p = apply(M, anchor("chest", f) + np.array([45.0, 40.0]))
        circle_draw(front, p, 110, ease_io((t - 5.85) / 0.4), a)
        a2 = win(t, 6.15, 6.92, 0.2, 0.12)
        if a2:
            e = (max(p[0] - 300, 190), p[1] - 290)
            draw_line(front, (p[0] - 80, p[1] - 85), e, a2, col=LIME, dot=False)
            place(front, S["cblogo"], e[0], e[1] - 10, anchor=(0.5, 0.6), s=back_out((t - 6.15) / 0.3, 2.0), alpha=a2)
    if sid == 5 and t < 8.4:
        a = win(t, 7.18, 8.38, 0.4, 0.08)
        k = ease_out((t - 7.18) / 0.6)
        place(back, S["thefit"], W / 2, 330, rx=-70 * (1 - k), alpha=a)
        for n_, it, br, gt, t0, kind, right in SPEC:
            a2 = win(t, t0, 8.38, 0.22, 0.08)
            if a2 <= 0: continue
            p = apply(M, anchor(kind, f))
            sp = S["spec_" + n_]; w_ = sp[1].shape[1]
            ty = {"chest": 760, "thigh": 1120, "foot": 1430}[kind]
            if right:
                x = W - 60; place(front, sp, x + (1 - ease_out((t - t0) / .35)) * 60, ty, anchor=(1 - 40 / w_, 0.62), alpha=a2)
                e = (W - 60 - (w_ - 80) - 14, ty + 6)
            else:
                x = 60; place(front, sp, x - (1 - ease_out((t - t0) / .35)) * 60, ty, anchor=(40 / w_, 0.62), alpha=a2)
                e = (60 + w_ - 80 + 14, ty + 6)
            prog = ease_io((t - t0 - 0.05) / 0.28)
            draw_line(front, e, (e[0] + (p[0] - e[0]) * prog, e[1] + (p[1] - e[1]) * prog), a2, w=2, dot=prog > .95)
    if sid == 5 and t >= 8.4:
        k = ease_out((t - 8.48) / 0.4); a = win(t, 8.48, 9.0, 0.3, 0.1)
        place(back, S["dior"], 300 - (1 - k) * 80, 1000, s=0.82 + 0.06 * k, alpha=a)
        a2 = win(t, 8.62, 9.0, 0.2, 0.1)
        if a2: place(front, S["dior_via"], 0.62 * W, 1520, s=back_out((t - 8.62) / 0.3, 2.0), alpha=a2)

def endcard(t, comp):
    if t < 9.45: return comp
    L = new_layer()
    k = ease_out((t - 9.45) / 0.5)
    place(L, S["best"], W / 2, 175 - (1 - k) * 20, alpha=k)
    k2 = ease_out((t - 9.55) / 0.55)
    sw = (t - 10.0) / 0.9 if 10.0 <= t <= 11.0 else None
    place(L, chrome_cached("gtb", GTB_M, 14, sw), W / 2, 315, s=0.9 + 0.1 * k2, rx=-60 * (1 - k2), alpha=clamp((t - 9.55) / .1))
    k3 = ease_out((t - 9.80) / 0.55)
    place(L, S["parcel"], W / 2, 750 + (1 - k3) * 120, s=0.94 + 0.06 * k3 + 0.006 * (t - 9.8), rot=-2.5 * (1 - k3) - 1.2, alpha=k3)
    for n, sp in enumerate(ROW_S):
        t0 = 10.15 + n * 0.2; kk = ease_out((t - t0) / 0.35)
        if kk <= 0: continue
        y = 1130 + n * 86
        place(L, check_sprite(26, clamp((t - t0) / 0.25)), 150, y, s=back_out((t - t0) / 0.3, 2.0), alpha=kk)
        place(L, sp, 200 + (1 - kk) * 30, y, anchor=(30 / sp[1].shape[1], 0.5), alpha=kk)
    k4 = ease_out((t - 10.85) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1420, s=back_out((t - 10.85) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

# ------------------------------------------------------------------ compositing helpers
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.24 * np.clip(np.sqrt(((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .46) / (H * .72)) ** 2) - .45, 0, 1) ** 1.5)[..., None]
def refine(frame, m):
    gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    ms = cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)
    return np.clip(cv2.resize(guided(gs, ms), (W, H)), 0, 1)

def studio(t, comp, cm, M, f):
    """Higgsfield studio replaces the room in shot 5; reveal grows out of the floor spotlight."""
    feet = apply(M, (lm(f, 27) + lm(f, 28)) / 2)
    s = M[0, 0]
    z = 1.05 * (1 + (s - 1) * 0.45)
    oy = (feet[1] + 25 - (H / 2 + 0.145 * H * z)) / H
    ox = (feet[0] - W / 2) / W * 0.8
    bg = cover(STUDIO, W, H, z, ox, oy)
    bg = np.clip(bg * 1.12, 0, 1)
    # contact shadow
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (int(feet[0]), int(feet[1] + 18)), (int(150 * s), int(26 * s)), 0, 0, 360, 1.0, -1)
    sh = cv2.GaussianBlur(sh, (0, 0), 18 * s) * 0.55
    bg = bg * (1 - sh[..., None])
    r = ease_out((t - 7.0) / 0.42) * 2400
    d = np.sqrt((XX - feet[0]) ** 2 + ((YY - feet[1]) * 1.6) ** 2)
    circ = np.clip((r - d) / 40, 0, 1)
    ring = np.exp(-((d - r) / 14) ** 2) * (r < 2300) * 0.9
    cmc = np.clip((cv2.erode(cm, np.ones((5, 5), np.uint8)) - 0.25) / 0.6, 0, 1)
    cmc = cv2.GaussianBlur(cmc, (0, 0), 1.2)
    band = np.clip(cm - cmc, 0, 1) * circ
    comp = comp * (1 - 0.65 * band[..., None])
    cm = cmc * circ + cm * (1 - circ)
    bm = ((1 - cm) * circ)[..., None]
    edge = np.clip(cv2.GaussianBlur(1 - cm, (0, 0), 5) * cm * 2.0, 0, 1) * circ * 0.18
    comp = comp * (1 - bm) + bg * bm
    comp = comp * (1 - edge[..., None]) + cv2.GaussianBlur(bg, (0, 0), 8) * edge[..., None]
    comp = comp + ring[..., None] * 0.6
    return comp

def render_shot(t, sc):
    f = src_frame(sc, t)
    frame, m = frame_at(sc, f)
    m = refine(frame, m)
    s, c, sp, oob = cam(sc, t, f)
    M = cam_M(s, c, sp, oob)
    zb = 0.0
    if t < 0.3: zb = 1 - t / 0.3
    if 3.36 <= t < 3.5: zb = ease_in((t - 3.36) / 0.14)
    if 3.5 <= t < 3.75: zb = 1 - ease_out((t - 3.5) / 0.25)
    dx = 0.0
    if 1.38 <= t < 1.5: dx = -ease_in((t - 1.38) / 0.12) * W * 0.6
    if 1.5 <= t < 1.64: dx = (1 - ease_out((t - 1.5) / 0.14)) * W * 0.6
    M2 = M.copy(); M2[0, 2] += dx
    if zb > 0.02:
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(6):
            sk = 1 + zb * 0.07 * k / 5
            Mk = M2.copy(); Mk[:, :2] *= sk; Mk[0, 2] = M2[0, 2] * sk + W / 2 * (1 - sk); Mk[1, 2] = M2[1, 2] * sk + H * .45 * (1 - sk)
            acc += cv2.warpAffine(frame, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cf = acc / 6
    else:
        cf = cv2.warpAffine(frame, M2, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    cm = cv2.warpAffine(m, M2, (W, H), borderMode=cv2.BORDER_CONSTANT if oob else cv2.BORDER_REFLECT)
    if abs(dx) > 1:
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    if sc[0] == 5 and s > 1.6:  # freeze zoom: gentle unsharp to counter the digital zoom softness
        cf = np.clip(cf * 1.35 - cv2.GaussianBlur(cf, (0, 0), 2.0) * 0.35, 0, 1)
    comp = cf
    if sc[0] == 5:
        comp = studio(t, comp, cm, M2, f)
        cm = np.clip((cv2.erode(cm, np.ones((5, 5), np.uint8)) - 0.25) / 0.6, 0, 1)
    back, front = new_layer(), new_layer()
    graphics(t, sc, f, M2, back, front)
    comp = comp * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = comp * (1 - front[1][..., None]) + front[0]
    return comp

def glitch(img, amt, seed):
    r = np.random.default_rng(seed); out = img.copy()
    y = 0
    while y < H:
        h = int(r.integers(20, 140)); dx = int(r.normal(0, 90 * amt))
        out[y:y + h] = np.roll(img[y:y + h], dx, 1); y += h
    sh = int(18 * amt)
    out[..., 0] = np.roll(out[..., 0], sh, 1); out[..., 2] = np.roll(out[..., 2], -sh, 1)
    return out

# ------------------------------------------------------------------ main loop
rng = np.random.default_rng(A + 5)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
for j in range(A, B):
    t = j / FPS
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    sc = scene_at(t)
    comp = render_shot(t, sc)
    # 5 -> 6: defocus dissolve
    if 8.86 <= t < 9.0 or 9.0 <= t < 9.14:
        other = render_shot(t, SC[5] if t < 9.0 else SC[4]) if True else None
        u = ease_io((t - 8.86) / 0.28)
        a_, b_ = (comp, other) if t < 9.0 else (other, comp)
        bl = math.sin(math.pi * u) * 18
        if bl > 0.5: a_ = cv2.GaussianBlur(a_, (0, 0), bl); b_ = cv2.GaussianBlur(b_, (0, 0), bl)
        comp = a_ * (1 - u) + b_ * u
    # 3 -> 4: glitch slices
    if 5.40 <= t < 5.62:
        amt = 1 - abs(t - 5.5) / 0.12
        if amt > 0: comp = glitch(comp, clamp(amt), j)
    # end card: background defocus + darken
    if t >= 9.35:
        k = ease_io((t - 9.35) / 0.6)
        comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.5 * k)
    comp = endcard(t, comp)
    # flashes: hook + freeze shutter
    fl = (0.5 * (1 - t / 0.1) if t < 0.1 else 0) + max(0.0, 0.6 * (1 - abs(t - 8.4) / 0.08))
    if fl > 0: comp = comp * (1 - fl) + np.array([1.0, .98, .95], np.float32) * fl
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
