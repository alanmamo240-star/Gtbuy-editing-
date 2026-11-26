NAME = 'v16 "Was ich nicht aus China bestellen würde"'
SIL = [(2.71, 3.48), (11.23, 11.78), (13.91, 14.88), (23.25, 23.78)]
END = 41.0
FREEZE = 1.8
NCH = 9
ENH = "hqdn3d=1.4:1.1:3:3,cas=0.5,colorbalance=rs=-0.07:rm=-0.06:rh=-0.03:bm=0.01,eq=contrast=1.05:saturation=0.93:gamma=1.04"
SHOTS = """
SHOTS = [(0.0, 1.08, None), (3.38, 1.0, None), (5.94, 1.12, None), (8.58, 1.0, None), (11.68, 1.12, None), (14.78, 1.0, None),
         (17.44, 1.12, None), (21.02, 1.0, None), (23.68, 1.12, None), (26.46, 1.0, None), (29.1, 1.14, None), (31.6, 1.0, None),
         (34.44, 1.1, None), (37.28, 1.0, None)]
"""
YFORM = "Y = 390 - (z - 1) * 150"
TITLES = """
TITLE_P, TITLE_S = title_sprite("NICHT BESTELLEN", "DAS WÜRDE ICH AUS CHINA", size=130)
T1_P, T1_S = title_sprite("PARFÜM", "NUMMER 1", size=200)
T2_P, T2_S = title_sprite("ELEKTRONIK", "NUMMER 2", size=150)
HEADS = [(TITLE_P, TITLE_S, 0.1, 2.75), (T1_P, T1_S, 3.38, 4.7), (T2_P, T2_S, 14.78, 16.3)]
"""
WORDRULES = """    if tok == "500,": words.append(dict(w="500–600 €", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
"""
KEY = """KEY = {"parfüm", "parfüm.", "elektronik", "elektronik.", "originale", "originalelektronik", "europa", "gleich", "fake", "500–600 €",
       "versand", "mehr", "china", "nicht", "deutlich"}"""
