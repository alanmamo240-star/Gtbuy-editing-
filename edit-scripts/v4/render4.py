"""v4 creator edit — '0 € Shipping Items'.
Everything is code: face-tracked camera, whip/zoom/wipe/push transitions, chrome/3D/outline typography
behind the head (MediaPipe matte), Higgsfield images as background / fullscreen / cards, word-synced captions.
Person pixels are only enhanced (denoise/sharpen/grade upstream) and moved by uniform scale/translate.
Usage: python render4.py <start_frame> <end_frame> <out.mkv> [preview_times_csv]"""
import json, subprocess, sys, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
N = 1087
DUR = N / FPS
SRC, MASK = "enh.mov", "mask.mkv"
A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None

LIME = np.array([196, 245, 62], np.float32) / 255
CREAM = np.array([246, 240, 228], np.float32) / 255
CORAL = np.array([255, 92, 72], np.float32) / 255
INK = np.array([12, 12, 14], np.float32) / 255

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def ease_io(x): x = clamp(x); return x * x * (3 - 2 * x)
def back_out(x, s=1.6):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1
def win(t, t0, t1, fi=0.25, fo=0.25):
    """0..1 envelope with eased in/out"""
    if t < t0 or t > t1: return 0.0
    return min(ease_out((t - t0) / fi) if fi > 0 else 1, ease_io((t1 - t) / fo) if fo > 0 else 1)

# ------------------------------------------------------------------ fonts
FC = {}
def font(name, size, wght=None, wdth=None):
    k = (name, int(size), wght, wdth)
    if k not in FC:
        f = ImageFont.truetype(f"fonts/{name}.ttf", int(size))
        if name == "Archivo": f.set_variation_by_axes([wght or 800, wdth or 100])
        elif name in ("Unbounded", "Syne", "SpaceGrotesk"): f.set_variation_by_axes([wght or 700])
        elif name == "Inter": f.set_variation_by_axes([32, wght or 600])
        FC[k] = f
    return FC[k]

def tmask(text, f, track=0.0, pad=40):
    """text -> float mask (h,w) with tracking; returns mask, baseline y within mask"""
    asc, desc = f.getmetrics()
    ws = [f.getlength(c) for c in text]
    tw = sum(ws) + track * (len(text) - 1)
    im = Image.new("L", (int(tw + 2 * pad), int(asc + desc + 2 * pad)), 0)
    d = ImageDraw.Draw(im); x = pad
    for c, w in zip(text, ws):
        d.text((x, pad + asc), c, font=f, fill=255, anchor="ls"); x += w + track
    return np.asarray(im).astype(np.float32) / 255, pad + asc

def vgrad(h, stops):
    y = np.linspace(0, 1, h)
    cols = np.stack([np.interp(y, [s for s, _ in stops], [c[i] for _, c in stops]) for i in range(3)], -1)
    return cols[:, None, :].astype(np.float32) / 255

CHROME = [(0, (252, 253, 255)), (.36, (182, 188, 198)), (.49, (96, 101, 112)), (.53, (52, 54, 62)),
          (.72, (176, 183, 194)), (1, (248, 249, 252))]

def sprite_chrome(M, depth=14, sweep=None, edge=True):
    """chrome face + 3D extrusion + soft shadow. returns rgb, a"""
    h, w = M.shape
    P = depth + 40
    Mp = np.pad(M, ((P // 2, P), (P // 2, P)))
    hh, ww = Mp.shape
    ext = np.zeros_like(Mp)
    for k in range(1, depth + 1):
        sh = np.roll(np.roll(Mp, int(k * 0.55), 1), k, 0); ext = np.maximum(ext, sh * (1 - 0.0 * k))
    shadow = cv2.GaussianBlur(np.roll(np.roll(Mp, 18, 0), 8, 1), (0, 0), 16) * 0.55
    face = vgrad(hh, CHROME) * np.ones((1, ww, 1), np.float32)
    # vertical gradient based on glyph box, not canvas
    ys = np.where(Mp.max(1) > 0.5)[0]
    if len(ys):
        y0, y1 = ys[0], ys[-1]
        g = vgrad(max(y1 - y0 + 1, 2), CHROME)
        face = np.zeros((hh, ww, 3), np.float32); face[:] = g[0]
        face[y0:y1 + 1] = g; face[y1 + 1:] = g[-1]
    if sweep is not None:
        X, Y = np.meshgrid(np.arange(ww), np.arange(hh))
        d = (X + Y * 0.45) / (ww + hh * 0.45) - sweep
        face = face + np.exp(-(d / 0.035) ** 2)[..., None] * 0.75
    if edge:  # bevel highlight on top edge
        top = np.clip(Mp - np.roll(Mp, 3, 0), 0, 1)
        face = face + top[..., None] * 0.5
    extc = np.array([34, 36, 44], np.float32) / 255
    # extrusion shading: darker further back
    rgb = np.zeros((hh, ww, 3), np.float32); a = np.zeros((hh, ww), np.float32)
    a = shadow * (1 - ext); rgb[:] = 0
    rgb = rgb * (1 - ext[..., None]) + extc * ext[..., None]; a = a * (1 - ext) + ext
    rgb = rgb * (1 - Mp[..., None]) + np.clip(face, 0, 1) * Mp[..., None]; a = a * (1 - Mp) + Mp
    return rgb, a, (P // 2, P // 2)

def sprite_fill(M, color, shadow=0.5, sblur=14, soff=(10, 6), glow=None, stroke=None):
    pad = 50
    Mp = np.pad(M, pad)
    rgb = np.zeros(Mp.shape + (3,), np.float32); a = np.zeros(Mp.shape, np.float32)
    if glow is not None:
        g = cv2.GaussianBlur(Mp, (0, 0), 22) * glow[1]
        rgb = rgb * (1 - g[..., None]) + glow[0] * g[..., None]; a = a * (1 - g) + g
    if shadow > 0:
        s = cv2.GaussianBlur(np.roll(np.roll(Mp, soff[0], 0), soff[1], 1), (0, 0), sblur) * shadow
        rgb = rgb * (1 - s[..., None]); a = a * (1 - s) + s
    if stroke is not None:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * stroke[1] + 1,) * 2)
        sm = cv2.dilate(Mp, k)
        rgb = rgb * (1 - sm[..., None]) + stroke[0] * sm[..., None]; a = a * (1 - sm) + sm
    col = color if np.ndim(color) == 3 and color.shape[0] == Mp.shape[0] else color
    rgb = rgb * (1 - Mp[..., None]) + col * Mp[..., None]; a = a * (1 - Mp) + Mp
    return rgb, a, (pad, pad)

def sprite_outline(M, color, width=4, fill_frac=None, fill_color=None):
    """outline only; optional left->right fill wipe (fill_frac 0..1)"""
    pad = 30
    Mp = np.pad(M, pad)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * width + 1,) * 2)
    ring = np.clip(cv2.dilate(Mp, k) - cv2.erode(Mp, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))), 0, 1)
    rgb = np.zeros(Mp.shape + (3,), np.float32); a = np.zeros(Mp.shape, np.float32)
    if fill_frac is not None and fill_frac > 0:
        xs = np.where(Mp.max(0) > 0.5)[0]
        x0, x1 = (xs[0], xs[-1]) if len(xs) else (0, Mp.shape[1])
        edge = x0 + (x1 - x0) * fill_frac
        X = np.arange(Mp.shape[1])[None, :]
        fm = Mp * np.clip((edge - X) / 6 + 0.5, 0, 1)
        rgb = rgb * (1 - fm[..., None]) + fill_color * fm[..., None]; a = np.maximum(a, fm)
    rgb = rgb * (1 - ring[..., None]) + color * ring[..., None]; a = a * (1 - ring) + ring
    return rgb, a, (pad, pad)

