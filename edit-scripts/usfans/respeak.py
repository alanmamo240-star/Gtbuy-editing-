"""Smoother word replacement: splice the creator's recorded take into the VOICE stem (music/SFX keep running),
match timbre (long-term spectrum), pitch (pYIN median F0) and level to the surrounding voice, time-fit with
rubberband (formant-preserving), equal-power crossfades, then rebuild the mix with the original ducking graph.
usage: python respeak.py vN"""
import sys, os, subprocess, json, numpy as np, librosa
S = "/tmp/claude-0/-home-user-Gtbuy-editing-/f9b90bf7-6ab1-5b45-a5b2-686521ff918d/scratchpad"
SR = 48000
US = os.environ.get("TAKE_US", f"{S}/usvoice/take6.wav"); KA = f"{S}/klarna/take3.wav"; KB = f"{S}/klarna/take4.wav"
CH = "highpass=f=80,afftdn=nr=10:nf=-45:tn=1,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3400:t=q:w=1.0:g=2.5,equalizer=f=9000:t=h:w=0.7:g=1,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=9"
CH13 = "volume=enable='gte(t,8.0)':volume=0,highpass=f=90,afftdn=nr=12:nf=-42:tn=1,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3400:t=q:w=1.0:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=150:makeup=3,loudnorm=I=-13:TP=-1.5:LRA=9"
TAKE_FX = "highpass=f=80,equalizer=f=250:t=q:w=1.2:g=-1.5,equalizer=f=3400:t=q:w=1.0:g=2.5,equalizer=f=9000:t=h:w=0.7:g=1,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=2"
CFG = {
 "v4":  dict(sfx="sfx.wav", dur=36.2217, fade=35.98, fd=0.24, W=[(9.74, 10.17, US)]),
 "v8":  dict(sfx="sfx8.wav", dur=36.4, fade=36.0, fd=0.4, W=[(1.48, 1.88, US), (5.15, 5.55, US), (15.55, 16.14, US), (17.32, 17.92, KA)]),
 "v9":  dict(sfx="sfx9.wav", dur=25.9, fade=25.5, fd=0.4, W=[(1.80, 2.20, KA), (3.24, 3.70, US), (6.10, 6.62, KB), (11.66, 12.02, KA)]),
 "v10": dict(sfx="sfx10.wav", dur=38.9, fade=38.5, fd=0.4, W=[(18.47, 19.04, US)]),
 "v12": dict(sfx="sfx12.wav", dur=29.0, fade=28.6, fd=0.4, W=[(7.02, 7.50, US)]),
 "v13": dict(sfx="music.wav", dur=26.8, fade=26.3, fd=0.5, W=[(0.87, 1.62, US)], trim=0.87169),
}
def run(c): subprocess.run(c, check=True)
def load(p, ch=1, af=None):
    c = ["ffmpeg", "-v", "error", "-i", p] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"]
    a = np.frombuffer(subprocess.run(c, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, ch).copy() if ch > 1 else a.copy()
def save(p, x):
    x = x if x.ndim == 2 else x[:, None]
    run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", str(x.shape[1]), "-ar", str(SR), "-i", "-", "-c:a", "pcm_f32le", p]) if False else None
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", str(x.shape[1]), "-ar", str(SR), "-i", "-", "-c:a", "pcm_f32le", p],
                   input=x.astype(np.float32).tobytes(), check=True)
def ltas(x, n=2048):
    S_ = np.abs(librosa.stft(x, n_fft=n, hop_length=512)); e = S_.sum(0)
    S_ = S_[:, e > np.percentile(e, 50)]     # voiced/loud frames only
    return np.sqrt((S_ ** 2).mean(1) + 1e-12)
def f0(x):
    y = librosa.resample(x, orig_sr=SR, target_sr=16000)
    f, v, _ = librosa.pyin(y, fmin=70, fmax=400, sr=16000, frame_length=1024)
    f = f[v] if v.any() else f[~np.isnan(f)]
    return float(np.median(f)) if len(f) else None
def trim(x, db=32):
    hop = SR // 200; e = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
    d = 20 * np.log10(e + 1e-9); on = np.where(d > d.max() - db)[0]
    return x[max(0, (on[0] - 2) * hop):(on[-1] + 3) * hop]

