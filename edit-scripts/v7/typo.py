"""Typography engine: text masks + premium styles (chrome, 3D extrusion, outline/echo, gradient + glow)
and perspective transforms. All layers are float32 RGBA in [0,1]."""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

F = "fonts/"
IN = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
FONTS = dict(  # name -> (file, variable-weight or None)
    anton=(F + "Anton.ttf", None), unb=(F + "Unbounded.ttf", 900), unb6=(F + "Unbounded.ttf", 600),
    mont=(F + "Montserrat.ttf", 800), montb=(F + "Montserrat.ttf", 900), montbi=(F + "Montserrat-Italic.ttf", 900),
    serif=(F + "InstrumentSerif.ttf", None), serifi=(F + "InstrumentSerif-Italic.ttf", None), grotesk=(F + "SpaceGrotesk.ttf", 700),
    inter=(IN.format("Bold"), None), inters=(IN.format("SemiBold"), None), interx=(IN.format("ExtraBold"), None),
    interb=(IN.format("Black"), None), interm=(IN.format("Medium"), None))
_fc = {}
def font(name, size):
    k = (name, int(size))
    if k not in _fc:
        p, wg = FONTS[name]; f = ImageFont.truetype(p, int(size))
        if wg is not None: f.set_variation_by_axes([wg])
        _fc[k] = f
    return _fc[k]

