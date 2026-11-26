NAME = 'v15 "Klarna bei USFans"'
SIL = [(2.83, 3.33), (7.02, 7.79), (19.39, 19.75)]
END = 20.4
FREEZE = 1.8
NCH = 6
SHOTS = """
SHOTS = [(0.0, 1.12, None), (2.94, 1.0, None), (5.14, 1.28, None), (7.69, 1.0, None), (10.06, 1.25, None), (11.98, 1.05, None),
         (13.4, 1.38, 345), (17.9, 1.0, None), (19.6, 1.25, None)]
"""
YFORM = "Y = 690 - (z - 1) * 280"
TITLES = """
TITLE_P, TITLE_S = title_sprite("KLARNA", "GUTE NEUIGKEITEN", size=230)
T1_P, T1_S = title_sprite("BESTELLEN", "ALSO JETZT", size=170)
HEADS = [(TITLE_P, TITLE_S, 0.1, 2.9), (T1_P, T1_S, 12.0, 13.38)]
"""
WORDRULES = """    if tok == "Klarna" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-User"):
        words.append(dict(w="Klarna-User,", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "40%,": words.append(dict(w="40 %,", s=w["s"], e=w["e"])); i += 1; continue
"""
REP = '"Büro": "Bio",'
KEY = """KEY = {"neuigkeiten", "klarna", "klarna-user", "usfans", "produktbestellung", "versand", "zahlen", "jetzt", "link", "bio",
       "40 %", "30 %", "shipping", "monaten"}"""
SECTIONS = "SECTIONS = []"
PH_MAP = """PH_MAP = ([13.4, 14.0, 14.46, 14.6, 14.75, 14.9, 15.05, 15.2, 15.95, 16.9, 17.2, 17.55, 17.9],
          [6.0, 6.5, 6.98, 7.22, 7.62, 7.9, 8.2, 8.76, 9.66, 11.3, 11.6, 12.2, 12.55])"""
