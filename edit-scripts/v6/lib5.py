import json, subprocess, sys, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30

LIME = np.array([255, 214, 10], np.float32) / 255
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


def card_sprite(img, cw, ch, z=1.0, label=None, label_top=False):
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
        ly = 50 if label_top else ch - 46; lf = font("SpaceGrotesk", 30, 700); lw = lf.getlength(label)
        pim = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(pim).rounded_rectangle([cw / 2 - lw / 2 - 20, ly - 26, cw / 2 + lw / 2 + 20, ly + 26], 26, fill=215)
        pm = np.asarray(pim).astype(np.float32)[..., None] / 255
        rgb[pad:pad + ch, pad:pad + cw] = rgb[pad:pad + ch, pad:pad + cw] * (1 - pm) + INK * pm
        lim = Image.new("L", (cw, ch), 0)
        ImageDraw.Draw(lim).text((cw / 2, 50 if label_top else ch - 46), label, font=font("SpaceGrotesk", 30, 700), fill=255, anchor="mm")
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
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 34, outline=(255, 214, 10, 120), width=2)
    # chain icon: two interlocked rounded links, rotated 45 deg
    cs = ic * 2; ci = Image.new("RGBA", (cs, cs), (0, 0, 0, 0)); cd = ImageDraw.Draw(ci)
    lw, lh, r = cs * 0.42, cs * 0.22, cs * 0.11; lc = (255, 214, 10, 255); wdt = max(5, cs // 16)
    cd.rounded_rectangle([cs * 0.14, cs / 2 - lh / 2, cs * 0.14 + lw, cs / 2 + lh / 2], r, outline=lc, width=wdt)
    cd.rounded_rectangle([cs * 0.86 - lw, cs / 2 - lh / 2, cs * 0.86, cs / 2 + lh / 2], r, outline=lc, width=wdt)
    ci = ci.rotate(45, resample=Image.BICUBIC).resize((ic, ic), Image.LANCZOS)
    im.alpha_composite(ci, (pad + 26, int(pad + ph / 2 - ic / 2)))
    x = pad + 30 + ic + 22
    d.text((x, pad + ph * 0.43), url, font=fu, fill=(246, 240, 228, 255), anchor="lm")
    d.text((x, pad + ph * 0.76), sub, font=fs_, fill=(255, 214, 10, 255), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 16) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)


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


def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=8, eps=2e-3):
    mI, mp_ = box(I, r), box(p, r)
    a = (box(I * p, r) - mI * mp_) / (box(I * I, r) - mI * mI + eps); b = mp_ - a * mI
    return box(a, r) * I + box(b, r)

