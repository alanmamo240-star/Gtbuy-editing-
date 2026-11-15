"""DER FÜNFTE — four episodes. Original story; POV = Alan, friends = Hame, Shiar, Zizo."""
import math
from show import Ep, PHOTOS, photo_from
from eng import kf, ease, clamp, lerp
import numpy as np, ui

DARK = (0.27, 0.27, 0.35)
def S(set, pos, yaw=0, pitch=0, f=620, amb=DARK, **kw): return dict(set=set, cam=dict(pos=pos, yaw=yaw, pitch=pitch, f=f), amb=amb, **kw)
def flick(t, seed=0.0): return 0.3 if (math.sin(t * 23.0 + seed) + math.sin(t * 61.7 + seed * 2)) > 1.5 else 1.0
def peep(t, t0, actors=(), lamp=None, **kw):
    lv = flick(t) if lamp is None else lamp
    return S("treppe", (0, 1.52, 0.0), 0, -4, f=380, amb=(0.14 + 0.5 * lv, 0.14 + 0.48 * lv, 0.17 + 0.34 * lv), peep=clamp((t - t0) / 0.45), nophone=True, lamp=lv, sway=0.5,
             lights=[dict(w=(0, 1.2, 1.4), rw=1.9, I=0.5 * lv)], actors=list(actors), **kw)
def steps(e, t0, t1, iv=0.72, db=-17):
    t = t0
    while t < t1: e.fx(t, "step", db); t += iv
def fin(e): e.screens.sort(key=lambda x: x[0]); e.msgs.sort(key=lambda m: m["t"]); return e

