"""
Prep: Brasil x Haiti v2 — só estrelasemcampo + vhs1728
Gera brasil_haiti_base.mp4 (18s)
"""
from moviepy import VideoFileClip, ColorClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

VAp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/d229a2a3-ssstik.io_estrelasemcampo2026_1781552426695.mp4'
VBp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/2bd222bb-ssstik.io_vhs1728_1781552473977.mp4'
OUT = '/home/user/alfredo/brasil_haiti_base.mp4'
W, H, FPS = 1080, 1920, 30

def to_916(clip):
    cw, ch = clip.size
    scale = max(W / cw, H / ch)
    nw, nh = round(cw * scale), round(ch * scale)
    r = clip.resized((nw, nh))
    x1, y1 = (nw - W) // 2, (nh - H) // 2
    return r.cropped(x1=x1, y1=y1, x2=x1+W, y2=y1+H).with_fps(FPS)

print("Loading...")
va = VideoFileClip(VAp)   # estrelasemcampo2026 — 60s
vb = VideoFileClip(VBp)   # vhs1728 — 28s

clips = [
    to_916(va.subclipped(0,   2)),    # 0-2s   Hook: estrelas em campo
    to_916(vb.subclipped(0,   2)),    # 2-4s   VHS: emoção/torcida
    to_916(va.subclipped(8,  10)),    # 4-6s   Disputa de bola
    to_916(vb.subclipped(5,   7)),    # 6-8s   VHS: jogador concentrado
    to_916(va.subclipped(18, 21)),    # 8-11s  Celebração (3s)
    to_916(vb.subclipped(12, 13)),    # 11-12s VHS: torcida
    to_916(va.subclipped(35, 36)),    # 12-13s Craque em campo
    to_916(vb.subclipped(18, 19)),    # 13-14s VHS: close emocional
]

# Áudio contínuo: vb tem energia constante, cobre os 18s
audio_src = VideoFileClip(VBp)
continuous_audio = audio_src.audio.subclipped(0, 18.0).with_effects([
    AudioFadeIn(0.3), AudioFadeOut(1.5)
])

video = concatenate_videoclips(clips).without_audio()
cta = ColorClip(size=(W, H), color=(0, 0, 0), duration=4).with_fps(FPS)
base = concatenate_videoclips([video, cta]).with_audio(continuous_audio)

print(f"Total: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf', '18'],
                     logger='bar')
for c in [va, vb, audio_src]:
    c.close()
print("Done →", OUT)
