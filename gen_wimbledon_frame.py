"""
Generates a single high-quality Wimbledon background frame.
Then ffmpeg creates the animated video from it with zoompan.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import math, random

W, H = 1080, 1920

rng  = np.random.default_rng(42)
rand = random.Random(7)

def make_background():
    arr = np.zeros((H, W, 3), dtype=np.float32)

    # ── Vertical gradient (grass) ──────────────────────────────────────────────
    ys = np.linspace(0, 1, H)
    r  = np.interp(ys, [0, 0.15, 0.50, 1.0], [15, 25, 52, 36])[:, None]
    g  = np.interp(ys, [0, 0.15, 0.50, 1.0], [48, 70, 120, 90])[:, None]
    b  = np.interp(ys, [0, 0.15, 0.50, 1.0], [10, 18, 42, 26])[:, None]
    arr[:,:,0] = r; arr[:,:,1] = g; arr[:,:,2] = b

    # ── Horizontal mowing stripes ──────────────────────────────────────────────
    xs     = np.linspace(0, 1, W)
    stripe = (np.sin(xs * W / 55 * math.pi) * 0.06 + 1.0)[None, :, None]
    arr    = arr * stripe

    # ── Radial vignette ────────────────────────────────────────────────────────
    Y, X  = np.ogrid[:H, :W]
    cx, cy = W / 2, H * 0.52
    dist   = np.sqrt(((X - cx)/(W*0.60))**2 + ((Y - cy)/(H*0.56))**2)
    vig    = np.clip(1.0 - dist * 0.40, 0.50, 1.0)[:, :, None]
    arr   *= vig

    # ── Golden afternoon light shaft (upper right) ─────────────────────────────
    sx  = (np.arange(W)[None,:] / W - 0.70)
    sy  = (np.arange(H)[:,None] / H - 0.08)
    shaft = np.exp(-(sx**2 * 5.0 + sy**2 * 1.5)) * 32.0
    arr[:,:,0] += shaft * 1.10
    arr[:,:,1] += shaft * 0.90
    arr[:,:,2] += shaft * 0.25

    arr = np.clip(arr, 0, 255).astype(np.uint8)

    img = Image.fromarray(arr)

    # ── First heavy blur (deep of field) ──────────────────────────────────────
    img = img.filter(ImageFilter.GaussianBlur(radius=24))

    # ── Bokeh circles ─────────────────────────────────────────────────────────
    bk   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bk, "RGBA")
    for _ in range(90):
        cx2 = rand.uniform(-0.08, 1.08)
        cy2 = rand.uniform(-0.05, 1.05)
        rad = rand.uniform(14, 85)
        hp  = rand.random()
        if hp < 0.5:
            col = (rand.randint(200,255), rand.randint(145,210), rand.randint(25, 95))
        elif hp < 0.75:
            col = (rand.randint(170,255), rand.randint(195,255), rand.randint(70,155))
        else:
            col = (rand.randint(55,135), rand.randint(85,160), rand.randint(130,220))
        alpha = rand.randint(10, 58)
        px, py, pr = int(cx2*W), int(cy2*H), int(rad)
        draw.ellipse([px-pr, py-pr, px+pr, py+pr], fill=(*col, alpha))

    bk  = bk.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img.convert("RGBA"), bk).convert("RGB")

    # ── Second softer blur ─────────────────────────────────────────────────────
    img = img.filter(ImageFilter.GaussianBlur(radius=7))

    # ── Film grain ────────────────────────────────────────────────────────────
    arr = np.array(img).astype(np.float32)
    grain = rng.standard_normal((H, W)) * 7.5
    arr  += grain[:, :, None] * 0.6

    # ── Warm colour grade ──────────────────────────────────────────────────────
    arr[:,:,0] = arr[:,:,0] * 1.05 + 7
    arr[:,:,1] = arr[:,:,1] * 1.07 + 3
    arr[:,:,2] = arr[:,:,2] * 0.87

    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


print("Rendering background frame…")
img = make_background()
out = "/home/user/alfredo/wimbledon_bg_frame.png"
img.save(out, optimize=False)
print(f"Saved → {out}  ({img.size})")
