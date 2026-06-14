"""
Prep script: montagem Copa do Mundo — Alexandre Falbo × Turista FC
Gera falbo_copa_base.mp4:
  - 5s: selfie foto animada (Ken Burns, crop 9:16)
  - 18s: melhor trecho do V2 (cerimônia bandeiras + hino)
  - 12s: melhor trecho do V1 (estádio, atmosfera)
Áudio: hino extraído do V2, aplicado em todo o vídeo.
"""

import numpy as np
from PIL import Image, ImageFilter
from moviepy import VideoFileClip, VideoClip, concatenate_videoclips, AudioFileClip
from moviepy.audio.fx import AudioFadeOut, AudioFadeIn
import math

PHOTO = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/6c70dd3d-177589.jpg'
V1    = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/8d7744e6-VID20260614WA00171.mp4'
V2    = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/a3c5d8ce-VID20260614WA00151.mp4'

W, H   = 1080, 1920
FPS    = 30
OUT    = '/home/user/alfredo/falbo_copa_base.mp4'

PHOTO_DUR = 5.0
V2_START  = 0.0;  V2_END = 18.0
V1_START  = 5.0;  V1_END  = 17.0

# ── helpers ───────────────────────────────────────────────────────────────────

def fit_to_frame(img, w=W, h=H):
    """Crop/scale PIL image to exact w×h preserving aspect (centre crop)."""
    iw, ih = img.size
    scale  = max(w / iw, h / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    img    = img.resize((nw, nh), Image.LANCZOS)
    x0     = (nw - w) // 2
    y0     = (nh - h) // 2
    return img.crop((x0, y0, x0 + w, y0 + h))


def fit_arr(arr, w=W, h=H):
    return np.array(fit_to_frame(Image.fromarray(arr), w, h))


# ── 1. Photo clip (Ken Burns: slow zoom in + subtle pan up) ───────────────────

photo_src = np.array(fit_to_frame(Image.open(PHOTO).convert('RGB')))

def photo_frame(t):
    zoom   = 1.0 + 0.10 * (t / PHOTO_DUR)   # 1.00 → 1.10
    pan_y  = int(30 * (t / PHOTO_DUR))        # drift up 30px

    crop_h = int(H / zoom)
    crop_w = int(W / zoom)
    y0 = max(0, (H - crop_h) // 2 - pan_y)
    x0 = (W - crop_w) // 2
    y0 = min(y0, H - crop_h)

    patch = photo_src[y0:y0 + crop_h, x0:x0 + crop_w]
    return np.array(Image.fromarray(patch).resize((W, H), Image.BILINEAR))

photo_clip = VideoClip(photo_frame, duration=PHOTO_DUR).with_fps(FPS)
print(f"Photo clip: {PHOTO_DUR}s")

# ── 2. V2 clip (bandeiras + hino) ────────────────────────────────────────────

v2_raw  = VideoFileClip(V2)
v2_clip = v2_raw.subclipped(V2_START, V2_END).resized((W, H)).with_fps(FPS)
print(f"V2 clip: {V2_END - V2_START}s  (source: {V2_START}-{V2_END}s of {round(v2_raw.duration,1)}s)")

# ── 3. V1 clip (estádio, atmosfera) ──────────────────────────────────────────

v1_raw  = VideoFileClip(V1)
v1_clip = v1_raw.subclipped(V1_START, V1_END).resized((W, H)).with_fps(FPS)
print(f"V1 clip: {V1_END - V1_START}s  (source: {V1_START}-{V1_END}s of {round(v1_raw.duration,1)}s)")

# ── 4. Concatenate video ──────────────────────────────────────────────────────

base_video = concatenate_videoclips([photo_clip, v2_clip, v1_clip])
total_dur  = base_video.duration
print(f"Total video: {total_dur:.1f}s")

# ── 5. Anthem audio from V2, stretched to cover full video ───────────────────

anthem = v2_raw.audio.subclipped(0, min(total_dur, v2_raw.audio.duration))
anthem = anthem.with_effects([AudioFadeIn(1.0), AudioFadeOut(1.5)])

base_video = base_video.with_audio(anthem)

# ── 6. Export base (no text overlays yet) ────────────────────────────────────

print(f"Exporting base video → {OUT}")
base_video.write_videofile(OUT, fps=FPS, codec='libx264',
                           preset='fast', ffmpeg_params=['-crf','18'],
                           logger='bar')

v2_raw.close(); v1_raw.close()
print("Done.")
