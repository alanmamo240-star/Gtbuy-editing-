"""Turn the creator's old TikTok/Beacons screenshots into USFans versions (his own pages)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
S = "/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad"
FD = f"{S}/v8/work/fonts"
def inter(sz, w=500):
    f = ImageFont.truetype(f"{FD}/Inter.ttf", sz); f.set_variation_by_axes([32, w]); return f
def unb(sz, w=600):
    f = ImageFont.truetype(f"{FD}/Unbounded.ttf", sz); f.set_variation_by_axes([w]); return f
logo = Image.open(f"{S}/uslogo/brand_logo.png").convert("RGBA")

# ---------- TikTok profile ----------
p = Image.open(f"{S}/v8/work/img/shot_profile.png").convert("RGB")
plane = p.crop((578, 846, 636, 900)); ticket = p.crop((946, 846, 1000, 900))
d = ImageDraw.Draw(p)
d.rectangle([40, 842, 1060, 902], fill=(255, 255, 255))
f = inter(39, 450); x = 51; y = 873
t1 = "Best new Agent USFANS "
d.text((x, y), t1, font=f, fill=(22, 24, 35), anchor="lm"); x += f.getlength(t1)
p.paste(plane, (int(x), 846)); x += 62
t2 = " link in bio "
d.text((x, y), t2, font=f, fill=(22, 24, 35), anchor="lm"); x += f.getlength(t2)
p.paste(ticket, (int(x), 846))
# red thumbnail label "KOSTENLOSE HAUL VON GTBUY"
d.rectangle([452, 1152, 729, 1223], fill=(220, 48, 61))
fl = inter(27, 800)
d.text((590, 1170), "KOSTENLOSE HAUL", font=fl, fill=(255, 255, 255), anchor="mm")
d.text((590, 1206), "VON USFANS", font=fl, fill=(255, 255, 255), anchor="mm")
# small caption "Gtbuy Haul part 3." on the lower thumbnail
reg = p.crop((470, 2205, 720, 2275)).filter(ImageFilter.GaussianBlur(14)); p.paste(reg, (470, 2205))
d.text((595, 2240), "USFans Haul part 3.", font=inter(25, 500), fill=(30, 30, 30), anchor="mm")
p.save(f"{S}/shots/shot_profile.png")

# ---------- Beacons ----------
b = Image.open(f"{S}/v8/work/img/shot_beacons.png").convert("RGB")
d = ImageDraw.Draw(b)
d.rectangle([270, 198, 1045, 252], fill=(255, 255, 255))
d.text((652, 224), "@fitsbyjoga | USFans", font=inter(37, 600), fill=(20, 20, 20), anchor="mm")
RED = (117, 20, 20)
d.rectangle([100, 1572, 1078, 2120], fill=RED)
lg = logo.resize((190, 190), Image.LANCZOS); b.paste(lg, (118, 1750), lg)
cx = 650
d.text((cx, 1640), "USFans – Shop", font=unb(46, 500), fill=(255, 255, 255), anchor="mm")
d.text((cx, 1705), "deine Hauls", font=unb(46, 500), fill=(255, 255, 255), anchor="mm")
lines = ["Direkt von Taobao, 1688", "und Weidian über USFans –", "Qualitätscheck, Lager und", "Versand zu dir nach Hause.", "Einfach und sicher."]
for i, ln in enumerate(lines):
    d.text((cx, 1790 + i * 54), ln, font=unb(33, 400), fill=(255, 255, 255), anchor="mm")
b.save(f"{S}/shots/shot_beacons.png")
a = p.resize((590, 1278)); bb = b.resize((590, 1278))
c = Image.new("RGB", (1180, 1278)); c.paste(a, (0, 0)); c.paste(bb, (590, 0)); c.save(f"{S}/shots/preview.png")
