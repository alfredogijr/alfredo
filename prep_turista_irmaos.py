"""
Turista FC — Os Irmãos: Atlético Madrid 2025 → Copa 2026
Gera turista_irmaos_base.mp4 (~44s, sem áudio original)

Capítulo 1 — Madrid 2025 (0-18s):  WA00201 + 3 fotos
Capítulo 2 — Copa 2026  (18-38s):  WA00222 + WA00162
CTA preta                (38-44s)
"""
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, ColorClip, concatenate_videoclips
from PIL import Image, ImageOps
import numpy as np

W, H, FPS = 1080, 1920, 30
UPL = Path('/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7')
OUT = '/home/user/alfredo/turista_irmaos_base.mp4'

V1p = UPL / '3d4c47f2-VID20260630WA00201.mp4'   # Madrid 2025  – 24s
V2p = UPL / 'eebf382a-VID20260630WA00222.mp4'   # Copa 2026    – 49.6s
V3p = UPL / 'cb890651-VID20260630WA00162.mp4'   # Copa 2026 B  – 31.3s
P1p = UPL / '3c8caffa-199185.jpg'
P2p = UPL / 'a23f8740-199186.jpg'
P3p = UPL / '885a0f0b-199190.jpg'


def to_916(clip):
    cw, ch = clip.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    r = clip.resized((nw, nh))
    x1, y1 = (nw - W) // 2, (nh - H) // 2
    return r.cropped(x1=x1, y1=y1, x2=x1 + W, y2=y1 + H).with_fps(FPS)


def photo(path, duration):
    img = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    cw, ch = img.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    x0, y0 = (nw - W) // 2, (nh - H) // 2
    img = img.crop((x0, y0, x0 + W, y0 + H))
    return ImageClip(np.array(img), duration=duration).with_fps(FPS)


print("Carregando...")
v1 = VideoFileClip(str(V1p))
v2 = VideoFileClip(str(V2p))
v3 = VideoFileClip(str(V3p))

clips = [
    # — Capítulo 1: Madrid 2025 —
    to_916(v1.subclipped(0,   4)),     # 0-4s    hook abertura
    to_916(v1.subclipped(5,   9)),     # 4-8s    segundo momento
    photo(P1p, 2.5),                   # 8-10.5s foto 1
    photo(P2p, 2.5),                   # 10.5-13s foto 2
    photo(P3p, 2.0),                   # 13-15s   foto 3
    to_916(v1.subclipped(16,  20)),    # 15-19s   reação/clímax Madrid
    # — Capítulo 2: Copa 2026 —
    to_916(v2.subclipped(0,   4)),     # 19-23s   Copa abertura
    to_916(v3.subclipped(0,   4)),     # 23-27s   Copa cena 2
    to_916(v2.subclipped(8,   12)),    # 27-31s   Copa energia
    to_916(v3.subclipped(10,  14)),    # 31-35s   Copa cena 4
    to_916(v2.subclipped(44,  49)),    # 35-40s   Copa clímax (fim do clip)
    # — CTA —
    ColorClip(size=(W, H), color=(0, 0, 0), duration=6).with_fps(FPS),  # 40-46s
]

base = concatenate_videoclips(clips).without_audio()
print(f"Duração: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf', '18'],
                     logger='bar')
for c in [v1, v2, v3]:
    c.close()
print("Done →", OUT)
