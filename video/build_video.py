"""Assemble the Kannada documentary video.

Inputs (relative to this folder):
  script_kn.json        narration + on-screen titles
  scenes.json           scene id -> list of photo files (in photos/)
  audio/<id>.wav        narration per scene (from tts.py)
Output:
  out/indian_racing_behind_the_scenes_kannada.mp4
"""
import json
import os
import re
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 25
FONT_B = "/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf"
BUILD = os.path.join(HERE, "build")
OUT = os.path.join(HERE, "out")
os.makedirs(BUILD, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

script = json.load(open(os.path.join(HERE, "script_kn.json"), encoding="utf-8"))
scenes = json.load(open(os.path.join(HERE, "scenes.json"), encoding="utf-8"))

LEAD, TAIL = 0.4, 0.5  # silence before/after narration in each scene


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def wav_dur(p):
    with wave.open(p) as w:
        return w.getnframes() / w.getframerate()


def font(path, size):
    return ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)


def wrap(draw, text, fnt, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt) <= maxw:
            cur = test
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def subtitle_png(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(FONT_R, 50)
    lines = wrap(d, text, f, W - 360)
    lh = 78
    y0 = H - 90 - lh * len(lines)
    # soft dark band for readability
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rounded_rectangle((140, y0 - 22, W - 140, H - 62), 24, fill=(0, 0, 0, 150))
    img = Image.alpha_composite(img, band)
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y0 + i * lh), ln, font=f, fill=(255, 255, 255, 255),
               stroke_width=2, stroke_fill=(0, 0, 0, 220))
    img.save(path)


def title_png(title, idx, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(FONT_B, 58)
    tw = d.textlength(title, font=f)
    x, y = 90, 80
    d.rectangle((x - 30, y - 6, x - 18, y + 92), fill=(255, 153, 51, 255))  # saffron bar
    d.rounded_rectangle((x - 10, y - 10, x + tw + 40, y + 96), 14, fill=(0, 0, 0, 140))
    d.text((x + 14, y), title, font=f, fill=(255, 255, 255, 255))
    small = font(FONT_R, 30)
    d.text((x + 14, y + 112), f"ಅಧ್ಯಾಯ {idx}", font=small, fill=(255, 220, 170, 235),
           stroke_width=2, stroke_fill=(0, 0, 0, 200))
    img.save(path)


def card_png(lines, path, sub=None):
    img = Image.new("RGB", (W, H), (8, 10, 16))
    d = ImageDraw.Draw(img)
    # tricolour accent line
    for i, c in enumerate([(255, 153, 51), (255, 255, 255), (19, 136, 8)]):
        d.rectangle((W // 2 - 240 + i * 160, 300, W // 2 - 80 + i * 160, 308), fill=c)
    f = font(FONT_B, 96)
    y = 380
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text(((W - tw) / 2, y), ln, font=f, fill=(255, 255, 255))
        y += 140
    if sub:
        fs = font(FONT_R, 44)
        for ln in sub:
            tw = d.textlength(ln, font=fs)
            d.text(((W - tw) / 2, y + 20), ln, font=fs, fill=(255, 200, 140))
            y += 70
    img.save(path)


def prep_photo(src, dst):
    """Cover-crop photo to 16:9 at 2304x1296 (headroom for Ken Burns)."""
    im = Image.open(src).convert("RGB")
    portrait = im.height > im.width
    tw, th = 2304, 1296
    r = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    # keep faces in frame for tall photos by biasing the crop upward
    l, t = (im.width - tw) // 2, int((im.height - th) * (0.25 if portrait else 0.5))
    im = im.crop((l, t, l + tw, t + th))
    im.save(dst, quality=95)


def kenburns(photo, dur, out, mode):
    """Smooth zoom/pan clip from a pre-cropped 2304x1296 photo."""
    D = f"{dur:.3f}"
    if mode == 0:   # slow zoom in
        vf = f"scale=w='1920*(1+0.18*t/{D})':h=-2:eval=frame,crop=1920:1080"
    elif mode == 1:  # slow zoom out
        vf = f"scale=w='1920*(1.18-0.18*t/{D})':h=-2:eval=frame,crop=1920:1080"
    elif mode == 2:  # pan left->right
        vf = f"crop=1920:1080:x='384*t/{D}':y=108"
    else:            # pan right->left
        vf = f"crop=1920:1080:x='384-384*t/{D}':y=108"
    vf += f",fps={FPS},format=yuv420p"
    run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", photo, "-t", D,
         "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])


def split_sentences(text):
    parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+", text) if p.strip()]
    # merge very short fragments into the previous sentence
    merged = []
    for p in parts:
        if merged and len(p) < 25:
            merged[-1] += " " + p
        else:
            merged.append(p)
    return merged


scene_clips = []
srt_entries = []
clock = 0.0

# ---- opening title card ----
card_png(["ವೇಗದ ಹಿಂದಿನ ಕಥೆ"], f"{BUILD}/card_open.png",
         sub=["ಭಾರತೀಯ ರೇಸಿಂಗ್ ಉದ್ಯಮ: ತೆರೆಮರೆಯ ಶ್ರಮ", "ಅಭ್ಯಾಸ  |  ಪ್ರಯಾಣ  |  ತರಬೇತಿ"])
open_dur = 3.5
run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", f"{BUILD}/card_open.png",
     "-f", "lavfi", "-t", str(open_dur), "-i", "anullsrc=r=44100:cl=stereo",
     "-t", str(open_dur), "-vf", f"fade=in:0:20,fade=out:st={open_dur-0.8}:d=0.8,format=yuv420p",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-shortest",
     f"{BUILD}/s00.mp4"])
scene_clips.append(f"{BUILD}/s00.mp4")
clock += open_dur

for n, sc in enumerate(script, start=1):
    sid = sc["id"]
    narr = os.path.join(HERE, "audio", f"{sid}.wav")
    nd = wav_dur(narr)
    total = LEAD + nd + TAIL
    photos = scenes[sid]
    per = total / len(photos)
    # --- visual: one Ken Burns sub-clip per photo, crossfaded by concat ---
    parts = []
    for k, ph in enumerate(photos):
        pp = f"{BUILD}/{sid}_{k}.jpg"
        prep_photo(os.path.join(HERE, "photos", ph), pp)
        clip = f"{BUILD}/{sid}_{k}.mp4"
        kenburns(pp, per, clip, (n + k) % 4)
        parts.append(clip)
    lst = f"{BUILD}/{sid}_list.txt"
    with open(lst, "w") as fh:
        fh.writelines(f"file '{p}'\n" for p in parts)
    base = f"{BUILD}/{sid}_base.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])

    # --- overlays: chapter title + timed subtitles ---
    tpng = f"{BUILD}/{sid}_title.png"
    title_png(sc["title"], n, tpng)
    sents = split_sentences(sc["text"])
    weights = [len(s) for s in sents]
    tot_w = sum(weights)
    inputs = ["-i", base, "-i", tpng]
    filt = f"[0:v][1:v]overlay=0:0:enable='between(t,0.3,{min(3.5, total):.2f})'[v1]"
    last = "v1"
    t0 = LEAD
    for j, (s, wgt) in enumerate(zip(sents, weights)):
        d = nd * wgt / tot_w
        spng = f"{BUILD}/{sid}_sub{j}.png"
        subtitle_png(s, spng)
        inputs += ["-i", spng]
        filt += f";[{last}][{j+2}:v]overlay=0:0:enable='between(t,{t0:.2f},{t0+d:.2f})'[v{j+2}]"
        srt_entries.append((clock + t0, clock + t0 + d, s))
        last = f"v{j+2}"
        t0 += d
    filt += f";[{last}]fade=in:st=0:d=0.5,fade=out:st={total-0.5:.2f}:d=0.5,format=yuv420p[vout]"
    filt += f";[{len(sents)+2}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=0:{total:.3f},aformat=sample_rates=44100:channel_layouts=stereo[aout]"
    inputs += ["-i", narr]
    out = f"{BUILD}/s{n:02d}.mp4"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[vout]", "-map", "[aout]",
         "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", out])
    scene_clips.append(out)
    clock += total
    print(f"scene {sid}: {total:.1f}s ({len(photos)} photos)")

