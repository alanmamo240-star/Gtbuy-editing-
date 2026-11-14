def strike(L, x0, y0, x1, y1, prog, alpha):
    if prog <= 0: return
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
S["logo"] = (lambda arr: (arr[..., :3], arr[..., 3], (0, 0)))(np.asarray(Image.open("img/gtbuy_logo.png").convert("RGBA").resize((300, 300), Image.LANCZOS)).astype(np.float32) / 255)
S["logo_s"] = (lambda arr: (arr[..., :3], arr[..., 3], (0, 0)))(np.asarray(Image.open("img/gtbuy_logo.png").convert("RGBA").resize((170, 170), Image.LANCZOS)).astype(np.float32) / 255)

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
    # GTBuy logo on "GTBuy"
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

