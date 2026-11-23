"""v9 talking-head edit (PayPal news) — built from v8 by build9.py. Original v8 doc:
v8 talking-head edit: '3 Gründe, warum du zu GTBuy wechseln solltest'.
Cobalt-blue / white / chrome. Creator's own TikTok + Beacons screenshots in an animated phone mock-up (zoom + tap on the link),
head-masked headlines, face-tracked camera, Higgsfield B-roll (coupons, payment, delivery, warehouse), timeline infographic,
word-synced captions, freeze end card. Usage: python render8.py <start> <end> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib8 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
NSRC = 705
DUR = 25.9
FREEZE = 688                        # 22.93 s, after the last word
BLUE = np.array([70, 125, 255], np.float32) / 255
WHITE = np.array([250, 250, 248], np.float32) / 255

# ------------------------------------------------------------------ camera (face tracked, no source re-timing)
faces = json.load(open("faces.json"))
CUTS = [0, 403, NSRC]
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
CAM = [(0.00, 2.70, 1.08, 1.12), (2.70, 6.60, 1.10, 1.14), (6.60, 12.40, 1.04, 1.08), (12.40, 13.24, 1.10, 1.12),
       (13.24, 18.90, 1.06, 1.09), (18.90, 40.0, 1.10, 1.15)]
def tx_at(t):   # where the face sits horizontally on screen (fraction of W)
    k = max(win(t, 13.55, 16.25, 0.4, 0.4), win(t, 19.9, 22.9, 0.4, 0.3))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
    if 22.10 <= t < 22.45: s *= 1 + 0.05 * math.exp(-(t - 22.10) / 0.08)
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
SKY = np.array([255, 168, 205], np.float32) / 255   # Klarna-style pink
NAVY = np.array([28, 20, 36], np.float32) / 255
NEWS_M = tmask("NEWS", font("Unbounded", 225, 900), 10)[0]
S["paypal_big"] = sprite_fill(tmask("Klarna.", font("Archivo", 230, 900, 118), 2)[0], SKY, shadow=0.0, stroke=(NAVY, 9))
S["users"] = sprite_fill(tmask("FÜR ALLE USER", font("SpaceGrotesk", 42, 700), 12)[0], SKY, shadow=0.0, stroke=(INK, 3))
GTB_M = tmask("USFans", font("Unbounded", 100, 900), 2)[0]
S["x"] = sprite_fill(tmask("×", font("Archivo", 130, 500, 100))[0], SKY, shadow=0.5, sblur=10)
S["pp2"] = sprite_fill(tmask("Klarna", font("InstrumentSerif-Italic", 150))[0], WHITE, shadow=0.6, sblur=12)
S["seit"] = chip("Jetzt mit Klarna", tick=True, size=46)
S["versand_l"] = chip("Versand  ·  Klarna", bg=SKY, fg=INK, size=40)
S["produkt_l"] = chip("Produkte  ·  Klarna", bg=SKY, fg=INK, size=40)
S["bezahlen"] = sprite_fill(tmask("BEZAHLEN", font("Archivo", 132, 900, 118), 4)[0], WHITE, shadow=0.0, stroke=(NAVY, 8))
S["c40"] = chip("Coupons", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("Über meinen Link", bg=BLUE, fg=WHITE, size=52)
S["aufship"] = sprite_fill(tmask("AUF SHIPPING", font("SpaceGrotesk", 38, 700), 9)[0], SKY, shadow=0.0, stroke=(INK, 3))
S["three_w"] = (np.zeros((4, 4, 3), np.float32), np.zeros((4, 4), np.float32), (0, 0))
FOUR_M = tmask("+", font("Unbounded", 380, 900))[0]
S["coupons_l"] = sprite_fill(tmask("COUPONS", font("SpaceGrotesk", 56, 700), 12)[0], BLUE, shadow=0.0, stroke=(INK, 3))
S["link"] = link_card(size=52)
S["cta1"] = sprite_fill(tmask("1. LINK", font("Archivo", 150, 900, 125), 2)[0], BLUE, shadow=0.0, stroke=(INK, 7))
S["cta2"] = sprite_fill(tmask("in meiner Bio", font("InstrumentSerif-Italic", 120))[0], WHITE, shadow=0.6, sblur=10)

def card(img, cw, ch, label=None, z=1.04):
    return card_sprite(img, cw, ch, z, label)
IMG = {k: load_img(f"img/{k}.png") for k in ("coupons", "payment_clean", "warehouse", "haul")}
S["coupon_card"] = card(IMG["coupons"], 360, 450, None)
S["ship_card"] = card(IMG["warehouse"], 360, 470, None)
S["prod_card"] = card(IMG["haul"], 360, 470, None)
S["pay_card"] = card(IMG["payment_clean"], 330, 410, None)

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
    if t < 15.0:
        z = 1 + 1.4 * ease_io((t - 14.05) / 0.45); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 14.05) / 0.45)
        return "profile", z, cy, ease_io((t - 14.25) / 0.3), (clamp((t - 14.55) / 0.35) if t >= 14.55 else -1), 0.0
    if t < 20.0:
        z = 1 + 0.9 * ease_io((t - 15.05) / 0.45); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 15.05) / 0.45)
        return "beacons", z, cy, ease_io((t - 15.3) / 0.3), (clamp((t - 15.65) / 0.35) if t >= 15.65 else -1), ease_out((t - 15.45) / 0.3)
    k = clamp((t - 23.7) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 24.0) / 0.3), (clamp((t - 24.4) / 0.4) if t >= 24.4 else -1), ease_out((t - 24.2) / 0.3)

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
    if t_ == "Paypal" and raw[i + 1]["w"] == "-User,": words.append(dict(w="PayPal-User,", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    rep = {"Paypal": "PayPal", "GTbuy": "USFans", "Büro": "Bio", "erhält": "erhaltet"}
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
words = _us_words(words, [16.22, 17.52, 20.5, 21.4])
KEY = {"usfans", "klarna", "usfans-haul", "klarna-user", "neuigkeiten", "paypal-user", "gtbuy", "paypal", "monaten", "versand", "produktbestellung", "bezahlen", "link", "bio",
       "coupons", "2× 40 %", "2× 30 %", "shipping", "3", "4"}
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
    nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 23.2
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
        col = (120, 165, 255) if (active or (spoken and k)) else (255, 255, 255)
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
def ticker(t, L):
    """news ticker band at the top during the hook ('Neuigkeiten')"""
    a = win(t, 0.95, 6.45, 0.35, 0.35)
    if a <= 0: return
    f = font("Archivo", 40, 900, 118); txt = "NEWS   •   USFANS × KLARNA   •   "
    unit = Image.new("RGB", (int(f.getlength(txt)) + 40, 70), tuple(int(c * 255) for c in NAVY))
    ImageDraw.Draw(unit).text((20, 35), txt, font=f, fill=(255, 255, 255), anchor="lm")
    u = np.asarray(unit).astype(np.float32) / 255
    strip = np.concatenate([u] * (W // u.shape[1] + 3), 1)
    x0 = int((t - 0.95) * 260) % u.shape[1]; band = strip[:, x0:x0 + W]
    lab = Image.new("RGB", (190, 70), tuple(int(c * 255) for c in SKY))
    ImageDraw.Draw(lab).text((95, 35), "LIVE", font=font("Archivo", 40, 900, 125), fill=(255, 255, 255), anchor="mm")
    band = band.copy(); band[:, :190] = np.asarray(lab).astype(np.float32) / 255
    k = ease_out((t - 0.95) / 0.4)
    place(L, (band, np.ones(band.shape[:2], np.float32), (0, 0)), W / 2, 60 - (1 - k) * 90, alpha=a)

def headline(t, back, key, M_, t0, t1, y=330):
    a = win(t, t0, t1, 0.3, 0.2)
    if a <= 0: return
    k = ease_out((t - t0) / 0.5); sw = (t - t0 - 0.3) / 0.9 if t0 + 0.3 <= t <= t0 + 1.2 else None
    place(back, chrome_cached(key, M_, 14, sw), W / 2, y, s=0.9 + 0.1 * k, rx=-60 * (1 - k), alpha=a)

def strike(L, x0, y0, x1, y1, prog, alpha):
    return
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(x0), int(y0)), (int(x0 + (x1 - x0) * prog), int(y0 + (y1 - y0) * prog)), 1.0, 16, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def calendar(t, L, x, y, a):
    return
    """little calendar icon whose pages flip (= 'seit einigen Monaten')"""
    if a <= 0: return
    months = ["MAI", "JUN", "JUL", "AUG", "SEP", "OKT"]
    n = min(int(max(t - 4.9, 0) / 0.22), len(months) - 1)
    im = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 24, 190, 190], 22, fill=(250, 250, 248, 255), outline=(10, 12, 20, 255), width=4)
    d.rounded_rectangle([10, 24, 190, 80], 22, fill=tuple(int(c * 255) for c in NAVY) + (255,))
    d.rectangle([10, 60, 190, 80], fill=tuple(int(c * 255) for c in NAVY) + (255,))
    for xx in (55, 145): d.rounded_rectangle([xx - 7, 8, xx + 7, 44], 6, fill=(10, 12, 20, 255))
    d.text((100, 135), months[n], font=font("Archivo", 54, 900, 112), fill=(10, 12, 20, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    sh = cv2.GaussianBlur(np.roll(arr[..., 3], 10, 0), (0, 0), 12) * .45; A_ = arr[..., 3] + sh * (1 - arr[..., 3])
    place(L, (arr[..., :3] * arr[..., 3:4] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)), x, y, alpha=a,
          s=1 + 0.06 * math.sin(math.pi * clamp(((t - 4.9) % 0.22) / 0.22)), rot=-6)

def scene(t, back, front):
    # HOOK: NEWS + PayPal
    a = win(t, 0.95, 2.75, 0.25, 0.2)
    if a:
        k = back_out((t - 0.95) / 0.45, 1.8); sw = (t - 1.2) / 0.9 if 1.2 <= t <= 2.1 else None
        place(back, chrome_cached("news", NEWS_M, 22, sw), W / 2, 300, s=1.45 - 0.45 * k, alpha=a * clamp((t - .95) / .06), blur=max(0, 1 - (t - .95) / .2) * 8)
    a = win(t, 1.78, 2.75, 0.2, 0.2)
    if a:
        place(front, S["paypal_big"], W / 2, 1180, s=back_out((t - 1.78) / 0.4, 2.0), rot=-4, alpha=a)
        place(front, S["users"], W / 2, 1345, alpha=a * ease_out((t - 2.05) / 0.3))
    # GTBuy x PayPal lockup behind the head
    a = win(t, 2.90, 4.75, 0.3, 0.25)
    if a:
        k = ease_out((t - 2.90) / 0.5); sw = (t - 3.2) / 0.9 if 3.2 <= t <= 4.1 else None
        place(back, chrome_cached("gtb", GTB_M, 14, sw), 300 - (1 - k) * 200, 310, alpha=a, s=0.9 + 0.1 * k)
        k2 = back_out((t - 3.10) / 0.35, 2.0); place(back, S["x"], 575, 300, s=k2, alpha=a)
        k3 = ease_out((t - 3.30) / 0.5); place(back, S["pp2"], 815 + (1 - k3) * 200, 300, alpha=a * k3)
    a = win(t, 4.80, 6.55, 0.3, 0.25)
    if a:
        calendar(t, front, 880, 420, a)
        place(front, S["seit"], 300, 420, s=back_out((t - 4.80) / 0.35, 2.0), alpha=a)
    # Versand + Produkte cards behind the head, then BEZAHLEN
    for key_, lab, t0, x, rot_ in (("ship_card", "versand_l", 7.85, 230, -4), ("prod_card", "produkt_l", 9.62, 850, 4)):
        a = win(t, t0, 11.25, 0.4, 0.3)
        if a <= 0: continue
        k = ease_out((t - t0) / 0.55)
        place(back, S[key_], x, 470 + (1 - k) * 160, rot=rot_, s=0.94 + 0.06 * k, alpha=a)
        place(front, S[lab], x, 760 + (1 - k) * 160, s=back_out((t - t0 - 0.15) / 0.35, 2.0), alpha=a)
    a = win(t, 11.30, 12.70, 0.15, 0.25)
    if a:
        k = back_out((t - 11.30) / 0.4, 1.8)
        place(back, S["bezahlen"], W / 2, 330, s=k, alpha=a)
        place(front, S["pay_card"], 860, 1050 + (1 - ease_out((t - 11.4) / .4)) * 120, rot=5, alpha=a * ease_out((t - 11.4) / .4))
    # Link in Bio: the creator's own screenshots in the phone
    a = win(t, 13.70, 16.25, 0.35, 0.3)
    if a:
        k = ease_out((t - 13.70) / 0.5); ko = ease_in((t - 15.95) / 0.3) if t > 15.95 else 0
        nm, z, cy, hl, tap, badge = phone_state(t)
        place(front, phone(nm, z, cy, hl, tap, badge), 865 + (1 - k) * 500 + ko * 600, 800, rot=-4 * (1 - k) + 3, alpha=a, s=0.9)
    for key_, t0, y in (("c40", 16.18, 520), ("c30", 17.48, 660)):
        a = win(t, t0, 18.85, 0.2, 0.2)
        if a: place(front, S[key_], 1030, y, anchor=(1.0, 0.5), s=back_out((t - t0) / 0.35, 2.2), alpha=a)
    a = win(t, 18.30, 18.85, 0.15, 0.2)
    if a: place(front, S["aufship"], 1000, 780, anchor=(1.0, 0.5), alpha=a)
    # 3 -> 4 coupons, only with my link
    a = win(t, 20.45, 22.95, 0.25, 0.25)
    if a:
        place(back, S["three_w"], 735, 420, alpha=a * (0.55 if t > 21.0 else 1.0), s=back_out((t - 20.45) / 0.3, 2.0))
        strike(back, 655, 520, 825, 330, ease_io((t - 20.80) / 0.2), a)
        if t >= 21.36: place(back, chrome_cached("four", FOUR_M, 20, (t - 21.5) / 0.8 if 21.5 <= t <= 22.3 else None), 935, 410, s=back_out((t - 21.36) / 0.42, 2.2), alpha=a)
        if t >= 21.55: place(front, S["coupons_l"], 850, 650, alpha=a * ease_out((t - 21.55) / .3))
        if t >= 21.60:
            kc = ease_out((t - 21.6) / 0.5); place(front, S["coupon_card"], 860, 940 + (1 - kc) * 120, rot=-3 + 4 * (1 - kc), alpha=a * kc, s=0.95 + 0.05 * kc)
    a = win(t, 22.08, 23.0, 0.05, 0.2)
    if a:
        k = ease_out((t - 22.08) / 0.18)
        place(front, S["stamp"], 250, 520, s=(1.7 - 0.7 * k) * 0.85, rot=14 - 3 * (t - 22.08), alpha=a)

def fullscreen(t, comp): return comp

def endcard(t, comp):
    if t < 22.98: return comp
    L = new_layer()
    k = ease_out((t - 23.0) / 0.45); place(L, S["cta1"], W / 2, 210 - (1 - k) * 30, alpha=k)
    k2 = ease_out((t - 23.2) / 0.45); place(L, S["cta2"], W / 2, 350, alpha=k2)
    k3 = ease_out((t - 23.35) / 0.55)
    nm, z, cy, hl, tap, badge = phone_state(t)
    place(L, phone(nm, z, cy, hl, tap, badge), W / 2, 980 + (1 - k3) * 300, rot=-2.5 * (1 - k3), alpha=k3, s=0.92)
    k4 = ease_out((t - 24.7) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1600, s=back_out((t - 24.7) / 0.4, 1.8), alpha=k4)
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
    if 13.12 <= t < 13.24: dx = -ease_in((t - 13.12) / 0.12) * W * 0.55
    if 13.24 <= t < 13.38: dx = (1 - ease_out((t - 13.24) / 0.14)) * W * 0.55
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
    if t >= 22.95:
        k = ease_io((t - 22.95) / 0.5); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.55 * k)
    comp = endcard(t, comp)
    P_ = new_layer(); ticker(t, P_); caption_layer(t, P_)
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
