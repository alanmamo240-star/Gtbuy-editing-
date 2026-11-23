"""Replace spoken words in a finished mix with the creator's own recorded 'USFans' takes.
usage: python splice_words.py in.wav out.wav s:e:take.wav [s:e:take.wav ...] [mute=s:e ...]
 - window s..e is muted (25 ms fades); the take is time-fitted (atempo, pitch kept) to the window and level-matched
   to the voice that was there; 'mute=' windows are only muted (with a soft swoosh), e.g. PayPal."""
import sys, subprocess, numpy as np, wave
SR = 48000
src, dst = sys.argv[1], sys.argv[2]
rep = [a for a in sys.argv[3:] if not a.startswith("mute=")]
mut = [tuple(map(float, a[5:].split(":"))) for a in sys.argv[3:] if a.startswith("mute=")]
def load(p, ch=2, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", p] + (["-af", af] if af else []) + ["-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()
x = load(src); g = np.ones(len(x), np.float32); fd = int(0.025 * SR); adds = []
def gate(s, e):
    a, b = int(s * SR), int(e * SR); g[a:b] = 0
    g[max(a - fd, 0):a] = np.minimum(g[max(a - fd, 0):a], np.linspace(1, 0, a - max(a - fd, 0)))
    g[b:b + fd] = np.minimum(g[b:b + fd], np.linspace(0, 1, len(g[b:b + fd])))
for r in rep:
    s, e, take = r.split(":", 2); s, e = float(s), float(e)
    seg = x[int(s * SR):int(e * SR)].mean(1)
    target = np.sqrt((seg ** 2).mean()) * 0.95                      # level of the voice that was there
    tl = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", take], capture_output=True, text=True).stdout)
    fac = max(1.0, tl / ((e - s) * 0.98))
    chain = []
    f = fac
    while f > 2.0: chain.append("atempo=2.0"); f /= 2.0
    chain.append(f"atempo={f:.4f}")
    y = load(take, 1, ",".join(chain))[:, 0]
    y *= target / (np.sqrt((y ** 2).mean()) + 1e-9)
    fe = int(0.006 * SR); y[:fe] *= np.linspace(0, 1, fe); y[-fe:] *= np.linspace(1, 0, fe)
    gate(s, e); adds.append((int(s * SR), y))
    print(f"{s:.2f}-{e:.2f}  {take.split('/')[-1]}  stretch x{fac:.2f}  ->{len(y)/SR:.2f}s")
rng = np.random.default_rng(1)
for s, e in mut:
    gate(s, e)
    n = int(min(max(e - s, 0.2), 0.5) * SR); t = np.linspace(0, 1, n); nz = rng.standard_normal(n); y = np.zeros(n); st = 0.0
    fc = 600 + 4000 * np.sin(np.pi * t)
    for i in range(n):
        al = np.exp(-2 * np.pi * fc[i] / SR); st = (1 - al) * nz[i] + al * st; y[i] = st
    y = (y - np.convolve(y, np.ones(40) / 40, "same")) * np.sin(np.pi * t) ** 1.5
    adds.append((int(s * SR), y / (np.abs(y).max() + 1e-9) * 10 ** (-22 / 20)))
    print(f"{s:.2f}-{e:.2f}  muted")
x *= g[:, None]
for a, y in adds:
    b = min(a + len(y), len(x)); x[a:b] += y[: b - a, None]
x = np.clip(x, -1, 1)
with wave.open(dst, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