CARDS = r'''
PINK = (255, 179, 199)
def klarna_badge(d, cx, cy, s=1.0, a=255):
    if s < 0.08: return
    f = T.font("interb", max(4, int(46 * s))); tw = f.getlength("Klarna."); h = 46 * s * 1.6
    d.rounded_rectangle([cx - tw / 2 - 26 * s, cy - h / 2, cx + tw / 2 + 26 * s, cy + h / 2], int(18 * s), fill=PINK + (a,))
    d.text((cx, cy + 2 * s), "Klarna.", font=f, fill=(10, 10, 12, a), anchor="mm")
def partner_card(ts):
    w, h = 860, 330; im, d = card_base(w, h)
    d.text((w / 2, 46), "JETZT VERFÜGBAR", font=T.font("unb", 30), fill=GREEN + (255,), anchor="mm")
    k1 = back((ts - 3.6) / 0.4, 1.6); k2 = back((ts - 5.14) / 0.45, 1.8)
    if k1 > 0:
        lw = int(300 * clamp(k1, 0, 1.1)); lh = int(LOGO.height * lw / LOGO.width)
        if lw > 10:
            bg = Image.new("RGBA", (lw + 40, lh + 40), (0, 0, 0, 0)); ImageDraw.Draw(bg).rounded_rectangle([0, 0, lw + 39, lh + 39], (lh + 40) // 2, fill=(250, 250, 250, 255))
            bg.paste(LOGO.resize((lw, lh), Image.LANCZOS), (20, 20)); im.alpha_composite(bg, (int(220 - bg.width / 2), int(180 - bg.height / 2)))
    if ts > 4.9: d.text((w / 2, 180), "×", font=T.font("interb", 64), fill=(255, 255, 255, int(255 * eo((ts - 4.9) / 0.2))), anchor="mm")
    if k2 > 0: klarna_badge(d, 650, 180, 1.2 * clamp(k2, 0, 1.15))
    if ts > 5.5:
        k = eo((ts - 5.5) / 0.3); d.text((w / 2, 285), "SEIT EINIGEN MONATEN", font=T.font("interx", 28), fill=(255, 255, 255, int(200 * k)), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def checkout_card(ts):
    w, h = 820, 430; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, fill=(250, 250, 250, 245))
    d.text((40, 50), "Bezahlen", font=T.font("interb", 40), fill=NAVY + (255,), anchor="lm")
    lw = 200; lh = int(LOGO.height * lw / LOGO.width); im.paste(LOGO.resize((lw, lh), Image.LANCZOS), (w - lw - 40, 50 - lh // 2))
    for j, (lab, t0) in enumerate((("Produktbestellung", 9.28), ("Versand", 10.52))):
        y = 130 + j * 100; on = eo((ts - t0) / 0.3)
        d.rounded_rectangle([40, y - 38, w - 40, y + 38], 22, fill=(236, 236, 240, 255), outline=(PINK if on > 0.5 else (220, 220, 226)) + (255,), width=4)
        d.text((70, y), lab, font=T.font("interx", 34), fill=NAVY + (255,), anchor="lm")
        if on > 0:
            klarna_badge(d, w - 190, y, 0.62 * clamp(back((ts - t0) / 0.35, 1.8), 0, 1.15))
            d.ellipse([w - 95, y - 20, w - 55, y + 20], fill=GREEN + (int(255 * on),)); d.text((w - 75, y + 1), "✓", font=T.font("interb", 28), fill=(10, 30, 10, int(255 * on)), anchor="mm")
    bx0, by0, bx1, by1 = 40, 330, w - 40, 400; press = np.sin(np.pi * clamp((ts - 11.02) / 0.25)) if ts > 11.02 else 0
    d.rounded_rectangle([bx0 + 6 * press, by0 + 4 * press, bx1 - 6 * press, by1 - 4 * press], 35, fill=(10, 10, 12, 255))
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "Mit Klarna zahlen", font=T.font("interb", 34), fill=PINK + (255,), anchor="mm")
    if 11.02 < ts < 11.6: tap(d, (bx0 + bx1) / 2, (by0 + by1) / 2, clamp((ts - 11.02) / 0.45), dark=False)
    return T.shadow(pil2np(im), 26, 0, 20, 0.5)
CARDS = [(partner_card, 3.45, 6.98, 390), (checkout_card, 8.1, 11.9, 400)]
'''
OPENING = """    if 18.6 <= ts <= 19.45:
        k = back((ts - 18.6) / 0.4, 1.8); a = win(ts, 18.6, 19.45, 0.12, 0.2)
        comp = over(comp, place(LOGO_P, 540, 380, 0.5 + 0.4 * clamp(k, 0, 1.2), a, rx=(1 - clamp(k)) * 30))
    return comp
"""
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True); place(impact(), 0.35, -13); place(chime(), 0.9, -26)
place(whoosh(0.35, 0.55, 800, 6000), 3.45, -27, 0.19); place(pop(560), 3.6, -19); place(pop(760), 5.14, -17); place(impact(1.0, 55), 5.14, -18)
place(whoosh(0.35, 0.55, 800, 6000), 8.1, -27, 0.19); place(tick(2600), 9.28, -23); place(tick(2900), 10.52, -23); place(tick(3000), 11.02, -21); place(chime(), 11.15, -26)
place(whoosh(0.5, 0.7), 12.42, -24, 0.35); place(impact(1.0, 50), 12.44, -16)
place(whoosh(0.45, 0.5, 500, 5000), 13.4, -22, 0.2); place(tick(2700), 14.0, -26); place(tick(3000), 14.46, -22)
place(whoosh(0.35, 0.55, 800, 6000), 14.6, -27, 0.19); place(tick(3000), 14.9, -22); place(whoosh(0.35, 0.55, 800, 6000), 15.05, -27, 0.19)
place(pop(620), 15.2, -17); place(pop(780), 15.95, -17); place(tick(3000), 17.2, -22)
place(whoosh(0.4, 0.5, 600, 5000), 17.55, -25, 0.2); place(impact(1.0, 55), 18.6, -17); place(chime(), 18.65, -26)
"""
