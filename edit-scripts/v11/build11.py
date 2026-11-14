s=open("../v7/render7.py").read()
def between(a,b): i=s.index(a); j=s.index(b,i); return i,j
def rep(a,b,cnt=1):
    global s
    assert s.count(a)==cnt,(a[:70],s.count(a)); s=s.replace(a,b)
rep('"""v7 Fit-Check','"""v11 monochrome fit-check, built from v7 by build11.py. Original v7 doc:\nv7 Fit-Check')
rep("DUR = 15.3\nNSRC = 423","DUR = 14.0\nNSRC = 359")
rep("RED = np.array([255, 40, 48], np.float32) / 255","RED = np.array([0.05, 0.05, 0.06], np.float32)   # monochrome: accent is ink black")
i,j=between("BEATS = [","def pulse(t")
s=s[:i]+"BEATS = [0.09, 1.0, 2.0, 3.0, 3.99, 4.99, 5.8, 6.78, 7.78, 8.75, 9.8, 10.75, 11.75]\n"+s[j:]
i,j=between("SC = [","def scene_at(t):")
s=s[:i]+'''SC = [
    (1, 0.00, 1.20, [(0.00, 0.00), (1.20, 1.18)], (0, 35)),
    (2, 1.20, 2.57, [(1.20, 1.21), (1.55, 1.38), (2.57, 2.40)], (36, 76)),       # short 0.5x ramp, tail trimmed
    (3, 2.57, 4.40, [(2.57, 2.58), (4.40, 4.38)], (77, 131)),
    (4, 4.40, 6.03, [(4.40, 4.41), (6.03, 6.01)], (132, 180)),
    (5, 6.03, 7.93, [(6.03, 6.04), (7.93, 7.91)], (181, 237)),
    (6, 7.93, 9.03, [(7.93, 7.94), (9.03, 9.01)], (238, 270)),
    (7, 9.03, 11.13, [(9.03, 9.04), (11.13, 11.11)], (271, 333)),
    (8, 11.13, 14.00, [(11.13, 11.14), (11.30, 11.31), (14.00, 11.31)], (334, 358)),
]
'''+s[j:]
rep("CL = [0, 61, 103, 136, 210, 256, 301, 358, 383, NSRC]","CL = [0, 36, 77, 132, 181, 238, 271, 334, NSRC]")
i,j=between("# ---- camera","# ---- source frames")
s=s[:i]+open("scene11.py").read()+s[j:]
# monochrome sprites: replace red accents in tag/label/row sprites
rep("(255, 40, 48, 255)","(20, 20, 22, 255)", s.count("(255, 40, 48, 255)"))
i,j=between('S = {}\nFIT_M','def tag_sprite(item, brand, gt):')
s=s[:i]+'S = {}\n'+s[j:]
i,j=between("TAGS2 = [(\"T-SHIRT\"","def label_card():")
s=s[:i]+s[j:]
rep('d.text((pad + 22 + gw / 2, pad + 144), "via GTBuy", font=fg, fill=(20, 20, 22, 255), anchor="mm")','d.text((pad + 22 + gw / 2, pad + 144), "via GTBuy", font=fg, fill=(250, 250, 246, 255), anchor="mm")')
rep('    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 8, fill=(250, 250, 246, 240))','    d.rounded_rectangle([pad, pad, pad + pw, pad + ph], 8, fill=(250, 250, 246, 245))')
i,j=between("# ---- per-scene graphics","# ---- compositing")
s=s[:i]+"ROW_S = [row_sprite(*r) for r in ROWS]\n"+open("graphics11.py").read()+s[j:] if "ROW_S = [row_sprite" not in s[:i] else s[:i]+open("graphics11.py").read()+s[j:]
# studio: white cove, reveal on the 6.03 cut, no red rim, dark ring
rep("    r = ease_out((t - 5.64) / 0.40) * 2400","    r = ease_out((t - 6.03) / 0.40) * 2400")
rep("    bg = np.clip(cover(STUDIO, W, H, z, ox, oy) * 1.05, 0, 1)","    bg = np.clip(cover(STUDIO, W, H, z, ox, oy) * 1.02, 0, 1)")
rep("    comp = comp * (1 - rim[..., None]) + RED * rim[..., None]","    comp = comp * (1 - rim[..., None] * 0.4) + WHITE * rim[..., None] * 0.4")
rep("    return comp + ring[..., None] * WHITE * 0.8, cm2","    return comp * (1 - ring[..., None] * 0.8) + INK * ring[..., None] * 0.8, cm2")
# render_shot timings
rep("    if 3.29 <= t < 3.43: zb = ease_in((t - 3.29) / 0.14)\n    if 3.43 <= t < 3.68: zb = 1 - ease_out((t - 3.43) / 0.25)\n    if 11.93 <= t < 12.15: zb = 1 - ease_out((t - 11.93) / 0.22)",
    "    if 2.43 <= t < 2.57: zb = ease_in((t - 2.43) / 0.14)\n    if 2.57 <= t < 2.82: zb = 1 - ease_out((t - 2.57) / 0.25)\n    if 9.03 <= t < 9.25: zb = 1 - ease_out((t - 9.03) / 0.22)")
rep("    if 1.91 <= t < 2.03: dx = -ease_in((t - 1.91) / 0.12) * W * 0.6\n    if 2.03 <= t < 2.17: dx = (1 - ease_out((t - 2.03) / 0.14)) * W * 0.6",
    "    if 1.08 <= t < 1.20: dx = -ease_in((t - 1.08) / 0.12) * W * 0.6\n    if 1.20 <= t < 1.34: dx = (1 - ease_out((t - 1.20) / 0.14)) * W * 0.6")
rep("    if sc[0] == 4 and t >= 5.64: comp, cm = studio(t, comp, cm, M, f)\n    if sc[0] == 5: comp = duotone(comp, 1.0)",
    "    if sc[0] == 5: comp, cm = studio(t, comp, cm, M, f)\n    if sc[0] == 6: g_ = comp @ np.array([0.3, 0.59, 0.11], np.float32); g_ = np.clip((g_ - 0.06) / 0.8, 0, 1) ** 1.1; comp = np.repeat(g_[..., None], 3, 2)")
rep("    if sc[0] == 7: tickers(t, back)","    if sc[0] == 6: tickers(t, back)")
# main loop effects
rep("    if 4.45 <= t < 4.75:  # RGB split shake on the 4.53 cut\n        comp = rgb_split(comp, clamp(1 - abs(t - 4.55) / 0.2), j)",
    "    if 4.32 <= t < 4.62:  # RGB split shake on the 4.40 cut (kept neutral: luminance split)\n        comp = rgb_split(comp, clamp(1 - abs(t - 4.42) / 0.2), j)")
rep("    if sc[0] == 5:  # beat strobe in the duotone shot\n        p_ = pulse(t, 0.05)\n        if p_ > 0.05 and t > 7.1: comp = comp * (1 - 0.55 * p_) + WHITE * 0.55 * p_\n    if 7.00 <= t < 7.034: comp = 1 - comp           # one inverted frame on the drop cut",
    "    if sc[0] == 6:  # beat strobe in the B/W shot\n        p_ = pulse(t, 0.05)\n        if p_ > 0.05: comp = comp * (1 - 0.55 * p_) + WHITE * 0.55 * p_\n    if 7.93 <= t < 7.966: comp = 1 - comp           # one inverted frame into the B/W shot")
rep("    if t >= 12.85:\n        k = ease_io((t - 12.85) / 0.5)","    if t >= 11.15:\n        k = ease_io((t - 11.15) / 0.5)")
open("render11.py","w").write(s)
print("built")
