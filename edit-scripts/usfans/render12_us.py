"""v12 talking-head edit (Haul in 7 Tagen, violet) — built from v8 by build12.py. Original v8 doc:
v8 talking-head edit: '3 Gründe, warum du zu GTBuy wechseln solltest'.
Cobalt-blue / white / chrome. Creator's own TikTok + Beacons screenshots in an animated phone mock-up (zoom + tap on the link),
head-masked headlines, face-tracked camera, Higgsfield B-roll (coupons, payment, delivery, warehouse), timeline infographic,
word-synced captions, freeze end card. Usage: python render8.py <start> <end> <out.mkv> [preview_times_csv]"""
import sys, json, math, subprocess
sys.path.insert(0, "..")
from lib12 import *

A, B, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
PREVIEW = [float(x) for x in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
NSRC = 784
DUR = 29.0
FREEZE = 778                        # 25.93 s
BLUE = np.array([140, 92, 255], np.float32) / 255   # violet accent (name kept from v8)
WHITE = np.array([250, 250, 248], np.float32) / 255

# ------------------------------------------------------------------ camera (face tracked, no source re-timing)
faces = json.load(open("faces.json"))
CUTS = [0, 130, 333, 478, 648, NSRC]
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
CAM = [(0.00, 4.33, 1.08, 1.13), (4.33, 11.10, 1.06, 1.10), (11.10, 15.93, 1.08, 1.12), (15.93, 21.60, 1.05, 1.09),
       (21.60, 40.0, 1.17, 1.21)]
def tx_at(t):
    k = max(win(t, 5.45, 11.0, 0.4, 0.3), win(t, 11.85, 14.35, 0.35, 0.35), win(t, 16.15, 21.55, 0.4, 0.2))
    return 0.5 - 0.10 * k
def camera(i, t):
    s = 1.1
    for k, (a, b, s0, s1) in enumerate(CAM):
        if a <= t < b:
            s = s0 + (s1 - s0) * ease_io((t - a) / (b - a))
            if k > 0 and a != 21.60: prev = CAM[k - 1][3]; s = prev + (s - prev) * ease_out((t - a) / 0.45)
            break
    if t < 0.5: s += 0.30 * (1 - ease_out(t / 0.5))
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
S["hooklab"] = chip("HAUL  ·  SCHNELL NACH HAUSE", size=38)
SEVEN_M = tmask("SCHNELL", font("Unbounded", 150, 900), 4)[0]
S["tage"] = sprite_fill(tmask("ZUHAUSE", font("Archivo", 118, 900, 118), 4)[0], WHITE, shadow=0.0, stroke=(BLUE * 0.8, 7))
for n in ("01", "02"): S["n" + n] = sprite_outline(tmask(n, font("Unbounded", 170, 900))[0], WHITE, 4)
ACC_M = tmask("ACCOUNT", font("Archivo", 150, 900, 118), 2)[0]
S["c40"] = chip("Coupons", bg=BLUE, fg=WHITE, size=60); S["c30"] = chip("Über meinen Link", bg=BLUE, fg=WHITE, size=52)
S["aufship"] = chip("Auf Shipping", tick=True, size=42)
S["nurkl"] = chip("Nur Klamotten?", size=44)
S["keine"] = sprite_fill(tmask("KEINE", font("Archivo", 130, 900, 125), 8)[0], WHITE, shadow=0.0, stroke=(INK, 6))
EXTRAS_M = tmask("EXTRAS", font("Unbounded", 150, 900), 4)[0]
S["nicht"] = sprite_fill(tmask("NICHT", font("Archivo", 120, 900, 125), 10)[0], CORAL, shadow=0.0, stroke=(INK, 6))
KOMB_M = tmask("KOMBINIEREN", font("Archivo", 108, 900, 108), 2)[0]
S["pluszeit"] = chip("+ Zeit", bg=CORAL, fg=WHITE, size=46)
S["mehrzeit"] = sprite_outline(tmask("MEHR ZEIT", font("Unbounded", 110, 900), 4)[0], WHITE, 4)
XS_M = tmask("EXTRA", font("Unbounded", 170, 900), 6)[0]
S["services"] = sprite_fill(tmask("Services", font("InstrumentSerif-Italic", 170))[0], WHITE, shadow=0.6, sblur=12)
IN7_M = tmask("SCHNELL ZU DIR", font("Archivo", 112, 900, 112), 2)[0]
S["link"] = link_card(size=52)
_lg = Image.open("img/brand_logo.png").convert("RGBA")
def _logo(sz):
    arr = np.asarray(_lg.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; return arr[..., :3], arr[..., 3], (0, 0)
S["logo_s"] = _logo(170); S["logo_m"] = _logo(210)

def card(img, cw, ch, label=None, z=1.04):
    return card_sprite(img, cw, ch, z, label)
S["haul_card"] = card(load_img("img/haul.png"), 360, 460, None)

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
    if t < 6.80:
        z = 1 + 1.4 * ease_io((t - 5.90) / 0.4); cy = 0.5 + (0.375 - 0.5) * ease_io((t - 5.90) / 0.4)
        return "profile", z, cy, ease_io((t - 6.05) / 0.3), (clamp((t - 6.35) / 0.35) if t >= 6.35 else -1), 0.0
    if t < 20.0:
        z = 1 + 0.9 * ease_io((t - 6.85) / 0.4); cy = 0.5 + (0.72 - 0.5) * ease_io((t - 6.85) / 0.4)
        return "beacons", z, cy, ease_io((t - 7.05) / 0.3), (clamp((t - 7.40) / 0.35) if t >= 7.40 else -1), ease_out((t - 7.15) / 0.3)
    k = clamp((t - 27.2) / 0.5)
    return "beacons", 1 + 0.55 * ease_io(k), 0.5 + 0.17 * ease_io(k), ease_io((t - 27.5) / 0.3), (clamp((t - 27.8) / 0.4) if t >= 27.8 else -1), ease_out((t - 27.7) / 0.3)

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
    if t_ == "BioingTiBa":
        words += [dict(w="Bio", s=6.44, e=6.72), dict(w="einen", s=6.72, e=6.90), dict(w="USFans", s=6.90, e=7.34)]; i += 1; continue
    if t_ == "240": words.append(dict(w="2× 40 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if t_ == "230": words.append(dict(w="2× 30 %", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    rep = {"erhält": "erhaltet", "Extraservices": "Extra-Services"}
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

KPINK = np.array([255, 179, 199], np.float32) / 255     # Klarna pink
_KI = Image.open("img/klarna_icon.png").convert("RGBA")   # Klarna app icon (pink square, black K.)
def klarna_icon(sz):
    arr = np.asarray(_KI.resize((sz, sz), Image.LANCZOS)).astype(np.float32) / 255; pad = 30
    a = np.pad(arr[..., 3], pad); rgb = np.pad(arr[..., :3], ((pad, pad), (pad, pad), (0, 0)))
    sh = cv2.GaussianBlur(np.roll(a, 10, 0), (0, 0), 12) * 0.45; A_ = a + sh * (1 - a)
    return rgb * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
def klarna_chip(text="Klarna", size=48):
    """dark pill, Klarna app icon on the left, pink text"""
    f = font("Archivo", size, 900, 112); ic = int(size * 1.45); ph = int(size * 1.9); pad = 40
    pw = int(14 + ic + 18 + f.getlength(text) + 34)
    im = Image.new("RGBA", (pw + 2 * pad, ph + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], ph // 2, fill=(18, 14, 16, 238))
    im.alpha_composite(_KI.resize((ic, ic), Image.LANCZOS), (pad + 14, pad + (ph - ic) // 2))
    d.text((pad + 14 + ic + 18, pad + ph / 2), text, font=f, fill=(255, 179, 199, 255), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255; a = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(a, 12, 0), (0, 0), 14) * 0.45; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (pad, pad)
words = _us_words(words, [2.24, 8.72, 9.68])
KEY = {"usfans", "klarna", "usfans-haul", "klarna-user", "hauls", "7", "tagen", "hause", "1", "link", "bio", "gtbuy", "2× 40 %", "2× 30 %", "shipping", "2", "klamotten",
       "extras", "paket", "zeit", "extra-services", "paketen"}
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
    nxt0 = chunks[j + 1][0]["s"] - 0.05 if j + 1 < len(chunks) else 26.2
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
VIO = BLUE
VIO_L = (196, 170, 255)

def caption_layer(t, L):
    """new caption style: a violet highlight box slides under the word being spoken"""
    ch = next((c for c in CH if c["t0"] <= t < c["t1"]), None)
    if ch is None: return
    toks = [clean(w["w"]) for w in ch["words"]]; keys = [tk.lower() in KEY for tk in toks]
    fs = [F_CAP for k in keys]; sp = 34
    wd = [f.getlength(tk) for f, tk in zip(fs, toks)]; total = sum(wd) + sp * (len(toks) - 1)
    scale = min(1.0, 940 / total)
    kin = 1.0 if ch["prev_adj"] else ease_out((t - ch["t0"]) / 0.16); kout = 1.0 if ch["adj"] else ease_io((ch["t1"] - t) / 0.12)
    a = kin * kout
    if a <= 0: return
    cw, chh = int(total + 120), 230
    img = Image.new("RGBA", (cw, chh), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([20, 58, cw - 20, 190], 40, fill=(10, 10, 18, 165))
    xs = []; x = 60
    for wdt in wd: xs.append(x); x += wdt + sp
    # sliding highlight box: interpolate between word boxes
    cur = None
    for n, w in enumerate(ch["words"]):
        if t >= w["s"] - 0.03: cur = n
    if cur is not None:
        k = ease_out((t - ch["words"][cur]["s"] + 0.03) / 0.12)
        pv = max(cur - 1, 0)
        bx0 = xs[pv] + (xs[cur] - xs[pv]) * k; bw = wd[pv] + (wd[cur] - wd[pv]) * k
        d.rounded_rectangle([bx0 - 14, 72, bx0 + bw + 14, 176], 22, fill=(140, 92, 255, 255))
    base = 150
    for n, (w, tk, f, k) in enumerate(zip(ch["words"], toks, fs, keys)):
        spoken = t > w["e"] + 0.03; active = cur == n
        col = (255, 255, 255) if active else (VIO_L if (spoken and k) else (255, 255, 255))
        al = 1.0 if (active or spoken) else 0.55
        d.text((xs[n], base), tk, font=f, fill=col + (int(255 * al),), anchor="ls")
    arr = np.asarray(img).astype(np.float32) / 255; ca = arr[..., 3]
    sh = cv2.GaussianBlur(np.roll(ca, 6, 0), (0, 0), 10) * 0.4; A_ = ca + sh * (1 - ca)
    rgb = arr[..., :3] * ca[..., None] / np.maximum(A_[..., None], 1e-4)
    rise = (1 - ease_out((t - ch["t0"]) / 0.18)) * 22 if not ch["prev_adj"] else 0
    place(L, (rgb, A_, (0, 0)), W / 2, CAP_Y + rise, s=scale, alpha=a)

def strike(L, x0, y0, x1, y1, prog, alpha):
    if prog <= 0: return
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(x0), int(y0)), (int(x0 + (x1 - x0) * prog), int(y0 + (y1 - y0) * prog)), 1.0, 16, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def forbid(L, cx, cy, r, prog, alpha):
    """prohibition sign drawn on: ring, then slash"""
    if prog <= 0: return
    m = np.zeros((H, W), np.float32)
    cv2.ellipse(m, (int(cx), int(cy)), (int(r), int(r)), 0, -90, -90 + 360 * clamp(prog / 0.6), 1.0, 16, cv2.LINE_AA)
    if prog > 0.6:
        q = clamp((prog - 0.6) / 0.4); d = r * 0.707
        cv2.line(m, (int(cx - d), int(cy - d)), (int(cx - d + 2 * d * q), int(cy - d + 2 * d * q)), 1.0, 16, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def box_sprite(sc_, label=None):
    col = tuple(int(v * 255) for v in VIO)
    w = int(220 * sc_); h = int(170 * sc_); d = int(110 * sc_); pad = 40
    im = Image.new("RGBA", (w + d + 2 * pad, h + d + 2 * pad), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    x0, y0 = pad, pad + d
    front = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)]
    top = [(x0, y0), (x0 + d, y0 - d), (x0 + w + d, y0 - d), (x0 + w, y0)]
    side = [(x0 + w, y0), (x0 + w + d, y0 - d), (x0 + w + d, y0 - d + h), (x0 + w, y0 + h)]
    dr.polygon(front, fill=(198, 150, 98, 255)); dr.polygon(top, fill=(222, 178, 122, 255)); dr.polygon(side, fill=(165, 120, 74, 255))
    for poly in (front, top, side): dr.line(poly + [poly[0]], fill=(40, 28, 16, 255), width=max(3, int(5 * sc_)), joint="curve")
    tw = max(10, int(26 * sc_))
    dr.polygon([(x0 + w / 2 - tw / 2, y0), (x0 + w / 2 + d - tw / 2, y0 - d), (x0 + w / 2 + d + tw / 2, y0 - d), (x0 + w / 2 + tw / 2, y0)], fill=col + (255,))
    dr.rectangle([x0 + w / 2 - tw / 2, y0, x0 + w / 2 + tw / 2, y0 + h * 0.35], fill=col + (255,))
    if label: dr.text((x0 + w / 2, y0 + h * 0.68), label, font=font("Archivo", max(18, int(40 * sc_)), 900, 112), fill=(40, 28, 16, 255), anchor="mm")
    arr = np.asarray(im).astype(np.float32) / 255
    a = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(a, 14, 0), (0, 0), 16) * 0.5; A_ = a + sh * (1 - a)
    return arr[..., :3] * a[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)
S["box_a"] = box_sprite(0.72, "A"); S["box_b"] = box_sprite(0.72, "B")

def route_bar(t, L):
    """hook infographic: plane flies China -> Zuhause while the day counter runs 1..7"""
    a = win(t, 1.15, 3.80, 0.3, 0.25)
    if a <= 0: return
    pw, ph = 940, 170
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], 44, fill=(10, 10, 18, 215))
    prog = ease_io((t - 1.45) / 2.0)
    x0, x1, y = 120, pw - 250, 95
    for k in range(22):
        xa = x0 + (x1 - x0) * k / 22
        d.line([(xa, y), (xa + (x1 - x0) / 44, y)], fill=(255, 255, 255, 110), width=4)
    d.line([(x0, y), (x0 + (x1 - x0) * prog, y)], fill=(140, 92, 255, 255), width=8)
    d.ellipse([x0 - 14, y - 14, x0 + 14, y + 14], fill=(255, 255, 255, 255))
    d.ellipse([x1 - 14, y - 14, x1 + 14, y + 14], fill=(140, 92, 255, 255) if prog > 0.98 else (255, 255, 255, 255))
    fs_ = font("SpaceGrotesk", 26, 700)
    d.text((x0, y + 44), "CHINA", font=fs_, fill=(255, 255, 255, 230), anchor="mm"); d.text((x1, y + 44), "ZUHAUSE", font=fs_, fill=(255, 255, 255, 230), anchor="mm")
    px = x0 + (x1 - x0) * prog; py = y - 34 - 22 * math.sin(math.pi * prog)
    d.polygon([(px + 30, py), (px - 22, py - 20), (px - 10, py), (px - 22, py + 20)], fill=(255, 255, 255, 255))
    arr = np.asarray(im).astype(np.float32) / 255
    k = ease_out((t - 1.15) / 0.4)
    place(L, (arr[..., :3], arr[..., 3], (0, 0)), W / 2, 1245 + (1 - k) * 40, alpha=a)

def clock(t, L, x, y, a, t0):
    if a <= 0: return
    sz = 230; im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = sz / 2
    d.ellipse([10, 10, sz - 10, sz - 10], fill=(250, 250, 248, 255), outline=(12, 12, 14, 255), width=8)
    for k in range(12):
        an = k * math.pi / 6; d.line([(c + 82 * math.sin(an), c - 82 * math.cos(an)), (c + 94 * math.sin(an), c - 94 * math.cos(an))], fill=(12, 12, 14, 255), width=5)
    am = (t - t0) * 2 * math.pi * 1.4; ah = am / 12
    d.line([(c, c), (c + 78 * math.sin(am), c - 78 * math.cos(am))], fill=(140, 92, 255, 255), width=9)
    d.line([(c, c), (c + 52 * math.sin(ah), c - 52 * math.cos(ah))], fill=(12, 12, 14, 255), width=11)
    d.ellipse([c - 9, c - 9, c + 9, c + 9], fill=(12, 12, 14, 255))
    arr = np.asarray(im).astype(np.float32) / 255
    al = arr[..., 3]; sh = cv2.GaussianBlur(np.roll(al, 12, 0), (0, 0), 14) * .45; A_ = al + sh * (1 - al)
    place(L, (arr[..., :3] * al[..., None] / np.maximum(A_[..., None], 1e-4), A_, (0, 0)), x, y, s=back_out((t - t0) / 0.4, 1.8), alpha=a)

def bars(t, L):
    a = win(t, 22.30, 25.92, 0.3, 0.2)
    if a <= 0: return
    pw, ph = 940, 250
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, pw - 1, ph - 1], 44, fill=(10, 10, 18, 215))
    f1 = font("SpaceGrotesk", 28, 700); f2 = font("Archivo", 34, 900, 110)
    k1 = ease_out((t - 22.4) / 0.5); k2 = ease_io((t - 23.4) / 1.6)
    d.text((40, 48), "OHNE EXTRAS", font=f1, fill=(255, 255, 255, 235), anchor="lm")
    d.rounded_rectangle([40, 74, 40 + 330 * k1 + 20, 112], 19, fill=(140, 92, 255, 255))
    if k1 > 0.9: d.text((40 + 350 + 18, 93), "schnell", font=f2, fill=(255, 255, 255, 255), anchor="lm")
    d.text((40, 160), "MIT EXTRA-SERVICES", font=f1, fill=(255, 255, 255, 235), anchor="lm")
    wl = 330 + 330 * k2
    d.rounded_rectangle([40, 186, 40 + wl, 224], 19, fill=(255, 92, 72, 255))
    if t > 23.6: d.text((40 + wl + 18, 205), "länger", font=f2, fill=(255, 255, 255, 255), anchor="lm")
    arr = np.asarray(im).astype(np.float32) / 255
    k = ease_out((t - 22.30) / 0.4)
    place(L, (arr[..., :3], arr[..., 3], (0, 0)), W / 2, 1215 + (1 - k) * 40, alpha=a)

CARGO = load_img("img/cargo.png")
def bg_replace(t, cf, cm):
    """hook: the room behind the creator becomes the air-cargo scene (circular reveal), plus portrait-mode blur later"""
    out = cf
    a = win(t, 1.30, 3.84, 0.01, 0.3)
    if a > 0:
        bg = cover(CARGO, W, H, 1.14 - 0.08 * clamp((t - 1.3) / 2.5), 0, -0.02)
        bg = cv2.GaussianBlur(bg, (0, 0), 2.0) * 0.8
        yy, xx = np.ogrid[:H, :W]; d = np.sqrt((xx - 540.0) ** 2 + (yy - 900.0) ** 2)
        r = ease_out((t - 1.30) / 0.42) * 2300
        circ = np.clip((r - d) / 30, 0, 1).astype(np.float32) * a
        cmc = cv2.GaussianBlur(np.clip((cv2.erode(cm, np.ones((5, 5), np.uint8)) - 0.25) / 0.6, 0, 1), (0, 0), 1.2)
        band = np.clip(cm - cmc, 0, 1) * circ
        out = out * (1 - 0.6 * band[..., None])
        bm = ((1 - cmc) * circ)[..., None]
        out = out * (1 - bm) + bg * bm
        ring = (np.exp(-((d - r) / 10) ** 2) * (r < 2200)).astype(np.float32)
        out = out * (1 - ring[..., None] * .8) + VIO * ring[..., None] * .8
    k = max(win(t, 14.35, 15.7, 0.3, 0.3), win(t, 16.1, 19.95, 0.4, 0.4), win(t, 20.0, 21.55, 0.2, 0.1)) * 0.8
    if k > 0.01:
        bl = cv2.GaussianBlur(cf, (0, 0), 2 + 9 * k) * (1 - 0.3 * k)
        out = cf * cm[..., None] + bl * (1 - cm[..., None])
    return out

def outline_fx(t, comp, cm):
    """sticker outline around the creator, pulses on the step numbers and the jump cut"""
    k = max(math.exp(-(t - c) / 0.35) if t >= c else 0 for c in (4.33, 11.10, 21.60))
    if k < 0.03: return comp
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    ring = np.clip(cv2.dilate(cm, ker) - cm, 0, 1); ring = cv2.GaussianBlur(ring, (0, 0), 1.5) * min(1, k * 1.4)
    return comp * (1 - ring[..., None]) + WHITE * ring[..., None]

def scene(t, back, front):
    # HOOK
    a = win(t, 0.25, 3.82, 0.25, 0.25)
    if a: place(front, S["hooklab"], W / 2, 96, alpha=a, s=1 + 0.15 * (1 - ease_out((t - .25) / .4)))
    a = win(t, 2.20, 3.82, 0.1, 0.25)
    if a:
        k = back_out((t - 2.20) / 0.45, 1.8)
        place(back, chrome_cached("seven", SEVEN_M, 24, (t - 2.5) / 0.9 if 2.5 <= t <= 3.4 else None), W / 2, 300, s=1.5 - 0.5 * k, alpha=a, blur=max(0, 1 - (t - 2.2) / .2) * 8)
        k2 = ease_out((t - 2.40) / 0.45); place(back, S["tage"], W / 2 + (1 - k2) * 200, 460, alpha=a * k2)
    route_bar(t, front)
    # STEP 1
    a = win(t, 4.40, 5.65, 0.25, 0.2)
    if a:
        k = ease_out((t - 4.40) / 0.5)
        place(back, S["n01"], W / 2 - 250, 190, s=0.8 + 0.2 * k, alpha=a)
        place(back, chrome_cached("acc", ACC_M, 14, (t - 4.7) / 0.8 if 4.7 <= t <= 5.5 else None), W / 2, 380, rx=-60 * (1 - k), alpha=a)
    a = win(t, 5.55, 8.15, 0.35, 0.3)
    if a:
        k = ease_out((t - 5.55) / 0.5); ko = ease_in((t - 7.85) / 0.3) if t > 7.85 else 0
        nm, z, cy, hl, tap, badge = phone_state(t)
        px = 865 + (1 - k) * 500 + ko * 600
        place(front, phone(nm, z, cy, hl, tap, badge), px, 820, rot=-4 * (1 - k) + 3, alpha=a, s=0.9)
        if t >= 6.85: place(front, S["logo_s"], px - 150, 330, s=back_out((t - 6.85) / 0.35, 2.0), alpha=a, rot=-8)
    for key_, t0, y in (("c40", 8.70, 520), ("c30", 9.66, 660)):
        a = win(t, t0, 10.98, 0.2, 0.2)
        if a: place(front, S[key_], 1030, y, anchor=(1.0, 0.5), s=back_out((t - t0) / 0.35, 2.2), alpha=a)
    a = win(t, 10.44, 10.98, 0.15, 0.2)
    if a: place(front, S["aufship"], 1030, 790, anchor=(1.0, 0.5), alpha=a)
    # STEP 2
    a = win(t, 11.15, 12.60, 0.25, 0.2)
    if a: place(back, S["n02"], W / 2 - 250, 250, s=0.8 + 0.2 * ease_out((t - 11.15) / .5), alpha=a)
    a = win(t, 11.95, 14.30, 0.4, 0.3)
    if a:
        k = ease_out((t - 11.95) / 0.55)
        place(front, S["haul_card"], 860, 720 + (1 - k) * 140, rot=4, s=0.94 + 0.06 * k, alpha=a)
        place(front, S["nurkl"], 1040, 1000, anchor=(1.0, 0.5), s=back_out((t - 12.1) / 0.35, 2.0), alpha=a)
    a = win(t, 14.40, 15.75, 0.12, 0.25)
    if a:
        k = back_out((t - 14.40) / 0.4, 1.8)
        place(back, S["keine"], W / 2, 190, alpha=a, s=k)
        place(back, chrome_cached("extras", EXTRAS_M, 16, (t - 14.8) / 0.7 if 14.8 <= t <= 15.5 else None), W / 2, 380, s=back_out((t - 14.80) / 0.4, 1.8), alpha=a * clamp((t - 14.8) / .05))
    # don't combine parcels
    a = win(t, 16.20, 19.92, 0.25, 0.3)
    if a:
        k = ease_out((t - 16.20) / 0.5)
        place(back, S["nicht"], W / 2, 170, alpha=a * ease_out((t - 16.9) / .3), s=back_out((t - 16.9) / .35, 2.0))
        place(back, chrome_cached("komb", KOMB_M, 14, (t - 16.6) / 0.8 if 16.6 <= t <= 17.4 else None), W / 2, 345, rx=-60 * (1 - k), alpha=a)
        j = ease_io((t - 16.9) / 0.4) * 40
        place(front, S["box_a"], 770 + j, 640, s=back_out((t - 16.26) / 0.35, 2.0), alpha=a)
        place(front, S["box_b"], 985 - j, 640, s=back_out((t - 16.40) / 0.35, 2.0), alpha=a)
        forbid(front, 878, 650, 150, ease_io((t - 16.92) / 0.5), a)
    a = win(t, 18.05, 21.55, 0.2, 0.15)
    if a:
        clock(t, front, 870, 960, a, 18.05)
        if t >= 19.16: place(front, S["pluszeit"], 870, 1125, s=back_out((t - 19.16) / 0.35, 2.0), alpha=a)
    a = win(t, 20.02, 21.55, 0.2, 0.1)
    if a: place(back, S["mehrzeit"], W / 2, 300, s=1.2 - 0.2 * ease_out((t - 20.02) / 0.4), alpha=a)
    # extra services
    a = win(t, 21.90, 25.92, 0.25, 0.2)
    if a:
        k = ease_out((t - 21.90) / 0.5)
        place(back, chrome_cached("xs", XS_M, 14, (t - 22.2) / 0.8 if 22.2 <= t <= 23.0 else None), W / 2, 250, rx=-60 * (1 - k), alpha=a)
        place(back, S["services"], W / 2, 400, alpha=a * ease_out((t - 22.1) / .4))
    bars(t, front)

def fullscreen(t, comp): return comp

ROWS12 = [chip("Account über den 1. Link", tick=True, size=40), chip("Keine Extras dazu", tick=True, size=40), chip("Pakete nicht kombinieren", tick=True, size=40)]
def endcard(t, comp):
    if t < 25.95: return comp
    L = new_layer()
    k0 = ease_out((t - 26.0) / 0.5)
    place(L, S["logo_m"], W / 2, 170, s=0.7 + 0.3 * back_out((t - 26.0) / 0.5, 1.8), rx=-70 * (1 - k0), alpha=k0)
    k = ease_out((t - 26.15) / 0.45)
    place(L, chrome_cached("in7", IN7_M, 16, (t - 26.5) / 0.9 if 26.5 <= t <= 27.4 else None), W / 2, 400, s=0.9 + 0.1 * k, rx=-60 * (1 - k), alpha=clamp((t - 26.15) / .1))
    for n, sp in enumerate(ROWS12):
        t0 = 26.45 + n * 0.18
        if t >= t0: place(L, sp, W / 2, 580 + n * 96, s=back_out((t - t0) / 0.35, 2.0), alpha=ease_out((t - t0) / .2))
    k3 = ease_out((t - 26.7) / 0.55)
    nm, z, cy, hl, tap, badge = phone_state(t)
    place(L, phone(nm, z, cy, hl, tap, badge), W / 2, 1230 + (1 - k3) * 300, rot=-2.5 * (1 - k3), alpha=k3, s=0.66)
    k4 = ease_out((t - 28.0) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1690, s=back_out((t - 28.0) / 0.4, 1.8), alpha=k4)
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
    if 4.21 <= t < 4.33: dx = -ease_in((t - 4.21) / 0.12) * W * 0.55
    if 4.33 <= t < 4.47: dx = (1 - ease_out((t - 4.33) / 0.14)) * W * 0.55
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
    base = bg_replace(t, cf, cm)
    comp = base * (1 - back[1][..., None] * (1 - cm[..., None])) + back[0] * (1 - cm[..., None])
    comp = outline_fx(t, comp, cm)
    comp = fullscreen(t, comp)
    comp = comp * (1 - front[1][..., None]) + front[0]
    if t >= 25.95:
        k = ease_io((t - 25.95) / 0.5); comp = cv2.GaussianBlur(comp, (0, 0), 0.1 + 16 * k) * (1 - 0.55 * k)
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