def place(layer, spr, x, y, s=1.0, alpha=1.0, rot=0.0, anchor=(0.5, 0.5), rx=0.0, blur=0.0):
    """composite sprite onto a full-frame (rgb,a) layer. x,y = anchor position on screen.
    rx = rotation around horizontal axis in degrees (perspective flip)"""
    if alpha <= 0.003: return
    rgb, a, _ = spr
    h, w = a.shape
    if blur > 0.4:
        rgb = cv2.GaussianBlur(rgb, (0, 0), blur); a = cv2.GaussianBlur(a, (0, 0), blur)
    ax, ay = w * anchor[0], h * anchor[1]
    pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]) - [ax, ay]
    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = pts @ np.float32([[c, sn], [-sn, c]])
    if abs(rx) > 0.01:
        th = math.radians(rx); f = 1600.0
        yy = pts[:, 1] * math.cos(th); z = pts[:, 1] * math.sin(th)
        pts = np.stack([pts[:, 0] * f / (f + z), yy * f / (f + z)], 1)
    dst = (pts * s + [x, y]).astype(np.float32)
    Hm = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), dst)
    pa = cv2.warpPerspective(np.dstack([rgb * a[..., None], a]), Hm, (W, H), flags=cv2.INTER_LINEAR)
    pr, pa_ = pa[..., :3], pa[..., 3] * alpha
    L_rgb, L_a = layer
    L_rgb *= (1 - pa_[..., None]); L_rgb += pr * alpha
    L_a *= (1 - pa_); L_a += pa_

def new_layer(): return [np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)]

def rounded(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    return np.asarray(m).astype(np.float32) / 255

def load_img(p):
    return np.asarray(Image.open(p).convert("RGB")).astype(np.float32) / 255

def cover(img, w, h, z=1.0, ox=0.0, oy=0.0):
    """crop-to-fill with zoom z and offset (fractions)"""
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih) * z
    M = np.float32([[s, 0, w / 2 - iw * s / 2 + ox * w], [0, s, h / 2 - ih * s / 2 + oy * h]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

IMG = {k: load_img(f"img/{k}.png") for k in ["haul", "coupons", "cardholder", "beanies", "tees"]}

def card_sprite(img, cw, ch, z=1.0, label=None):
    tile = cover(img, cw, ch, z)
    rm = rounded(cw, ch, 36)
    g = np.linspace(0, 1, ch)[:, None] ** 2.4 * 0.5
    tile = tile * (1 - g[..., None])
    pad = 70
    rgb = np.zeros((ch + 2 * pad, cw + 2 * pad, 3), np.float32); a = np.zeros((ch + 2 * pad, cw + 2 * pad), np.float32)
    sh = np.zeros_like(a); sh[pad + 30:pad + ch + 26, pad + 16:pad + cw - 16] = 1
    sh = cv2.GaussianBlur(sh, (0, 0), 26) * 0.5
    a = sh.copy()
    rgb[pad:pad + ch, pad:pad + cw] = tile
    a[pad:pad + ch, pad:pad + cw] = np.maximum(a[pad:pad + ch, pad:pad + cw] * (1 - rm), rm)
    rgb[pad:pad + ch, pad:pad + cw] *= rm[..., None]
    # hairline border
    br = np.zeros((ch, cw), np.uint8); cv2.rectangle(br, (1, 1), (cw - 2, ch - 2), 255, 2)
    br = (br.astype(np.float32) / 255 * rm * 0.35)[..., None]
    rgb[pad:pad + ch, pad:pad + cw] = rgb[pad:pad + ch, pad:pad + cw] * (1 - br) + br
    if label:
        lim = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(lim).text((cw / 2, ch - 46), label, font=font("SpaceGrotesk", 30, 700), fill=255, anchor="mm")
        lm = np.asarray(lim).astype(np.float32)[..., None] / 255
        rgb[pad:pad + ch, pad:pad + cw] = rgb[pad:pad + ch, pad:pad + cw] * (1 - lm) + lm * CREAM
    return rgb, a, (pad, pad)

def chip(text, icon=None, bg=None, fg=None, size=46, tick=False):
    """pill chip with optional check icon; front layer UI"""
    bg = INK if bg is None else bg; fg = CREAM if fg is None else fg
    f = font("Archivo", size, 900, 112)
    tw = f.getlength(text)
    ic = size * 1.05 if tick else 0
    pw, ph = int(tw + 2 * 34 + (ic + 16 if tick else 0)), int(size * 1.9)
    pad = 40
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    bgc = tuple(int(c * 255) for c in bg); fgc = tuple(int(c * 255) for c in fg)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], ph // 2, fill=bgc + (235,))
    x = pad + 34
    if tick:
        cy = pad + ph / 2; r = ic / 2
        d.ellipse([x, cy - r, x + 2 * r, cy + r], fill=tuple(int(c * 255) for c in LIME) + (255,))
        d.line([(x + r * .55, cy + r * .02), (x + r * .9, cy + r * .38), (x + r * 1.5, cy - r * .35)], fill=(12, 12, 14, 255), width=max(4, int(size * .11)), joint="curve")
        x += ic + 16
    d.text((x, pad + ph / 2), text, font=f, fill=fgc + (255,), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 14) * 0.45
    A_ = a + sh * (1 - a)
    rgb = arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4)
    return rgb, A_, (pad, pad)

