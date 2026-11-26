s = open("render8.py").read()
def R(a, b):
    global s
    assert a in s, a[:70]; s = s.replace(a, b)
def RB(start, end, new):  # replace block from start marker up to (not incl.) end marker
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]
R('"""v7 USFans partner edit:', '"""v8 USFans "5 Tipps für günstigen Versand" (built on the v7 engine):')
RB("SHOTS = [", "SHOT_END =", """SHOTS = [(0.0, 1.12, None), (2.06, 1.3, None), (5.92, 1.0, None), (9.3, 1.25, None), (SEGS[1][0], 1.08, None),
         (SEGS[2][0], 1.3, None), (17.88, 1.05, None), (SEGS[3][0], 1.22, None), (21.4, 1.38, 345), (SEGS[5][0], 1.0, None),
         (SEGS[6][0], 1.3, None), (SEGS[7][0], 1.1, None), (SEGS[8][0], 1.0, None)]
""")
R("    Y = 690 - (z - 1) * 280", "    Y = 1000 - (z - 1) * 700")
RB("TITLE_P, TITLE_S = title_sprite(", "def headline(", """TITLE_P, TITLE_S = title_sprite("5 TIPPS", "GÜNSTIGER VERSAND", size=220)
T1_P, T1_S = title_sprite("KARTONS RAUS", "SCHUH", size=150)
T2_P, T2_S = title_sprite("VAKUUMIEREN", "JACKEN", size=150)
T3_P, T3_S = title_sprite("3–5 KG", "MINDESTENS", size=210)
T4_P, T4_S = title_sprite("ACCOUNT", "NEUER", size=180)
T5_P, T5_S = title_sprite("WIEDERHOLEN", "IMMER", size=150)
# (sprite big, sprite small, t0, t_end) -- source time; centred just above the head top so the head covers the lower part
HEADS = [(TITLE_P, TITLE_S, 0.12, 2.0), (T1_P, T1_S, 2.8, 3.95), (T2_P, T2_S, 6.64, 7.75), (T3_P, T3_S, 16.06, 17.4),
         (T4_P, T4_S, 20.96, 22.0), (T5_P, T5_S, 29.86, 31.12)]
""")
R("    for P, S, t0, t1, cy in HEADS:", "    for P, S, t0, t1 in HEADS:")
R("        cy = min(cy, head_y - 10) if t0 > 1 else cy\n", "        cy = head_y - 25\n")
# captions
R('''    if tok == "KC":''', '''    if tok == "3" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-5"):
        words.append(dict(w="3–5 kg", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "Shipping" and i + 1 < len(raw) and raw[i + 1]["w"].startswith("-Coupons"):
        words.append(dict(w="Shipping-Coupons", s=w["s"], e=raw[i + 1]["e"])); i += 2; continue
    if tok == "KC":''')
