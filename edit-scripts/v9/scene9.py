def ticker(t, L):
    """news ticker band at the top during the hook ('Neuigkeiten')"""
    a = win(t, 0.95, 6.45, 0.35, 0.35)
    if a <= 0: return
    f = font("Archivo", 40, 900, 118); txt = "NEWS   •   GTBUY × PAYPAL   •   "
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
    if prog <= 0: return
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(x0), int(y0)), (int(x0 + (x1 - x0) * prog), int(y0 + (y1 - y0) * prog)), 1.0, 16, cv2.LINE_AA)
    m *= alpha; L[0] *= (1 - m[..., None]); L[0] += CORAL * m[..., None]; L[1] *= (1 - m); L[1] += m

def calendar(t, L, x, y, a):
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