def text_mask(text, fname, size, tracking=0.0, pad=40):
    """Tight L-mask (float 0..1) of a single text line with letter tracking (in em)."""
    f = font(fname, size); sp = tracking * size
    w = int(sum(f.getlength(c) for c in text) + sp * max(len(text) - 1, 0)) + 2 * pad
    asc, desc = f.getmetrics(); h = asc + desc + 2 * pad
    im = Image.new("L", (w, h), 0); d = ImageDraw.Draw(im); x = pad
    for c in text:
        d.text((x, pad), c, font=f, fill=255); x += f.getlength(c) + sp
    m = np.asarray(im).astype(np.float32) / 255
    ys, xs = np.where(m > 0.02)
    y0, y1, x0, x1 = max(ys.min() - pad // 2, 0), ys.max() + pad // 2, max(xs.min() - pad // 2, 0), xs.max() + pad // 2
    return m[y0:y1, x0:x1].copy()

def stack(masks, gap=0.12, align="center"):
    """Stack several masks vertically."""
    W = max(m.shape[1] for m in masks); H = sum(m.shape[0] for m in masks) + int(gap * masks[0].shape[0]) * (len(masks) - 1)
    out = np.zeros((H, W), np.float32); y = 0
    for m in masks:
        x = (W - m.shape[1]) // 2 if align == "center" else 0
        out[y:y + m.shape[0], x:x + m.shape[1]] = np.maximum(out[y:y + m.shape[0], x:x + m.shape[1]], m); y += m.shape[0] + int(gap * masks[0].shape[0])
    return out

def pad_mask(m, p):
    return np.pad(m, p)

def _rgba(rgb, a): return np.dstack([rgb, a]).astype(np.float32)

def solid(m, color, pad=0):
    m = pad_mask(m, pad); return _rgba(np.ones(m.shape + (3,), np.float32) * np.array(color, np.float32) / 255, m)

def gradient(m, top, bottom, pad=0, angle=0.0):
    m = pad_mask(m, pad); h, w = m.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = (yy / max(h - 1, 1)) * np.cos(angle) + (xx / max(w - 1, 1)) * np.sin(angle)
    t = np.clip(t, 0, 1)[..., None]
    rgb = (np.array(top, np.float32) * (1 - t) + np.array(bottom, np.float32) * t) / 255
    return _rgba(rgb, m)

def outline(m, width=4, color=(255, 255, 255), pad=8):
    m = pad_mask(m, pad); k = np.ones((2 * width + 1, 2 * width + 1), np.uint8)
    dil = cv2.dilate((m > 0.5).astype(np.uint8), k).astype(np.float32)
    ero = (m > 0.5).astype(np.float32)
    ring = np.clip(cv2.GaussianBlur(dil - ero, (0, 0), 0.8), 0, 1)
    return _rgba(np.ones(m.shape + (3,), np.float32) * np.array(color, np.float32) / 255, ring)

def chrome(m, pad=24, dark=False):
    """Metallic chrome: banded reflection gradient + bevel lighting + dark rim."""
    m = pad_mask(m, pad); h, w = m.shape
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None] * np.ones((1, w), np.float32)
    # horizon-style chrome bands
    bands = np.interp(y, [0, .38, .5, .52, .7, 1], [0.97, 0.80, 0.38, 0.22, 0.62, 0.93]).astype(np.float32)
    if dark: bands = bands * 0.75
    # bevel from blurred mask gradient (light from top-left)
    b = cv2.GaussianBlur(m, (0, 0), max(2, h / 60))
    gx = cv2.Sobel(b, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(b, cv2.CV_32F, 0, 1, ksize=3)
    light = np.clip(-(gx * -0.6 + gy * -0.8) * 6, -0.5, 0.6)
    lum = np.clip(bands + light, 0, 1)
    tint = np.dstack([lum * 0.97, lum * 0.99, lum * 1.03])
    rim = outline(m[pad:-pad, pad:-pad], 2, (40, 42, 48), pad)[..., 3]
    rgb = np.clip(tint, 0, 1) * (1 - rim[..., None]) + np.array([0.12, 0.13, 0.15]) * rim[..., None]
    return _rgba(rgb, np.maximum(m, rim))

def extrude(face_rgba, depth=18, dx=0.6, dy=1.0, side=(25, 25, 30), shade=0.55):
    """3D block extrusion: stack darker copies of the alpha behind the face."""
    a = face_rgba[..., 3]; h, w = a.shape; P = depth + 4
    out = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    sc = np.array(side, np.float32) / 255
    for k in range(depth, 0, -1):
        ox, oy = int(round(P + dx * k)), int(round(P + dy * k))
        sub = out[oy:oy + h, ox:ox + w]
        f = 1 - shade * (k / depth)
        col = sc * f + 0.04 * (1 - k / depth)
        sub[..., :3] = sub[..., :3] * (1 - a[..., None]) + col * a[..., None]
        sub[..., 3] = np.maximum(sub[..., 3], a)
    sub = out[P:P + h, P:P + w]
    fa = face_rgba[..., 3:4]
    sub[..., :3] = sub[..., :3] * (1 - fa) + face_rgba[..., :3] * fa
    sub[..., 3] = np.maximum(sub[..., 3], face_rgba[..., 3])
    return out

def shadow(layer, blur=18, dx=0, dy=16, opacity=0.45):
    a = layer[..., 3]; P = blur * 2 + max(abs(dx), abs(dy))
    h, w = a.shape; out = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    sa = np.zeros((h + 2 * P, w + 2 * P), np.float32); sa[P + dy:P + dy + h, P + dx:P + dx + w] = a
    sa = cv2.GaussianBlur(sa, (0, 0), blur) * opacity
    out[..., 3] = sa
    l = layer; la = l[..., 3:4]; sub = out[P:P + h, P:P + w]
    sub[..., :3] = sub[..., :3] * (1 - la) + l[..., :3] * la
    sub[..., 3] = la[..., 0] + sub[..., 3] * (1 - la[..., 0])
    return out

def glow(layer, color, blur=22, strength=0.8):
    a = layer[..., 3]; P = blur * 2; h, w = a.shape
    out = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    g = np.zeros((h + 2 * P, w + 2 * P), np.float32); g[P:P + h, P:P + w] = a
    g = np.clip(cv2.GaussianBlur(g, (0, 0), blur) * strength, 0, 1)
    out[..., :3] = np.array(color, np.float32) / 255; out[..., 3] = g
    sub = out[P:P + h, P:P + w]; la = layer[..., 3:4]
    sub[..., :3] = sub[..., :3] * (1 - la) + layer[..., :3] * la; sub[..., 3] = la[..., 0] + sub[..., 3] * (1 - la[..., 0])
    return out

def over(a, b):
    """a over b (same size RGBA)."""
    aa = a[..., 3:4]; out = b.copy()
    out[..., :3] = b[..., :3] * (1 - aa) + a[..., :3] * aa
    out[..., 3] = aa[..., 0] + b[..., 3] * (1 - aa[..., 0]); return out

def place_canvas(layer, W, H, cx, cy, scale=1.0, rot_y=0.0, rot_x=0.0, rot_z=0.0, alpha=1.0, blur=0.0, persp=1400.0):
    """Project an RGBA layer onto a W×H canvas centred at (cx,cy) with 3D rotation (degrees) + scale."""
    h, w = layer.shape[:2]
    pts = np.float32([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]]) * scale
    ry, rx, rz = np.radians([rot_y, rot_x, rot_z])
    Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
    Rz = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])
    p = pts @ (Rz @ Rx @ Ry).T
    z = persp / (persp + p[:, 2])
    dst = np.float32(np.stack([cx + p[:, 0] * z, cy + p[:, 1] * z], 1))
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(layer, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    if blur > 0.3: out = cv2.GaussianBlur(out, (0, 0), blur)
    out[..., 3] *= alpha
    return out
