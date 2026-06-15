"""
Prep: Brasil x Haiti / 2ª rodada Filadélfia
Gera brasil_haiti_base.mp4 (18s)
"""
from moviepy import VideoFileClip, ColorClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut

VAp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/37927e8d-ssstik.io_bscec__1781552763919.mp4'
VBp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/97e91829-ssstik.io_estrelasemcampo2026_1781552426695.mp4'
VCp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/39d31303-ssstik.io_futnews78_1781552656076.mp4'
VEp = '/root/.claude/uploads/cfe6de6c-15a3-5643-91b8-6c82cc893ef7/6b016403-ssstik.io_vhs1728_1781552473977.mp4'
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
va = VideoFileClip(VAp)
vb = VideoFileClip(VBp)
vc = VideoFileClip(VCp)
ve = VideoFileClip(VEp)

clips = [
    to_916(va.subclipped(13, 15)),   # 0-2s   Hook: torcedores com bandeira
    to_916(ve.subclipped(1,  3)),    # 2-4s   Campo ao vivo, bola rolando
    to_916(ve.subclipped(11, 13)),   # 4-6s   Disputa/tackle tenso
    to_916(vc.subclipped(14, 16)),   # 6-8s   Jogador emocional/concentrado
    to_916(vc.subclipped(23, 26)),   # 8-11s  Celebração + torcida cantando
    to_916(va.subclipped(19, 20)),   # 11-12s Torcedor fanático, pintado
    to_916(vc.subclipped(4,  5)),    # 12-13s Torcedor com Copa, emoção
    to_916(va.subclipped(7,  8)),    # 13-14s Rua com bandeiras do Brasil
]

video = concatenate_videoclips(clips)
audio = video.audio.with_effects([AudioFadeIn(0.3), AudioFadeOut(1.5)])
video = video.with_audio(audio)

cta = ColorClip(size=(W, H), color=(0, 0, 0), duration=4).with_fps(FPS)
base = concatenate_videoclips([video, cta])
print(f"Total: {base.duration:.1f}s")
base.write_videofile(OUT, fps=FPS, codec='libx264',
                     preset='fast', ffmpeg_params=['-crf', '18'],
                     logger='bar')
for c in [va, vb, vc, ve]:
    c.close()
print("Done →", OUT)
