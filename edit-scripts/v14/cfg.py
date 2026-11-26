NAME = 'v14 "3 Tipps, die du bei jeder Haul beachten musst"'
SIL = [(2.32, 2.74), (7.46, 7.95), (9.01, 9.66), (13.88, 14.38), (16.73, 17.26), (18.77, 19.25)]
END = 22.05
FREEZE = 1.8
NCH = 6
SHOTS = """
SHOTS = [(0.0, 1.12, None), (2.64, 1.0, None), (3.0, 1.38, 345), (9.56, 1.0, None), (11.62, 1.28, None), (14.28, 1.0, None),
         (15.72, 1.25, None), (17.16, 1.05, None), (19.15, 1.3, None)]
"""
YFORM = "Y = 690 - (z - 1) * 280"
TITLES = """
TITLE_P, TITLE_S = title_sprite("3 TIPPS", "BEI JEDER HAUL", size=220)
T1_P, T1_S = title_sprite("3–10 KG", "NUMMER ZWEI", size=210)
HEADS = [(TITLE_P, TITLE_S, 0.1, 2.4), (T1_P, T1_S, 9.66, 10.85)]
"""
WORDRULES = """    if tok == "US" and i + 2 < len(raw) and raw[i + 2]["w"].startswith("-Account"):
        words.append(dict(w="USFans-Account,", s=w["s"], e=raw[i + 2]["e"])); i += 3; continue
    if tok == "3" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-10kg"):
        words.append(dict(w="3–10 kg", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
"""
REP = '"3kg": "3 kg", "10kg": "10 kg", "erhält": "erhaltet", "meiner": "in meiner",'
KEY = """KEY = {"link", "bio", "usfans-account,", "40 %", "30 %", "shipping", "niemals", "3 kg", "10 kg", "3–10 kg", "spart", "meisten",
       "versandpreise", "günstigsten", "tipps", "haul"}"""
SECTIONS = """SECTIONS = [("01", "USFANS-ACCOUNT", 2.64, 9.12), ("02", "3–10 KG PRO HAUL", 9.56, 22.0)]"""
PH_MAP = """PH_MAP = ([3.0, 3.6, 4.3, 4.55, 4.8, 5.05, 5.35, 6.68, 8.2, 8.45, 8.65, 8.8, 9.1],
          [6.0, 6.5, 6.98, 7.22, 7.62, 7.9, 8.2, 8.76, 9.66, 11.3, 11.6, 12.2, 12.55])"""
CARDS = r'''
def pill(d, cx, cy, txt, k, col=GREEN, fcol=(10, 30, 10), size=32):
    f = T.font("interb", size); tw = f.getlength(txt); kk = clamp(k)
    d.rounded_rectangle([cx - tw / 2 - 26, cy - size * 0.85, cx + tw / 2 + 26, cy + size * 0.85], int(size * 0.85), fill=col + (int(255 * kk),))
    d.text((cx, cy), txt, font=f, fill=fcol + (int(255 * kk),), anchor="mm")
RED = (230, 60, 50)
def kg_card(ts):
    w, h = 860, 440; im, d = card_base(w, h)
    d.text((w / 2, 44), "GEWICHT PRO HAUL", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
    cx, cy, R = w / 2, 360, 230; MX = 15
    for j in range(75):
        a0 = np.pi + np.pi * j / 75; a1 = np.pi + np.pi * (j + 0.8) / 75; kg = MX * j / 75
        col = GREEN if 3 <= kg < 10 else (RED if (kg < 3 and ts > 10.9) or (kg >= 10 and ts > 12.6) else (80, 80, 90))
        d.line([(cx + R * np.cos(a0), cy + R * np.sin(a0)), (cx + R * np.cos(a1), cy + R * np.sin(a1))], fill=col + (255,), width=26)
    for kg in (0, 3, 5, 10, 15):
        a = np.pi + np.pi * kg / MX; d.text((cx + (R - 54) * np.cos(a), cy + (R - 54) * np.sin(a)), str(kg), font=T.font("interx", 28), fill=(255, 255, 255, 200), anchor="mm")
    keys = [(10.5, 0.0), (11.1, 1.6), (12.6, 1.6), (12.9, 12.5), (15.0, 12.5), (15.5, 6.5)]
    v = float(np.interp(ts, [k[0] for k in keys], [k[1] for k in keys])); v += 0.12 * np.sin(ts * 6)
    a = np.pi + np.pi * v / MX; good = 3 <= v < 10
    d.line([(cx, cy), (cx + (R - 30) * np.cos(a), cy + (R - 30) * np.sin(a))], fill=OR + (255,), width=9)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=OR + (255,))
    if 11.1 < ts < 12.6: pill(d, cx, cy - 90, "✗ UNTER 3 KG", back((ts - 11.1) / 0.35, 1.7), RED, (255, 255, 255))
    elif 12.9 < ts < 15.3: pill(d, cx, cy - 90, "✗ ÜBER 10 KG", back((ts - 12.9) / 0.35, 1.7), RED, (255, 255, 255))
    elif ts >= 15.5: pill(d, cx, cy - 90, "✓ 3–10 KG", back((ts - 15.5) / 0.35, 1.7))
    if ts > 17.46: pill(d, 170, 95, "€ AM MEISTEN SPAREN", back((ts - 17.46) / 0.35, 1.7), size=24)
    if ts > 19.68: pill(d, w - 180, 95, "↓ GÜNSTIGSTER VERSAND", back((ts - 19.68) / 0.35, 1.7), size=24)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(kg_card, 10.5, 22.03, 425)]
'''
OPENING = ""
SFX = """
place(whoosh(0.5, 0.4, 600, 6000), 0.0, -20, 0.0, out=True); place(impact(), 0.35, -13)
for t_ in (2.64, 9.56): place(pop(440), t_, -21)
place(whoosh(0.45, 0.5, 500, 5000), 3.0, -22, 0.2); place(tick(2700), 3.6, -26); place(tick(3000), 4.3, -22)
place(whoosh(0.35, 0.55, 800, 6000), 4.55, -27, 0.19); place(tick(3000), 5.05, -22); place(whoosh(0.35, 0.55, 800, 6000), 5.35, -27, 0.19)
place(pop(620), 6.68, -17); place(pop(780), 8.2, -17); place(tick(3000), 8.65, -22)
place(whoosh(0.4, 0.5, 600, 5000), 8.8, -25, 0.2)
place(whoosh(0.5, 0.7), 10.08, -24, 0.35); place(impact(1.0, 50), 10.1, -16)
place(whoosh(0.35, 0.55, 800, 6000), 10.5, -27, 0.19)
place(impact(0.6, 70), 11.1, -21); place(impact(0.6, 70), 12.9, -21); place(chime(), 15.5, -24)
place(coin(), 17.46, -21); place(tick(2600), 19.68, -24)
"""