def link_card(url="beacons.ai/fitsbyjoga", sub="1. Link  →  GTBuy", size=46):
    """dark pill with drawn chain-link icon, url and a small sub line"""
    fu = font("Archivo", size, 800, 104); fs_ = font("SpaceGrotesk", int(size * 0.58), 700)
    tw = max(fu.getlength(url), fs_.getlength(sub))
    ic = int(size * 1.5); pw, ph = int(tw + ic + 3 * 30), int(size * 2.55); pad = 40
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 34, fill=(12, 12, 14, 238))
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 34, outline=(196, 245, 62, 120), width=2)
    # chain icon: two interlocked rounded links, rotated 45 deg
    cs = ic * 2; ci = Image.new("RGBA", (cs, cs), (0, 0, 0, 0)); cd = ImageDraw.Draw(ci)
    lw, lh, r = cs * 0.42, cs * 0.22, cs * 0.11; lc = (196, 245, 62, 255); wdt = max(5, cs // 16)
    cd.rounded_rectangle([cs * 0.14, cs / 2 - lh / 2, cs * 0.14 + lw, cs / 2 + lh / 2], r, outline=lc, width=wdt)
    cd.rounded_rectangle([cs * 0.86 - lw, cs / 2 - lh / 2, cs * 0.86, cs / 2 + lh / 2], r, outline=lc, width=wdt)
    ci = ci.rotate(45, resample=Image.BICUBIC).resize((ic, ic), Image.LANCZOS)
    im.alpha_composite(ci, (pad + 26, int(pad + ph / 2 - ic / 2)))
    x = pad + 30 + ic + 22
    d.text((x, pad + ph * 0.43), url, font=fu, fill=(246, 240, 228, 255), anchor="lm")
    d.text((x, pad + ph * 0.76), sub, font=fs_, fill=(196, 245, 62, 255), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 16) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)

# ------------------------------------------------------------------ prebuilt typography sprites
S = {}
S["label"] = sprite_fill(tmask("HAUL HACKS", font("SpaceGrotesk", 34, 700), 9)[0], CREAM, shadow=0.55, sblur=8, soff=(3, 2))
S["shipping"] = sprite_fill(tmask("SHIPPING", font("Anton-Regular", 150), 14)[0], CREAM, shadow=0.6)
ZERO_M = tmask("0€", font("Unbounded", 470, 900), -10)[0]
S["speichern"] = sprite_fill(tmask("Speichern", font("InstrumentSerif-Italic", 200))[0], CREAM, shadow=0.6, sblur=16)

S["link"] = sprite_fill(tmask("LINK IN BIO", font("Syne", 104, 800), 2)[0], LIME, shadow=0.7, sblur=12)
GT_M = tmask("GTBuy", font("Unbounded", 196, 900), 4)[0]
S["die"] = sprite_fill(tmask("die", font("InstrumentSerif-Italic", 170))[0], CREAM, shadow=0.6)
S["items"] = sprite_fill(tmask("0 € ITEMS", font("Archivo", 158, 900, 125), 2)[0], LIME, shadow=0.0, stroke=(INK, 7))
S["01"] = sprite_outline(tmask("01", font("Unbounded", 230, 900))[0], CREAM, 3)
CARD_LET = []
fC = font("Archivo", 150, 900, 125)
_x = 0
for ch_ in "CARDHOLDER":
    m_ = tmask(ch_, fC, 0, pad=40)[0]; sp_ = sprite_chrome(m_, depth=10); CARD_LET.append((sp_, _x, (40 + sp_[2][0]) / sp_[1].shape[1])); _x += fC.getlength(ch_) + 2
CARD_W = _x
S["02"] = sprite_outline(tmask("02", font("Unbounded", 150, 900))[0], LIME, 3)
MUE_LET = []
fM = font("Anton-Regular", 360)
_x = 0
for ch_ in "MÜTZEN":
    m_ = tmask(ch_, fM, 0, pad=50)[0]; sp_ = sprite_fill(m_, CREAM, shadow=0.75, sblur=22, soff=(22, 10)); MUE_LET.append((sp_, _x, (50 + sp_[2][0]) / sp_[1].shape[1])); _x += fM.getlength(ch_) + 6
MUE_W = _x
S["nicht"] = sprite_fill(tmask("nicht", font("InstrumentSerif-Italic", 150))[0], LIME, shadow=0.7)
S["zerbr"] = sprite_fill(tmask("ZERBRECHLICH", font("Archivo", 104, 900, 100), 1)[0], CREAM, shadow=0.7, stroke=(INK, 5))
S["03"] = sprite_outline(tmask("03", font("Unbounded", 150, 900))[0], LIME, 3)
S["blank"] = sprite_outline(tmask("BLANK", font("Unbounded", 205, 900), 6)[0], CREAM, 4)
TEES_M = tmask("TEES", font("Unbounded", 265, 900), 6)[0]
S["c_coupon"] = card_sprite(IMG["coupons"], 400, 520, 1.05, "GTBuy Coupons")
S["c_card"] = card_sprite(IMG["cardholder"], 390, 510, 1.08, "Cardholder")
S["zuhoeren"] = chip("Und gut zuhören", tick=True, size=44)
S["linkcard"] = link_card(size=54)
S["linkcard_end"] = link_card(sub="Alle Links  ·  @fitsbyjoga", size=50)
S["chip40"] = chip("2× 40 %", bg=LIME, fg=INK, size=60)
S["chip30"] = chip("2× 30 %", bg=LIME, fg=INK, size=60)
S["auf"] = sprite_fill(tmask("AUF SHIPPING", font("SpaceGrotesk", 34, 700), 8)[0], CREAM, shadow=0.7, sblur=6, soff=(3, 2))
S["k_0g"] = chip("≈ 0 g", tick=True, size=46)
S["k_platz"] = chip("Kaum Platz", tick=True, size=46)
S["k_free"] = chip("0 € extra", tick=True, size=46)
S["k_haul"] = chip("Passt in jeden Haul", tick=True, size=44)
S["k_0g2"] = chip("Wiegen nichts", tick=True, size=46)
S["k_cheap"] = chip("Kosten wenig", tick=True, size=46)

# recap panel (static parts)
def recap_rows():
    rows = []
    for name in ["Cardholder", "Mützen", "Blank Tees"]:
        rows.append(sprite_fill(tmask(name, font("Archivo", 66, 800, 110))[0], CREAM, shadow=0.0))
    return rows
