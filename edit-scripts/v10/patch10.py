s = open("render10.py").read()
def R(a, b):
    global s
    assert a in s, a[:70]; s = s.replace(a, b)
def RB(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]
R('"""v9 "Winter-Hauls jetzt bestellen" (v7/v8 engine, 720p source upscaled):', '"""v10 "Top 5 Schuhe für eure nächste Haul" brand list (v7-v9 engine):')
RB("SHOTS = [", "SHOT_END =", """SHOTS = [(0.0, 1.05, None), (SEGS[1][0], 1.28, None), (2.85, 1.0, None), (SEGS[2][0], 1.3, None), (SEGS[3][0], 1.05, None),
         (6.15, 1.32, None)]
""")
RB("TITLE_P, TITLE_S = title_sprite(", "def headline(", """TITLE_P, TITLE_S = title_sprite("TOP 5 SCHUHE", "FÜR EURE NÄCHSTE HAUL", size=160)
HEADS = [(TITLE_P, TITLE_S, 0.2, 7.0)]
""")
R('    if tok == "Winterhals":', '''    if tok == "Let's": i += 1; continue
    if tok == "The" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("Gallerist"):
        words.append(dict(w="The Gallerist,", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Golden" and i + 1 < len(raw): words.append(dict(w="Golden Goose", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Winterhals":''')
R('REP = {', 'REP = {"Oncloot,": "On Cloud,", "Timberlands,": "Timberland,", "Zaukoni,": "Saucony,", "Zuguta,": "Zegna,", ')
RB("KEY = {", "def clean(", """KEY = {"on cloud", "timberland", "saucony", "the gallerist", "zegna", "golden goose"}
""")
RB("def holiday_card(", "def cards(", '''BRANDS = [("On Cloud", 0.31), ("Timberland", 1.70), ("Saucony", 2.85), ("The Gallerist", 4.07), ("Zegna", 5.49), ("Golden Goose", 6.2)]
def list_card(ts):
    w, h = 760, 470; im, d = card_base(w, h)
    d.text((w / 2, 42), "MEINE PICKS", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    cur = max([j for j, (_, t0) in enumerate(BRANDS) if ts >= t0] or [-1])
    for j, (name, t0) in enumerate(BRANDS):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.7); y = 82 + j * 63; act = j == cur
        x0 = 30 + (1 - clamp(k)) * 60
        d.rounded_rectangle([x0, y, w - 30, y + 54], 27, fill=(OR if act else (40, 40, 46)) + (int(255 * clamp(k)),))
        d.ellipse([x0 + 16, y + 16, x0 + 38, y + 38], fill=(255, 255, 255, int(255 * clamp(k))) if act else OR + (int(255 * clamp(k)),))
        d.text((x0 + 58, y + 28), name.upper(), font=T.font("interb", 34), fill=(255, 255, 255, int(255 * clamp(k))), anchor="lm")
        if not act: d.text((w - 56, y + 28), "✓", font=T.font("interb", 32), fill=GREEN + (int(255 * clamp(k)),), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(list_card, 0.3, 7.03, 455)]
''')
open("render10.py", "w").write(s); print("patched")
