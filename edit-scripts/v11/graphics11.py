# ---- per-scene graphics (monochrome: black / white / chrome)
INKC = np.array([0.05, 0.05, 0.06], np.float32)
FIT_M = tmask("FIT", font("Unbounded", 330, 900), 8)[0]
S["fit_echo"] = sprite_outline(FIT_M, WHITE, 3)
S["check"] = sprite_fill(tmask("CHECK", font("Archivo", 120, 900, 125), 26)[0], WHITE, shadow=0.6, sblur=10, stroke=(INKC, 5))
MAI_M = tmask("MAISON", font("Anton-Regular", 200), 16)[0]; MAR_M = tmask("MARGIELA", font("Anton-Regular", 200), 16)[0]
S["c_jacke"] = chip("Jacke  ·  via GTBuy", bg=WHITE, fg=INKC, size=44)
S["zara_o"] = sprite_outline(tmask("ZARA", font("Archivo", 260, 900, 125), 10)[0], WHITE, 4)
S["teehose"] = chip("T-Shirt  &  Hose  ·  Zara", bg=WHITE, fg=INKC, size=42)
S["dior"] = sprite_fill(tmask("Dior", font("InstrumentSerif-Regular", 380), 4)[0], INKC, shadow=0.25, sblur=24, soff=(20, 10))
S["c_schuhe"] = chip("Schuhe  ·  via GTBuy", bg=INKC, fg=WHITE, size=44)
AB_M = tmask("ALL BLACK", font("Unbounded", 118, 900), 6)[0]
S["every"] = sprite_outline(tmask("EVERYTHING", font("Archivo", 86, 900, 118), 10)[0], WHITE, 3)
S["best"] = sprite_fill(tmask("BESTELLT  ÜBER", font("SpaceGrotesk", 36, 700), 9)[0], WHITE, shadow=0.0)
GTB_M = tmask("GTBuy", font("Unbounded", 170, 900), 2)[0]
S["link"] = link_card(size=50)
LOGO = np.asarray(Image.open("img/gtbuy_logo.png").convert("RGBA").resize((210, 210), Image.LANCZOS)).astype(np.float32) / 255
S["logo"] = (LOGO[..., :3], LOGO[..., 3], (0, 0))
STUDIO = load_img("img/studio.png"); POOL_Y = 0.80
TAGS2 = [("JACKE", "MAISON MARGIELA", True, 1.35, "chest", "L", 640), ("HOSE", "ZARA", False, 1.65, "thigh", "R", 1230),
         ("SCHUHE", "DIOR", True, 1.95, "foot", "L", 1520)]
for it, br, gt, *_ in TAGS2: S["tag_" + it + br] = tag_sprite(it, br, gt)

