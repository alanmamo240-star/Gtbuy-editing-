NAME = 'v13 "3 Tipps für eure nächste Haul"'
SIL = [(1.63, 2.36), (10.54, 11.17), (14.30, 14.87), (22.33, 23.28), (27.33, 28.33), (35.18, 35.59), (37.05, 37.50),
       (38.24, 38.94), (39.78, 40.67), (44.32, 44.82)]
END = 47.0
FREEZE = 1.8
NCH = 9
SHOTS = """
SHOTS = [(0.0, 1.12, None), (2.26, 1.0, None), (2.8, 1.38, 345), (11.07, 1.0, None), (13.28, 1.3, None), (14.77, 1.05, None),
         (17.14, 1.26, None), (19.7, 1.0, None), (23.18, 1.3, None), (25.82, 1.05, None), (28.23, 1.0, None), (30.2, 1.28, None),
         (32.8, 1.05, None), (35.49, 1.32, None), (37.4, 1.0, None), (38.84, 1.2, None), (40.57, 1.0, None), (42.42, 1.3, None),
         (44.72, 1.08, None), (46.34, 1.0, None)]
"""
YFORM = "Y = 690 - (z - 1) * 280"
TITLES = """
TITLE_P, TITLE_S = title_sprite("3 TIPPS", "FÜR EURE NÄCHSTE HAUL", size=220)
T1_P, T1_S = title_sprite("VAKUUM SEALS", "ZWEITENS", size=140)
T2_P, T2_S = title_sprite("WAS IST DAS?", "VAKUUM SEALS –", size=150)
T3_P, T3_S = title_sprite("OHNE KARTON", "SCHUHE", size=150)
T4_P, T4_S = title_sprite("KARTONS RAUS", "DESWEGEN IMMER", size=140)
T5_P, T5_S = title_sprite("IN BIO", "1. LINK", size=200)
HEADS = [(TITLE_P, TITLE_S, 0.1, 1.73), (T1_P, T1_S, 13.42, 14.4), (T2_P, T2_S, 14.77, 16.08), (T3_P, T3_S, 29.6, 31.15),
         (T4_P, T4_S, 35.62, 37.15), (T5_P, T5_S, 40.9, 42.4)]
"""
WORDRULES = """    if tok == "Vakuum" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("Seals"):
        words.append(dict(w="Vakuum-Seals" + raw[i + 1]["w"][5:], s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Bio" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Helty"):
        words.append(dict(w="Bio", s=w["s"], e=w["e"])); words.append(dict(w="erhaltet", s=raw[i + 1]["s"], e=raw[i + 1]["e"])); i += 2; continue
"""
REP = '"Vakuumien,": "vakuumiert", "könntet": "könnt",'
KEY = """KEY = {"account", "account,", "link", "40 %", "30 %", "shipping", "vakuum-seals", "luft", "leichter", "platz", "billiger", "sparen",
       "schuhe", "karton", "schwerer", "schuhkartons", "entfernen", "vakuumiert", "bio", "usfans", "tipps", "haul", "maximal", "neuen"}"""
SECTIONS = """SECTIONS = [("01", "NEUER ACCOUNT", 2.26, 10.62), ("02", "VAKUUM SEALS", 11.07, 27.4), ("03", "SCHUHE OHNE KARTON", 28.23, 39.85)]"""
PH_MAP = """PH_MAP = ([2.8, 3.3, 3.75, 4.0, 4.35, 4.6, 4.95, 6.2, 7.1, 9.3, 9.6, 10.25, 10.6],
          [6.0, 6.5, 6.98, 7.22, 7.62, 7.9, 8.2, 8.76, 9.66, 11.3, 11.6, 12.2, 12.55])"""
