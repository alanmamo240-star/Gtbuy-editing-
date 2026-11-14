# ---- camera
def cam(sc, t, f):
    sid, o0, o1 = sc[0], sc[1], sc[2]; u = clamp((t - o0) / (o1 - o0)); rot = 0.0; oob = False
    bp = 1 + 0.02 * pulse(t)
    if sid == 1:      # close lean-in (tee), hook
        s = (1.06 + 0.34 * (1 - ease_out(t / 0.5)) + 0.03 * u) * bp
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.52 * H)
    elif sid == 2:    # full front, jacket
        s = 1.12 + 0.06 * ease_io(u)
        if t > 2.43: s *= 1 + 0.45 * ease_in((t - 2.43) / 0.14)
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
    elif sid == 3:    # back close, jacket
        s = 1.05 + 0.06 * ease_io(u)
        if t < 2.92: s *= 1 + 0.42 * (1 - ease_out((t - 2.57) / 0.35))
        n = mid(f, 11, 12); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1] - 100); sp = (W / 2, 0.45 * H)
        if t > 4.27: rot = 14 * ease_in((t - 4.27) / 0.13)
    elif sid == 4:    # back/side full, tee
        s = 1.10 + 0.06 * ease_io(u)
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
        if t < 4.57: rot = -14 * (1 - ease_out((t - 4.40) / 0.17))
    elif sid == 5:    # side, looking at shoes -> white studio
        h = mid(f, 23, 24); c = (h[0], h[1] - 40)
        s = 1.08 + 0.08 * ease_io(u)
        k = ease_io((t - 6.30) / 0.5)
        sx = W / 2 + (min(W - W / (2 * s), max(W / (2 * s), c[0])) - c[0]) * s * (1 - k)
        sp = (sx, 0.52 * H); oob = t > 6.15
    elif sid == 6:    # back walking, B/W strobe
        s = (1.10 + 0.08 * ease_io(u)) * bp
        h = mid(f, 23, 24); c = (h[0], h[1] - 60); sp = (W / 2, 0.53 * H)
    elif sid == 7:    # close lean, jacket
        s = (1.06 + 0.30 * (1 - ease_out((t - 9.03) / 0.3)) + 0.04 * u) * bp
        n = lm(f, 0); c = (W / 2 + (n[0] - W / 2) * 0.5, n[1]); sp = (W / 2, 0.50 * H)
    else:
        s = 1.08 + 0.06 * ease_io(clamp((t - 11.13) / 1.0))
        h = mid(f, 11, 12); c = (W / 2 + (h[0] - W / 2) * 0.5, h[1] + 200); sp = (W / 2, 0.5 * H)
    return s, c, sp, oob, rot
def cam_M(s, c, sp, oob, rot):
    x0 = c[0] - sp[0] / s; y0 = c[1] - sp[1] / s
    if not oob: x0 = clamp(x0, 0, W - W / s); y0 = clamp(y0, 0, H - H / s)
    M = np.float32([[s, 0, -s * x0], [0, s, -s * y0]])
    if abs(rot) > 0.01:
        R = cv2.getRotationMatrix2D((W / 2, H / 2), rot, 1 + abs(rot) / 40)
        M = (np.vstack([R, [0, 0, 1]]) @ np.vstack([M, [0, 0, 1]]))[:2].astype(np.float32)
    return M
def apply(M, p): return np.array([M[0, 0] * p[0] + M[0, 1] * p[1] + M[0, 2], M[1, 0] * p[0] + M[1, 1] * p[1] + M[1, 2]])