# ------------------------------------------------------------------------------------------------ EP 1
def ep1():
    e = Ep(1, "Die Klingel", (23, 41))
    for t, w, x in [(-30, "Hame", "Morgen Fußball?"), (-20, "Shiar", "Safe"), (-10, "Hame", "18 Uhr am Käfig")]: e.msg(t, w, x, banner=False)
    e.shot(0, 19.4, lambda t: S("zimmer", (0.25, 1.15, 0.9), kf(t, [(16.4, -6), (17.2, -125)]), kf(t, [(16.4, -8), (17.2, -2)]), amb=(0.25, 0.25, 0.33)))
    e.msg(1.2, "Zizo", "Alan. Egal was gleich passiert: Mach NICHT auf.")
    e.say(3.5, "alan", "Hä?")
    e.scr(4.4, "chat"); e.up(4.6, 15.9)
    e.typd(5.8, 7.4, "Was meinst du?"); e.msg(7.5, "Alan", "Was meinst du?", banner=False)
    e.typ(8.3, 9.9, "Zizo"); e.msg(10.0, "Zizo", "Gleich klingelt es bei dir.", banner=False)
    e.typ(10.9, 12.2, "Zizo"); e.msg(12.3, "Zizo", "Es sieht aus wie ich. Aber ich bin zuhause.", banner=False)
    e.say(13.9, "alan", "Sehr witzig, Zizo.")
    e.scr(16.0, "lock"); e.fx(16.3, "doorbell", -4)
    e.say(18.0, "alan", "Nein …", fx="quiet")
    def B(t):
        return S("flur", (0.0, 1.5, kf(t, [(19.4, 0.7), (23.2, 2.5), (24.8, 2.5), (32.2, 5.15)])), 0, -4, walk=1.0 if (19.6 < t < 23.0 or 25.0 < t < 32.0) else 0.0)
    e.shot(19.4, 33.05, B); steps(e, 19.8, 23.0); steps(e, 25.2, 32.0, 0.8)
    e.fx(19.4, "heart", -11, t1=33.0, b0=66, b1=92); e.fx(23.2, "doorbell", -2)
    e.say(26.0, "zizo", "Alan? Mach auf. Ich bin's, Zizo.", fx="door", key="it1", it=True)
    e.msg(30.2, "Zizo", "Ich bin zuhause. Das bin NICHT ich.")
    e.dip(33.05)
    e.shot(33.05, 46.1, lambda t: peep(t, 33.25, [dict(ch="zizo", pos=(0.0, 1.1), expr="creepy", lean=kf(t, [(41.6, 0), (42.6, 0.1)]))]))
    e.fx(33.2, "flicker", -14, t1=46.0)
    e.say(35.0, "zizo", "Mach auf, Bruder. Mir ist kalt.", fx="peep", key="it2", it=True)
    e.say(39.3, "alan", "Er hat deine Jacke an.", fx="quiet")
    e.say(42.8, "zizo", "Alan?", fx="peep", key="it3", it=True)
    e.dip(46.1)
    def D(t):
        sh = max([clamp(1 - abs(t - tk) / 0.25) * 0.5 for tk in (72.0, 73.3, 74.6)])
        return S("flur", (0.03, 1.5, kf(t, [(72.2, 5.2), (76.0, 4.35)])), 0, -3, handle=kf(t, [(76.4, 0), (78.0, 1), (79.2, 1), (79.5, 0)]), shake=sh)
    e.shot(46.1, 84.5, D); e.scr(46.1, "chat"); e.up(46.6, 51.9)
    e.msg(46.3, "Alan", "Es steht vor meiner Tür. Mit deiner Jacke.", banner=False)
    e.typ(47.6, 49.5, "Zizo"); e.msg(49.6, "Zizo", "Frag es etwas, das nur ich weiß.", banner=False)
    e.scr(52.0, "lock"); e.fx(52.0, "heart", -9, t1=84.0, b0=84, b1=104)
    e.say(52.6, "alan", "Was hab ich dir zum Geburtstag geschenkt?", key="q")
    e.say(58.6, "zizo", "Mach auf, Bruder. Mir ist kalt.", fx="door", key="it2", it=True)
    e.say(62.4, "alan", "Das hast du schon gesagt.")
    e.say(65.0, "zizo", "Alan? Mach auf. Ich bin's, Zizo.", fx="door", key="it1", it=True)
    e.msg(68.8, "Zizo", "Es kann nur wiederholen, was es gehört hat.")
    for tk in (72.0, 73.3, 74.6): e.fx(tk, "knock", -3)
    e.fx(76.4, "creak", -8); e.fx(79.5, "click", -8); e.fx(80.6, "stairs", -12)
    e.say(83.0, "alan", "Weg?", fx="quiet")
    e.dip(84.5)
    e.shot(84.5, 90.1, lambda t: peep(t, 84.7, []))
    e.say(87.4, "alan", "Es ist weg.")
    e.dip(90.1)
    e.shot(90.1, 111.4, lambda t: S("flur", (0.03, 1.5, 4.6), 0, -3))
    e.scr(90.1, "chat"); e.up(90.5, 111.0)
    e.msg(91.0, "Hame", "Jungs??", banner=False); e.msg(92.5, "Hame", "Bei mir klingelt es.", banner=False)
    e.msg(94.1, "Hame", "Shiar steht vor meiner Tür.", banner=False); e.msg(96.1, "Shiar", "Ich bin nicht bei dir, Hame.", banner=False)
    e.say(97.3, "alan", "Hame, mach nicht auf!")
    e.typd(97.6, 99.3, "HAME MACH NICHT AUF"); e.msg(99.4, "Alan", "HAME MACH NICHT AUF", banner=False)
    e.msg(101.0, "Hame", "Zu spät haha", banner=False); e.msg(102.6, "Hame", "Er ist schon drin", banner=False)
    e.typ(104.0, 108.6, "Hame"); e.say(106.0, "alan", "Hame?")
    e.msg(109.6, "Zizo", "Hame??", banner=False); e.scr(111.2, "lock")
    def G(t):
        u = ease((t - 111.6) / 3.6)
        tex = ui.icom_tex(t, "hame", on=clamp((t - 111.5) / 0.3), near=kf(t, [(112.0, 0.15), (118.0, 1.0)]))
        return S("flur", (lerp(0.03, 0.45, u), 1.5, lerp(4.6, 5.55, u)), lerp(0, 25.5, u), lerp(-3, 0, u), f=lerp(620, 1500, u), icom=tex, hide=clamp((t - 111.4) / 0.5), capy=1560,
                 lights=[dict(w=(0.74, 1.5, 6.1), rw=0.5, I=0.55, c=(0.7, 1.0, 0.85))])
    e.shot(111.4, 118.31, G); e.fx(111.5, "static", -12, t1=118.3)
    e.say(113.2, "alan", "Was hab ich dir zum Geburtstag geschenkt?", fx="icom", key="q", it=True)
    e.say(116.6, "alan", "Das ist meine Stimme.", fx="quiet")
    e.fx(118.3, "boom"); e.end(118.3); return fin(e)