# ---- closing card ----
card_png(["ವೇಗದ ಹಿಂದೆ ಶ್ರಮ", "ಶ್ರಮದ ಹಿಂದೆ ಕನಸು"], f"{BUILD}/card_end.png",
         sub=["ಭಾರತೀಯ ರೇಸಿಂಗ್‌ನ ಎಲ್ಲಾ ತೆರೆಮರೆಯ ಹೀರೋಗಳಿಗೆ ಅರ್ಪಣೆ"])
end_dur = 4.0
run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", f"{BUILD}/card_end.png",
     "-f", "lavfi", "-t", str(end_dur), "-i", "anullsrc=r=44100:cl=stereo",
     "-t", str(end_dur), "-vf", f"fade=in:0:20,fade=out:st={end_dur-1.2}:d=1.2,format=yuv420p",
     "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-shortest",
     f"{BUILD}/s99.mp4"])
scene_clips.append(f"{BUILD}/s99.mp4")
clock += end_dur

# ---- join + music bed ----
lst = f"{BUILD}/all.txt"
with open(lst, "w") as fh:
    fh.writelines(f"file '{p}'\n" for p in scene_clips)
joined = f"{BUILD}/joined.mp4"
run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:v", "copy", "-c:a", "aac", joined])
music = f"{BUILD}/music.wav"
run(["python3", os.path.join(HERE, "make_music.py"), f"{clock + 1:.2f}", music])
final = os.path.join(OUT, "indian_racing_behind_the_scenes_kannada.mp4")
run(["ffmpeg", "-y", "-i", joined, "-i", music, "-filter_complex",
     "[1:a]volume=0.22[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,"
     "loudnorm=I=-16:TP=-1.5:LRA=11[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", final])


def ts(x):
    h, r = divmod(x, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


with open(os.path.join(OUT, "indian_racing_behind_the_scenes_kannada.srt"), "w", encoding="utf-8") as fh:
    for i, (a, b, s) in enumerate(srt_entries, 1):
        fh.write(f"{i}\n{ts(a)} --> {ts(b)}\n{s}\n\n")
print("DONE", final, f"{clock:.1f}s")

MAX_LEN = 120.0
real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final],
                            capture_output=True, text=True).stdout)
print(f"final length: {real:.1f}s")
assert real <= MAX_LEN, f"video is {real:.1f}s, over the {MAX_LEN:.0f}s limit"
