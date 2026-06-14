"""
Prep: Hamilton × Ferrari — Turista FC
Sequência: V1(0-8s) → V2(0-9s) → V1(22-27s) → V1(40-48s)
Total base: ~30s + 4.5s CTA via briefing
"""

from moviepy import VideoFileClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

V1  = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/f5764dad-VID20260614WA00391.mp4'
V2  = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/fe761a03-VID20260614WA00381.mp4'
OUT = '/home/user/alfredo/hamilton_base.mp4'
W, H = 1080, 1920
FPS  = 30

v1 = VideoFileClip(V1)
v2 = VideoFileClip(V2)

seg1 = v1.subclipped(0,    8).resized((W, H)).with_fps(FPS)   # "from this" fãs
seg2 = v2.subclipped(0,    9).resized((W, H)).with_fps(FPS)   # Londres "remember who you are"
seg3 = v1.subclipped(22,  27).resized((W, H)).with_fps(FPS)   # standings HAM #1
seg4 = v1.subclipped(40,  48).resized((W, H)).with_fps(FPS)   # pódio champagne GOAT

base = concatenate_videoclips([seg1, seg2, seg3, seg4])

# Fade in/out no áudio total
audio = base.audio.with_effects([AudioFadeIn(0.8), AudioFadeOut(1.2)])
base  = base.with_audio(audio)

print(f"Total: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf','18'],
                     logger='bar')
v1.close(); v2.close()
print("Done →", OUT)