# ------------------------------------------------------------------------------------------------ EP 2
def ep2():
    e = Ep(2, "Der Fünfte", (23, 58))
    for t, w, x in [(-9, "Hame", "Er ist schon drin"), (-5, "Zizo", "Hame??")]: e.msg(t, w, x, banner=False)
    def A(t):
        tex = ui.icom_tex(t, "hame", on=1.0 if t < 14.3 else clamp(1 - (t - 14.3) / 0.15), near=kf(t, [(0, 1.0), (6, 0.88), (7, 1.0)]))
        u = ease((t - 14.8) / 1.2)
        return S("flur", (lerp(0.45, 0.03, u), 1.5, lerp(5.55, 4.6, u)), lerp(25.5, 0, u), lerp(0, -3, u), f=lerp(1500, 620, u), icom=tex if t < 14.5 else None, hide=1 - clamp((t - 15.0) / 0.6), capy=1560 if t < 15 else None,
                 lights=[dict(w=(0.74, 1.5, 6.1), rw=0.5, I=0.55 if t < 14.4 else 0.0, c=(0.7, 1.0, 0.85))])
    e.shot(0, 30.0, A); e.fx(0.0, "static", -12, t1=14.3)
    e.say(1.0, "alan", "Was hab ich dir zum Geburtstag geschenkt?", fx="icom", key="q", it=True)
    e.say(4.8, "alan", "Das ist nicht Hame.", fx="quiet")
    e.say(7.0, "zizo", "Mach auf, Bruder. Mir ist kalt.", fx="icom", key="it2", it=True)
    e.msg(10.6, "Zizo", "Geh NICHT an die Sprechanlage!")
    e.say(12.5, "alan", "Ich fass das nicht an.")
    e.fx(14.3, "click", -6); e.scr(14.5, "chat"); e.up(15.6, 29.6)
    e.msg(16.2, "Shiar", "Ich fahr jetzt zu Hame.", banner=False); e.msg(18.0, "Zizo", "Bleib zuhause!!", banner=False)
    e.msg(19.8, "Shiar", "Er ist mein Bruder.", banner=False); e.msg(21.2, "Shiar", "Ich lass ihn nicht allein.", banner=False)
    e.say(22.5, "alan", "Shiar, warte!")
    e.typd(22.8, 24.2, "Shiar warte"); e.msg(24.3, "Alan", "Shiar warte", banner=False)
    e.msg(26.2, "", "Shiar ist offline", banner=False, kind="sys"); e.say(27.5, "alan", "Verdammt.")
    e.scr(29.8, "lock")
    def C(t):
        sl = flick(t, 1.3) if 45.6 < t < 47.0 else 1.0
        acts = [] if t >= 47.0 else [dict(ch="hame", pos=(1.45, 5.2), expr="creepy", pose="wave" if t > 34.6 else "stand", wave=t * 2.2)]
        return S("strasse", (0, 5.4, 0), kf(t, [(30, 6), (40, 12), (52, 13)]), kf(t, [(30, -34), (40, -38), (52, -38)]), f=kf(t, [(30, 900), (40, 1350), (52, 1350)]), amb=(0.34, 0.34, 0.46), slamp=sl, nophone=True,
                 lights=[dict(w=(1.3, 0.1, 4.9), rw=2.5, I=0.32 * sl)], actors=acts)
    e.shot(30.0, 52.0, C); e.fx(30.0, "heart", -12, t1=52.0, b0=70, b1=88)
    e.say(31.6, "alan", "Da unten steht jemand.")
    e.say(36.2, "alan", "Das ist Hames Pulli.")
    e.msg(38.8, "Hame", "Komm runter, Alan. Mir ist kalt.")
    e.say(43.0, "alan", "Es schreibt von Hames Handy.")
    e.fx(45.6, "flicker", -8, t1=47.0); e.say(48.2, "alan", "Wo ist es hin?")
    e.msg(50.2, "Zizo", "Schau in die Gruppeninfo. SOFORT.")
    e.shot(52.0, 84.0, lambda t: S("zimmer", (-0.3, 1.5, 2.6), kf(t, [(80.6, 160), (81.4, 199)]), -6, amb=(0.25, 0.25, 0.33)))
    e.scr(52.0, "chat"); e.up(52.6, 80.3)
    e.msg(54.0, "Zizo", "Wir sind vier.", banner=False); e.msg(55.6, "Zizo", "Warum steht da fünf?", banner=False)
    e.scr(57.6, "members", n=5); e.fx(57.6, "sting", -8)
    e.say(58.8, "alan", "Fünf Mitglieder?"); e.say(61.6, "alan", "Wer ist der Fünfte?")
    e.scr(64.0, "chat", sub="5 Mitglieder", subc=(255, 96, 84)); e.typ(64.4, 66.9, "")
    for t in (67.0, 68.3, 69.3): e.msg(t, "", "Mach auf.", banner=False)
    e.msg(70.2, "", "Mir ist kalt.", banner=False)
    e.say(71.4, "alan", "Hör auf!")
    e.msg(73.4, "Zizo", "Es ist in unserer Gruppe.", banner=False); e.msg(75.4, "Zizo", "Es liest alles mit.", banner=False)
    e.say(77.2, "alan", "Dann weiß es, wo wir sind.")
    e.scr(80.4, "lock"); e.fx(80.6, "doorbell", -3); e.say(82.4, "alan", "Nicht schon wieder.", fx="quiet")
    e.shot(84.0, 88.9, lambda t: S("flur", (0, 1.5, kf(t, [(84.0, 1.6), (87.6, 5.2)])), 0, -4, walk=1.3 if t < 87.5 else 0)); steps(e, 84.2, 87.5, 0.45, -14)
    e.say(85.4, "hame", "Alan! Ich bin's, Hame! Mach auf, bitte!", fx="door", key="h1")
    e.dip(88.9)
    def F(t):
        lv = 1.0 if t < 100.2 else (flick(t, 2.0) if t < 103.0 else 0.06)
        return peep(t, 89.1, [dict(ch="hame", pos=(0.05, 0.95), expr="scared", pose="knock" if t < 91 else "scared", look=(-1, 0) if int(t * 0.8) % 3 == 0 else (0, 0), bob=0.012 * math.sin(t * 5), dark=1.0 if lv > 0.2 else 0.3)], lamp=lv,
                    stair_actors=[dict(ch="shadow", pos=(1.15, 3.85), y=kf(t, [(100.6, -2.2), (104.6, -1.0)]), expr="creepy")] if t > 100.6 else [])
    e.shot(88.9, 104.7, F); e.fx(88.9, "heart", -9, t1=116.4, b0=98, b1=126)
    e.msg(90.6, "Zizo", "Frag ihn was Neues!")
    e.say(92.9, "alan", "Wie heißt deine Schwester?")
    e.say(95.3, "hame", "Lina! Alan, bitte!", fx="peep"); e.say(97.7, "hame", "Es kommt die Treppe hoch!", fx="peep")
    e.say(100.1, "alan", "Er hat geantwortet.", fx="quiet")
    e.fx(100.2, "flicker", -6, t1=103.0); e.fx(103.0, "powerdown", -6)
    for tk in (101.4, 102.7, 104.0): e.fx(tk, "thud", -8)
    e.dip(104.7)
    def G(t):
        return S("flur", (-0.08, 1.46, 5.3), -6, -12, lhand=kf(t, [(105.2, 0), (106.6, 1), (111.0, 1), (111.8, 0.55)]), handle=kf(t, [(106.8, 0), (107.6, 0.35), (110.8, 0.35), (111.6, 0)]), shake=clamp(1 - abs(t - 115.7) / 0.3) * 0.8)
    e.shot(104.7, 116.41, G)
    e.say(105.8, "hame", "Alan!", fx="door")
    e.msg(108.0, "Hame", "Ich liege unter meinem Bett. Es ist noch in meinem Zimmer. MACH NICHT AUF.")
    e.say(111.9, "alan", "Was?"); e.say(113.2, "hame", "Alan, bitte! Es ist gleich da!", fx="door")
    e.fx(115.7, "bang", -2); e.fx(116.4, "boom"); e.end(116.4); return fin(e)

