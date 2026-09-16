#!/usr/bin/env python3
"""OBSKURA 360 — FX katmanı üretici.
   Yeşil zemin (chroma key) mp4 ve/veya alfa kanallı VP9 webm üretir. 1080x1920 @30fps.
   kullanım: fxgen.py <yildiz|kalp|konfeti|sparkle|all> [--alpha] [--sec 30] [--out DIR]"""
import sys, math, random, subprocess, pathlib
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 1080, 1920, 30
GREEN = (0, 255, 0)

def poly_star(cx, cy, r, n=5, inner=0.45, rot=0.0):
    pts = []
    for i in range(2 * n):
        a = rot + math.pi * i / n - math.pi / 2
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def sprite(kind, size, rot, color, soft):
    """RGBA sprite; size = px (final). 4x çizim + LANCZOS küçültme ile pürüzsüz kenar."""
    S = 4
    pad = int(size * 0.9) + 6
    cw = (size + 2 * pad) * S
    im = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = cw / 2
    r = size * S / 2
    col = color + (255,)
    if kind == "star":
        d.polygon(poly_star(c, c, r, 5, 0.46, rot), fill=col)
    elif kind == "sparkle":
        d.polygon(poly_star(c, c, r, 4, 0.16, rot), fill=col)
        d.ellipse((c - r * 0.14, c - r * 0.14, c + r * 0.14, c + r * 0.14), fill=(255, 255, 255, 255))
    elif kind == "heart":
        # kalp: iki daire + üçgen
        rr = r * 0.52
        d.ellipse((c - r * 0.5 - rr, c - r * 0.35 - rr, c - r * 0.5 + rr, c - r * 0.35 + rr), fill=col)
        d.ellipse((c + r * 0.5 - rr, c - r * 0.35 - rr, c + r * 0.5 + rr, c - r * 0.35 + rr), fill=col)
        d.polygon([(c - r * 1.0, c - r * 0.2), (c + r * 1.0, c - r * 0.2), (c, c + r * 1.0)], fill=col)
        if rot:
            im = im.rotate(math.degrees(rot), resample=Image.BICUBIC)
    elif kind == "confetti":
        w, h = r * 1.0, r * 0.55
        rect = Image.new("RGBA", (cw, cw), (0, 0, 0, 0))
        ImageDraw.Draw(rect).rectangle((c - w, c - h, c + w, c + h), fill=col)
        im = rect.rotate(math.degrees(rot), resample=Image.BICUBIC)
    if soft:
        glow = im.filter(ImageFilter.GaussianBlur(radius=size * S * 0.25))
        ga = glow.split()[3].point(lambda a: int(a * 0.55))
        glow.putalpha(ga)
        im = Image.alpha_composite(glow, im)
    im = im.resize((cw // S, cw // S), Image.LANCZOS)
    if not soft:
        # yeşil perde için kenarı sertleştir (yarı saydam piksel yeşile karışmasın)
        a = im.split()[3].point(lambda v: 255 if v > 110 else 0)
        im.putalpha(a)
    return im

class Bank:
    """(kind,color,size,rot) → sprite önbelleği"""
    def __init__(self, kind, colors, sizes, rots, soft):
        self.kind, self.colors, self.sizes, self.rots, self.soft = kind, colors, sizes, rots, soft
        self.cache = {}
    def get(self, ci, size, rot):
        si = min(range(len(self.sizes)), key=lambda i: abs(self.sizes[i] - size))
        ri = int(round((rot % (2 * math.pi)) / (2 * math.pi) * len(self.rots))) % len(self.rots)
        k = (ci, si, ri)
        if k not in self.cache:
            self.cache[k] = sprite(self.kind, self.sizes[si], self.rots[ri], self.colors[ci], self.soft)
        return self.cache[k]

def rots(n):
    return [2 * math.pi * i / n for i in range(n)]

class P:  # parçacık
    __slots__ = ("x", "y", "vx", "vy", "s", "rot", "rv", "ci", "ph", "life", "age", "sway")

def spawn(kind, rnd, t0=False):
    p = P()
    p.age = 0.0
    p.ph = rnd.random() * 6.283
    if kind == "yildiz":
        p.x = rnd.uniform(-40, W + 40); p.y = rnd.uniform(-60, H) if t0 else rnd.uniform(-120, -30)
        p.vx = rnd.uniform(-25, 25); p.vy = rnd.uniform(260, 520)
        p.s = rnd.choice([18, 26, 36, 48, 64]); p.rot = rnd.random() * 6.283; p.rv = rnd.uniform(-1.2, 1.2)
        p.ci = rnd.choice([0, 0, 1, 2]); p.sway = rnd.uniform(20, 60); p.life = 99
    elif kind == "kalp":
        p.x = rnd.uniform(20, W - 20); p.y = rnd.uniform(0, H) if t0 else rnd.uniform(H + 40, H + 160)
        p.vx = 0; p.vy = -rnd.uniform(150, 320)
        p.s = rnd.choice([30, 40, 52, 68, 88]); p.rot = rnd.uniform(-0.35, 0.35); p.rv = rnd.uniform(-0.4, 0.4)
        p.ci = rnd.choice([0, 1, 1, 2, 3]); p.sway = rnd.uniform(25, 70); p.life = 99
    elif kind == "konfeti":
        p.x = rnd.uniform(-20, W + 20); p.y = rnd.uniform(-60, H) if t0 else rnd.uniform(-100, -20)
        p.vx = rnd.uniform(-40, 40); p.vy = rnd.uniform(320, 620)
        p.s = rnd.choice([20, 26, 32, 38]); p.rot = rnd.random() * 6.283; p.rv = rnd.uniform(-9, 9)
        p.ci = rnd.randrange(8); p.sway = rnd.uniform(30, 90); p.life = 99
    elif kind == "sparkle":
        p.x = rnd.uniform(20, W - 20); p.y = rnd.uniform(20, H - 20)
        p.vx = 0; p.vy = rnd.uniform(-20, 20)
        p.s = rnd.choice([16, 24, 34, 46, 60]); p.rot = rnd.random() * 6.283; p.rv = rnd.uniform(-0.8, 0.8)
        p.ci = rnd.choice([0, 0, 1]); p.sway = 0; p.life = rnd.uniform(0.5, 1.1)
        if t0: p.age = rnd.random() * p.life
    return p

CFG = {
    "yildiz":  dict(kind="star",     colors=[(255, 210, 63), (255, 255, 255), (255, 236, 160)], sizes=[18, 26, 36, 48, 64], n=90),
    "kalp":    dict(kind="heart",    colors=[(255, 93, 143), (255, 46, 99), (255, 179, 198), (255, 255, 255)], sizes=[30, 40, 52, 68, 88], n=45),
    "konfeti": dict(kind="confetti", colors=[(255, 59, 92), (255, 196, 0), (0, 200, 255), (120, 240, 120), (255, 120, 220), (255, 255, 255), (160, 100, 255), (255, 140, 40)], sizes=[20, 26, 32, 38], n=170),
    "sparkle": dict(kind="sparkle",  colors=[(255, 255, 255), (255, 220, 120)], sizes=[16, 24, 34, 46, 60], n=60),
}

def render(fx, sec, alpha, out_dir):
    cfg = CFG[fx]
    rnd = random.Random(360 + len(fx))
    bank = Bank(cfg["kind"], cfg["colors"], cfg["sizes"], rots(24), soft=alpha)
    parts = [spawn(fx, rnd, True) for _ in range(cfg["n"])]
    frames = int(sec * FPS)
    out_dir.mkdir(parents=True, exist_ok=True)
    if alpha:
        out = out_dir / f"{fx}_a.webm"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "32", "-row-mt", "1", "-speed", "6", "-an", str(out)]
    else:
        out = out_dir / f"{fx}.mp4"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    dt = 1.0 / FPS
    for fi in range(frames):
        t = fi * dt
        if alpha:
            fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        else:
            fr = Image.new("RGB", (W, H), GREEN)
        for i, p in enumerate(parts):
            p.age += dt
            p.x += (p.vx + (p.sway * math.sin(t * 1.7 + p.ph) if p.sway else 0)) * dt
            p.y += p.vy * dt
            p.rot += p.rv * dt
            size = p.s
            if fx == "yildiz":
                size = p.s * (0.75 + 0.25 * math.sin(t * 6 + p.ph))
            elif fx == "kalp":
                size = p.s * (0.9 + 0.1 * math.sin(t * 5 + p.ph))
            elif fx == "konfeti":
                size = p.s
            elif fx == "sparkle":
                k = p.age / p.life
                size = p.s * math.sin(min(1, max(0, k)) * math.pi)
            dead = (fx in ("yildiz", "konfeti") and p.y > H + 80) or (fx == "kalp" and p.y < -100) or (fx == "sparkle" and p.age >= p.life)
            if dead:
                parts[i] = spawn(fx, rnd)
                continue
            if size < 3:
                continue
            sp = bank.get(p.ci, size, p.rot)
            if fx == "konfeti":
                # 3B dönüş hissi: genişliği kos ile daralt
                wscale = abs(math.cos(t * 7 + p.ph)) * 0.85 + 0.15
                sw = max(2, int(sp.width * wscale))
                sp = sp.resize((sw, sp.height), Image.BILINEAR)
            x = int(p.x - sp.width / 2); y = int(p.y - sp.height / 2)
            if x + sp.width < 0 or y + sp.height < 0 or x > W or y > H:
                continue
            if alpha:
                box = (max(0, x), max(0, y), min(W, x + sp.width), min(H, y + sp.height))
                if box[2] <= box[0] or box[3] <= box[1]:
                    continue
                crop = sp.crop((box[0] - x, box[1] - y, box[2] - x, box[3] - y))
                region = fr.crop(box)
                fr.paste(Image.alpha_composite(region, crop), box)
            else:
                fr.paste(sp, (x, y), sp)
        proc.stdin.write(fr.tobytes())
        if fi % 150 == 0:
            print(f"  {fx}{'_a' if alpha else ''}: kare {fi}/{frames}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("bitti:", out, out.stat().st_size // 1024, "KB")
    return out

if __name__ == "__main__":
    args = sys.argv[1:]
    which = args[0] if args else "all"
    alpha = "--alpha" in args
    sec = float(args[args.index("--sec") + 1]) if "--sec" in args else 30
    out_dir = pathlib.Path(args[args.index("--out") + 1]) if "--out" in args else pathlib.Path(__file__).parent.parent / "fx"
    for fx in (list(CFG) if which == "all" else [which]):
        render(fx, sec, alpha, out_dir)
