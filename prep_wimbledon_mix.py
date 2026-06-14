"""
Prep: Wimbledon Mix — tela preta + rally Nadal×Federer
Gera wimbledon_mix_base.mp4:
  5s preto silencioso + 18s rally (1 loop completo + 4.8s do segundo)
"""

import numpy as np
from moviepy import VideoFileClip, ColorClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

RALLY = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/eb00cd28-Rafael_Nadals_ICONIC_2008_Forehand_against_Roger_Federer.mp4'
OUT   = '/home/user/alfredo/wimbledon_mix_base.mp4'
W, H  = 1080, 1920
FPS   = 30

BLACK_DUR   = 5.0
RALLY_TOTAL = 18.0   # rally + segundo início

print("Loading rally…")
raw = VideoFileClip(RALLY)          # 13.21s
scaled = raw.resized((W, H)).with_fps(FPS)

# Loop: 13.21s + 4.79s = 18s
loop1 = scaled.with_duration(raw.duration)
loop2 = scaled.subclipped(0, RALLY_TOTAL - raw.duration)

# Apply audio fade only on the rally portion
rally_audio = concatenate_videoclips([loop1, loop2]).audio
rally_audio = rally_audio.with_effects([AudioFadeIn(1.2), AudioFadeOut(1.5)])

rally = concatenate_videoclips([loop1, loop2]).with_audio(rally_audio)

# Tela preta (sem áudio)
black = ColorClip(size=(W, H), color=(0, 0, 0), duration=BLACK_DUR).with_fps(FPS)

base = concatenate_videoclips([black, rally])
print(f"Total: {base.duration:.1f}s")

base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf','18'],
                     logger='bar')
raw.close()
print("Done →", OUT)