# ------------------------------------------------------------------------------------------------ EP 3
def ep3():
    e = Ep(3, "Zwei", (0, 13))
    e.shot(0, 8.0, lambda t: S("flur", (-0.08, 1.46, 5.3), -6, -12, lhand=kf(t, [(0, 1), (6.6, 1), (7.6, 0)]), handle=kf(t, [(0, 0.35), (6.6, 0.35), (7.2, 0)])))
    e.fx(0, "heart", -9, t1=22.0, b0=120, b1=104)
    e.say(0.9, "hame", "Alan, bitte!", fx="door")
    e.msg(2.6, "Zizo", "Mach ein Foto durch den Spion. Auf Fotos sieht man es.")
    e.say(6.7, "alan", "Ein Foto …")
    e.shot(8.0, 22.0, lambda t: S("flur", (0.0, 1.5, kf(t, [(8.0, 5.3), (10.0, 5.55)])), 0, 0))
    e.scr(8.0, "camera", img="peep_dark", ft=11.2); e.up(8.2, 21.8)
    e.fx(11.2, "shutter"); e.scr(11.5, "photo", img="peep_flash", label="Foto · 00:14")
    e.say(12.8, "alan", "Da ist Hame …"); e.say(15.0, "alan", "… und hinter ihm steht noch einer.")
    e.scr(17.4, "photo", img="peep_zoom", label="Foto · 00:14"); e.fx(17.4, "sting", -8)
    e.say(18.4, "alan", "Derselbe Pulli."); e.say(20.1, "alan", "Der vorne ist echt.")
    e.scr(21.9, "lock")
    def C(t):
        dr = kf(t, [(22.8, 0), (23.5, 1), (24.9, 1), (25.3, 0)])
        acts = [dict(ch="hame", pos=(0.12, kf(t, [(23.3, 6.6), (24.7, 4.75)])), expr="scared", pose="scared", bob=0.02 * abs(math.sin(t * 9)) if t < 24.7 else 0.008 * math.sin(t * 5))] if t > 23.3 else []
        sh = max(clamp(1 - abs(t - 25.3) / 0.25) * 0.6, clamp(1 - abs(t - 27.4) / 0.3), clamp(1 - abs(t - 28.6) / 0.3) * 0.7)
        return S("flur", (0.0, 1.5, kf(t, [(22.0, 5.55), (23.0, 4.0), (26, 3.4)])), 0, -4, door=dr, actors=acts, shake=sh)
    e.shot(22.0, 37.4, C)
    e.fx(22.6, "lock", -6); e.say(23.6, "alan", "Rein! Schnell!"); e.fx(25.3, "slam", -2); e.fx(25.9, "lock", -6)
    e.fx(27.4, "bang", -1); e.fx(28.6, "bang", -3)
    e.say(29.8, "hame", "Alan! Ich bin's, Hame! Mach auf, bitte!", fx="door", key="h1", it=True)
    e.say(33.7, "hame", "Das hab ich gerade gesagt.", fx="quiet"); e.say(35.7, "alan", "Es wiederholt nur.")
    e.shot(37.4, 88.0, lambda t: S("flur", (0.35, 1.0, 4.9), 200, -5, actors=[dict(ch="hame", pos=(-0.45, 3.4), pose="sit", expr="scared" if 69 < t < 84 else "normal", look=(0.6, 0))]))
    e.say(38.4, "hame", "Es stand in meinem Zimmer."); e.say(40.9, "hame", "Es sah aus wie Shiar."); e.say(43.3, "hame", "Ich bin aus dem Fenster.")
    e.say(45.9, "alan", "Aber du hast geschrieben, du liegst unter dem Bett.")
    e.say(50.0, "hame", "Ich hab mein Handy gar nicht mehr."); e.say(53.0, "alan", "Wer schreibt dann?")
    e.scr(55.0, "chat"); e.up(55.6, 87.6)
    e.msg(56.0, "Shiar", "Bin bei Hame. Tür steht offen.", banner=False); e.msg(58.2, "Shiar", "Hame sitzt auf dem Bett. Im Dunkeln.", banner=False)
    e.msg(60.4, "Shiar", "Er sagt nichts.", banner=False)
    e.say(61.5, "alan", "Shiar, raus da!")
    e.typd(61.9, 63.6, "SHIAR RAUS DA"); e.msg(63.7, "Alan", "SHIAR RAUS DA", banner=False)
    e.typd(64.5, 65.9, "Hame ist bei MIR"); e.msg(66.0, "Alan", "Hame ist bei MIR", banner=False)
    e.typ(67.0, 69.4, "Shiar"); e.msg(69.5, "Shiar", "Wer sitzt dann hier?", banner=False)
    e.msg(71.8, "Shiar", "", banner=False, kind="photo", img="bed1")
    e.say(73.6, "hame", "Das ist mein Zimmer.")
    e.msg(76.2, "Shiar", "", banner=False, kind="photo", img="bed2"); e.fx(76.4, "sting", -6)
    e.msg(78.6, "Shiar", "Es steht auf.", banner=False); e.msg(80.8, "", "Shiar ist offline", banner=False, kind="sys")
    e.say(82.2, "hame", "Shiar!"); e.say(84.4, "alan", "Wir müssen zu ihm.")
    e.scr(87.8, "lock")
    def E(t):
        if t < 92.0: return S("flur", (0.2, 1.5, kf(t, [(88.0, 4.6), (91.6, 2.95)])), kf(t, [(88.0, 180), (90.8, 180), (92.0, 270)]), -3, walk=1.0 if t < 91.4 else 0)
        mir = [dict(ch="alan", u=0.45, s=1.25, v=0.62, dark=0.8), dict(ch="hame", u=0.80, s=0.78, v=0.63, dark=0.6)]
        if t < 103.0: return S("flur", (0.25, 1.5, 2.95), 270, -2, f=kf(t, [(92.0, 620), (94.0, 760)]), mirror=mir + [dict(ch="shadow", u=0.13, s=0.5, v=0.66, eyes=True)])
        if t < 107.4: return S("flur", (0.25, 1.5, 2.95), kf(t, [(103.0, 270), (103.5, 180)]), -3, actors=[dict(ch="hame", pos=(-0.25, 1.5), expr="scared")])
        sh = dict(ch="shadow", u=kf(t, [(107.4, 0.27), (113.6, 0.31)]), s=kf(t, [(107.4, 1.1), (113.6, 1.42)]), v=0.68, eyes=True)
        return S("flur", (0.25, 1.5, 2.95), kf(t, [(107.4, 180), (107.9, 270)]), -2, f=kf(t, [(107.9, 760), (113.6, 880)]), mirror=[sh] + mir, plight=flick(t, 3) if t > 109.5 else 1.0)
    e.shot(88.0, 113.61, E); steps(e, 88.2, 91.4, 0.7)
    e.say(93.6, "alan", "Hame, bleib stehen."); e.say(96.0, "alan", "Wie viele sind wir?")
    e.say(98.2, "hame", "Zwei. Wieso?"); e.say(100.4, "alan", "Im Spiegel sind drei.")
    e.fx(102.2, "sting", -5); e.fx(103.0, "whoosh", -10); e.say(104.6, "hame", "Da ist niemand.")
    e.fx(107.4, "whoosh", -12); e.fx(107.4, "heart", -7, t1=113.6, b0=110, b1=134)
    e.say(109.0, "alan", "Es steht hinter mir.", fx="quiet")
    e.fx(113.6, "boom"); e.end(113.6); return fin(e)