v = sys.argv[1]; C = CFG[v]; wd = f"{S}/{v}/work"
chain = CH13 if v == "v13" else CH
# 1) voice stem exactly as in the original mix graph
voice = load(f"{wd}/input.mov", 1, f"aresample=48000,{chain}")
L = int(C["dur"] * SR); voice = np.pad(voice, (0, max(0, L - len(voice))))[:L]
spec_v = ltas(voice)
out = voice.copy()
for s, e, take in C["W"]:
    a, b = int(s * SR), int(e * SR)
    ctx = voice[max(0, a - 2 * SR):min(L, b + 2 * SR)]
    # 2) take through the same EQ/comp, tight trim
    t = trim(load(take, 1, TAKE_FX))
    # timbre match: smoothed LTAS ratio, clamped +-9 dB
    st = ltas(t); g = spec_v / st
    g = np.exp(np.convolve(np.log(g), np.ones(9) / 9, mode="same")); g = np.clip(g, 10 ** (-9 / 20), 10 ** (9 / 20))
    g = g ** float(os.environ.get('EQAMT', '0.35'))
    T = librosa.stft(t, n_fft=2048, hop_length=512); t = librosa.istft(T * g[:, None], hop_length=512, length=len(t))
    # pitch + time fit with rubberband (formants preserved)
    fv, ft = f0(ctx), f0(t)
    semi = float(np.clip(12 * np.log2(fv / ft), -2.5, 2.5)) if fv and ft else 0.0
    semi *= float(os.environ.get('PAMT', '0.35'))
    target = (e - s) - 0.01
    tempo = max(0.85, len(t) / SR / target)
    tmp_i, tmp_o = f"{wd}/_rs_in.wav", f"{wd}/_rs_out.wav"
    save(tmp_i, t)
    run(["ffmpeg", "-v", "error", "-y", "-i", tmp_i, "-af", f"rubberband=tempo={tempo:.4f}:pitch={2 ** (semi / 12):.4f}:formant=preserved:transients={os.environ.get('TR', 'crisp')}:window=standard", "-ar", str(SR), tmp_o])
    t = load(tmp_o, 1)
    n = min(len(t), b - a)
    t = t[:n]
    # level: match RMS of the original word (loud part)
    seg = voice[a:b]; r0 = np.sqrt(np.mean(seg[np.abs(seg) > 0.02 * np.abs(seg).max()] ** 2)); r1 = np.sqrt(np.mean(t[np.abs(t) > 0.02 * np.abs(t).max()] ** 2))
    t *= r0 / max(r1, 1e-6)
    # equal-power crossfades: original out, take in
    fd = int(0.030 * SR); gate = np.ones(L, np.float32)
    gate[a:b] = 0; gate[a - fd:a] = np.cos(np.linspace(0, np.pi / 2, fd)); gate[b:b + fd] = np.sin(np.linspace(0, np.pi / 2, fd))
    out *= gate
    w = np.ones(n, np.float32); f2 = min(int(0.012 * SR), n // 4)
    w[:f2] = np.sin(np.linspace(0, np.pi / 2, f2)); w[-f2:] = np.cos(np.linspace(0, np.pi / 2, f2))
    off = a + max(0, (b - a - n) // 2)
    out[off:off + n] += t * w
    print(f"f0 ctx {fv} take {ft}"); print(f"{v} {s:.2f}-{e:.2f} {take.split('/')[-1]} tempo x{tempo:.2f} pitch {semi:+.1f} st gain {20*np.log10(r0/max(r1,1e-6)):+.1f} dB")
save(f"{wd}/voice_us.wav", out)
# 3) rebuild the mix with the original ducking graph
if v == "v13":
    g = (f"[0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,asplit=2[v][key];[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,volume=0.8[s];"
         f"[s][key]sidechaincompress=threshold=0.02:ratio=8:attack=5:release=350:makeup=1[sd];"
         f"[v][sd]amix=inputs=2:normalize=0:duration=longest,atrim=0:{C['dur']},alimiter=limit=0.89:level=false,afade=t=out:st={C['fade']}:d={C['fd']},"
         f"atrim=start={C['trim']},asetpts=PTS-STARTPTS,volume=3dB,alimiter=limit=0.89:level=false[out]")
    name = os.environ.get("OUT", "mix2_us.wav")
else:
    g = (f"[0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,asplit=2[v][key];[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[s];"
         f"[s][key]sidechaincompress=threshold=0.04:ratio=3:attack=5:release=280:makeup=1[sd];"
         f"[v][sd]amix=inputs=2:normalize=0:duration=longest,atrim=0:{C['dur']},alimiter=limit=0.89:level=false,afade=t=out:st={C['fade']}:d={C['fd']}[out]")
    name = os.environ.get("OUT", "mix_us2.wav")
run(["ffmpeg", "-v", "error", "-y", "-i", f"{wd}/voice_us.wav", "-i", f"{wd}/{C['sfx']}", "-filter_complex", g, "-map", "[out]", "-c:a", "pcm_s24le", "-ar", "48000", f"{wd}/{name}"])
# sanity: the same graph with the untouched voice must reproduce the original mix
save(f"{wd}/_voice_orig.wav", voice)
run(["ffmpeg", "-v", "error", "-y", "-i", f"{wd}/_voice_orig.wav", "-i", f"{wd}/{C['sfx']}", "-filter_complex", g, "-map", "[out]", "-c:a", "pcm_s24le", "-ar", "48000", f"{wd}/_mix_check.wav"])
ref = load(f"{wd}/{'mix2.wav' if v == 'v13' else 'mix.wav'}"); chk = load(f"{wd}/_mix_check.wav"); n = min(len(ref), len(chk))
print(v, "rebuild check: corr", round(float(np.corrcoef(ref[:n], chk[:n])[0, 1]), 4), "len", len(ref) / SR, len(chk) / SR)
