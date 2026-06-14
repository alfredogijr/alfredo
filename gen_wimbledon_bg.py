"""
Generates a synthetic Wimbledon-atmosphere background video.
Centre Court aesthetic: blurred grass, stadium bokeh, cinematic grain, golden light.
Output: 1080x1920 vertical, 30fps, ~30s.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from moviepy import VideoClip
from pathlib import Path
import math, random

W, H = 1080, 1920
FPS  = 30
DUR  = 31.0  # slightly longer than needed

rng = np.random.default_rng(42)

# ── Precompute noise for grain so it's consistent but changes per-frame ──────
GRAIN_FRAMES = int(DUR * FPS) + 2
grain_cache  = rng.standard_normal((GRAIN_FRAMES, H // 4, W // 4)).astype(np.float32) * 8.0

# ── Bokeh circles (precomputed) ───────────────────────────────────────────────
random.seed(7)
BOKEH = []
for _ in range(80):
    cx  = random.uniform(-0.1, 1.1)
    cy  = random.uniform(-0.05, 1.05)
    rad = random.uniform(18, 90)
    # warm golden / amber tones from stadium lights
    hue_pick = random.random()
    if hue_pick < 0.5:
        col = (random.randint(200, 255), random.randint(150, 210), random.randint(30, 100))
    elif hue_pick < 0.75:
        col = (random.randint(180, 255), random.randint(200, 255), random.randint(80, 160))
    else:
        col = (random.randint(60, 140), random.randint(90, 160), random.randint(140, 220))
    alpha = random.uniform(0.04, 0.22)
    drift_x = random.uniform(-0.006, 0.006)
    drift_y = random.uniform(-0.003, 0.003)
    pulse   = random.uniform(0.3, 1.2)
    BOKEH.append((cx, cy, rad, col, alpha, drift_x, drift_y, pulse))


def grass_base(t):
    """Build the blurred grass court base."""
    arr = np.zeros((H, W, 3), dtype=np.float32)

    # Vertical gradient – darker at very top (crowd shadow), lighter mid, slightly dark bottom
    ys = np.linspace(0, 1, H)
    r  = np.interp(ys, [0, 0.18, 0.55, 1.0], [18, 28, 55, 38])[:, None]
    g  = np.interp(ys, [0, 0.18, 0.55, 1.0], [55, 75, 125, 95])[:, None]
    b  = np.interp(ys, [0, 0.18, 0.55, 1.0], [12, 20, 45, 28])[:, None]
    arr[:,:,0] = r
    arr[:,:,1] = g
    arr[:,:,2] = b

    # Horizontal mowing stripes (subtle)
    xs    = np.linspace(0, 1, W)
    speed = 0.018
    phase = t * speed
    stripe = (np.sin((xs + phase) * W / 55 * math.pi) * 0.055 + 1.0)[None, :, None]
    arr   = arr * stripe

    # Very subtle vignette
    cx, cy = W / 2, H * 0.55
    Y, X   = np.ogrid[:H, :W]
    dist   = np.sqrt(((X - cx) / (W * 0.62))**2 + ((Y - cy) / (H * 0.58))**2)
    vig    = np.clip(1.0 - dist * 0.38, 0.55, 1.0)[:, :, None]
    arr   *= vig

    # Golden afternoon light shaft from upper-right
    shaft_x = np.linspace(0, 1, W)[None, :] - 0.72
    shaft_y = np.linspace(0, 1, H)[:, None] - 0.10
    shaft   = np.exp(-(shaft_x**2 * 4.5 + shaft_y**2 * 1.2)) * 28.0
    arr[:,:,0] += shaft * 1.0
    arr[:,:,1] += shaft * 0.85
    arr[:,:,2] += shaft * 0.20

    return np.clip(arr, 0, 255).astype(np.uint8)


def add_bokeh(img_arr, t):
    """Composite semi-transparent bokeh circles onto the frame."""
    base = Image.fromarray(img_arr).convert("RGBA")
    bk   = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bk, "RGBA")

    for (cx, cy, rad, col, alpha, dx, dy, pulse) in BOKEH:
        tx  = cx + dx * t
        ty  = cy + dy * t
        r   = rad * (1.0 + 0.06 * math.sin(t * pulse * 2 * math.pi / 7.0))
        px  = int(tx * W)
        py  = int(ty * H)
        pr  = int(r)
        a   = int(alpha * 255)
        draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                     fill=(col[0], col[1], col[2], a))

    # Heavy blur to make bokeh soft
    bk = bk.filter(ImageFilter.GaussianBlur(radius=28))
    base = Image.alpha_composite(base, bk)
    return np.array(base.convert("RGB"))


def add_grain(arr, frame_idx):
    """Add subtle film grain."""
    fi   = min(frame_idx, GRAIN_FRAMES - 1)
    g_sm = grain_cache[fi]
    # Resize grain up via PIL for speed
    g_img = Image.fromarray(
        np.clip(g_sm + 128, 0, 255).astype(np.uint8)
    ).resize((W, H), Image.NEAREST)
    g_arr = (np.array(g_img).astype(np.float32) - 128.0)[:, :, None]
    out   = arr.astype(np.float32) + g_arr * 0.55
    return np.clip(out, 0, 255).astype(np.uint8)


def make_frame(t):
    frame_idx = int(t * FPS)

    # 1. Grass base
    arr = grass_base(t)

    # 2. Apply blur to simulate shallow depth of field
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=22))
    arr = np.array(img)

    # 3. Bokeh overlay
    arr = add_bokeh(arr, t)

    # 4. Second light blur pass to smooth bokeh edges
    img = Image.fromarray(arr)
    img = img.filter(ImageFilter.GaussianBlur(radius=6))
    arr = np.array(img)

    # 5. Grain
    arr = add_grain(arr, frame_idx)

    # 6. Slight warm colour grade (lift shadows, push greens)
    f   = arr.astype(np.float32)
    f[:,:,0] = f[:,:,0] * 1.04 + 6    # red lift
    f[:,:,1] = f[:,:,1] * 1.06 + 3    # green push
    f[:,:,2] = f[:,:,2] * 0.88        # blue pull
    arr = np.clip(f, 0, 255).astype(np.uint8)

    return arr


print("Generating synthetic Wimbledon background…")
clip = VideoClip(make_frame, duration=DUR)
out  = "/home/user/alfredo/wimbledon_bg.mp4"
clip.write_videofile(out, fps=FPS, codec="libx264",
                     preset="fast", ffmpeg_params=["-crf","20"],
                     logger=None)
print(f"Done → {out}")
