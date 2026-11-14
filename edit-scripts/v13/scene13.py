ITEMS = [("Puffer-Weste", 8.0), ("Hose", 9.5), ("Jogger", 11.0), ("Half-Zip Schwarz", 12.5), ("Half-Zip Beige", 14.0),
         ("Half-Zip Weiß", 15.5), ("Trainingshose", 17.0), ("Polo", 18.5), ("Pufferjacke", 20.0)]
BOUNDS = [2.10] + [t0 for _, t0 in ITEMS] + [22.0, 23.0]
NUM = [sprite_chrome(tmask(f"{k + 1:02d}", font("Unbounded", 150, 900))[0], depth=12) for k in range(len(ITEMS))]
NAME = [sprite_fill(tmask(nm.upper(), font("Archivo", 96 if len(nm) < 14 else 78, 900, 118), 2)[0], WHITE, shadow=0.0, stroke=(INK, 7)) for nm, _ in ITEMS]

def whip(t):
    for n, b in enumerate(BOUNDS):
        sg = -1 if n % 2 == 0 else 1
        if b - 0.10 <= t < b: return sg * ease_in((t - (b - 0.10)) / 0.10) * W * 0.5
        if b <= t < b + 0.12: return -sg * (1 - ease_out((t - b) / 0.12)) * W * 0.5
    return 0.0

