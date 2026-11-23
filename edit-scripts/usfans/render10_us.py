"""v10 talking-head edit (Winter-Haul vakuumieren, GTBuy orange) — built from v8 by build10.py. Original v8 doc:
v8 talking-head edit: '3 Gründe, warum du zu GTBuy wechseln solltest'.
Cobalt-blue / white / chrome. Creator's own TikTok + Beacons screenshots in an animated phone mock-up (zoom + tap on the link),
head-masked headlines, face-tracked camera, Higgsfield B-roll (coupons, payment, delivery, warehouse), timeline infographic,
word-synced captions, freeze end card. Usage: python render8.py <start> <end> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib10 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
NSRC = 1088
DUR = 38.9
FREEZE = 1074                       # 35.80 s
BLUE = np.array([255, 140, 0], np.float32) / 255   # GTBuy orange (name kept from v8)
WHITE = np.array([250, 250, 248], np.float32) / 255

# ------------------------------------------------------------------ camera (face tracked, no source re-timing)
faces = json.load(open("faces.json"))
CUTS = [0, 323, NSRC]
fx = np.array([np.nan if f[1] is None else f[1] + f[3] / 2 for f in faces[:NSRC]], np.float32)
fy = np.array([np.nan if f[1] is None else f[2] + f[4] * 0.45 for f in faces[:NSRC]], np.float32)
def smooth(v, sig):
    out = v.copy()
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        seg = v[a:b].copy(); idx = np.arange(len(seg)); ok = ~np.isnan(seg)
        seg = np.interp(idx, idx[ok], seg[ok])
        k = np.exp(-0.5 * (np.arange(-3 * sig, 3 * sig + 1) / sig) ** 2); k /= k.sum()
        out[a:b] = np.convolve(np.pad(seg, 3 * sig, mode="edge"), k, "valid")
    return out
FX, FY = smooth(fx, 14), smooth(fy, 14)
CAM = [(0.00, 3.85, 1.08, 1.12), (3.85, 7.25, 1.12, 1.16), (7.25, 10.80, 1.05, 1.08), (10.80, 13.35, 1.08, 1.12),
       (13.35, 17.50, 1.06, 1.10), (17.50, 19.55, 1.12, 1.16), (19.55, 28.50, 1.06, 1.09), (28.50, 40.0, 1.08, 1.13)]
def tx_at(t):
    k = max(win(t, 11.0, 13.1, 0.35, 0.35), win(t, 14.2, 17.4, 0.35, 0.35), win(t, 19.5, 22.6, 0.4, 0.4),
            win(t, 24.4, 28.5, 0.4, 0.3), win(t, 30.4, 35.8, 0.4, 0.3))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
    if 27.80 <= t < 28.15: s *= 1 + 0.05 * math.exp(-(t - 27.80) / 0.08)
    x0 = clamp(FX[i] - tx_at(t) * W / s, 0, W - W / s)
    y0 = clamp(FY[i] - 0.47 * H / s, 0, H - H / s) * 0.6 + (H / 2 - H / (2 * s)) * 0.4
    return np.float32([[s, 0, -s * x0], [0, s, -s * y0]])

# ------------------------------------------------------------------ typography
_cache = {}
def chrome_cached(key, M_, depth, sw):
    k = (key, None if sw is None else round(round(sw / 0.05) * 0.05, 2))
    if k not in _cache: _cache[k] = sprite_chrome(M_, depth=depth, sweep=k[1])
    return _cache[k]
S = {}
S["winter"] = sprite_fill(tmask("WINTER", font("Unbounded", 120, 900), 14)[0], WHITE, shadow=0.0, stroke=(np.array([0.45, 0.7, 1.0], np.float32), 5))
HAUL_M = tmask("HAUL", font("Archivo", 250, 900, 125), 6)[0]
S["guenstiger"] = chip("Günstiger als zuvor", bg=BLUE, fg=WHITE, size=54)
S["sparst"] = sprite_fill(tmask("GESPART", font("SpaceGrotesk", 48, 700), 14)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["teurer"] = chip("Größer = teurer", size=42)
S["winterhauls"] = chip("Für Winter-Hauls", tick=True, size=42)
VAK_M = tmask("VAKUUMIEREN", font("Archivo", 98, 900, 108), 2)[0]
S["agent"] = sprite_fill(tmask("Als Agent:", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=12)
S["c40"] = chip("Coupons", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("Über meinen Link", bg=BLUE, fg=WHITE, size=52)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["three_w"] = (np.zeros((4, 4, 3), np.float32), np.zeros((4, 4), np.float32), (0, 0))
FOUR_M = tmask("+", font("Unbounded", 380, 900))[0]
S["coupons_l"] = sprite_fill(tmask("COUPONS", font("SpaceGrotesk", 56, 700), 12)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["link"] = link_card(size=52)
S["cta1"] = sprite_fill(tmask("1. LINK", font("Archivo", 150, 900, 125), 2)[0], BLUE, shadow=0.0, stroke=(INK, 7))
S["cta2"] = sprite_fill(tmask("in meiner Bio", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=10)

def card(img, cw, ch, label=None, z=1.04):
    return card_sprite(img, cw, ch, z, label)
IMG_FS = {k: load_img(f"img/{k}.png") for k in ("winterhaul", "vacuum")}
S["coupon_card"] = card(load_img("img/coupons.png"), 340, 420, None)

def stamp_sprite():
    sz = 420; im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = sz / 2
    bl = tuple(int(v * 255) for v in BLUE)
    d.ellipse([10, 10, sz - 10, sz - 10], outline=bl + (255,), width=12)
    d.ellipse([46, 46, sz - 46, sz - 46], outline=bl + (255,), width=4)
    f = font("SpaceGrotesk", 30, 700); txt = "NUR HIER  •  NUR ÜBER MEINEN LINK  •  "
    for k, ch_ in enumerate(txt):
        ang = -math.pi / 2 + k / len(txt) * 2 * math.pi; r = 160
        li = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); ImageDraw.Draw(li).text((30, 30), ch_, font=f, fill=bl + (255,), anchor="mm")
        li = li.rotate(-math.degrees(ang) - 90, resample=Image.BICUBIC)
        im.alpha_composite(li, (int(c + r * math.cos(ang) - 30), int(c + r * math.sin(ang) - 30)))
    d.rounded_rectangle([60, c - 52, sz - 60, c + 52], 14, fill=bl + (255,))
    d.text((c, c), "NUR HIER", font=font("Archivo", 64, 900, 118), fill=(255, 255, 255, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 14) * 0.45; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)
S["stamp"] = stamp_sprite()

# ------------------------------------------------------------------ phone mock-up with the creator's screenshots
SHOT = {k: load_img(f"img/shot_{k}.png") for k in ("profile", "beacons")}
SW_, SH_ = 1179, 2556
HL = {"profile": (40, 912, 625, 1000), "beacons": (58, 1545, 1121, 2145)}   # highlight rects in screenshot pixels
PW, PH, BZ = 452, 980, 14
def phone(name, zoom, cy_frac, hl=0.0, tap=-1.0, badge=0.0):
    """renders the phone: screenshot viewed at `zoom` centred at cy_frac, highlight box + tap ripple"""
    img = SHOT[name]
    vh, vw = SH_ / zoom, SW_ / zoom
    cy = clamp(cy_frac * SH_, vh / 2, SH_ - vh / 2); cx = SW_ / 2 if zoom <= 1.001 else clamp((HL[name][0] + HL[name][2]) / 2, vw / 2, SW_ - vw / 2)
    x0, y0 = cx - vw / 2, cy - vh / 2
    sw, sh = PW - 2 * BZ, PH - 2 * BZ
    M = np.float32([[sw / vw, 0, -x0 * sw / vw], [0, sh / vh, -y0 * sh / vh]])
    scr = cv2.warpAffine(img, M, (sw, sh), flags=cv2.INTER_AREA if zoom < 1.5 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    L = Image.new("RGBA", (sw, sh), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    bx = HL[name]; p0 = (bx[0] - x0) * sw / vw, (bx[1] - y0) * sh / vh; p1 = (bx[2] - x0) * sw / vw, (bx[3] - y0) * sh / vh
    bl = tuple(int(v * 255) for v in BLUE)
    if hl > 0:
        d.rounded_rectangle([p0[0] - 8, p0[1] - 8, p0[0] + (p1[0] - p0[0] + 16) * hl - 8, p1[1] + 8], 16, outline=bl + (255,), width=6)
    if tap >= 0:
        tx, ty = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        r = 18 + 70 * tap; d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 255, 255, int(230 * (1 - tap))), width=5)
        d.ellipse([tx - 22, ty - 22, tx + 22, ty + 22], fill=(255, 255, 255, int(200 * (1 - tap * 0.6))))
    if badge > 0:
        f = font("Archivo", 40, 900, 112); txt = "1. LINK"
        bw = f.getlength(txt) + 36; bx_ = min(max(p0[0] + 10, 12), sw - bw - 12); by_ = max(p0[1] - 74, 12)
        d.rounded_rectangle([bx_, by_, bx_ + bw, by_ + 58], 12, fill=bl + (int(255 * badge),))
        d.text((bx_ + bw / 2, by_ + 29), txt, font=f, fill=(255, 255, 255, int(255 * badge)), anchor="mm")
    ov = np.asarray(L).astype(np.float32) / 255
    scr = scr * (1 - ov[..., 3:4]) + ov[..., :3] * ov[..., 3:4]
    rgb = np.zeros((PH, PW, 3), np.float32) + 0.05
    rgb[BZ:BZ + sh, BZ:BZ + sw] = scr * rounded(sw, sh, 46)[..., None] + 0.05 * (1 - rounded(sw, sh, 46)[..., None])
    a = rounded(PW, PH, 60)
    # glass reflection
    X, Y = np.meshgrid(np.arange(PW), np.arange(PH)); refl = np.clip(1 - np.abs((X + Y * 0.6) / (PW + PH * 0.6) - 0.3) / 0.08, 0, 1) * 0.08
    rgb = np.clip(rgb + refl[..., None], 0, 1)
    pad = 70
    R = np.zeros((PH + 2 * pad, PW + 2 * pad, 3), np.float32); Al = np.zeros((PH + 2 * pad, PW + 2 * pad), np.float32)
    sh_ = np.zeros_like(Al); sh_[pad + 30:pad + PH + 26, pad + 16:pad + PW - 16] = 1; sh_ = cv2.GaussianBlur(sh_, (0, 0), 28) * 0.55
    Al[:] = sh_; R[pad:pad + PH, pad:pad + PW] = rgb * a[..., None]
    Al[pad:pad + PH, pad:pad + PW] = np.maximum(sh_[pad:pad + PH, pad:pad + PW] * (1 - a), a)
    R = R / np.maximum(Al[..., None], 1e-4) * (Al[..., None] > 0)
    return R, Al, (pad, pad)

def phone_state(t):
    if t < 20.95:
        z = 1 + 1.4 * ease_io((t - 20.0) / 0.45); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 20.0) / 0.45)
        return "profile", z, cy, ease_io((t - 20.2) / 0.3), (clamp((t - 20.5) / 0.35) if t >= 20.5 else -1), 0.0
    if t < 30.0:
        z = 1 + 0.9 * ease_io((t - 21.0) / 0.45); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 21.0) / 0.45)
        return "beacons", z, cy, ease_io((t - 21.25) / 0.3), (clamp((t - 21.6) / 0.35) if t >= 21.6 else -1), ease_out((t - 21.4) / 0.3)
    k = clamp((t - 36.8) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 37.1) / 0.3), (clamp((t - 37.4) / 0.4) if t >= 37.4 else -1), ease_out((t - 37.3) / 0.3)

# ------------------------------------------------------------------ captions
raw = json.load(open("words.json"))
words = []; i = 0
while i < len(raw):
    w = raw[i]; t_ = w["w"]
    if t_ == "2x40": words.append(dict(w="2× 40 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "2x30": words.append(dict(w="2× 30 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "6" and raw[i + 1]["w"] == "-7": words.append(dict(w="6–7", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "1" and raw[i + 1]["w"] == "-3": words.append(dict(w="1–3", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "Express" and raw[i + 1]["w"] == "-Versand": words.append(dict(w="Express-Versand", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "Das" and raw[i + 1]["w"] == "Agent": words.append(dict(w="Als", s=w["s"], e=w["e"])); i += 1; continue
    if t_ == "die" and raw[i + 1]["w"] == "T" and raw[i + 2]["w"] == "-Buy":
        words.append(dict(w="USFans", s=raw[i + 1]["s"], e=raw[i + 2]["e"])); i += 3; continue
    if t_ == "2x" and raw[i + 1]["w"] in ("40", "30"): words.append(dict(w=f"2× {raw[i + 1]['w']} %", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    rep = {"erhält": "erhaltet", "Vakuminium": "Vakuumieren", "Haul": "Haul"}
    words.append(dict(w=rep.get(t_, t_), s=w["s"], e=w["e"])); i += 1
# shared USFans rebrand helpers (inserted into each talking-head render script)
def _us_words(words, drop_times):
    out = []
    for w in words:
        if any(abs(w["s"] - d) < 0.06 for d in drop_times): continue   # spoken offer numbers stay in the audio, not on screen
        t = w["w"]
        for a, b in (("GTBuy", "USFans"), ("GTbuy", "USFans"), ("PayPal", "Klarna"), ("Paypal", "Klarna")): t = t.replace(a, b)
        out.append(dict(w=t, s=w["s"], e=w["e"]))
    return out

KPINK = np.array([255, 179, 199], np.float32) / 255     # Klarna-style pink (own type, not the Klarna logo file)
def klarna_chip(text="Klarna", size=48): return chip(text, bg=KPINK, fg=INK, size=size)
words = _us_words(words, [21.08, 22.68, 24.62, 25.92])
KEY = {"usfans", "klarna", "usfans-haul", "klarna-user", "winter", "haul", "günstiger", "50", "100", "euro", "gewicht", "volumen", "paket", "teurer", "vakuumieren", "gtbuy",
       "link", "bio", "2× 40 %", "2× 30 %", "coupons", "3", "4", "shipping", "kleiner", "kompakter", "hauls"}
def clean(s): return s.strip(",.!?;:")
chunks, cur = [], []
for j, w in enumerate(words):
    cur.append(w); nxt = words[j + 1] if j + 1 < len(words) else None
    txt = " ".join(clean(x["w"]) for x in cur)
    if nxt is None or w["w"][-1] in ",.!?" or len(cur) >= 3 or len(txt) >= 15 or (nxt["s"] - w["e"] > 0.35):
        chunks.append(cur); cur = []
CH = []
for j, c in enumerate(chunks):
    t0 = c[0]["s"] - 0.05
    nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 34.6
    adj = nxt0 - c[-1]["e"] < 0.45
    t1 = nxt0 if adj else min(c[-1]["e"] + 0.3, nxt0)
    CH.append(dict(words=c, t0=t0, t1=t1, adj=adj))
for j in range(len(CH)): CH[j]["prev_adj"] = j > 0 and CH[j - 1]["adj"]
F_CAP = font("Archivo", 72, 850, 108); F_KEY = font("InstrumentSerif-Italic", 100)
CAP_Y = 1430
def caption_layer(t, L):
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return
    toks = [clean(w["w"]) for w in ch["words"]]; keys = [tk.lower() in KEY for tk in toks]
    fs = [F_KEY if k else F_CAP for k in keys]; sp = 30
    wd = [f.getlength(tk) for f, tk in zip(fs, toks)]; total = sum(wd) + sp * (len(toks) - 1)
    scale = min(1.0, 960 / total)
    kin = 1.0 if ch["prev_adj"] else ease_out((t - ch["t0"]) / 0.16); kout = 1.0 if ch["adj"] else ease_io((ch["t1"] - t) / 0.12)
    a = kin * kout
    if a <= 0: return
    cw, chh = int(total + 120), 230
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([20, 58, cw - 20, 190], 40, fill=(10, 12, 20, 150))   # legibility over the white sweater
    x = 60; base = 150
    for w, tk, wdt, f, k in zip(ch["words"], toks, wd, fs, keys):
        active = w["s"] - 0.03 <= t <= w["e"] + 0.03; spoken = t > w["e"] + 0.03
        col = (255, 170, 60) if (active or (spoken and k)) else (255, 255, 255)
        al = 1.0 if (active or spoken) else 0.55
        lay = Image.new("RGBA", (int(wdt) + 60, chh), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((30, base), tk, font=f, fill=col + (int(255 * al),), anchor="ls", stroke_width=2, stroke_fill=(10, 10, 12, int(200 * al)))
        if active:
            pk = clamp((t - w["s"] + 0.03) / 0.16); sc = 1.0 + 0.07 * math.sin(math.pi * pk)
            if sc > 1.003:
                nw, nh = int(lay.width * sc), int(lay.height * sc); lay = lay.resize((nw, nh), Image.BICUBIC)
                img.alpha_composite(lay, (int(x - 30 - (nw - wdt - 60) / 2), int(-(nh - chh) * base / chh))); x += wdt + sp; continue
        img.alpha_composite(lay, (int(x - 30), 0)); x += wdt + sp
    arr = np.asarray(img).astype(np.float32) / 255; ca = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(ca, 6, 0), (0, 0), 10) * 0.4; A_ = ca + sh * (1 - ca)
    rgb = arr[..., :3] * ca[..., None] / np.maximum(A_[..., None], 1e-4)
    rise = (1 - ease_out((t - ch["t0"]) / 0.18)) * 22 if not ch["prev_adj"] else 0
    place(L, (rgb, A_, (0, 0)), W / 2, CAP_Y + rise, s=scale, alpha=a)

# ------------------------------------------------------------------ graphics
def strike(L, x0, y0, x1, y1, prog, alpha):
    return
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(x0), int(y0)), (int(x0 + (x1 - x0) * prog), int(y0 + (y1 - y0) * prog)), 1.0, 16, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def snow(t, L, t0, t1, n=70):
    a = win(t, t0, t1, 0.4, 0.5)
    if a <= 0: return
    r = np.random.default_rng(5); m = np.zeros((H, W), np.float32)
    xs = r.uniform(0, W, n); sp = r.uniform(120, 320, n); ph = r.uniform(0, H, n); sz = r.uniform(2, 7, n); dr = r.uniform(0, 6.28, n)
    for k in range(n):
        y = (ph[k] + sp[k] * t) % (H + 40) - 20; x = xs[k] + 25 * math.sin(t * 1.3 + dr[k])
        cv2.circle(m, (int(x), int(y)), int(sz[k]), 1.0, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 1.2) * a * 0.75
    L[0] *= (1 - m[..., None]); L[0] += WHITE * m[..., None]; L[1] *= (1 - m); L[1] += m

def box_sprite(sc_, color=None, label=None, tape=True):
    """isometric parcel drawn in code; sc_ = size factor"""
    col = tuple(int(v * 255) for v in (BLUE if color is None else color))
    w = int(220 * sc_); h = int(170 * sc_); d = int(110 * sc_); pad = 40
    im = Image.new("RGBA", (w + d + 2 * pad, h + d + 2 * pad), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    x0, y0 = pad, pad + d
    front = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    top = [(x0, y0), (x0 + d, y0 - d), (x0 + w + d, y0 - d), (x0 + w, y0)]
    side = [(x0 + w, y0), (x0 + w + d, y0 - d), (x0 + w + d, y0 - d + h), (x0 + w, y0 + h)]
    dr.polygon(front, fill=(198, 150, 98, 255)); dr.polygon(top, fill=(222, 178, 122, 255)); dr.polygon(side, fill=(165, 120, 74, 255))
    lw = max(3, int(5 * sc_))
    for poly in (front, top, side): dr.line(poly + [poly[0]], fill=(40, 28, 16, 255), width=lw, joint="curve")
    if tape:
        tw = max(10, int(26 * sc_))
        dr.polygon([(x0 + w / 2 - tw / 2, y0), (x0 + w / 2 + d - tw / 2, y0 - d), (x0 + w / 2 + d + tw / 2, y0 - d), (x0 + w / 2 + tw / 2, y0)], fill=col + (255,))
        dr.rectangle([x0 + w / 2 - tw / 2, y0, x0 + w / 2 + tw / 2, y0 + h * 0.35], fill=col + (255,))
    if label:
        f = font("Archivo", max(18, int(34 * sc_)), 900, 112)
        dr.text((x0 + w / 2, y0 + h * 0.66), label, font=f, fill=(40, 28, 16, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 14, 0), (0, 0), 16) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)

def icon_sprite(kind, size=150):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    col = tuple(int(v * 255) for v in BLUE) + (255,); ink = (12, 12, 14, 255)
    if kind == "kg":
        d.polygon([(c - 48, 50), (c + 48, 50), (c + 64, size - 18), (c - 64, size - 18)], fill=col, outline=ink)
        d.ellipse([c - 20, 18, c + 20, 58], outline=ink, width=8)
        d.text((c, size * 0.66), "KG", font=font("Archivo", 40, 900, 118), fill=(255, 255, 255, 255), anchor="mm")
    else:  # volume cube wireframe
        s = 70; o = 30
        p = [(c - s / 2 - o / 2, c - s / 2 + o / 2), (c + s / 2 - o / 2, c - s / 2 + o / 2), (c + s / 2 - o / 2, c + s / 2 + o / 2), (c - s / 2 - o / 2, c + s / 2 + o / 2)]
        q = [(x + o, y - o) for x, y in p]
        for a_, b_ in zip(p, p[1:] + p[:1]): d.line([a_, b_], fill=col, width=8)
        for a_, b_ in zip(q, q[1:] + q[:1]): d.line([a_, b_], fill=col, width=8)
        for a_, b_ in zip(p, q): d.line([a_, b_], fill=col, width=8)
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 8, 0), (0, 0), 10) * .45; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)
S["i_kg"] = icon_sprite("kg"); S["i_vol"] = icon_sprite("vol")
S["l_kg"] = chip("Gewicht", size=40); S["l_vol"] = chip("Volumen", bg=BLUE, fg=WHITE, size=40)
S["plus"] = sprite_fill(tmask("+", font("Archivo", 140, 900, 100))[0], WHITE, shadow=0.6, sblur=8)
S["box_big"] = box_sprite(1.35, label="€€€"); S["box_mid"] = box_sprite(0.95, label="€€"); S["box_small"] = box_sprite(0.62, label="€")
S["vorher"] = chip("Vorher", size=38); S["nachher"] = chip("Vakuumiert", bg=BLUE, fg=WHITE, size=38)
S["vac_card"] = card_sprite(load_img("img/vacuum.png"), 360, 460, 1.04, None)
S["logo"] = (lambda arr: (arr[..., :3], arr[..., 3], (0, 0)))(np.asarray(Image.open("img/brand_logo.png").convert("RGBA").resize((300, 300), Image.LANCZOS)).astype(np.float32) / 255)
S["logo_s"] = (lambda arr: (arr[..., :3], arr[..., 3], (0, 0)))(np.asarray(Image.open("img/brand_logo.png").convert("RGBA").resize((170, 170), Image.LANCZOS)).astype(np.float32) / 255)

def logo_glow(L, x, y, s, a, t, t0):
    """GTBuy app icon with glow halo, 3D flip-in and a light sweep"""
    k = ease_out((t - t0) / 0.55)
    halo = np.zeros((H, W), np.float32); cv2.circle(halo, (int(x), int(y)), int(190 * s), 1.0, -1)
    halo = cv2.GaussianBlur(halo, (0, 0), 45) * 0.55 * a * k
    L[0] *= (1 - halo[..., None]); L[0] += BLUE * halo[..., None]; L[1] *= (1 - halo); L[1] += halo
    rgb, al, _ = S["logo"]
    sw = (t - t0 - 0.45) / 0.6
    if 0 <= sw <= 1:
        hh, ww = al.shape; X, Y = np.meshgrid(np.arange(ww), np.arange(hh))
        d = (X + Y * 0.6) / (ww + hh * 0.6) - sw
        rgb = np.clip(rgb + np.exp(-(d / 0.06) ** 2)[..., None] * 0.55 * al[..., None], 0, 1)
    sh = cv2.GaussianBlur(np.roll(al, 14, 0), (0, 0), 16) * 0.5; A_ = al + sh * (1 - al)
    place(L, (rgb * al[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)), x, y, s=s * (0.7 + 0.3 * back_out((t - t0) / 0.5, 1.8)), rx=-75 * (1 - k), alpha=a)

def word_stack(t, back):
    """KLEINER / KOMPAKTER / GÜNSTIGER appear on the spoken words, each in its own style"""
    for key, t0, y in (("w_klein", 31.30, 150), ("w_komp", 31.96, 300), ("w_guen", 33.62, 455)):
        a = win(t, t0, 35.75, 0.25, 0.25)
        if a <= 0: continue
        k = back_out((t - t0) / 0.4, 1.8)
        if key == "w_komp": place(back, S[key], W / 2, y, s=1.3 - 0.3 * ease_out((t - t0) / 0.35), alpha=a)
        elif key == "w_guen": place(back, chrome_cached("guen", GUEN_M, 16, (t - t0 - .2) / .8 if t0 + .2 <= t <= t0 + 1 else None), W / 2, y, s=k, alpha=a)
        else: place(back, S[key], W / 2 - (1 - ease_out((t - t0) / .4)) * 300, y, alpha=a)
S["w_klein"] = sprite_fill(tmask("KLEINER.", font("Archivo", 130, 900, 125), 2)[0], WHITE, shadow=0.0, stroke=(INK, 6))
S["w_komp"] = sprite_outline(tmask("KOMPAKTER.", font("Unbounded", 105, 900), 4)[0], BLUE, 4)
GUEN_M = tmask("GÜNSTIGER.", font("Archivo", 112, 900, 112), 2)[0]

def scene(t, back, front):
    # HOOK: WINTER HAUL + snow + price down
    snow(t, front, 0.0, 3.85)
    a = win(t, 0.80, 3.80, 0.25, 0.25)
    if a:
        k = ease_out((t - 0.80) / 0.45)
        place(back, S["winter"], W / 2, 175 - (1 - k) * 50, alpha=a)
        kh = back_out((t - 1.05) / 0.45, 1.8)
        place(back, chrome_cached("haul", HAUL_M, 22, (t - 1.3) / 0.9 if 1.3 <= t <= 2.2 else None), W / 2, 370, s=1.4 - 0.4 * kh, alpha=a * clamp((t - 1.05) / .06))
    a = win(t, 1.75, 3.80, 0.2, 0.25)
    if a: place(front, S["guenstiger"], W / 2, 1240, s=back_out((t - 1.75) / 0.35, 2.0), rot=-4, alpha=a)
    # savings counter 50 -> 100 €
    a = win(t, 4.55, 6.15, 0.2, 0.2)
    if a:
        v = 50 if t < 5.26 else 100
        if t < 4.95: v = int(50 * ease_out((t - 4.55) / 0.4))
        if 5.26 <= t < 5.6: v = int(50 + 50 * ease_out((t - 5.26) / 0.34))
        place(back, chrome_cached(f"eur{v}", tmask(f"-{v} €", font("Unbounded", 190, 900), 2)[0], 16, None), W / 2, 330, s=1 + 0.06 * math.exp(-max(t - 5.26, 0) / 0.1) * (t >= 5.26), alpha=a)
        place(front, S["sparst"], W / 2, 520, alpha=a * ease_out((t - 4.7) / 0.3))
    # winter haul fullscreen (circle wipe)
    # weight + volume
    a = win(t, 9.20, 10.80, 0.2, 0.2)
    if a:
        place(front, S["i_kg"], 230, 420, s=back_out((t - 9.20) / 0.35, 2.0), alpha=a); place(front, S["l_kg"], 230, 545, alpha=a)
    a = win(t, 9.95, 10.80, 0.15, 0.2)
    if a: place(front, S["plus"], 540, 410, s=back_out((t - 9.95) / 0.3, 2.0), alpha=a)
    a = win(t, 10.20, 10.80, 0.2, 0.2)
    if a:
        place(front, S["i_vol"], 850, 420, s=back_out((t - 10.20) / 0.35, 2.0), alpha=a); place(front, S["l_vol"], 850, 545, alpha=a)
    # bigger box -> more expensive
    a = win(t, 11.10, 13.05, 0.25, 0.25)
    if a:
        key = "box_small" if t < 11.6 else ("box_mid" if t < 12.3 else "box_big")
        pop = 1 + 0.08 * math.exp(-min(abs(t - 11.6), abs(t - 12.3)) / 0.08)
        place(front, S[key], 860, 560, s=pop, alpha=a)
        place(front, S["teurer"], 860, 820, alpha=win(t, 12.30, 13.05, 0.15, 0.25))
    # VAKUUMIEREN + vacuum card
    a = win(t, 14.30, 17.35, 0.4, 0.3)
    if a:
        k = ease_out((t - 14.30) / 0.55)
        place(front, S["vac_card"], 860, 760 + (1 - k) * 140, rot=4, s=0.94 + 0.06 * k, alpha=a)
        if t >= 15.35: place(front, S["winterhauls"], 1040, 1030, anchor=(1.0, 0.5), s=back_out((t - 15.35) / 0.35, 2.0), alpha=a)
    a = win(t, 16.10, 17.40, 0.15, 0.25)
    if a:
        k = back_out((t - 16.10) / 0.4, 1.8)
        place(back, chrome_cached("vak", VAK_M, 16, (t - 16.3) / 0.8 if 16.3 <= t <= 17.1 else None), W / 2, 330, s=k, alpha=a)
    # GTBuy logo on "USFans"
    a = win(t, 18.40, 20.0, 0.1, 0.35)
    if a:
        logo_glow(front, W / 2 + 280, 380, 1.0, a, t, 18.40)
        place(back, S["agent"], W / 2 - 150, 300, alpha=a * ease_out((t - 17.95) / 0.35))
    # Link in bio: screenshots in the phone, small logo badge on top
    a = win(t, 19.60, 22.55, 0.35, 0.3)
    if a:
        k = ease_out((t - 19.60) / 0.5); ko = ease_in((t - 22.25) / 0.3) if t > 22.25 else 0
        nm, z, cy, hl, tap, badge = phone_state(t)
        px = 865 + (1 - k) * 500 + ko * 600
        place(front, phone(nm, z, cy, hl, tap, badge), px, 820, rot=-4 * (1 - k) + 3, alpha=a, s=0.9)
        place(front, S["logo_s"], px - 150, 330, s=back_out((t - 19.9) / 0.35, 2.0), alpha=a * clamp((t - 19.9) / .1), rot=-8)
    for key_, t0, y in (("c40", 21.55, 330), ("c30", 22.90, 470)):
        a = win(t, t0, 23.75, 0.2, 0.2)
        if a: place(front, S[key_], 50, y, anchor=(0.0, 0.5), s=back_out((t - t0) / 0.35, 2.2), alpha=a)
    # 3 -> 4 coupons on shipping, only with my link
    a = win(t, 24.55, 28.45, 0.25, 0.25)
    if a:
        place(back, S["three_w"], 735, 420, alpha=a * (0.55 if t > 25.2 else 1.0), s=back_out((t - 24.55) / 0.3, 2.0))
        strike(back, 655, 520, 825, 330, ease_io((t - 25.05) / 0.22), a)
        if t >= 25.88: place(back, chrome_cached("four", FOUR_M, 20, (t - 26.0) / 0.8 if 26.0 <= t <= 26.8 else None), 935, 410, s=back_out((t - 25.88) / 0.42, 2.2), alpha=a)
        if t >= 26.45: place(front, S["coupons_l"], 850, 650, alpha=a * ease_out((t - 26.45) / .3))
        if t >= 26.50:
            kc = ease_out((t - 26.5) / 0.5); place(front, S["coupon_card"], 860, 930 + (1 - kc) * 120, rot=-3 + 4 * (1 - kc), alpha=a * kc, s=0.95 + 0.05 * kc)
        if t >= 27.15: place(front, S["aufship"], 860, 1210, alpha=a * ease_out((t - 27.15) / .3))
    a = win(t, 27.80, 28.55, 0.05, 0.2)
    if a:
        k = ease_out((t - 27.80) / 0.18)
        place(front, S["stamp"], 250, 520, s=(1.7 - 0.7 * k) * 0.85, rot=14 - 3 * (t - 27.8), alpha=a)
    # before / after compression
    a = win(t, 30.45, 35.75, 0.3, 0.3)
    if a:
        place(front, S["box_big"], 850, 800, alpha=a * (1 - 0.45 * ease_io((t - 31.3) / 0.4)), s=0.85)
        place(front, S["vorher"], 850, 1010, alpha=a * (1 - 0.45 * ease_io((t - 31.3) / 0.4)))
        if t >= 31.30:
            k = back_out((t - 31.30) / 0.4, 2.0)
            place(front, S["box_small"], 900, 1180, s=k, alpha=a)
            place(front, S["nachher"], 900, 1300, alpha=a * ease_out((t - 31.5) / .3))
        word_stack(t, back)

def fullscreen(t, comp):
    for key, t0, t1 in (("winterhaul", 6.05, 7.25), ("vacuum", 28.55, 30.45)):
        if not (t0 <= t < t1): continue
        u = (t - t0) / (t1 - t0)
        img = cover(IMG_FS[key], W, H, 1.12 - 0.08 * u, 0, 0)
        img = img * (0.8 + 0.2 * np.linspace(0, 1, H)[:, None, None] ** 0.5)
        r = ease_out((t - t0) / 0.38) * 2300; yy, xx = np.ogrid[:H, :W]
        d = np.sqrt((xx - 540.0) ** 2 + (yy - 900.0) ** 2)
        m = np.clip((r - d) / 30, 0, 1)
        if t > t1 - 0.3: m = m * ease_io((t1 - t) / 0.3)
        comp = comp * (1 - m[..., None]) + img * m[..., None]
        ring = np.exp(-((d - r) / 10) ** 2) * (r < 2200); comp = comp * (1 - ring[..., None] * .8) + BLUE * ring[..., None] * .8
    return comp

def endcard(t, comp):
    if t < 35.85: return comp
    L = new_layer()
    k0 = ease_out((t - 35.85) / 0.5)
    logo_glow(L, W / 2, 230, 0.75, k0, t, 35.85)
    k = ease_out((t - 36.05) / 0.45); place(L, S["cta1"], W / 2, 450 - (1 - k) * 30, alpha=k)
    k2 = ease_out((t - 36.2) / 0.45); place(L, S["cta2"], W / 2, 575, alpha=k2)
    k3 = ease_out((t - 36.3) / 0.55)
    nm, z, cy, hl, tap, badge = phone_state(t)
    place(L, phone(nm, z, cy, hl, tap, badge), W / 2, 1110 + (1 - k3) * 300, rot=-2.5 * (1 - k3), alpha=k3, s=0.8)
    k4 = ease_out((t - 37.5) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1650, s=back_out((t - 37.5) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

# ------------------------------------------------------------------ main
def box(x, r): return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1))
def guided(I, p, r=8, eps=2e-3):
    mI, mp_ = box(I, r), box(p, r); a = (box(I * p, r) - mI * mp_) / (box(I * I, r) - mI * mI + eps); b = mp_ - a * mI
    return box(a, r) * I + box(b, r)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = (1 - 0.22 * np.clip(np.sqrt(((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .45) / (H * .72)) ** 2) - .45, 0, 1) ** 1.5)[..., None]
rng = np.random.default_rng(A + 31)
sA, sB = min(A, FREEZE), min(B, NSRC)
sel = f"select='between(n\\,{sA}\\,{max(sB, sA + 1) - 1})'"
dv = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "enh.mov", "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
dm = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "mask.mkv", "-vf", sel, "-vsync", "0", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
if PREVIEW is None:
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "ffv1", "-level", "3", OUT], stdin=subprocess.PIPE)
frozen = None; frame = m = None
for i in range(A, B):
    t = i / FPS
    if i <= FREEZE or frozen is None:
        fb = dv.stdout.read(W * H * 3); mb = dm.stdout.read(W * H)
        if len(fb) == W * H * 3:
            frame = np.frombuffer(fb, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            m = np.frombuffer(mb, np.uint8).reshape(H, W).astype(np.float32) / 255
        if i == FREEZE or (i > FREEZE and frozen is None): frozen = (frame, m)
    if PREVIEW is not None and not any(abs(t - o) < 0.5 / FPS for o in PREVIEW): continue
    fr, mm = (frozen if i >= FREEZE else (frame, m))
    gs = cv2.resize(cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY), (540, 960), interpolation=cv2.INTER_AREA)
    mm = np.clip(cv2.resize(guided(gs, cv2.resize(mm, (540, 960), interpolation=cv2.INTER_AREA)), (W, H)), 0, 1)
    fi = min(i, FREEZE)
    M = camera(fi, t)
    dx = 0.0
    if 10.66 <= t < 10.78: dx = -ease_in((t - 10.66) / 0.12) * W * 0.55
    if 10.78 <= t < 10.92: dx = (1 - ease_out((t - 10.78) / 0.14)) * W * 0.55
    M[0, 2] += dx
    zb = (1 - t / 0.3) if t < 0.3 else 0
    if zb > 0.02:
        acc = np.zeros((H, W, 3), np.float32)
        for k in range(6):
            sk = 1 + zb * 0.07 * k / 5; Mk = M.copy(); Mk[:, :2] *= sk; Mk[0, 2] = M[0, 2] * sk + W / 2 * (1 - sk); Mk[1, 2] = M[1, 2] * sk + H * .45 * (1 - sk)
            acc += cv2.warpAffine(fr, Mk, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        cf = acc / 6
    else:
        cf = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    cm = cv2.warpAffine(mm, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if abs(dx) > 1:
        k = int(abs(dx) / 6) | 1; cf = cv2.blur(cf, (k, 1)); cm = cv2.blur(cm, (k, 1))
    back, front = new_layer(), new_layer()
    scene(t, back, front)
    comp = cf * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = fullscreen(t, comp)
    comp = comp * (1 - front[1][..., None]) + front[0]
    if t >= 35.82:
        k = ease_io((t - 35.82) / 0.5); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.55 * k)
    comp = endcard(t, comp)
    P_ = new_layer(); caption_layer(t, P_)
    comp = comp * (1 - P_[1][..., None]) + P_[0]
    comp = comp * VIGN
    comp += rng.normal(0, 0.011, (H // 2, W // 2, 1)).astype(np.float32).repeat(2, 0).repeat(2, 1)
    if t > DUR - 0.3: comp *= ease_io((DUR - t) / 0.3)
    out = (np.clip(comp, 0, 1) * 255 + 0.5).astype(np.uint8)
    if PREVIEW is not None: Image.fromarray(out).save(f"frames/p_{t:05.2f}.jpg", quality=88)
    else:
        enc.stdin.write(out.tobytes())
        if (i - A) % 60 == 0: print(A, "frame", i, flush=True)
if PREVIEW is None: enc.stdin.close(); enc.wait()
print("done", A, B)
