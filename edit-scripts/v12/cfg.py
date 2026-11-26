NAME = 'v12 "Top 5 Anzüge" brand list'
SIL = [(1.19, 1.65), (5.04, 5.46), (5.74, 6.44)]
END = 7.6
FREEZE = 1.8
NCH = 3
SHOTS = """
SHOTS = [(0.0, 1.05, None), (SEGS[1][0], 1.16, None), (2.98, 1.0, None), (4.3, 1.18, None), (SEGS[2][0], 1.05, None),
         (6.9, 1.16, None)]
"""
YFORM = "Y = 690 - (z - 1) * 280"
TITLES = """
TITLE_P, TITLE_S = title_sprite("TOP 5 ANZÜGE", "FÜR EURE NÄCHSTE HAUL", size=160)
HEADS = [(TITLE_P, TITLE_S, 0.1, 7.55)]
"""
WORDRULES = """    if tok == "Nike" and i + 1 < len(raw) and raw[i + 1]["w"] == "Miller":
        words.append(dict(w="Nike Miler", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "A" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Law"):
        words.append(dict(w="Alo", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Under" and i + 1 < len(raw): words.append(dict(w="Under Armour", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Encloth": words.append(dict(w="On Cloud", s=7.0, e=7.4)); i += 1; continue
"""
REP = '"Lululeven": "Lululemon",'
KEY = """KEY = {"lululemon", "under armour", "nike miler", "alo", "on cloud"}"""
SECTIONS = "SECTIONS = []"
CARDS = r'''
BRANDS = [("Lululemon", 0.05), ("Under Armour", 1.64), ("Nike Miler", 2.98), ("Alo", 4.3), ("On Cloud", 7.03)]
def list_card(ts):
    w, h = 720, 370; im, d = card_base(w, h)
    d.text((w / 2, 42), "TRAININGSANZÜGE", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    cur = max([j for j, (_, t0) in enumerate(BRANDS) if ts >= t0] or [-1])
    for j, (name, t0) in enumerate(BRANDS):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.7); y = 76 + j * 56; act = j == cur
        x0 = 30 + (1 - clamp(k)) * 60
        d.rounded_rectangle([x0, y, w - 30, y + 48], 24, fill=(OR if act else (40, 40, 46)) + (int(255 * clamp(k)),))
        d.ellipse([x0 + 15, y + 13, x0 + 35, y + 33], fill=(255, 255, 255, int(255 * clamp(k))) if act else OR + (int(255 * clamp(k)),))
        d.text((x0 + 52, y + 25), name.upper(), font=T.font("interb", 31), fill=(255, 255, 255, int(255 * clamp(k))), anchor="lm")
        if not act: d.text((w - 56, y + 25), "✓", font=T.font("interb", 32), fill=GREEN + (int(255 * clamp(k)),), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(list_card, 0.05, 7.58, 250)]
'''
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -21, 0.0, out=True); place(impact(), 0.4, -14)
for k, t_ in enumerate((0.05, 1.64, 2.98, 4.3)): place(pop(480 + 70 * k), t_, -17); place(tick(2400 + 150 * k), t_ + 0.02, -27)
place(riser(0.8), 7.03, -24, 0.8); place(impact(1.0, 55), 7.03, -15); place(pop(800), 7.03, -17)
"""
