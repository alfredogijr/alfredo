"""
Creates the animated Wimbledon background video from the static frame.
Uses moviepy's ImageClip with a Ken Burns zoom/drift effect.
"""

import numpy as np
from PIL import Image
from moviepy import ImageClip, VideoClip
import math

FRAME_PATH = "/home/user/alfredo/wimbledon_bg_frame.png"
OUT_PATH   = "/home/user/alfredo/wimbledon_bg.mp4"
DUR        = 31.0
FPS        = 30
W, H       = 1080, 1920

print("Loading frame…")
src = np.array(Image.open(FRAME_PATH).convert("RGB"))

def make_frame(t):
    # Slow zoom in: 1.0→1.05 over 31s
    zoom  = 1.0 + 0.05 * (t / DUR)
    # Gentle horizontal drift (sine) + slow vertical drift
    shift_x = math.sin(t * 2 * math.pi / 22.0) * 12
    shift_y = (t / DUR) * 20

    # Crop region in source
    crop_w = int(W / zoom)
    crop_h = int(H / zoom)
    cx = W // 2 + int(shift_x)
    cy = H // 2 + int(shift_y)
    x0 = max(0, min(cx - crop_w // 2, W - crop_w))
    y0 = max(0, min(cy - crop_h // 2, H - crop_h))
    x1 = x0 + crop_w
    y1 = y0 + crop_h

    patch = src[y0:y1, x0:x1]
    # Resize to output size
    out = np.array(
        Image.fromarray(patch).resize((W, H), Image.BILINEAR)
    )
    return out

print("Building video clip…")
clip = VideoClip(make_frame, duration=DUR)
clip.write_videofile(OUT_PATH, fps=FPS, codec="libx264",
                     preset="fast", ffmpeg_params=["-crf","20"],
                     logger="bar")
print(f"Done → {OUT_PATH}")