SECTIONS = "SECTIONS = []"
CARDS = r'''
RED = (230, 60, 50)
def pill(d, cx, cy, txt, k, col=GREEN, fcol=(10, 30, 10), size=32):
    f = T.font("interb", size); tw = f.getlength(txt); kk = clamp(k)
    d.rounded_rectangle([cx - tw / 2 - 26, cy - size * 0.85, cx + tw / 2 + 26, cy + size * 0.85], int(size * 0.85), fill=col + (int(255 * kk),))
    d.text((cx, cy), txt, font=f, fill=fcol + (int(255 * kk),), anchor="mm")
def bottle(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 70 * s, cy - 60 * s, cx + 70 * s, cy + 90 * s], int(26 * s), fill=(230, 200, 140, 255), outline=(255, 255, 255, 230), width=4)
    d.rectangle([cx - 22 * s, cy - 95 * s, cx + 22 * s, cy - 60 * s], fill=(200, 200, 210, 255))
    d.rounded_rectangle([cx - 34 * s, cy - 130 * s, cx + 34 * s, cy - 95 * s], int(10 * s), fill=(40, 40, 46, 255))
    d.rounded_rectangle([cx - 46 * s, cy - 20 * s, cx + 46 * s, cy + 40 * s], int(8 * s), fill=(255, 255, 255, 200))
def perfume_card(ts):
    w, h = 880, 360; im, d = card_base(w, h)
    bottle(d, 190, 200, 1.0)
    if ts > 5.18:
        k = back((ts - 5.18) / 0.35, 1.8); d.text((190, 205), "?", font=T.font("unb", max(4, int(60 * clamp(k, 0, 1.2)))), fill=RED + (255,), anchor="mm")
        d.text((600, 120), "WAS IST DA DRIN?", font=T.font("interb", 38), fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    if ts > 9.3: pill(d, 600, 205, "⚠ UNBEKANNTER INHALT", back((ts - 9.3) / 0.35, 1.7), (255, 196, 60), (40, 25, 0), 28)
    if ts > 12.34: pill(d, 600, 290, "✗ NICHT BESTELLEN", back((ts - 12.34) / 0.35, 1.8), RED, (255, 255, 255), 34)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def device(d, cx, cy, s=1.0):
    d.rounded_rectangle([cx - 60 * s, cy - 110 * s, cx + 60 * s, cy + 110 * s], int(20 * s), fill=(30, 30, 34, 255), outline=(200, 200, 210, 255), width=4)
    d.rounded_rectangle([cx - 50 * s, cy - 96 * s, cx + 50 * s, cy + 96 * s], int(12 * s), fill=(60, 90, 160, 255))
    d.rounded_rectangle([cx - 20 * s, cy - 104 * s, cx + 20 * s, cy - 98 * s], 3, fill=(0, 0, 0, 255))
def eu_flag(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 51, 153, 255), outline=(255, 255, 255, 230), width=3)
    for j in range(12):
        a = 2 * np.pi * j / 12; x, y = cx + 0.62 * r * np.cos(a), cy + 0.62 * r * np.sin(a); rs = 0.1 * r
        d.polygon([(x + rs * (1 if q % 2 == 0 else 0.42) * np.sin(q * np.pi / 5), y - rs * (1 if q % 2 == 0 else 0.42) * np.cos(q * np.pi / 5)) for q in range(10)], fill=(255, 204, 0, 255))
def elec_card(ts):
    w, h = 880, 360; im, d = card_base(w, h)
    device(d, 170, 190)
    if ts > 17.16: pill(d, 560, 90, "ES GIBT AUCH ORIGINALE", back((ts - 17.16) / 0.35, 1.7), (255, 255, 255), (20, 20, 24), 28)
    if ts > 20.22:
        k = back((ts - 20.22) / 0.4, 1.8); eu_flag(d, 360, 200, int(46 * clamp(k, 0, 1.15)) + 1)
        d.text((610, 200), "IN EUROPA KAUFEN", font=T.font("interb", 36), fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    if ts > 22.34: pill(d, 600, 295, "PREISE ≈ GLEICH", back((ts - 22.34) / 0.35, 1.7), size=30)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def fake_card(ts):
    w, h = 880, 360; im, d = card_base(w, h)
    device(d, 170, 190)
    flip = int((ts - 24.0) * 3) % 2 == 0 if ts < 28.64 else False
    lab = "ORIGINAL?" if flip else "FAKE?"
    d.text((560, 90), "ÜBER DIE APP:", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    d.text((560, 160), lab if ts < 28.64 else "FAKE", font=T.font("unb", 56), fill=((255, 255, 255) if flip else RED) + (255,), anchor="mm")
    if ts > 30.06:
        k = back((ts - 30.06) / 0.4, 1.8); f = T.font("unb", max(4, int(54 * clamp(k, 0, 1.15))))
        d.text((560, 255), "500–600 €", font=f, fill=RED + (255,), anchor="mm")
        if ts > 33.54: d.line([(400, 255), (400 + 320 * eo((ts - 33.54) / 0.3), 255)], fill=(255, 255, 255, 255), width=8)
    if ts > 33.54: pill(d, 560, 320, "FÜR FAKE AUSGEGEBEN", back((ts - 33.54) / 0.35, 1.7), RED, (255, 255, 255), 24)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def ship_card(ts):
    w, h = 880, 360; im, d = card_base(w, h)
    d.text((w / 2, 40), "VERSANDKOSTEN", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    for j, (lab, n, col, t0) in enumerate((("MIT ELEKTRONIK", 3, RED, 35.4), ("OHNE ELEKTRONIK", 1, GREEN, 39.08))):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.7); y = 130 + j * 120
        d.text((50, y), lab, font=T.font("interx", 32), fill=(255, 255, 255, int(255 * clamp(k))), anchor="lm")
        for q in range(n):
            x = 560 + q * 90; r = 34 * clamp(k, 0, 1.15)
            if r > 3: d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,)); d.text((x, y), "€", font=T.font("unb", max(4, int(38 * clamp(k, 0, 1.15)))), fill=(255, 255, 255, 255), anchor="mm")
    if ts > 37.28: pill(d, w / 2, 315, "DEUTLICH MEHR", back((ts - 37.28) / 0.35, 1.7), RED, (255, 255, 255), 30)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(perfume_card, 4.72, 13.92, 1260), (elec_card, 16.42, 23.24, 1260), (fake_card, 23.78, 34.25, 1260), (ship_card, 34.44, 39.9, 1260)]
'''
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True); place(impact(), 0.35, -13)
for t_ in (3.38, 14.78): place(whoosh(0.5, 0.7), t_ + 0.42, -24, 0.35); place(impact(1.0, 50), t_ + 0.44, -16)
place(whoosh(0.35, 0.55, 800, 6000), 4.72, -27, 0.19); place(pop(600), 5.18, -19); place(tick(2400), 9.3, -24); place(impact(0.8, 60), 12.34, -18)
place(whoosh(0.35, 0.55, 800, 6000), 16.42, -27, 0.19); place(tick(2600), 17.16, -24); place(pop(560), 20.22, -19); place(chime(), 22.4, -26)
place(whoosh(0.35, 0.55, 800, 6000), 23.78, -27, 0.19)
for t_ in np.arange(24.0, 28.6, 0.333): place(tick(2000, 0.04), float(t_), -31)
place(impact(0.8, 60), 28.64, -18); place(coin(), 30.06, -20); place(scratch(), 33.54, -21)
place(whoosh(0.35, 0.55, 800, 6000), 34.44, -27, 0.19)
for q in range(3): place(coin(), 35.4 + q * 0.1, -24)
place(impact(0.8, 60), 37.28, -18); place(pop(700), 39.08, -20)
place(whoosh(0.6, 0.4, 300, 5000), DUR_MAIN - 0.05, -18, 0.24, out=True)
"""
CARDS_FRONT = True