def progress(t, L):
    if t < 8.0 or t >= 23.0: return
    cur = max(k for k, (_, t0) in enumerate(ITEMS) if t >= t0) if t < 22.0 else len(ITEMS) - 1
    n = len(ITEMS); sw, gap = 86, 12; x0 = W / 2 - (n * sw + (n - 1) * gap) / 2
    im = Image.new("RGBA", (W, 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(n):
        x = x0 + k * (sw + gap)
        d.rounded_rectangle([x, 20, x + sw, 34], 7, fill=(10, 10, 14, 170))
        if k < cur: d.rounded_rectangle([x, 20, x + sw, 34], 7, fill=(250, 250, 248, 255))
        elif k == cur:
            t0 = ITEMS[k][1]; t1 = ITEMS[k + 1][1] if k + 1 < n else 23.0
            d.rounded_rectangle([x, 20, x + max(14, sw * clamp((t - t0) / (t1 - t0))), 34], 7, fill=(255, 140, 0, 255))
    arr = np.asarray(im).astype(np.float32) / 255
    place(L, (arr[..., :3], arr[..., 3], (0, 0)), W / 2, 70, alpha=ease_out((t - 8.0) / 0.3))

def scene(t, back, front):
    # HOOK
    a = win(t, 0.05, 2.05, 0.15, 0.12)
    if a:
        k = back_out((t - 0.05) / 0.45, 1.8)
        place(back, chrome_cached("5kg", KG_M, 22, (t - 0.4) / 0.9 if 0.4 <= t <= 1.3 else None), W / 2, 240, s=1.5 - 0.5 * k, alpha=a * clamp(t / .06), blur=max(0, 1 - t / .2) * 8)
        k2 = ease_out((t - 0.85) / 0.4)
        place(back, S["haulw"], W / 2, 440, s=1.25 - 0.25 * k2, alpha=a * k2)
    a = win(t, 1.72, 2.05, 0.1, 0.1)
    if a: place(front, S["yalla"], 820, 640, s=back_out((t - 1.72) / 0.3, 2.2), rot=-8, alpha=a)
    # COUPONS + link screenshots
    a = win(t, 2.45, 4.75, 0.3, 0.25)
    if a:
        k = ease_out((t - 2.45) / 0.45); ko = ease_in((t - 4.5) / 0.25) if t > 4.5 else 0
        nm, z, cy, hl, tap, badge = phone_state(t)
        px = 840 + (1 - k) * 500 + ko * 600
        place(front, phone(nm, z, cy, hl, tap, badge), px, 540, rot=-4 * (1 - k) + 3, alpha=a, s=0.74)
        place(front, S["logo_s"], px - 150, 150, s=back_out((t - 2.8) / 0.35, 2.0), alpha=a * clamp((t - 2.8) / .1), rot=-8)
    for key_, t0, y in (("c40", 4.48, 250), ("c30", 5.46, 390)):
        a = win(t, t0, 6.85, 0.2, 0.2)
        if a: place(front, S[key_], 1030, y, anchor=(1.0, 0.5), s=back_out((t - t0) / 0.35, 2.2), alpha=a)
    a = win(t, 6.36, 6.85, 0.15, 0.2)
    if a: place(front, S["aufship"], 1030, 520, anchor=(1.0, 0.5), alpha=a)
    a = win(t, 6.90, 7.98, 0.12, 0.12)
    if a:
        k = back_out((t - 6.90) / 0.4, 1.8)
        place(front, S["jetzt"], W / 2, 170, alpha=a, s=k)
        place(front, chrome_cached("anm", ANM_M, 16, (t - 7.1) / 0.7 if 7.1 <= t <= 7.8 else None), W / 2, 330, s=back_out((t - 7.02) / 0.4, 1.8), alpha=a * clamp((t - 7.02) / .05))
    # ITEM MONTAGE
    for k, (nm, t0) in enumerate(ITEMS):
        t1 = ITEMS[k + 1][1] if k + 1 < len(ITEMS) else 22.0
        if not (t0 <= t < t1): continue
        u = t - t0; a = min(ease_out(u / 0.15), ease_io((t1 - t) / 0.1))
        place(front, NUM[k], 215, 250, s=1.35 - 0.35 * back_out(u / 0.35, 1.8), alpha=a, rot=-6)
        ks = ease_out((u - 0.08) / 0.35)
        ns = min(1.0, 960 / (NAME[k][1].shape[1] - 100))
        place(front, NAME[k], W / 2, 1560 + (1 - ks) * 60, s=ns, alpha=a * ks)
        m = np.zeros((H, W), np.float32); wl = (NAME[k][1].shape[1] - 100) * ns
        cv2.line(m, (int(W / 2 - wl / 2), 1632), (int(W / 2 - wl / 2 + wl * ease_io((u - 0.2) / 0.35)), 1632), 1.0, 12, cv2.LINE_AA)
        m *= a * (u > 0.2); front[0] *= (1 - m[..., None]); front[0] += BLUE * m[..., None]; front[1] *= (1 - m); front[1] += m
    a = win(t, 22.05, 22.98, 0.15, 0.1)
    if a: place(front, S["detail"], W / 2, 1560, s=back_out((t - 22.05) / 0.35, 2.0), alpha=a)
    progress(t, front)

def fullscreen(t, comp): return comp

def endcard(t, comp):
    if t < 23.45: return comp
    L = new_layer()
    k0 = ease_out((t - 23.5) / 0.5)
    place(L, S["logo_m"], W / 2, 160, s=0.7 + 0.3 * back_out((t - 23.5) / 0.5, 1.8), rx=-70 * (1 - k0), alpha=k0)
    k = ease_out((t - 23.65) / 0.45)
    place(L, chrome_cached("5kgh", KGH_M, 16, (t - 24.0) / 0.9 if 24.0 <= t <= 24.9 else None), W / 2, 385, s=0.9 + 0.1 * k, rx=-60 * (1 - k), alpha=clamp((t - 23.65) / .1))
    for n, key in enumerate(("e1", "e2")):
        t0 = 23.95 + n * 0.18
        if t >= t0: place(L, S[key], W / 2, 545 + n * 96, s=back_out((t - t0) / 0.35, 2.0), alpha=ease_out((t - t0) / .2))
    k3 = ease_out((t - 24.2) / 0.55)
    place(L, S["haul_card"], 300, 1180 + (1 - k3) * 300, rot=-4, alpha=k3)
    nm, z, cy, hl, tap, badge = phone_state(t)
    place(L, phone(nm, z, cy, hl, tap, badge), 790, 1180 + (1 - k3) * 380, rot=3 * (1 - k3) + 2, alpha=k3, s=0.66)
    k4 = ease_out((t - 25.6) / 0.4)
    if k4 > 0: place(L, S["link"], W / 2, 1690, s=back_out((t - 25.6) / 0.4, 1.8), alpha=k4)
    return comp * (1 - L[1][..., None]) + L[0]