RECAP_ROWS = recap_rows()
S["recap_h"] = sprite_fill(tmask("0 € SHIPPING", font("Archivo", 54, 900, 125), 4)[0], LIME, shadow=0.0)
S["recap_s"] = sprite_fill(tmask("IMMER MIT REINPACKEN", font("SpaceGrotesk", 26, 700), 6)[0], CREAM, shadow=0.0)

def check_sprite(r=34, prog=1.0):
    pad = 20; sz = 2 * r + 2 * pad
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([pad, pad, pad + 2 * r, pad + 2 * r], fill=tuple(int(c * 255) for c in LIME) + (255,))
    p1, p2, p3 = (pad + r * .55, pad + r * 1.02), (pad + r * .88, pad + r * 1.36), (pad + r * 1.48, pad + r * .66)
    if prog > 0:
        q = clamp(prog * 2); m1 = (p1[0] + (p2[0] - p1[0]) * q, p1[1] + (p2[1] - p1[1]) * q)
        d.line([p1, m1], fill=(12, 12, 14, 255), width=7)
        if prog > .5:
            q = clamp(prog * 2 - 1); m2 = (p2[0] + (p3[0] - p2[0]) * q, p2[1] + (p3[1] - p2[1]) * q)
            d.line([p2, m2], fill=(12, 12, 14, 255), width=7, joint="curve")
    arr = np.asarray(im).astype(np.float32) / 255
    return arr[..., :3], arr[..., 3], (pad, pad)

# ------------------------------------------------------------------ camera + face tracking
faces = json.load(open("faces.json"))
CUTS = [0, 141, 218, 416, 510, N]
fx = np.array([np.nan if f[1] is None else f[1] + f[3] / 2 for f in faces[:N]], np.float32)
fy = np.array([np.nan if f[1] is None else f[2] + f[4] * 0.45 for f in faces[:N]], np.float32)
def smooth(v, sig):
    out = v.copy()
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        seg = v[a:b].copy(); idx = np.arange(len(seg)); ok = ~np.isnan(seg)
        seg = np.interp(idx, idx[ok], seg[ok]) if ok.any() else np.full(len(seg), np.nan)
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2); k /= k.sum()
        sp = np.pad(seg, 3 * sig, mode="edge"); out[a:b] = np.convolve(sp, k, "valid")
    return out
FX, FY = smooth(fx, 14), smooth(fy, 14)

# camera keys: (t0, t1, s0, s1, follow, screen_y_of_face)
CAM = [(0.00, 4.70, 1.10, 1.17, .65, .47),
       (4.70, 7.27, 1.22, 1.26, .70, .46),
       (7.27, 13.87, 1.06, 1.12, .55, .50),
       (13.87, 17.00, 1.04, 1.09, .50, .50),
       (17.00, 24.16, 1.08, 1.15, .60, .48),
       (24.16, 29.30, 1.05, 1.07, .55, .49),
       (29.30, 30.48, 1.07, 1.17, .65, .47),
       (30.48, 36.30, 1.10, 1.16, .60, .48)]
def cam_scale(t):
    for k, (a, b, s0, s1, fo, sy) in enumerate(CAM):
        if a <= t < b or k == len(CAM) - 1:
            u = ease_io((t - a) / (b - a))
            s = s0 + (s1 - s0) * u
            if k == 6: s = s0 + (s1 - s0) * ease_out((t - 29.30) / 0.6)  # push-in on "zerbrechlich"
            if k > 0 and k != 6 and CAM[k - 1][1] == a and k not in (1, 2, 4):
                prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.5)
            return s, fo, sy
def camera(i, t):
    s, fo, sy = cam_scale(t)
    # hook: punch-out reveal
    if t < 0.5: s = s + 0.30 * (1 - ease_out(t / 0.5))
    # zoom-through into 7.27
    if 7.12 <= t < 7.27: s = s * (1 + 0.28 * ease_in((t - 7.12) / 0.15))
    if 7.27 <= t < 7.65: s = s * (1 + 0.40 * (1 - ease_out((t - 7.27) / 0.38)))
    fxv, fyv = FX[i], FY[i]
    cx = W / 2 + (fxv - W / 2) * fo
    cy_target = fyv  # keep face at screen height sy*H
    x0 = cx - W / (2 * s)
    y0 = cy_target - sy * H / s
    y0 = y0 * fo + (H / 2 - H / (2 * s)) * (1 - fo)
    x0 = clamp(x0, 0, W - W / s); y0 = clamp(y0, 0, H - H / s)
    return s, x0, y0
def cam_matrix(s, x0, y0, dx=0.0, dy=0.0):
    return np.float32([[s, 0, -s * x0 + dx], [0, s, -s * y0 + dy]])
def zoom_blur_amount(t):
    if t < 0.32: return 1 - t / 0.32
    if 7.12 <= t < 7.27: return ease_in((t - 7.12) / 0.15)
    if 7.27 <= t < 7.55: return 1 - ease_out((t - 7.27) / 0.28)
    return 0.0

