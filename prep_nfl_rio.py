"""
Prep: NFL no Rio — histórico Turista FC
Gera nfl_rio_base.mp4 (24s)
Sequência:
  V5[0:2]     0-2s   Hook: campo NFL endzone ao vivo
  V3[0:2]     2-4s   Histórico: bar NFL festivo com bandeiras
  V4[0:3]     4-7s   USA: camarote na final nos EUA
  V2[4.5:6.5] 7-9s   SP: clientes no estádio São Paulo
  V1[2:3]     9-10s  Montagem 1
  V3[3:4]     10-11s Montagem 2
  V5[2:3]     11-12s Montagem 3
  V1[5:6]     12-13s Logística 1
  V2[0.5:1.5] 13-14s Logística 2 (jerseys NFL)
  V4[4:5]     14-15s Logística 3
  V4[2:5]     15-18s Relaxado: camarote torcedores
  V5[3:6]     18-21s Clímax: estádio NFL
  black 3s    21-24s CTA
"""
from moviepy import VideoFileClip, ColorClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

V1p = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/70482390-20250905_181800.mp4'
V2p = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/6bb08744-20250905_192135.mp4'
V3p = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/bb5d6e9e-20250905_193810.mp4'
V4p = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/85d024ee-20250905_202412.mp4'
V5p = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/193af85f-20250905_213309.mp4'
OUT = '/home/user/alfredo/nfl_rio_base.mp4'
W, H, FPS = 1080, 1920, 30

def to_916(clip):
    cw, ch = clip.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    r = clip.resized((nw, nh))
    x1, y1 = (nw - W) // 2, (nh - H) // 2
    return r.cropped(x1=x1, y1=y1, x2=x1+W, y2=y1+H).with_fps(FPS)

print("Loading...")
v1 = VideoFileClip(V1p)
v2 = VideoFileClip(V2p)
v3 = VideoFileClip(V3p)
v4 = VideoFileClip(V4p)
v5 = VideoFileClip(V5p)

clips = [
    to_916(v5.subclipped(0,   2)),      # 0-2s   Hook
    to_916(v3.subclipped(0,   2)),      # 2-4s   Histórico
    to_916(v4.subclipped(0,   3)),      # 4-7s   USA final
    to_916(v2.subclipped(4.5, 6.5)),   # 7-9s   SP clientes
    to_916(v1.subclipped(2,   3)),      # 9-10s  Montagem 1
    to_916(v3.subclipped(3,   4)),      # 10-11s Montagem 2
    to_916(v5.subclipped(2,   3)),      # 11-12s Montagem 3
    to_916(v1.subclipped(5,   6)),      # 12-13s Logística 1
    to_916(v2.subclipped(0.5, 1.5)),   # 13-14s Logística 2 jerseys
    to_916(v4.subclipped(4,   5)),      # 14-15s Logística 3
    to_916(v4.subclipped(2,   5)),      # 15-18s Relaxado
    to_916(v5.subclipped(3,   6)),      # 18-21s Clímax
]

video = concatenate_videoclips(clips)
audio = video.audio.with_effects([AudioFadeIn(0.5), AudioFadeOut(1.5)])
video = video.with_audio(audio)

cta = ColorClip(size=(W, H), color=(0, 0, 0), duration=3).with_fps(FPS)
base = concatenate_videoclips([video, cta])

print(f"Total: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf', '18'],
                     logger='bar')
for c in [v1, v2, v3, v4, v5]:
    c.close()
print("Done →", OUT)