def graphics(t, sc, f, M, back, front):
    sid = sc[0]; bp = pulse(t)
    if sid == 1:
        a = win(t, 0.05, 1.17, 0.2, 0.08)
        k = back_out((t - 0.05) / 0.4, 1.8)
        for dy, al in ((150, 0.35), (80, 0.6)):
            place(back, S["fit_echo"], W / 2, 170 + dy * (0.6 + 0.4 * bp), s=1.0 + 0.04 * bp, alpha=a * al * clamp((t - 0.2) / 0.2))
        sw = (t - 0.3) / 0.8 if 0.3 <= t <= 1.1 else None
        place(back, chrome_cached("fit", FIT_M, 22, sw), W / 2, 170, s=(1.5 - 0.5 * k) * (1 + 0.04 * bp), alpha=clamp(t / 0.06) * a, blur=max(0, 1 - t / 0.2) * 8)
        k2 = ease_out((t - 0.3) / 0.45)
        place(back, S["check"], W / 2, 350, s=(1.25 - 0.25 * k2) * 0.85, alpha=a * k2)
    if sid == 2: tags(t, f, M, front, TAGS2, 2.50)
    if sid == 3:
        a = win(t, 2.75, 4.30, 0.3, 0.1); k = ease_out((t - 2.75) / 0.5)
        sw = (t - 3.0) / 0.9 if 3.0 <= t <= 3.9 else None
        place(back, chrome_cached("mai", MAI_M, 14, sw), W / 2 - (1 - k) * 250, 230, alpha=a)
        place(back, chrome_cached("mar", MAR_M, 14, sw), W / 2 + (1 - k) * 250, 440, alpha=a)
        a2 = win(t, 3.05, 4.30, 0.25, 0.1); k2 = ease_out((t - 3.05) / 0.45)
        place(back, S["label"], 345, 700 - (1 - k2) * 60, alpha=a2, rot=-3)
        scribble_circle(back, (345 - 340 + 40 + 40 + 10 * 47, 700 - 140 + 40 + 72 + 6), 32, 30, ease_io((t - 3.35) / 0.3), a2, col=INKC, w=5, seed=3)
        a3 = win(t, 3.55, 4.30, 0.2, 0.1)
        if a3: place(front, S["c_jacke"], W / 2, 1300, s=back_out((t - 3.55) / 0.3, 2.0), alpha=a3)
    if sid == 4:
        a = win(t, 4.50, 5.95, 0.3, 0.1)
        for r in range(3):
            y = 380 + r * 330; dx = ((t - 4.4) * (90 if r % 2 == 0 else -90)) + (r - 1) * 140
            place(back, S["zara_o"], W / 2 + dx, y, alpha=a * (0.9 - 0.2 * r), s=1.0 + 0.03 * bp)
        a2 = win(t, 4.85, 5.95, 0.2, 0.1)
        if a2: place(front, S["teehose"], W / 2, 1560, s=back_out((t - 4.85) / 0.3, 2.0), alpha=a2)
    if sid == 5:
        a = win(t, 6.35, 7.88, 0.35, 0.1); k = ease_out((t - 6.35) / 0.55)
        place(back, S["dior"], W / 2, 640 + (1 - k) * 80, s=0.9 + 0.1 * k, alpha=a)
        p = apply(M, anchor("feet", f))
        scribble_circle(front, p + np.array([0, -10.0]), 190, 90, ease_io((t - 6.75) / 0.4), a, col=INKC, w=7, seed=4)
        a2 = win(t, 7.05, 7.88, 0.2, 0.1)
        if a2: place(front, S["c_schuhe"], W / 2, min(p[1] + 190, 1640), s=back_out((t - 7.05) / 0.3, 2.0), alpha=a2)
    if sid == 7:
        a = win(t, 9.20, 11.05, 0.35, 0.15); k = ease_out((t - 9.20) / 0.55)
        sw = (t - 9.5) / 0.9 if 9.5 <= t <= 10.4 else None
        place(back, chrome_cached("ab", AB_M, 16, sw), W / 2, 210, rx=-70 * (1 - k), alpha=a, s=1 + 0.03 * bp)
        a2 = win(t, 9.75, 11.05, 0.3, 0.15)
        if a2: place(back, S["every"], W / 2, 380, alpha=a2, s=1.1 - 0.1 * ease_out((t - 9.75) / 0.4))

def tickers(t, back):
    a = win(t, 7.96, 9.00, 0.2, 0.1)
    if a <= 0: return
    k = ease_out((t - 7.96) / 0.3)
    for text, bg, fg, y, speed, ang in (("VIA GTBUY   •   MAISON MARGIELA   •   DIOR   •   ", WHITE, INKC, 760, 560, -7),
                                        ("ALL BLACK   •   ALL BLACK   •   ", INKC, WHITE, 1050, -460, 5)):
        band = ticker_band(text, bg, fg, 130, (t - 7.9) * speed + 2000)
        hh, ww = band.shape[:2]
        place(back, (band, np.ones((hh, ww), np.float32), (0, 0)), W / 2 + (1 - k) * (W if speed > 0 else -W), y, rot=ang, alpha=a)

def endcard(t, comp):
    if t < 11.30: return comp
    L = new_layer()
    k0 = ease_out((t - 11.30) / 0.5)
    place(L, S["logo"], W / 2, 190, s=0.7 + 0.3 * back_out((t - 11.3) / 0.5, 1.8), rx=-70 * (1 - k0), alpha=k0)
    k = ease_out((t - 11.45) / 0.4); place(L, S["best"], W / 2, 365 - (1 - k) * 20, alpha=k)
    k2 = ease_out((t - 11.55) / 0.5)
    place(L, chrome_cached("gtb", GTB_M, 14, (t - 12.0) / 0.9 if 12.0 <= t <= 12.9 else None), W / 2, 495, s=0.9 + 0.1 * k2, rx=-60 * (1 - k2), alpha=clamp((t - 11.55) / .1))
    for n, sp in enumerate(ROW_S):
        t0 = 11.85 + n * 0.17; kk = ease_out((t - t0) / 0.3)
        if kk <= 0: continue
        y = 760 + n * 100
        place(L, check_sprite(26, clamp((t - t0) / 0.22)), 140, y, s=back_out((t - t0) / 0.3, 2.0), alpha=kk)
        place(L, sp, 190 + (1 - kk) * 30, y, anchor=(30 / sp[1].shape[1], 0.5), alpha=kk)
    k4 = ease_out((t - 12.6) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1260, s=back_out((t - 12.6) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

