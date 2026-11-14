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
    day = 1 + int(min(prog, 0.999) * 7)
    d.text((pw - 112, 52), "TAG", font=font("SpaceGrotesk", 30, 700), fill=VIO_L + (255,), anchor="mm")
    d.text((pw - 112, 110), str(day), font=font("Unbounded", 76, 900), fill=(255, 255, 255, 255), anchor="mm")
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
    if k1 > 0.9: d.text((40 + 350 + 18, 93), "7 Tage", font=f2, fill=(255, 255, 255, 255), anchor="lm")
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
        place(back, chrome_cached("seven", SEVEN_M, 24, (t - 2.5) / 0.9 if 2.5 <= t <= 3.4 else None), 235, 400, s=1.5 - 0.5 * k, alpha=a, blur=max(0, 1 - (t - 2.2) / .2) * 8)
        k2 = ease_out((t - 2.40) / 0.45); place(back, S["tage"], 775 + (1 - k2) * 200, 330, alpha=a * k2)
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

