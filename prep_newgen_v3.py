"""
New Generation 8ª Etapa v3 — base video
Mix: 2 video clips + 8 fotos → newgen_base_v3.mp4 (30s)

Segmentos:
  0-2s    V1   20260621_103717.mp4  (clip de ação - abertura)
  2-5s    P1   103619.jpg
  5-7.5s  P2   103523.jpg
  7.5-10.5s P3 103601.jpg
  10.5-13.5s P4 103613.jpg
  13.5-16s  P5 103540.jpg
  16-18s  V2   20260621_103722.mp4  (clip de ação - clímax, roda SOBRE "ELE NÃO ESTAVA SÓ BRINCANDO")
  18-21s  P6   103618.jpg
  21-24s  P7   103532.jpg
  24-27s  P8   103602.jpg
  27-30s  BLACK CTA
"""
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, ColorClip, concatenate_videoclips
from PIL import Image, ImageOps
import numpy as np

W, H, FPS = 1080, 1920, 30
BASE = Path("/home/user/alfredo")
VIDEOS = BASE / "videos_newgen"
FOTOS  = BASE / "fotos_newgen"
OUT    = BASE / "newgen_base_v3.mp4"


def load_photo(path: str, duration: float):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    cw, ch = img.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0 = (nw - W) // 2
    y0 = (nh - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    arr = np.array(img)
    return ImageClip(arr, duration=duration).with_fps(FPS)


def load_video(path: str, target_dur: float):
    v = VideoFileClip(path)
    cw, ch = v.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    v = v.resized((nw, nh))
    x1, y1 = (nw - W) // 2, (nh - H) // 2
    v = v.cropped(x1=x1, y1=y1, x2=x1 + W, y2=y1 + H).with_fps(FPS)
    # pad to target duration by freezing last frame if clip is shorter
    if v.duration < target_dur:
        last = ImageClip(v.get_frame(v.duration - 0.05), duration=target_dur - v.duration).with_fps(FPS)
        v = concatenate_videoclips([v, last])
    else:
        v = v.subclipped(0, target_dur)
    return v


print("Carregando clips e fotos...")

clips = [
    load_video(str(VIDEOS / "20260621_103717.mp4"), 2.0),    # 0-2s   V1 abertura
    load_photo(str(FOTOS  / "20260621_103619.jpg"), 3.0),    # 2-5s   P1
    load_photo(str(FOTOS  / "103523.jpg"),          2.5),    # 5-7.5s P2
    load_photo(str(FOTOS  / "20260621_103601.jpg"), 3.0),    # 7.5-10.5s P3
    load_photo(str(FOTOS  / "20260621_103613.jpg"), 3.0),    # 10.5-13.5s P4
    load_photo(str(FOTOS  / "20260621_103540.jpg"), 2.5),    # 13.5-16s P5
    load_video(str(VIDEOS / "20260621_103722.mp4"), 2.0),    # 16-18s V2 clímax
    load_photo(str(FOTOS  / "20260621_103618.jpg"), 3.0),    # 18-21s P6
    load_photo(str(FOTOS  / "103532.jpg"),          3.0),    # 21-24s P7
    load_photo(str(FOTOS  / "20260621_103602.jpg"), 3.0),    # 24-27s P8
    ColorClip(size=(W, H), color=(0, 0, 0), duration=3.0).with_fps(FPS),  # 27-30s CTA black
]

base = concatenate_videoclips(clips).without_audio()
print(f"Duração total: {base.duration:.1f}s")
base.write_videofile(str(OUT), fps=FPS, codec="libx264",
                     preset="fast", ffmpeg_params=["-crf", "18"],
                     logger="bar")
print("Done →", OUT)