# ------------------------------------------------------------------------------------------------ EP 4
def ep4():
    e = Ep(4, "Zählt durch", (0, 24))
    mir0 = [dict(ch="shadow", u=0.31, s=1.42, v=0.68, eyes=True), dict(ch="alan", u=0.45, s=1.25, v=0.62, dark=0.8), dict(ch="hame", u=0.80, s=0.78, v=0.63, dark=0.6)]
    e.shot(0, 2.2, lambda t: S("flur", (0.25, 1.5, 2.95), kf(t, [(1.5, 270), (2.1, 150)]), -2, f=kf(t, [(0, 880), (1.5, 880), (2.1, 620)]), mirror=mir0, plight=flick(t, 3), shake=0.3 if t > 1.5 else 0))
    e.say(0.7, "hame", "Lauf!"); e.fx(1.6, "whoosh", -8)
    e.shot(2.2, 38.0, lambda t: S("zimmer", (0.3, 1.5, 2.5), kf(t, [(2.2, 207), (6.0, 200), (34.8, 200), (35.8, 207)]), -4, amb=(0.25, 0.25, 0.33), shake=clamp(1 - abs(t - 3.0) / 0.3) * 0.6,
            actors=[dict(ch="hame", pos=(-0.5, 1.3), face="back" if t < 5.6 else "front", expr="scared" if t < 12 else "normal")]))
    e.fx(3.0, "slam", -2); e.fx(3.7, "lock", -6); e.say(4.6, "alan", "Abgeschlossen.")
    e.fx(6.4, "ring", -6); e.scr(6.4, "call", t0=8.6); e.up(7.6, 33.9)
    e.say(9.2, "zizo", "Alan! Hört zu.", fx="phone"); e.say(11.2, "zizo", "Ich hab's rausgefunden.", fx="phone")
    e.say(13.6, "zizo", "Es nimmt immer den Platz von dem, der fehlt.", fx="phone")
    e.say(17.8, "alan", "Was heißt das?")
    e.say(19.6, "zizo", "Solange wir nicht alle vier zusammen sind, ist ein Platz frei.", fx="phone")
    e.say(24.8, "hame", "Dann müssen wir zusammen sein.")
    e.say(27.4, "zizo", "Ich bin gleich bei euch. Shiar ist bei mir.", fx="phone")
    e.say(31.2, "hame", "Shiar ist okay?"); e.say(32.8, "zizo", "Er ist einfach gerannt.", fx="phone")
    e.scr(34.3, "lock"); e.fx(35.0, "doorbell", -3); e.say(36.6, "alan", "Das sind sie.")
    e.shot(38.0, 41.5, lambda t: S("flur", (0, 1.5, kf(t, [(38.0, 2.4), (41.0, 5.25)])), 0, -4, walk=1.3 if t < 40.9 else 0)); steps(e, 38.2, 40.9, 0.45, -14); e.dip(41.5)
    e.shot(41.5, 47.0, lambda t: peep(t, 41.7, [dict(ch="zizo", pos=(-0.32, 1.0), blink=1 if 0 < (t % 2.7) < 0.12 else 0, bob=0.01 * math.sin(t * 4)),
                                                dict(ch="shiar", pos=(0.36, 1.2), expr="scared", look=(1, 0) if int(t) % 2 else (0, 0), bob=0.012 * math.sin(t * 5 + 1))], lamp=1.0, flash=clamp(1 - abs(t - 46.5) / 0.2)))
    e.say(42.6, "zizo", "Alan, wir sind's!", fx="peep"); e.say(44.6, "alan", "Erst das Foto."); e.fx(46.5, "shutter")
    e.shot(47.0, 55.0, lambda t: S("flur", (0.0, 1.5, 5.2), 0, -3))
    e.scr(47.0, "photo", img="peep_two", label="Foto · 00:25"); e.up(47.1, 54.6)
    e.say(48.6, "alan", "Nur zwei."); e.say(50.4, "hame", "Sauber."); e.say(52.0, "alan", "Ich mach auf.")
    e.scr(54.8, "lock")
    def D(t):
        acts = []
        if t > 56.0: acts.append(dict(ch="zizo", pos=(-0.3, kf(t, [(56.0, 6.6), (57.6, 4.9)])), bob=0.02 * abs(math.sin(t * 8)) if t < 57.6 else 0))
        if t > 56.8: acts.append(dict(ch="shiar", pos=(0.3, kf(t, [(56.8, 6.7), (58.6, 5.3)])), expr="scared", bob=0.02 * abs(math.sin(t * 8 + 1)) if t < 58.6 else 0))
        return S("flur", (0.0, 1.5, kf(t, [(55.0, 5.2), (56.2, 3.6)])), 0, -4, door=kf(t, [(55.3, 0), (56.0, 1), (59.6, 1), (60.1, 0)]), actors=acts, shake=clamp(1 - abs(t - 60.1) / 0.25) * 0.5)
    e.shot(55.0, 62.0, D); e.fx(55.2, "lock", -6); e.say(57.0, "shiar", "Mach zu! Schnell!"); e.say(59.0, "zizo", "Alle in ein Zimmer."); e.fx(60.1, "slam", -3); e.fx(60.7, "lock", -6)
    def circle(t, sc=False, back=0.0, look=True):
        return [dict(ch="hame", pos=(-0.95 - back * 0.5, 2.3 + back), pose="sit", expr="scared" if sc else "normal", look=(0.6, 0) if look else (0, 0)),
                dict(ch="shiar", pos=(0.0, 3.0 + back), pose="sit", expr="scared" if sc else "normal"),
                dict(ch="zizo", pos=(0.95 + back * 0.5, 2.3 + back), pose="sit", expr="scared" if sc else "normal", look=(-0.6, 0) if look else (0, 0))]
    e.shot(62.0, 82.0, lambda t: S("zimmer", (0.0, 1.0, 0.9), 0, -8, amb=(0.9, 0.86, 0.74), lamp=1, actors=circle(t), plight=0.15))
    e.say(63.0, "zizo", "Vier."); e.say(64.6, "zizo", "Jetzt ist kein Platz mehr frei.")
    e.say(67.8, "shiar", "Und jetzt?"); e.say(69.4, "zizo", "Jetzt warten wir, bis es hell wird.")
    e.scr(72.6, "members", n=4, hot=False); e.up(73.0, 79.8)
    e.say(74.6, "alan", "Vier Mitglieder."); e.say(76.6, "alan", "Es ist weg."); e.say(78.4, "hame", "Endlich.")
    e.scr(80.0, "lock"); e.fx(82.0, "powerdown", -3)
    def I(t):
        sc = t >= 97.8; acts = circle(t, sc, ease((t - 110.4) / 1.2) * 0.3, t < 99)
        L = [dict(w=(a["pos"][0], 0.75, a["pos"][1] - 0.25), rw=0.62, I=0.5, c=(0.8, 0.88, 1.0)) for a in acts]
        return S("zimmer", (0.0, 1.0, 0.9), 0, -8, amb=(0.11, 0.11, 0.16), actors=acts, lights=L)
    e.shot(82.0, 117.41, I)
    e.say(83.4, "shiar", "Was war das?"); e.say(85.0, "zizo", "Der Strom.")
    e.say(87.6, "hame", "Zählt durch.")
    e.say(89.6, "alan", "Eins.", key="eins"); e.say(90.9, "hame", "Zwei."); e.say(92.2, "shiar", "Drei."); e.say(93.5, "zizo", "Vier.")
    e.fx(94.4, "heart", -8, t1=117.4, b0=80, b1=128)
    e.say(97.4, "alan", "Eins.", fx="room", key="eins", it=True)
    e.say(99.6, "zizo", "Alan, warst du das?"); e.say(101.8, "alan", "Nein.")
    e.msg(103.2, "", "Alan hat die Gruppe verlassen.", head="Die 4")
    e.say(106.2, "alan", "Ich hab nichts gemacht!")
    e.msg(108.2, "", "Jetzt ist ein Platz frei.", head="Unbekannt · jetzt")
    e.say(110.8, "shiar", "Alan …"); e.say(112.0, "shiar", "Wer sitzt hinter dir?")
    e.scr(113.0, "camera", img="black"); e.up(113.2, 117.6); e.scr(115.2, "camera", img="selfie"); e.fx(115.2, "sting", -3)
    e.fx(117.4, "boom"); e.end(117.4); return fin(e)

