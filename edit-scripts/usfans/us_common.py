# shared USFans rebrand helpers (inserted into each talking-head render script)
def _us_words(words, drop_times):
    out = []
    for w in words:
        if any(abs(w["s"] - d) < 0.06 for d in drop_times): continue   # spoken offer numbers stay in the audio, not on screen
        t = w["w"]
        for a, b in (("GTBuy", "USFans"), ("GTbuy", "USFans"), ("PayPal", "Klarna"), ("Paypal", "Klarna")): t = t.replace(a, b)
        out.append(dict(w=t, s=w["s"], e=w["e"]))
    return out
