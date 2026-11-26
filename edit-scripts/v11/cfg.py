NAME = 'v11 "Kombinieren im Winter"'
SIL = [(9.18, 9.79), (10.21, 12.79)]          # second cut also drops the stumble "tun sollen oder müsstet"
END = 21.95
FREEZE = 1.8
NCH = 6
SHOTS = """
SHOTS = [(0.0, 1.0, None), (3.68, 1.3, None), (5.5, 1.05, None), (SEGS[1][0], 1.28, None), (SEGS[2][0], 1.0, None),
         (14.56, 1.25, None), (16.96, 1.05, None), (19.42, 1.32, None)]
"""
YFORM = "Y = 690 - (z - 1) * 280"
TITLES = """
TITLE_P, TITLE_S = title_sprite("KOMBINIEREN", "DAS WICHTIGSTE IM WINTER", size=150)
T1_P, T1_S = title_sprite("KLICKEN", "ALSO NOCHMAL: IMMER", size=190)
HEADS = [(TITLE_P, TITLE_S, 0.1, 3.62), (T1_P, T1_S, 12.82, 14.5)]
"""
WORDRULES = """    if tok == "Haul" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Versenden"):
        words.append(dict(w="Haul-Versenden", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
"""
KEY = """KEY = {"kombinieren", "kombinieren.", "klick", "mehr", "zahlen", "shipping", "kombiniert", "platz", "weniger", "winter", "jacken"}"""
SECTIONS = "SECTIONS = []"
CARDS = r'''
def toggle_card(ts):
    w, h = 820, 300; im, d = card_base(w, h)
    d.text((44, 60), "VERSAND-OPTIONEN", font=T.font("grotesk", 28), fill=(255, 255, 255, 160), anchor="lm")
    y = 160; d.rounded_rectangle([40, y - 55, w - 40, y + 55], 28, fill=(40, 40, 46, 255))
    d.text((80, y), "Pakete kombinieren", font=T.font("interx", 40), fill=(255, 255, 255, 255), anchor="lm")
    on = eio((ts - 4.16) / 0.25); sx = w - 200
    d.rounded_rectangle([sx, y - 34, sx + 120, y + 34], 34, fill=tuple(int(80 + (c - 80) * on) for c in GREEN) + (255,))
    kx = sx + 34 + 52 * on; d.ellipse([kx - 28, y - 28, kx + 28, y + 28], fill=(255, 255, 255, 255))
    if 4.16 <= ts <= 4.7: tap(d, kx, y, clamp((ts - 4.16) / 0.45), dark=False)
    if ts > 4.3:
        k = back((ts - 4.3) / 0.35, 1.7); d.text((w / 2, 255), "NUR 1 KLICK", font=T.font("unb", 34), fill=OR + (int(255 * clamp(k)),), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def mini_box(d, cx, cy, s, a=255, tag=None):
    box_icon(d, cx, cy, s)
    if tag: d.rounded_rectangle([cx - 30 * s, cy - 95 * s, cx + 40 * s, cy - 55 * s], int(16 * s), fill=(230, 60, 50, a)); d.text((cx + 5 * s, cy - 75 * s), tag, font=T.font("interb", int(30 * s)), fill=(255, 255, 255, a), anchor="mm")
def cost_card(ts):
    w, h = 860, 360; im, d = card_base(w, h)
    d.text((w / 2, 46), "OHNE KOMBINIEREN", font=T.font("unb", 32), fill=(255, 90, 80, 255), anchor="mm")
    for j in range(3):
        k = back((ts - 5.6 - j * 0.18) / 0.4, 1.7)
        if k > 0: mini_box(d, 170 + j * 260, 200, 0.85 * clamp(k, 0, 1.1), tag="€")
    if ts > 6.04:
        k = back((ts - 6.04) / 0.4, 1.8); f = T.font("interb", 34); txt = "= 3× VERSAND ZAHLEN"; tw = f.getlength(txt)
        d.rounded_rectangle([w / 2 - tw / 2 - 26, 290, w / 2 + tw / 2 + 26, 340], 25, fill=(230, 60, 50, int(255 * clamp(k))))
        d.text((w / 2, 315), txt, font=f, fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def merge_card(ts):
    w, h = 860, 380; im, d = card_base(w, h)
    d.text((w / 2, 46), "EURE JACKEN", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    m = eio((ts - 15.86) / 0.6)
    if m < 1:
        for j, x in enumerate((170, 430, 690)):
            xx = x + (430 - x) * m; jacket(d, xx, 200, 0.55 * (1 - 0.3 * m), int(255 * (1 - m)))
    if m > 0:
        box_icon(d, 410, 210, 0.6 + 0.6 * m)
    lab = "KOMBINIERT ✓" if ts > 16.2 else "3 PAKETE"
    d.text((w / 2, 340), lab, font=T.font("interx", 34), fill=(GREEN if ts > 16.2 else WHITE) + (255,), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def jacket(d, cx, cy, s, a=255):
    col = (70, 110, 200, a); dk = (40, 70, 150, a)
    d.rounded_rectangle([cx - 80 * s, cy - 90 * s, cx + 80 * s, cy + 95 * s], int(40 * s), fill=col, outline=dk, width=4)
    d.rounded_rectangle([cx - 150 * s, cy - 80 * s, cx - 70 * s, cy + 60 * s], int(36 * s), fill=col, outline=dk, width=4)
    d.rounded_rectangle([cx + 70 * s, cy - 80 * s, cx + 150 * s, cy + 60 * s], int(36 * s), fill=col, outline=dk, width=4)
    for j in range(1, 4): d.line([(cx - 78 * s, cy - 90 * s + j * 46 * s), (cx + 78 * s, cy - 90 * s + j * 46 * s)], fill=dk, width=4)
    d.line([(cx, cy - 90 * s), (cx, cy + 95 * s)], fill=(220, 220, 230, a), width=4)
def benefit_card(ts):
    w, h = 820, 330; im, d = card_base(w, h)
    d.text((w / 2, 46), "MIT KOMBINIEREN", font=T.font("unb", 32), fill=GREEN + (255,), anchor="mm")
    for j, (lab, t0) in enumerate((("✓  PLATZ SPAREN", 17.96), ("✓  VIEL WENIGER ZAHLEN", 20.28))):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.7); y = 130 + j * 100
        d.rounded_rectangle([60 + (1 - clamp(k)) * 60, y - 38, w - 60, y + 38], 38, fill=GREEN + (int(255 * clamp(k)),))
        d.text((w / 2, y), lab, font=T.font("interb", 38), fill=(10, 30, 10, int(255 * clamp(k))), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(toggle_card, 3.68, 5.48, 380), (cost_card, 5.5, 10.3, 380), (merge_card, 14.5, 16.92, 380), (benefit_card, 16.96, 21.93, 380)]
'''
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True); place(impact(), 0.35, -13)
place(whoosh(0.35, 0.55, 800, 6000), 3.68, -27, 0.19); place(tick(3000), 4.16, -20); place(chime(), 4.3, -26)
place(whoosh(0.35, 0.55, 800, 6000), 5.5, -27, 0.19)
for j in range(3): place(pop(500 + 90 * j), 5.6 + j * 0.18, -21)
place(impact(1.0, 55), 6.04, -17)
place(whoosh(0.5, 0.7), 13.24, -24, 0.35); place(impact(1.0, 50), 13.26, -16)
place(whoosh(0.35, 0.55, 800, 6000), 14.5, -27, 0.19); place(whoosh(0.5, 0.5, 400, 5000), 15.86, -22, 0.25); place(impact(0.8, 60), 16.45, -19)
place(whoosh(0.35, 0.55, 800, 6000), 16.96, -27, 0.19); place(chime(), 17.96, -25); place(coin(), 20.28, -21)
"""