# ------------------------------------------------------------------------------------------------ photos shown on the phone
def _pz(st, **cam): st = dict(st); st["cam"] = dict(st["cam"], **cam); return st
PHOTOS["peep_dark"] = lambda: photo_from(peep(0, -9, [dict(ch="hame", pos=(0.05, 0.95), expr="scared", pose="scared", dark=0.3)], lamp=0.06))
_fl = lambda: dict(peep(0, -9, [dict(ch="hame", pos=(-0.2, 0.95), expr="closed", pose="scared")], lamp=1.0, stair_actors=[dict(ch="hame", pos=(1.15, 3.85), y=-1.0, expr="creepy", dark=0.8)]), amb=(1.0, 1.0, 0.97))
PHOTOS["peep_flash"] = lambda: photo_from(_fl())
PHOTOS["peep_zoom"] = lambda: photo_from(dict(_pz(_fl(), yaw=17.5, pitch=-13.5, f=1500), peep=None))
PHOTOS["peep_two"] = lambda: photo_from(dict(peep(0, -9, [dict(ch="zizo", pos=(-0.32, 1.0), expr="closed"), dict(ch="shiar", pos=(0.36, 1.2), expr="scared")], lamp=1.0), amb=(1.0, 1.0, 0.97)))
PHOTOS["bed1"] = lambda: photo_from(S("zimmer", (-1.0, 1.5, 0.5), 38, -8, amb=(0.2, 0.2, 0.26), lights=[dict(x=560, y=900, r=560, I=0.5)], actors=[dict(ch="hame", pos=(1.3, 2.5), y=0.42, pose="sit", face="back", dark=0.7)]))
PHOTOS["bed2"] = lambda: photo_from(S("zimmer", (-1.0, 1.5, 0.5), 38, -5, f=1000, amb=(0.2, 0.2, 0.26), lights=[dict(x=560, y=900, r=560, I=0.5)], actors=[dict(ch="hame", pos=(1.3, 2.5), y=0.42, pose="sit", expr="creepy", dark=0.7)]))
PHOTOS["black"] = lambda: np.full((1500, 900, 3), 10, np.uint8)
PHOTOS["selfie"] = lambda: photo_from(S("zimmer", (0.0, 1.05, 1.75), 180, 2, f=700, amb=(0.12, 0.12, 0.17), lights=[dict(x=540, y=1000, r=520, I=0.6, c=(0.8, 0.88, 1.0))],
                                       actors=[dict(ch="shadow", pos=(0.22, 0.35), h=2.0, expr="creepy"), dict(ch="alan", pos=(0.0, 0.9), pose="sit", expr="scared")]))

EPS = {1: ep1(), 2: ep2(), 3: ep3(), 4: ep4()}
