"""
Turista FC — Os Irmãos: estrutura de flashback
Gera turista_irmaos_base.mp4 (~46s, sem áudio original)

Capítulo 1 — HOOK: Copa 2026 agora     (0-6s):   V2
Capítulo 2 — FLASHBACK: Madrid 2025   (6-24s):   V1 + 3 fotos
Capítulo 3 — VOLTA: Copa 2026         (24-40s):  V2 + V3
CTA preta                              (40-46s)
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
    # — Cap. 1: HOOK — Copa 2026 agora —
    to_916(v2.subclipped(0,   3)),     # 0-3s    Copa abertura (hook)
    to_916(v3.subclipped(0,   3)),     # 3-6s    Copa segunda cena

    # — Cap. 2: FLASHBACK — Madrid 2025 —
    to_916(v1.subclipped(0,   4)),     # 6-10s   Madrid abertura
    to_916(v1.subclipped(5,   9)),     # 10-14s  Madrid ação
    photo(P1p, 2.0),                   # 14-16s  foto Madrid 1
    photo(P2p, 2.0),                   # 16-18s  foto Madrid 2
    photo(P3p, 2.0),                   # 18-20s  foto Madrid 3
    to_916(v1.subclipped(18,  22)),    # 20-24s  Madrid clímax

    # — Cap. 3: VOLTA — Copa 2026 —
    to_916(v2.subclipped(6,   10)),    # 24-28s  Copa energia
    to_916(v3.subclipped(8,   12)),    # 28-32s  Copa cena 2
    to_916(v2.subclipped(14,  18)),    # 32-36s  Copa ação
    to_916(v2.subclipped(44,  49)),    # 36-41s  Copa clímax final

    # — CTA —
    ColorClip(size=(W, H), color=(0, 0, 0), duration=5).with_fps(FPS),  # 41-46s
]

base = concatenate_videoclips(clips).without_audio()
print(f"Duração: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf', '18'],
                     logger='bar')
for c in [v1, v2, v3]:
    c.close()
print("Done →", OUT)