# ------------------------------------------------------------------ captions
raw = json.load(open("words.json"))
words = []
i = 0
while i < len(raw):
    w = raw[i]; t = w["w"]
    if t == "T" and i + 2 < len(raw) and raw[i + 1]["w"] == "-Buy":
        words.append(dict(w="GTBuy-Account,", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    if t == "T" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Shirts"):
        words.append(dict(w="T-Shirts,", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t == "240": words.append(dict(w="2× 40 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t == "2x30": words.append(dict(w="2× 30 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t == "0" and raw[i + 1]["w"] == "Euro": words.append(dict(w="0 €", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t == "Nummer":  # re-timed from the second transcription pass: "Nummer 3, das sind"
        words += [dict(w="Nummer", s=30.50, e=30.66), dict(w="3,", s=30.66, e=30.80),
                  dict(w="das", s=30.80, e=30.86), dict(w="sind", s=30.86, e=30.90)]
        i += 3; continue
    rep = {"erhält": "erhaltet"}
    words.append(dict(w=rep.get(t, t), s=w["s"], e=w["e"])); i += 1
KEY = {"shipping", "0 €", "abspeichern", "bio", "gtbuy-account", "2× 40 %", "2× 30 %", "haul", "cardholder",
       "nichts", "kostenlos", "mützen", "zerbrechlich", "blank", "t-shirts", "wenig", "zuhören", "easy"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nxt = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nxt is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 14 or (nxt["s"] - w["e"] > 0.35):
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    t0 = c[0]["s"] - 0.05
    nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else DUR
    adj = nxt0 - c[-1]["e"] < 0.45
    t1 = nxt0 if adj else min(c[-1]["e"] + 0.3, nxt0)
    CH.append(dict(words=c, t0=t0, t1=t1, adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]

F_CAP = font("Archivo", 74, 850, 108)
F_KEY = font("InstrumentSerif-Italic", 104)
CAP_Y = 1420
def caption_layer(t, L):
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return
    toks = [clean(w["w"]) for w in ch["words"]]
    keys = [tk.lower() in KEY for tk in toks]
    fs = [F_KEY if k else F_CAP for k in keys]
    sp = 30
    wd = [f.getlength(tk) for f, tk in zip(fs, toks)]
    total = sum(wd) + sp * (len(toks) - 1)
    scale = min(1.0, 980 / total)
    kin = 1.0 if ch["prev_adj"] else ease_out((t - ch["t0"]) / 0.16)
    kout = 1.0 if ch["adj"] else ease_io((ch["t1"] - t) / 0.12)
    a = kin * kout
    if a <= 0: return
    cw, chh = int(total + 120), 230
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    x = 60; base = 150
    for w, tk, wdt, f, k in zip(ch["words"], toks, wd, fs, keys):
        active = w["s"] - 0.03 <= t <= w["e"] + 0.03
        spoken = t > w["e"] + 0.03
        col = (196, 245, 62) if (active or (spoken and k)) else (255, 255, 255)
        al = 1.0 if (active or spoken) else 0.55
        lay = Image.new("RGBA", (int(wdt) + 60, chh), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.text((30, base), tk, font=f, fill=col + (int(255 * al),), anchor="ls",
                stroke_width=3 if not k else 2, stroke_fill=(10, 10, 12, int(200 * al)))
        if active:
            pk = clamp((t - w["s"] + 0.03) / 0.16)
            sc = 1.0 + 0.07 * math.sin(math.pi * pk) * (1.2 if k else 1)
            if sc > 1.003:
                nw, nh = int(lay.width * sc), int(lay.height * sc)
                lay = lay.resize((nw, nh), Image.BICUBIC)
                img.alpha_composite(lay, (int(x - 30 - (nw - wdt - 60) / 2), int(-(nh - chh) * base / chh)))
                x += wdt + sp; continue
        img.alpha_composite(lay, (int(x - 30), 0)); x += wdt + sp
    arr = np.asarray(img).astype(np.float32) / 255
    ca = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(ca, 6, 0), (0, 0), 10) * 0.55
    A_ = ca + sh * (1 - ca)
    rgb = arr[..., :3] * ca[..., None] / np.maximum(A_[..., None], 1e-4)
    rise = (1 - ease_out((t - ch["t0"]) / 0.18)) * 22 if not ch["prev_adj"] else 0
    place(L, (rgb, A_, (0, 0)), W / 2, CAP_Y + rise, s=scale, alpha=a)

# ------------------------------------------------------------------ graphics helpers
def bookmark_sprite(fill, pop=0.0):
    sz = 220; im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    poly = [(60, 30), (160, 30), (160, 190), (110, 150), (60, 190)]
    lc = tuple(int(c * 255) for c in LIME)
    if fill > 0:
        mk = Image.new("L", (sz, sz), 0); ImageDraw.Draw(mk).polygon(poly, fill=255)
        fl = Image.new("L", (sz, sz), 0); ImageDraw.Draw(fl).rectangle([0, 190 - 170 * fill, sz, sz], fill=255)
        mm = Image.fromarray(np.minimum(np.asarray(mk), np.asarray(fl)))
        im.paste(Image.new("RGBA", (sz, sz), lc + (255,)), (0, 0), mm)
    d.line(poly + [poly[0]], fill=lc + (255,), width=10, joint="curve")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 8, 0), (0, 0), 10) * .5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)

def arrow_layer(L, prog, alpha, x0, y0, x1, y1):
    """animated drawn curved arrow from (x0,y0) to (x1,y1)"""
    if prog <= 0 or alpha <= 0: return
    im = Image.new("L", (W, H), 0); d = ImageDraw.Draw(im)
    pts = []
    for k in range(41):
        u = k / 40 * prog
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * (x0 + 120) + u * u * x1
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * ((y0 + y1) / 2) + u * u * y1
        pts.append((bx, by))
    d.line(pts, fill=255, width=9, joint="curve")
    if prog > 0.85:
        (ax, ay), (bx, by) = pts[-2], pts[-1]; ang = math.atan2(by - ay, bx - ax)
        for da in (2.6, -2.6):
            d.line([(bx, by), (bx + 34 * math.cos(ang + da), by + 34 * math.sin(ang + da))], fill=255, width=9)
    m = np.asarray(im).astype(np.float32) / 255 * alpha
    L[0] *= (1 - m[..., None]); L[0] += LIME * m[..., None]; L[1] *= (1 - m); L[1] += m

def strike_layer(L, cx, cy, w, prog, alpha):
    if prog <= 0: return
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).line([(cx - w / 2, cy + 8), (cx - w / 2 + w * prog, cy - 8)], fill=255, width=14)
    m = np.asarray(im).astype(np.float32) / 255 * alpha
    L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def glass_panel(comp, x0, y0, x1, y1, alpha):
    if alpha <= 0: return comp
    x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
    roi = comp[y0:y1, x0:x1]
    bl = cv2.GaussianBlur(roi, (0, 0), 24) * 0.45 + INK * 0.35
    rm = rounded(x1 - x0, y1 - y0, 44)[..., None] * alpha
    out = comp.copy(); out[y0:y1, x0:x1] = roi * (1 - rm) + bl * rm
    br = np.zeros((y1 - y0, x1 - x0), np.uint8); cv2.rectangle(br, (1, 1), (x1 - x0 - 2, y1 - y0 - 2), 255, 2)
    br = (br.astype(np.float32) / 255 * rounded(x1 - x0, y1 - y0, 44) * 0.22 * alpha)[..., None]
    out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - br) + br
    return out

# ------------------------------------------------------------------ scene graphics
def scene_layers(t, back, front):
    # ---- HOOK
    a = win(t, 0.12, 4.55, 0.35, 0.18)
    if a: place(front, S["label"], W / 2 + 0, 112, s=1.0 + 0.25 * (1 - ease_out((t - .12) / .5)), alpha=a)
    a = win(t, 1.38, 4.55, 0.3, 0.18)
    if a:
        k = ease_out((t - 1.38) / 0.45)
        place(back, S["shipping"], W / 2, 238 + (1 - k) * 40, s=1.0 + 0.012 * (t - 1.38), alpha=a, blur=(1 - k) * 8)
    if 1.70 <= t <= 4.62:
        k = back_out((t - 1.72) / 0.42, 2.0)
        sw = (t - 2.05) / 0.9 if 2.05 <= t <= 3.2 else None
        key = round(round(sw / 0.04) * 0.04, 2) if sw is not None else None
        if key not in S.setdefault("_zero", {}): S["_zero"][key] = sprite_chrome(ZERO_M, depth=22, sweep=key)
        spr = S["_zero"][key]
        out = ease_io((4.62 - t) / 0.2)
        s = (1.9 - 0.9 * k) * (1 + 0.025 * (t - 1.72)) * (1 + 0.2 * (1 - out))
        place(back, spr, W / 2 + 6, 445, s=s * 0.94, alpha=clamp((t - 1.72) / 0.08) * out, blur=max(0, 1 - (t - 1.72) / 0.18) * 10)
    # ---- SAVE
    a = win(t, 4.82, 7.18, 0.3, 0.2)
    if a:
        k = ease_out((t - 4.82) / 0.55)
        place(back, S["speichern"], 40 - (1 - k) * 160, 300, anchor=(0.0, 0.5), alpha=a, s=1.0 + 0.01 * (t - 4.8))
        fill = ease_out((t - 5.78) / 0.3)
        pop = math.sin(math.pi * clamp((t - 5.78) / 0.25)) * 0.18
        place(front, bookmark_sprite(fill), 935, 250, s=(0.6 + 0.4 * k) * (1 + pop), alpha=a)
        a2 = win(t, 6.40, 7.18, 0.3, 0.2)
        if a2: place(front, S["zuhoeren"], 40, 450, anchor=(0.0, 0.5), alpha=a2, s=1 + 0.1 * (1 - ease_out((t - 6.4) / .4)))
    # ---- LINK IN BIO + GTBUY
    a = win(t, 8.50, 9.95, 0.3, 0.22)
    if a:
        k = ease_out((t - 8.50) / 0.45)
        place(front, S["link"], W / 2 - 20, 250 - (1 - k) * 50, s=0.9, alpha=a)
        arrow_layer(front, ease_io((t - 8.65) / 0.45), a, 850, 225, 950, 70)
        a3 = win(t, 8.70, 9.95, 0.25, 0.22)
        if a3: place(front, S["linkcard"], W / 2, 410, s=back_out((t - 8.70) / 0.4, 1.8), alpha=a3)
    if 9.88 <= t <= 11.35:
        prog = ease_io((t - 10.0) / 0.55)
        key = round(round(prog / 0.03) * 0.03, 2)
        if key not in S.setdefault("_gt", {}): S["_gt"][key] = sprite_outline(GT_M, CREAM, 4, key, LIME)
        k = ease_out((t - 9.88) / 0.5); out = ease_io((11.35 - t) / 0.25)
        place(back, S["_gt"][key], W / 2, 470, s=(0.86 + 0.14 * k) * (1 + 0.02 * (t - 9.9)), alpha=k * out, rx=(1 - k) * 55)
    a = win(t, 11.05, 13.82, 0.45, 0.25)
    if a:
        k = ease_out((t - 11.05) / 0.6)
        place(back, S["c_coupon"], 835 + (1 - k) * 200, 470, s=0.92 + 0.08 * k, rot=4 * (1 - k) + 2.5, alpha=a)
    for key_, t0, y in (("chip40", 11.42, 330), ("chip30", 12.28, 470)):
        a = win(t, t0 - 0.04, 13.82, 0.2, 0.25)
        if a: place(front, S[key_], 60, y, anchor=(0, 0.5), s=back_out((t - t0 + .04) / 0.35, 2.2), alpha=a)
    a = win(t, 12.95, 13.82, 0.25, 0.25)
    if a: place(front, S["auf"], 100, 575, anchor=(0, 0.5), alpha=a)
    # ---- HAUL TITLE (perspective flip)
    a = win(t, 14.55, 16.92, 0.1, 0.22)
    if a:
        k = ease_out((t - 14.55) / 0.6)
        place(back, S["die"], W / 2 - 250, 300, alpha=a * k, s=1.0)
        k2 = ease_out((t - 14.75) / 0.7)
        place(back, S["items"], W / 2, 450, rx=-75 * (1 - k2), s=1.0 + 0.02 * (t - 14.75), alpha=a * clamp((t - 14.75) / 0.15))
    # ---- 01 CARDHOLDER
    a = win(t, 17.05, 19.45, 0.4, 0.3)
    if a:
        k = ease_out((t - 17.05) / 0.6)
        place(back, S["01"], W / 2, 330, s=0.8 + 0.2 * k, alpha=a * 0.95)
        sc = min(1.0, 960 / CARD_W)
        x0 = W / 2 - CARD_W * sc / 2
        for n, (spr, ox, axf) in enumerate(CARD_LET):
            kk = ease_out((t - 17.98 - n * 0.035) / 0.5)
            if kk <= 0: continue
            place(back, spr, x0 + ox * sc, 560 + (1 - kk) * 70, s=sc, anchor=(axf, 0.62), alpha=a * kk, blur=(1 - kk) * 6)
    a = win(t, 19.30, 24.00, 0.5, 0.25)
    if a:
        k = ease_out((t - 19.30) / 0.6)
        place(back, S["c_card"], 838, 455 + (1 - k) * 80, s=0.92 + 0.08 * k + 0.008 * (t - 19.3), rot=-3, alpha=a)
    for key_, t0, y in (("k_0g", 19.70, 300), ("k_platz", 20.94, 410), ("k_free", 23.36, 520)):
        a = win(t, t0 - 0.04, 24.00, 0.2, 0.25)
        if a: place(front, S[key_], 50, y, anchor=(0, 0.5), s=back_out((t - t0 + .04) / 0.35, 2.0), alpha=a)
    # ---- MÜTZEN fullscreen headline drawn in fullscreen() ; after: chips + ZERBRECHLICH
    a = win(t, 27.30, 29.20, 0.2, 0.25)
    if a: place(front, S["k_haul"], W / 2, 330, s=back_out((t - 27.26) / 0.35, 2.0), alpha=a)
    a = win(t, 29.30, 30.40, 0.25, 0.1)
    if a:
        k = ease_out((t - 29.30) / 0.4)
        place(back, S["nicht"], W / 2 - 240, 330, alpha=a * k)
        place(back, S["zerbr"], W / 2, 470 + (1 - k) * 40, alpha=a, s=1 + 0.03 * (t - 29.3))
        strike_layer(back, W / 2, 470, 900, ease_io((t - 29.95) / 0.22), a)
    # ---- after tees: card + chips
    for key_, t0, y in (("k_0g2", 32.30, 300), ("k_cheap", 33.10, 410)):
        a = win(t, t0 - 0.04, 34.05, 0.2, 0.22)
        if a: place(front, S[key_], 50, y, anchor=(0, 0.5), s=back_out((t - t0 + .04) / 0.35, 2.0), alpha=a)

def fullscreen(t, comp, m, cam):
    """Higgsfield fullscreen visuals with their own transitions. Returns comp, person_visible_mask_scale"""
    # beanies: diagonal wipe in 24.30, push-up out 25.78
    if 24.28 <= t < 25.98:
        img = cover(IMG["beanies"], W, H, 1.10 - 0.06 * clamp((t - 24.28) / 1.7), 0, 0.02)
        g = np.linspace(0, 1, H)[:, None, None]
        img = img * (0.72 + 0.28 * g)  # darker top for type
        X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        if t < 24.62:
            p = ease_io((t - 24.28) / 0.34)
            d = (X * 0.5 + Y) - ((1 - p) * (H + W * 0.5 + 200) - 100)
            wm = np.clip(d / 10, 0, 1)
            edge = np.exp(-(d / 7) ** 2) * (p < 1)
        else:
            wm = np.ones((H, W), np.float32); edge = 0
        dy = 0
        if t >= 25.62:
            p = ease_in((t - 25.62) / 0.36); dy = -p * H
            M = np.float32([[1, 0, 0], [0, 1, dy]])
            img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_CONSTANT)
            wm = cv2.warpAffine(wm.astype(np.float32), M, (W, H), borderValue=0)
            if p > 0.05:
                k = int(5 + p * 60) | 1; img = cv2.blur(img, (1, k)); wm = cv2.blur(wm, (1, k))
        T = new_layer()
        place(T, S["02"], W / 2, 215 + dy, s=0.9 + 0.1 * ease_out((t - 24.40) / 0.5), alpha=clamp((t - 24.40) / 0.2))
        sc = min(1.0, 960 / MUE_W); x0 = W / 2 - MUE_W * sc / 2
        for n, (spr, ox, axf) in enumerate(MUE_LET):
            kk = ease_out((t - 24.45 - n * 0.045) / 0.45)
            if kk <= 0: continue
            place(T, spr, x0 + ox * sc, 650 + (1 - kk) * 120 + dy, s=sc, anchor=(axf, 0.7), alpha=kk, blur=(1 - kk) * 5)
        img = img * (1 - T[1][..., None]) + T[0]
        wmf = wm[..., None]
        comp = comp * (1 - wmf) + img * wmf
        if np.ndim(edge): comp = comp * (1 - edge[..., None]) + LIME * edge[..., None]
    # tees: push-down in 30.12, shrink to card 31.88 -> stays to 34.0
    if 30.10 <= t < 34.20:
        if t < 31.88:
            img = cover(IMG["tees"], W, H, 1.12 - 0.07 * clamp((t - 30.1) / 1.8), 0, 0.03)
            g = np.linspace(0, 1, H)[:, None, None]; img = img * (0.70 + 0.30 * g)
            T = new_layer()
            k = ease_out((t - 30.30) / 0.55)
            place(T, S["03"], W / 2, 240, alpha=clamp((t - 30.3) / .2))
            place(T, S["blank"], W / 2, 420, s=0.9 + 0.1 * k, alpha=k)
            k2 = ease_out((t - 30.50) / 0.6)
            sw = round(round((t - 30.9) / 0.8 / 0.04) * 0.04, 2) if 30.9 <= t <= 31.8 else None
            if sw not in S.setdefault("_tees", {}): S["_tees"][sw] = sprite_chrome(TEES_M, depth=18, sweep=sw)
            place(T, S["_tees"][sw], W / 2, 640, rx=80 * (1 - k2), alpha=clamp((t - 30.5) / .12))
            img = img * (1 - T[1][..., None]) + T[0]
            p = ease_out((t - 30.10) / 0.30)
            dy = -(1 - p) * H
            if p < 1:
                Mi = np.float32([[1, 0, 0], [0, 1, dy]])
                img = cv2.warpAffine(img, Mi, (W, H), borderMode=cv2.BORDER_REFLECT)
                k_ = int(5 + (1 - p) * 70) | 1; img = cv2.blur(img, (1, k_))
                # the person frame is pushed down
                comp = cv2.warpAffine(comp, np.float32([[1, 0, 0], [0, 1, H * p]]), (W, H), borderMode=cv2.BORDER_REFLECT)
                comp = cv2.blur(comp, (1, k_))
                cut = int(clamp(H + dy, 0, H))
                comp[:cut] = img[:cut]
            else:
                comp = img
        else:
            # shrink into a card (top-right) — match-cut continuity, then exit right at 33.85
            p = ease_io((t - 31.88) / 0.42)
            cw, ch_ = int(W + (380 - W) * p), int(H + (500 - H) * p)
            cx = W / 2 + (835 - W / 2) * p; cy = H / 2 + (460 - H / 2) * p
            if t > 33.80: cx += ease_in((t - 33.80) / 0.38) * 700
            tile = cover(IMG["tees"], cw, ch_, 1.05, 0, 0.03)
            r = int(36 * p)
            rm = rounded(cw, ch_, max(r, 1)) if r > 0 else np.ones((ch_, cw), np.float32)
            Lr = new_layer()
            pad = 70
            rgb = np.zeros((ch_ + 2 * pad, cw + 2 * pad, 3), np.float32); al = np.zeros((ch_ + 2 * pad, cw + 2 * pad), np.float32)
            sh = np.zeros_like(al); sh[pad + 30:pad + ch_ + 26, pad + 16:pad + cw - 16] = 1
            sh = cv2.GaussianBlur(sh, (0, 0), 26) * 0.5 * p
            al[:] = sh; rgb[pad:pad + ch_, pad:pad + cw] = tile * rm[..., None]
            al[pad:pad + ch_, pad:pad + cw] = np.maximum(sh[pad:pad + ch_, pad:pad + cw] * (1 - rm), rm)
            place(Lr, (rgb, al, (pad, pad)), cx, cy, rot=3 * p)
            # behind the head once it is small
            pb = ease_io((p - 0.9) / 0.1)
            bm = (1 - m * pb)[..., None]
            aa = Lr[1][..., None] * bm
            comp = comp * (1 - aa) + Lr[0] * bm
    return comp

def haul_bg(t, comp, frame_cam, m):
    """13.87–17.00: Higgsfield haul flat-lay replaces the room; circular reveal from the head."""
    if not (13.87 <= t < 17.00): return comp
    bg = cover(IMG["haul"], W, H, 1.12 - 0.08 * clamp((t - 13.87) / 3.1), 0, 0.0)
    bg = cv2.GaussianBlur(bg, (0, 0), 2.2) * 0.62
    yy, xx = np.ogrid[:H, :W]
    r = ease_out((t - 13.87) / 0.42) * 2300
    cx, cy = W / 2, 900
    circ = np.clip((r - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)) / 30, 0, 1).astype(np.float32)
    ring = np.exp(-((np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - r) / 10) ** 2).astype(np.float32) * (r < 2200)
    out_k = ease_io((17.0 - t) / 0.12)
    bm = (1 - m) * circ * out_k
    # light wrap: bleed a little of the bg into the person edge
    edge = np.clip(cv2.GaussianBlur(1 - m, (0, 0), 6) * m * 2.2, 0, 1) * circ * out_k * 0.35
    comp = comp * (1 - bm[..., None]) + bg * bm[..., None]
    comp = comp * (1 - edge[..., None]) + cv2.GaussianBlur(bg, (0, 0), 8) * edge[..., None]
    comp = comp * (1 - ring[..., None] * 0.8) + LIME * ring[..., None] * 0.8
    return comp

def recap(t, comp):
    if t < 34.10: return comp
    a = ease_out((t - 34.10) / 0.35)
    y0 = 100 - (1 - a) * 40
    comp = glass_panel(comp, 110, y0, 970, y0 + 430, a)
    L = new_layer()
    place(L, S["recap_h"], 170, y0 + 82, anchor=(0, 0.5), alpha=a)
    place(L, S["recap_s"], 170, y0 + 140, anchor=(0, 0.5), alpha=a * 0.8)
    for n, spr in enumerate(RECAP_ROWS):
        t0 = 34.32 + n * 0.25
        k = ease_out((t - t0) / 0.3)
        if k <= 0: continue
        yy = y0 + 222 + n * 80
        place(L, check_sprite(30, clamp((t - t0) / 0.25)), 200, yy, s=back_out((t - t0) / 0.3, 2.0), alpha=k)
        place(L, spr, 260 + (1 - k) * 30, yy, anchor=(0, 0.55), alpha=k)
    kc = ease_out((t - 35.10) / 0.4)
    if kc > 0: place(L, S["linkcard_end"], W / 2, 1270 + (1 - kc) * 30, s=back_out((t - 35.10) / 0.4, 1.8), alpha=kc)
    return comp * (1 - L[1][..., None]) + L[0]

# ------------------------------------------------------------------ guided filter for mask edges
def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=8, eps=2e-3):
    mI, mp_ = box(I, r), box(p, r)
    a = (box(I * p, r) - mI * mp_) / (box(I * I, r) - mI * mI + eps); b = mp_ - a * mI
    return box(a, r) * I + box(b, r)

VIGN = None
def vignette():
    global VIGN
    if VIGN is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.72)) ** 2)
        VIGN = (1 - 0.22 * np.clip(d - 0.45, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return VIGN

FREEZE = 1072  # 35.73 s, after the last word
rng = np.random.default_rng(A + 11)

# ------------------------------------------------------------------ main loop
sel = f"select='between(n\\,{A}\\,{B - 1})'"
dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", MASK, "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
frozen = None
for i in range(A, B):
    fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
    if len(fb) < W * H * 3:
        if frozen is None: break
    t = i / FPS
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    if i >= FREEZE and frozen is not None:
        frame, m = frozen
    else:
        frame = np.frombuffer(fb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
        gs = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
        ms = cv2.resize(m, (540, 960), interpolation=cv2.INTER_AREA)
        m = np.clip(cv2.resize(guided(gs, ms), (W, H)), 0, 1)
        if i == FREEZE: frozen = (frame, m)
    fi = min(i, FREEZE)
    s, x0, y0 = camera(fi, t)
    if i >= FREEZE:  # freeze-frame: slow push + settle
        s *= 1 + 0.05 * ease_out((t - FREEZE / FPS) / 0.5)
    dx = 0.0
    if 4.58 <= t < 4.70: dx = -ease_in((t - 4.58) / 0.12) * W * 0.55
    if 4.70 <= t < 4.84: dx = (1 - ease_out((t - 4.70) / 0.14)) * W * 0.55
    M = cam_matrix(s, x0, y0, dx)
    zb = zoom_blur_amount(t)
    if zb > 0.02:  # radial zoom blur = average of slightly different scales
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(6):
            sk = 1 + zb * 0.06 * k / 5
            Mk = M.copy(); Mk[:, :2] *= sk; Mk[0, 2] = M[0, 2] * sk + W / 2 * (1 - sk); Mk[1, 2] = M[1, 2] * sk + H * .45 * (1 - sk)
            acc += cv2.warpAffine(frame, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cf = acc / 6
    else:
        cf = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    cm = cv2.warpAffine(m, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if abs(dx) > 1:  # whip-pan motion blur
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    comp = haul_bg(t, cf.copy(), cf, cm)
    back, front = new_layer(), new_layer()
    scene_layers(t, back, front)
    bk = back[1][..., None] * (1 - cm[..., None])
    comp = comp * (1 - bk) + back[0] * (1 - cm[..., None])
    comp = fullscreen(t, comp, cm, (s, x0, y0))
    comp = comp * (1 - front[1][..., None]) + front[0]
    if i >= FREEZE:  # subtle 'paused' look on freeze
        p = ease_out((t - FREEZE / FPS) / 0.3)
        g = comp.mean(2, keepdims=True); comp = comp * (1 - 0.25 * p) + g * 0.25 * p
    comp = recap(t, comp)
    cap = new_layer(); caption_layer(t, cap)
    comp = comp * (1 - cap[1][..., None]) + cap[0]
    # flash transitions (17.00 cut, hook start)
    fl = max(0.0, 0.55 * (1 - abs(t - 17.0) / 0.12)) + (0.35 * (1 - t / 0.12) if t < 0.12 else 0)
    if fl > 0: comp = comp * (1 - fl) + np.array([1.0, 0.97, 0.92], np.float32) * fl
    comp = comp * vignette()
    comp += rng.normal(0, 0.012, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)  # fine grain
    if t > DUR - 0.25: comp *= ease_io((DUR - t) / 0.25)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if PREVIEW is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=88)
    else:
        enc.stdin.write(out.tobytes())
        if (i - A) % 60 == 0: print(A, "frame", i, flush=True)
if PREVIEW is None: enc.stdin.close(); enc.wait()
print("done", A, B)