CARDS = r'''
def pill(d, cx, cy, txt, k, col=GREEN, fcol=(10, 30, 10), size=32):
    f = T.font("interb", size); tw = f.getlength(txt); kk = clamp(k)
    d.rounded_rectangle([cx - tw / 2 - 26, cy - size * 0.85, cx + tw / 2 + 26, cy + size * 0.85], int(size * 0.85), fill=col + (int(255 * kk),))
    d.text((cx, cy), txt, font=f, fill=fcol + (int(255 * kk),), anchor="mm")
def vacuum_card(ts):
    w, h = 880, 400; im, d = card_base(w, h)
    d.text((w / 2, 44), "VAKUUM SEAL", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    k = eio((ts - 18.34) / 1.0); cx, cy = 300, 215
    bw, bh = 330 - 50 * k, 230 - 140 * k
    d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], int(46 - 22 * k), fill=(190, 205, 225, 150 + int(70 * k)), outline=(255, 255, 255, 230), width=4)
    for j in range(5): d.line([(cx - bw / 2 + 22, cy - bh / 2 + 20 + j * (bh - 40) / 4), (cx + bw / 2 - 22, cy - bh / 2 + 20 + j * (bh - 40) / 4 + 6)], fill=(255, 255, 255, int(60 + 60 * k)), width=2)
    if ts > 17.26:                                                       # air leaves the bag
        for j in range(9):
            q = ((ts - 17.26) * 0.9 + j / 9) % 1.0; ang = -0.9 + 1.8 * (j / 8)
            x = cx + bw / 2 + 30 + 260 * q * np.cos(ang * 0.5); y = cy + 120 * np.sin(ang) * q
            r = 10 + 8 * (1 - q); d.ellipse([x - r, y - r, x + r, y + r], outline=(200, 230, 255, int(220 * (1 - q) * (1 - 0.7 * k))), width=3)
        d.text((cx + bw / 2 + 170, cy - 120), "LUFT RAUS", font=T.font("interx", 30), fill=(200, 230, 255, int(255 * eo((ts - 17.3) / 0.3))), anchor="mm")
    if ts > 20.56: pill(d, 680, 230, "✓ LEICHTER", back((ts - 20.56) / 0.4, 1.7))
    if ts > 21.54: pill(d, 680, 320, "✓ MEHR PLATZ", back((ts - 21.54) / 0.4, 1.7))
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def price_card(ts):
    w, h = 820, 360; im, d = card_base(w, h)
    d.text((40, 52), "SHIPPINGPREIS", font=T.font("grotesk", 30), fill=(255, 255, 255, 170), anchor="lm")
    pts = [(0, .9), (.2, .84), (.38, .7), (.55, .62), (.7, .42), (.85, .3), (1, .12)]
    pr = eio((ts - 23.4) / 1.5); gx0, gx1, gy0, gy1 = 50, w - 60, h - 40, 100
    P = [(gx0 + (gx1 - gx0) * x, gy0 + (gy1 - gy0) * y) for x, y in pts]
    seg = [np.hypot(P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]) for i in range(len(P) - 1)]; L = sum(seg) * pr; dr = [P[0]]
    for i, sl in enumerate(seg):
        if L <= 0: break
        f = min(1, L / sl); dr.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)); L -= sl
    if len(dr) > 1:
        d.polygon(dr + [(dr[-1][0], gy0), (dr[0][0], gy0)], fill=GREEN + (60,)); d.line(dr, fill=GREEN + (255,), width=7, joint="curve")
        ex, ey = dr[-1]; d.ellipse([ex - 11, ey - 11, ex + 11, ey + 11], fill=(255, 255, 255, 255))
    if ts > 24.88: pill(d, w - 190, 55, "↓ BILLIGER", back((ts - 24.88) / 0.35, 1.6), size=30)
    if ts > 26.4: pill(d, w - 230, 150, "€ MAXIMAL SPAREN", back((ts - 26.4) / 0.35, 1.6), size=30)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def shoe_card(ts):
    w, h = 880, 400; im, d = card_base(w, h)
    d.text((w / 2, 44), "SCHUHE BESTELLEN", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    box_icon(d, 230, 210, 1.3, col=(235, 120, 60), edge=(140, 60, 25))
    d.text((230, 345), "SCHUHKARTON", font=T.font("interx", 30), fill=(255, 255, 255, 255), anchor="mm")
    if ts > 31.45:
        k = eo((ts - 31.45) / 0.25); L = 95
        d.line([(230 - L, 210 - L * 0.8), (230 - L + 2 * L * k, 210 - L * 0.8 + 1.6 * L * k)], fill=(255, 70, 60, 255), width=12)
        k2 = eo((ts - 31.62) / 0.25)
        if k2 > 0: d.line([(230 + L, 210 - L * 0.8), (230 + L - 2 * L * k2, 210 - L * 0.8 + 1.6 * L * k2)], fill=(255, 70, 60, 255), width=12)
    if ts > 32.48: pill(d, 640, 170, "− FRISST PLATZ", back((ts - 32.48) / 0.4, 1.7), col=(230, 60, 50), fcol=(255, 255, 255))
    if ts > 34.66: pill(d, 640, 270, "↑ SCHWERER", back((ts - 34.66) / 0.4, 1.7), col=(230, 60, 50), fcol=(255, 255, 255))
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(vacuum_card, 16.1, 22.43, 400), (price_card, 23.18, 27.42, 400), (shoe_card, 31.2, 35.25, 400)]
'''
OPENING = """    for tx, t0, x, rz in ((TIX40, 42.84, 300, -8), (TIX30, 43.66, 780, 7)):
        if t0 <= ts <= 46.3:
            k = back((ts - t0) / 0.45, 1.8); a = win(ts, t0, 46.3, 0.12, 0.25)
            comp = over(comp, place(tx, x, 400 + 5 * np.sin((ts - t0) * 2.4), 0.5 + 0.55 * clamp(k, 0, 1.3), a, rz=rz * clamp(k)))
    if 45.6 <= ts <= 46.3:
        k = back((ts - 45.6) / 0.4, 1.8); a = win(ts, 45.6, 46.3, 0.12, 0.2)
        comp = over(comp, place(LOGO_S, 540, 1380, 0.5 + 0.4 * clamp(k, 0, 1.2), a, rx=(1 - clamp(k)) * 30))
    return comp
"""
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True); place(impact(), 0.35, -13)
for t_ in (2.26, 11.07, 28.23): place(pop(440), t_, -21)
place(whoosh(0.45, 0.5, 500, 5000), 2.8, -22, 0.2); place(tick(2700), 3.3, -26); place(tick(3000), 3.75, -22)
place(whoosh(0.35, 0.55, 800, 6000), 4.0, -27, 0.19); place(tick(3000), 4.6, -22); place(whoosh(0.35, 0.55, 800, 6000), 4.95, -27, 0.19)
place(pop(620), 6.2, -17); place(pop(780), 7.1, -17); place(tick(3000), 9.6, -22); place(chime(), 9.7, -27)
place(whoosh(0.4, 0.5, 600, 5000), 10.25, -25, 0.2)
for t_ in (13.42, 14.77, 29.6, 35.62, 40.9): place(whoosh(0.5, 0.7), t_ + 0.42, -24, 0.35); place(impact(1.0, 50), t_ + 0.44, -16)
place(whoosh(0.35, 0.55, 800, 6000), 16.1, -27, 0.19); place(hiss(), 17.3, -19); place(chime(), 20.6, -26); place(tick(2600), 21.54, -24)
place(whoosh(0.35, 0.55, 800, 6000), 23.18, -27, 0.19); place(tick(2400), 24.88, -24); place(coin(), 26.4, -21)
place(whoosh(0.35, 0.55, 800, 6000), 31.2, -27, 0.19); place(scratch(), 31.47, -21); place(scratch(), 31.64, -24)
place(tick(2300), 32.48, -24); place(impact(0.8, 60), 34.66, -19)
place(pop(620), 42.84, -17); place(pop(780), 43.66, -17); place(impact(1.0, 55), 45.6, -17); place(chime(), 45.65, -26)
"""
