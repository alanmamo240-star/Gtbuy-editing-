"""Soft-mute spoken words (e.g. 'GTBuy', 'PayPal') in a finished mix and lay a short accent swoosh on each gap.
usage: python mute_words.py in.wav out.wav s1:e1 s2:e2 ..."""
import sys, subprocess, numpy as np, wave
src, dst, wins = sys.argv[1], sys.argv[2], [tuple(map(float, a.split(":"))) for a in sys.argv[3:]]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "f32le", "-ac", "2", "-ar", "48000", "-"], capture_output=True, check=True).stdout
x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy(); SR = 48000
g = np.ones(len(x), np.float32); fd = int(0.025 * SR)
rng = np.random.default_rng(1)
for s, e in wins:
    a, b = int(s * SR), int(e * SR)
    g[a:b] = 0.0
    g[max(a - fd, 0):a] = np.minimum(g[max(a - fd, 0):a], np.linspace(1, 0, a - max(a - fd, 0)))
    g[b:b + fd] = np.minimum(g[b:b + fd], np.linspace(0, 1, len(g[b:b + fd])))
x *= g[:, None]
for s, e in wins:  # airy swoosh accent filling the gap
    n = int(min(max(e - s, 0.2), 0.5) * SR); t = np.linspace(0, 1, n)
    nz = rng.standard_normal(n); y = np.zeros(n); al = 0.0; st = 0.0
    fc = 600 + 4000 * np.sin(np.pi * t)
    for i in range(n):
        a_ = np.exp(-2 * np.pi * fc[i] / SR); st = (1 - a_) * nz[i] + a_ * st; y[i] = st
    y = (y - np.convolve(y, np.ones(40) / 40, "same")) * np.sin(np.pi * t) ** 1.5
    y = y / (np.abs(y).max() + 1e-9) * 10 ** (-22 / 20)
    a = int(s * SR); x[a:a + n] += np.stack([y, y], 1)[: len(x) - a]
x = np.clip(x, -1, 1)
with wave.open(dst, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype(np.int16).tobytes())
print("muted", wins)