RB("KEY = {", "def clean(", """KEY = {"usfans", "40 %", "30 %", "shipping", "shipping,", "link", "bio", "schuhkartons", "platz", "jacken", "vakuumieren",
       "vakuumiert", "karton", "shippingpreis", "weniger", "3–5 kg", "haul", "spart", "account", "wiederholen", "shipping-coupons",
       "tipps", "günstigen", "versand", "2", "meisten"}
""")
# sections
RB("SECTIONS = [", "def chips(", """SECTIONS = [("01", "SCHUHKARTONS RAUS", 2.06, 5.75), ("02", "JACKEN VAKUUMIEREN", 5.92, 14.75), ("03", "3–5 KG PRO HAUL", 15.07, 19.9),
            ("04", "NEUER ACCOUNT", 20.33, 27.55), ("05", "WIEDERHOLEN", 27.97, 35.58)]
""")
# phone: remap v8 source time onto the v7 phone timeline
R("def phone_layer(comp, ts):\n    if not (6.0 <= ts <= 12.55): return comp\n", """PH_MAP = ([21.4, 22.0, 22.46, 22.7, 23.0, 23.2, 23.55, 24.48, 25.40, 26.55, 26.85, 27.2, 27.55],
          [6.0, 6.5, 6.98, 7.22, 7.62, 7.9, 8.2, 8.76, 9.66, 11.3, 11.6, 12.2, 12.55])
def phone_layer(comp, ts):
    if not (21.4 <= ts <= 27.55): return comp
    ts = float(np.interp(ts, *PH_MAP))
""")
# cards
RB("# (renderer, t0, t1, centre y)\nCARDS", "def cards(", '''def parcel(d, x0, y0, w, h, fill, t):
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], 18, outline=(255, 255, 255, 220), width=5)
    fh = (h - 16) * fill; d.rounded_rectangle([x0 + 8, y0 + h - 8 - fh, x0 + w - 8, y0 + h - 8], 12, fill=(205, 150, 95, 255))
    d.text((x0 + w / 2, y0 + h - 8 - fh / 2), f"{int(round(fill * 100))}%", font=T.font("interb", 40), fill=(60, 35, 15, 255), anchor="mm")
def shoebox_card(ts):
    w, h = 900, 380; im, d = card_base(w, h)
    d.text((w / 2, 44), "SCHUHKARTONS ENTFERNEN", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
    box_icon(d, 230, 205, 1.3, col=(235, 120, 60), edge=(140, 60, 25))
    d.text((230, 330), "SCHUHKARTON", font=T.font("interx", 30), fill=(255, 255, 255, 255), anchor="mm")
    if ts > 3.44:
        k = eo((ts - 3.44) / 0.25); L = 95
        d.line([(230 - L, 205 - L * 0.8), (230 - L + 2 * L * k, 205 - L * 0.8 + 1.6 * L * k)], fill=(255, 70, 60, 255), width=12)
        k2 = eo((ts - 3.62) / 0.25)
        if k2 > 0: d.line([(230 + L, 205 - L * 0.8), (230 + L - 2 * L * k2, 205 - L * 0.8 + 1.6 * L * k2)], fill=(255, 70, 60, 255), width=12)
    fill = 0.9 - 0.45 * eio((ts - 4.9) / 0.6)
    parcel(d, 560, 95, 220, 210, fill, ts); d.text((670, 330), "PLATZ IM PAKET", font=T.font("interx", 30), fill=(255, 255, 255, 255), anchor="mm")
    if ts > 5.12:
        k = back((ts - 5.12) / 0.35, 1.8); d.rounded_rectangle([790, 120, 790 + 90 * clamp(k), 175], 26, fill=GREEN + (255,))
        if k > 0.8: d.text((835, 148), "+", font=T.font("interb", 44), fill=(10, 30, 10, 255), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def jacket(d, cx, cy, s, a=255):
    col = (70, 110, 200, a); dk = (40, 70, 150, a)
    d.rounded_rectangle([cx - 80 * s, cy - 90 * s, cx + 80 * s, cy + 95 * s], int(40 * s), fill=col, outline=dk, width=4)
    d.rounded_rectangle([cx - 150 * s, cy - 80 * s, cx - 70 * s, cy + 60 * s], int(36 * s), fill=col, outline=dk, width=4)
    d.rounded_rectangle([cx + 70 * s, cy - 80 * s, cx + 150 * s, cy + 60 * s], int(36 * s), fill=col, outline=dk, width=4)
    for j in range(1, 4): d.line([(cx - 78 * s, cy - 90 * s + j * 46 * s), (cx + 78 * s, cy - 90 * s + j * 46 * s)], fill=dk, width=4)
    d.line([(cx, cy - 90 * s), (cx, cy + 95 * s)], fill=(220, 220, 230, a), width=4)
def jacket_card(ts):
    w, h = 900, 400; im, d = card_base(w, h)
    d.text((w / 2, 44), "JACKEN VAKUUMIEREN", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
    k = eio((ts - 9.72) / 0.9); cx, cy = 450, 215
    if k < 1: jacket(d, cx, cy, 1.0 - 0.15 * k, int(255 * (1 - k)))
    if ts > 9.5:
        bw, bh = 420 - 60 * k, 260 - 170 * k; ba = eo((ts - 9.5) / 0.3)
        d.rounded_rectangle([cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], int(40 - 20 * k), fill=(190, 205, 225, int(120 * ba + 100 * k)), outline=(255, 255, 255, int(230 * ba)), width=4)
        if k > 0.5: jacket(d, cx, cy, 0.32 * (bh / 90) if bh < 90 else 0.32, int(200 * (k - 0.5) * 2))
        for sgn in (-1, 1):
            ax = cx + sgn * (bw / 2 + 50 - 18 * np.sin(ts * 8) * (1 - k)); d.line([(ax + sgn * 44, cy), (ax, cy)], fill=OR + (int(255 * ba),), width=7)
            d.polygon([(ax, cy), (ax + sgn * 18, cy - 14), (ax + sgn * 18, cy + 14)], fill=OR + (int(255 * ba),))
    lab = "JACKE" if ts < 9.72 else "VAKUUMIERT"
    d.text((cx, 360), lab, font=T.font("interx", 32), fill=(255, 255, 255, 255), anchor="mm")
    if ts > 10.8:
        q = back((ts - 10.8) / 0.4, 1.7); f = T.font("interx", 30); txt = "✓ MEHR PLATZ IM KARTON"; tw = f.getlength(txt)
        x0 = w - tw - 70; d.rounded_rectangle([x0, 70, x0 + (tw + 40) * clamp(q), 124], 27, fill=GREEN + (255,))
        if q > 0.9: d.text((x0 + 20, 97), txt, font=f, fill=(10, 30, 10, 255), anchor="lm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def price_card(ts):
    w, h = 820, 360; im, d = card_base(w, h)
    d.text((40, 52), "SHIPPINGPREIS", font=T.font("grotesk", 30), fill=(255, 255, 255, 170), anchor="lm")
    pts = [(0, .9), (.2, .84), (.38, .7), (.55, .62), (.7, .42), (.85, .3), (1, .12)]
    pr = eio((ts - 12.9) / 1.3); gx0, gx1, gy0, gy1 = 50, w - 60, h - 40, 100
    P = [(gx0 + (gx1 - gx0) * x, gy0 + (gy1 - gy0) * y) for x, y in pts]
    seg = [np.hypot(P[i + 1][0] - P[i][0], P[i + 1][1] - P[i][1]) for i in range(len(P) - 1)]; L = sum(seg) * pr; dr = [P[0]]
    for i, sl in enumerate(seg):
        if L <= 0: break
        f = min(1, L / sl); dr.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)); L -= sl
    if len(dr) > 1:
        d.polygon(dr + [(dr[-1][0], gy0), (dr[0][0], gy0)], fill=GREEN + (60,)); d.line(dr, fill=GREEN + (255,), width=7, joint="curve")
        ex, ey = dr[-1]; d.ellipse([ex - 11, ey - 11, ex + 11, ey + 11], fill=(255, 255, 255, 255))
    if ts > 14.26:
        k = back((ts - 14.26) / 0.3, 1.6); f = T.font("interb", 38); txt = "↓ WENIGER"; tw = f.getlength(txt)
        d.rounded_rectangle([w - tw - 90, 30, w - 50, 80], 25, fill=GREEN + (int(255 * clamp(k)),))
        d.text((w - tw - 70, 55), txt, font=f, fill=(10, 30, 10, int(255 * clamp(k))), anchor="lm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def kg_card(ts):
    w, h = 820, 420; im, d = card_base(w, h)
    d.text((w / 2, 44), "GEWICHT PRO HAUL", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
    cx, cy, R = w / 2, 330, 220
    for j in range(60):                                                 # gauge 0..8 kg, sweet spot 3-5
        a0 = np.pi + np.pi * j / 60; a1 = np.pi + np.pi * (j + 0.8) / 60; kg = 8 * j / 60
        col = GREEN if 3 <= kg < 5 else (80, 80, 90)
        d.line([(cx + R * np.cos(a0), cy + R * np.sin(a0)), (cx + R * np.cos(a1), cy + R * np.sin(a1))], fill=col + (255,), width=26)
    for kg in range(0, 9, 1):
        a = np.pi + np.pi * kg / 8; d.text((cx + (R - 52) * np.cos(a), cy + (R - 52) * np.sin(a)), str(kg), font=T.font("interx", 26), fill=(255, 255, 255, 180), anchor="mm")
    v = 4.0 * eio((ts - 16.3) / 1.0) + 0.12 * np.sin(ts * 6) * eo((ts - 17.3) / 0.3)
    a = np.pi + np.pi * v / 8; d.line([(cx, cy), (cx + (R - 30) * np.cos(a), cy + (R - 30) * np.sin(a))], fill=OR + (255,), width=9)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=OR + (255,))
    d.text((cx, cy - 75), "3–5 KG", font=T.font("unb", 52), fill=(GREEN if v > 2.9 else WHITE) + (255,), anchor="mm")
    if ts > 18.3:
        k = back((ts - 18.3) / 0.35, 1.8); f = T.font("interx", 30); txt = "€  AM MEISTEN SPAREN"; tw = f.getlength(txt)
        d.rounded_rectangle([w / 2 - tw / 2 - 26, 76, w / 2 + tw / 2 + 26, 126], 25, fill=GREEN + (int(255 * clamp(k)),))
        d.text((w / 2, 101), txt, font=f, fill=(10, 30, 10, int(255 * clamp(k))), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
TIXS = ticket("40%", 220), ticket("30%", 220)
def repeat_card(ts):
    w, h = 900, 430; im, d = card_base(w, h)
    d.text((w / 2, 44), "PRO ACCOUNT  =  2 SHIPPING-COUPONS", font=T.font("grotesk", 27), fill=(255, 255, 255, 160), anchor="mm")
    L = pil2np(im)
    rows = [(31.8, "ACCOUNT 1"), (32.6, "ACCOUNT 2"), (33.4, "ACCOUNT 3")]
    can = Image.fromarray((L * 255).astype(np.uint8)); dd = ImageDraw.Draw(can)
    for j, (t0, lab) in enumerate(rows):
        if ts < t0: continue
        k = eo((ts - t0) / 0.3); y = 105 + j * 105
        dd.rounded_rectangle([40, y, 300, y + 80], 20, fill=(40, 40, 46, int(255 * k)), outline=(255, 255, 255, int(90 * k)), width=2)
        dd.text((170, y + 40), lab, font=T.font("interx", 30), fill=(255, 255, 255, int(255 * k)), anchor="mm")
        for q, tx in enumerate(TIXS):
            kk = back((ts - t0 - 0.12 - q * 0.12) / 0.35, 1.8)
            if kk <= 0: continue
            t = Image.fromarray((np.clip(tx, 0, 1) * 255).astype(np.uint8)); sc = 0.55 * clamp(kk, 0, 1.2)
            t = t.resize((max(1, int(t.width * sc)), max(1, int(t.height * sc))), Image.LANCZOS)
            can.alpha_composite(t, (int(400 + q * 170 + 60 - t.width / 2), int(y + 40 - t.height / 2)))
    ang = (ts - 30.3) * 240                                              # repeat loop icon
    lp = Image.new("RGBA", (150, 150), (0, 0, 0, 0)); ld = ImageDraw.Draw(lp)
    ld.arc([15, 15, 135, 135], 30, 320, fill=OR + (255,), width=14); ld.polygon([(118, 32), (140, 72), (98, 66)], fill=OR + (255,))
    lp = lp.rotate(-ang, resample=Image.BICUBIC); can.alpha_composite(lp, (w - 190, 150))
    if ts > 34.8:
        k = back((ts - 34.8) / 0.35, 1.8); dd.rounded_rectangle([w - 230, 320, w - 40, 370], 25, fill=GREEN + (int(255 * clamp(k)),))
        dd.text((w - 135, 345), "IMMER WIEDER", font=T.font("interx", 24), fill=(10, 30, 10, int(255 * clamp(k))), anchor="mm")
    return T.shadow(pil2np(can), 24, 0, 18, 0.45)
# (renderer, t0, t1, centre y)
CARDS = [(shoebox_card, 3.95, 5.72, 470), (jacket_card, 7.75, 11.93, 470), (price_card, 12.6, 14.75, 470), (kg_card, 17.4, 19.92, 480),
         (repeat_card, 31.15, 35.55, 480)]
''')
# opening / cta
RB("def opening(comp, ts, bgk):", "def cta(comp, ts):", """def opening(comp, ts, bgk):
    if 26.8 <= ts <= 27.55:                                             # "nur bei USFans"
        k = back((ts - 26.8) / 0.4, 1.8); a = win(ts, 26.8, 27.55, 0.12, 0.2)
        comp = over(comp, place(LOGO_S, 790, 1470, 0.5 + 0.4 * clamp(k, 0, 1.2), a, rx=(1 - clamp(k)) * 30))
    return comp
""")
RB("def cta(comp, ts):", "MASCOT =", "def cta(comp, ts):\n    return comp\n")
# freeze: hand covers the lens -> blur the whole frame for the end card
R("""        k = eo(fz / 0.35); g = comp.mean(2, keepdims=True); bg = (comp * (1 - 0.7 * k) + g * 0.7 * k) * (1 - 0.35 * k)
        comp = comp * (1 - bgk) + bg * bgk""", """        k = eo(fz / 0.35); comp = cv2.GaussianBlur(comp, (0, 0), 3 + 30 * k) * (1 - 0.45 * k); bgk = np.ones_like(bgk)""")
R("comp = over(comp, place(LOGO_P, 540, 300,", "comp = over(comp, place(LOGO_P, 540, 560,")
R("comp = over(comp, place(FUN, 540, 470,", "comp = over(comp, place(FUN, 540, 740,")
R("comp = over(comp, place(MASC, 860, 1180 + (1 - clamp(k3)) * 300, 0.72,", "comp = over(comp, place(MASC, 540, 1180 + (1 - clamp(k3)) * 300, 0.85,")
R("    if freeze: extra = 1 + 0.05 * eo(fz / 0.4)", "    if freeze: extra = 1.0")
R("        chips(ts, canvas); choice(ts, canvas); caption(ts, canvas)", "        chips(ts, canvas); caption(ts, canvas)")
open("render8.py", "w").write(s); print("patched")
