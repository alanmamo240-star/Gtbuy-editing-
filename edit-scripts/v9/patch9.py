s = open("render9.py").read()
def R(a, b):
    global s
    assert a in s, a[:70]; s = s.replace(a, b)
def RB(start, end, new):
    global s
    i = s.index(start); j = s.index(end, i); s = s[:i] + new + s[j:]
R('"""v8 USFans "5 Tipps für günstigen Versand" (built on the v7 engine):', '"""v9 "Winter-Hauls jetzt bestellen" (v7/v8 engine, 720p source upscaled):')
RB("SHOTS = [", "SHOT_END =", """SHOTS = [(0.0, 1.15, None), (1.62, 1.0, None), (5.46, 1.3, None), (SEGS[1][0], 1.05, None), (11.68, 1.32, None),
         (SEGS[2][0], 1.0, None), (16.6, 1.22, None), (18.12, 1.05, None), (SEGS[3][0], 1.3, None)]
""")
RB("TITLE_P, TITLE_S = title_sprite(", "def headline(", """TITLE_P, TITLE_S = title_sprite("WINTER HAUL", "JETZT BESTELLEN", size=170)
T1_P, T1_S = title_sprite("DELAYS", "GANZ VIELE", size=210)
T2_P, T2_S = title_sprite("ZEIT", "SO SPART IHR", size=230)
HEADS = [(TITLE_P, TITLE_S, 0.1, 1.55), (T1_P, T1_S, 11.68, 12.62), (T2_P, T2_S, 18.68, 20.05)]
""")
R('    if tok == "3" and', '    if tok == "Winterhals": words.append(dict(w="Winter-Hauls", s=w["s"], e=w["e"])); i += 1; continue\n    if tok == "3" and')
RB("KEY = {", "def clean(", """KEY = {"winter-hauls", "jetzt", "feiertage", "china", "deutschland", "weihnachtens", "delays", "später", "schnell", "möglich",
       "bestellen", "zeit", "früher", "pakete", "paket"}
""")
RB("SECTIONS = [", "def chips(", "SECTIONS = []\n")
R("    if not (21.4 <= ts <= 27.55): return comp\n", "    if True: return comp\n")
RB("def parcel(", "def cards(", '''def holiday_card(ts):
    w, h = 900, 400; im, d = card_base(w, h)
    d.text((w / 2, 46), "BALD: FEIERTAGE", font=T.font("unb", 34), fill=OR + (255,), anchor="mm")
    for (x, kind, lab, t0) in ((180, "cn", "CHINA", 4.34), (720, "de", "DEUTSCHLAND", 5.08)):
        if ts < t0 - 0.02: continue
        k = back((ts - t0) / 0.4, 1.8); r = int(70 * clamp(k, 0, 1.15))
        if r > 4:
            f, m = flag(d, x, 200, r, kind); im.paste(f, (x - r, 200 - r), m); d.ellipse([x - r, 200 - r, x + r, 200 + r], outline=(255, 255, 255, 230), width=4)
        d.text((x, 315), lab, font=T.font("interx", 30), fill=(255, 255, 255, int(255 * clamp(k))), anchor="mm")
    if ts > 5.7:                                                        # calendar page: Weihnachten
        k = back((ts - 5.7) / 0.45, 1.6); s_ = clamp(k, 0, 1.15); cx, cy = 450, 205
        cw, ch = 190 * s_, 200 * s_
        if cw > 10:
            d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2], int(22 * s_), fill=(250, 250, 250, 255))
            d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy - ch / 2 + 56 * s_], int(22 * s_), fill=(220, 40, 40, 255))
            d.rectangle([cx - cw / 2, cy - ch / 2 + 30 * s_, cx + cw / 2, cy - ch / 2 + 56 * s_], fill=(220, 40, 40, 255))
            d.text((cx, cy - ch / 2 + 28 * s_), "DEZ", font=T.font("interx", int(32 * s_) + 1), fill=(255, 255, 255, 255), anchor="mm")
            d.text((cx, cy + 30 * s_), "24", font=T.font("unb", int(84 * s_) + 1), fill=(30, 30, 34, 255), anchor="mm")
        lk = eo((ts - 7.58) / 0.3)
        d.text((cx, 340), "WEIHNACHTEN", font=T.font("interx", 32), fill=(255, 90, 80, int(255 * lk)), anchor="mm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def delay_card(ts):
    w, h = 900, 360; im, d = card_base(w, h)
    d.text((40, 52), "DEIN PAKET", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="lm")
    blink = 0.5 + 0.5 * np.sin(ts * 9)
    d.rounded_rectangle([w - 300, 28, w - 40, 78], 25, fill=(230, 50, 45, int(160 + 95 * blink)))
    d.text((w - 170, 53), "VERSPÄTET", font=T.font("interb", 30), fill=(255, 255, 255, 255), anchor="mm")
    xs = [120, 340, 560, 780]; y = 170; labs = ["Bestellt", "Warehouse", "Zoll", "Zuhause"]
    d.line([(xs[0], y), (xs[-1], y)], fill=(255, 255, 255, 60), width=8); d.line([(xs[0], y), (xs[1] + 60, y)], fill=OR + (255,), width=8)
    for j, x in enumerate(xs):
        done = j <= 1; d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(OR if done else (40, 40, 46)) + (255,), outline=(255, 255, 255, 200), width=3)
        d.text((x, y + 55), labs[j], font=T.font("interx", 26), fill=(255, 255, 255, 255 if done else 120), anchor="mm")
    # stalled package with clock
    bx, by = xs[1] + 60, y - 58
    d.rounded_rectangle([bx - 26, by - 22, bx + 26, by + 22], 8, fill=(205, 150, 95, 255), outline=(120, 80, 45, 255), width=3)
    ang = (ts - 12.6) * 4; cx, cy = w - 120, 270
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(255, 255, 255, 230), width=5)
    d.line([(cx, cy), (cx + 26 * np.sin(ang), cy - 26 * np.cos(ang))], fill=(255, 90, 80, 255), width=5); d.line([(cx, cy), (cx, cy - 18)], fill=(255, 255, 255, 255), width=5)
    k = eo((ts - 13.18) / 0.3)
    d.text((60, 300), "ANKUNFT:", font=T.font("interx", 30), fill=(255, 255, 255, 200), anchor="lm")
    d.text((230, 300), "SPÄTER", font=T.font("interb", 34), fill=(255, 90, 80, int(255 * k)), anchor="lm")
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
def order_card(ts):
    w, h = 760, 380; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 36, fill=(250, 250, 250, 245))
    lw = 260; lh = int(LOGO.height * lw / LOGO.width); im.paste(LOGO.resize((lw, lh), Image.LANCZOS), (40, 34))
    d.text((w - 40, 34 + lh / 2), "WINTER HAUL", font=T.font("interx", 28), fill=NAVY + (255,), anchor="rm")
    for j, (lab, col) in enumerate((("Jacke", (70, 110, 200)), ("Hoodie", (90, 90, 100)), ("Boots", (150, 100, 60)))):
        x = 40 + j * 230; d.rounded_rectangle([x, 120, x + 210, 220], 20, fill=(236, 236, 240, 255))
        d.rounded_rectangle([x + 18, 138, x + 82, 202], 14, fill=col + (255,)); d.text((x + 100, 170), lab, font=T.font("interx", 28), fill=NAVY + (255,), anchor="lm")
    bx0, by0, bx1, by1 = 40, 250, w - 40, 340; done = ts > 17.7
    press = np.sin(np.pi * clamp((ts - 17.56) / 0.25)) if ts > 17.56 else 0
    d.rounded_rectangle([bx0 + 6 * press, by0 + 4 * press, bx1 - 6 * press, by1 - 4 * press], 45, fill=(GREEN if done else OR) + (255,))
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "✓  BESTELLT" if done else "JETZT BESTELLEN", font=T.font("interb", 38), fill=((10, 30, 10) if done else WHITE) + (255,), anchor="mm")
    if 17.56 < ts < 18.1: tap(d, (bx0 + bx1) / 2, (by0 + by1) / 2, clamp((ts - 17.56) / 0.45))
    if ts > 16.78 and not done:                                          # urgency pulse on "schnell"
        q = ((ts - 16.78) % 0.6) / 0.6; d.rounded_rectangle([bx0 - 8 * q, by0 - 8 * q, bx1 + 8 * q, by1 + 8 * q], 50, outline=OR + (int(200 * (1 - q)),), width=4)
    return T.shadow(pil2np(im), 26, 0, 20, 0.5)
def compare_card(ts):
    w, h = 900, 380; im, d = card_base(w, h)
    d.text((w / 2, 46), "WANN KOMMT DEIN PAKET?", font=T.font("grotesk", 28), fill=(255, 255, 255, 170), anchor="mm")
    rows = [("JETZT BESTELLT", 0.42, GREEN, "✓ FRÜHER DA", 20.9), ("SPÄTER BESTELLT", 0.95, (230, 60, 50), "DELAYS", 21.2)]
    for j, (lab, L, col, tag, t0) in enumerate(rows):
        y = 125 + j * 125; k = eio((ts - t0) / 0.7)
        d.text((40, y), lab, font=T.font("interx", 30), fill=(255, 255, 255, 230), anchor="lm")
        d.rounded_rectangle([40, y + 28, w - 40, y + 72], 22, fill=(40, 40, 46, 255))
        x1 = 40 + (w - 80) * L * k
        if x1 > 60: d.rounded_rectangle([40, y + 28, x1, y + 72], 22, fill=col + (255,))
        if k > 0.98:
            f = T.font("interb", 28); tw = f.getlength(tag)
            hi = j == 0 and ts > 22.1
            tx = min(x1 + 20, w - 50 - tw)
            d.text((tx if j == 0 else x1 - tw - 20, y + 50), tag, font=f, fill=(255, 255, 255, 255) if not hi else (255, 255, 255, 255), anchor="lm")
            if hi:
                q = clamp((ts - 22.1) / 0.5); d.rounded_rectangle([36 - 6 * q, y + 24 - 6 * q, x1 + 4 + 6 * q, y + 76 + 6 * q], 26, outline=GREEN + (int(255 * (1 - q)),), width=4)
    return T.shadow(pil2np(im), 24, 0, 18, 0.45)
CARDS = [(holiday_card, 1.8, 8.47, 480), (delay_card, 12.62, 14.13, 480), (order_card, 14.55, 18.05, 480), (compare_card, 20.85, 22.95, 480)]
''')
RB("def opening(comp, ts, bgk):", "def cta(comp, ts):", "def opening(comp, ts, bgk):\n    return comp\n")
open("render9.py", "w").write(s); print("patched")
