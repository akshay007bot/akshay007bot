"""Cinematic 2.5-D reel renderer: real photos + AI depth -> parallax camera moves, film grade,
light leaks, grain, synced captions, crossfades. Frames are piped to ffmpeg.

usage: python tools/cine.py <spec.py> <out.mp4>
The spec is a Python file defining SPEC = {...} (see brand-reels/cine/*.py).
Needs: numpy, opencv-python-headless, pillow, transformers+torch (depth), ffmpeg.
"""
import os, sys, json, math, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
os.environ.setdefault('HF_HUB_DISABLE_XET', '1')
_DEPTH = None

def depth_of(path):
    cache = path + '.depth.npy'
    if os.path.exists(cache): return np.load(cache)
    global _DEPTH
    if _DEPTH is None:
        from transformers import pipeline
        _DEPTH = pipeline('depth-estimation', model='depth-anything/Depth-Anything-V2-Small-hf', device='cpu')
    im = Image.open(path).convert('RGB')
    d = np.array(_DEPTH(im)['depth'].resize(im.size, Image.BICUBIC), dtype=np.float32)
    d = (d - d.min()) / (d.max() - d.min() + 1e-6)                    # 1 = near
    d = cv2.GaussianBlur(d, (0, 0), 3)
    np.save(cache, d); return d

ease = lambda k: k * k * (3 - 2 * k)
def lerp(a, b, k): return a + (b - a) * k

def grade(img, g):
    x = img.astype(np.float32) / 255.0
    x = np.clip((x - 0.5) * g.get('contrast', 1.12) + 0.5 + g.get('lift', 0.0), 0, 1)
    lum = x.mean(axis=2, keepdims=True)
    sh, hi = np.array(g.get('shadow', [0.0, 0.03, 0.06]), np.float32), np.array(g.get('high', [0.06, 0.03, -0.02]), np.float32)
    x = x + sh * (1 - lum) ** 2 + hi * lum ** 2
    sat = g.get('sat', 0.95); x = lum + (x - lum) * sat
    # bloom
    small = cv2.resize(x, (W // 4, H // 4)); br = np.clip(small - 0.65, 0, 1); br = cv2.GaussianBlur(br, (0, 0), 12)
    x = x + cv2.resize(br, (W, H)) * g.get('bloom', 0.7)
    return np.clip(x, 0, 1)

_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)
_VIG = (1 - 0.55 * np.clip(((_XX - W / 2) / (W * 0.75)) ** 2 + ((_YY - H / 2) / (H * 0.7)) ** 2, 0, 1))[..., None]

def leak(t, color, strength):
    cx = W * (0.2 + 0.6 * (0.5 + 0.5 * math.sin(t * 0.37))); cy = H * (0.15 + 0.2 * math.sin(t * 0.23))
    r = ((_XX - cx) ** 2 + (_YY - cy) ** 2) / (W * 0.9) ** 2
    return (np.exp(-r * 3)[..., None] * np.array(color, np.float32)) * strength

def shot_frame(sh, k, t):
    """k: 0..1 progress through the shot."""
    img, dep = sh['_img'], sh['_dep']; h0, w0 = dep.shape
    e = ease(k)
    cx, cy = lerp(sh['c0'][0], sh['c1'][0], e), lerp(sh['c0'][1], sh['c1'][1], e)
    z = max(lerp(sh['z0'], sh['z1'], e), 1.1)                        # zoom: 1 = cover-fit (min margin for parallax)
    s = max(w0 / W, h0 / H) / z                                       # source px per output px (cover)
    hw, hh = W / 2 * s / w0, H / 2 * s / h0; m = 0.035
    cx = min(max(cx, hw + m), 1 - hw - m) if hw + m < 0.5 else 0.5; cy = min(max(cy, hh + m), 1 - hh - m) if hh + m < 0.5 else 0.5
    x0 = cx * w0 + (_XX - W / 2) * s; y0 = cy * h0 + (_YY - H / 2) * s
    d = cv2.remap(dep, x0, y0, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) - sh.get('focus', 0.5)
    px, py = sh.get('par', (0.0, 0.0)); dz = sh.get('dolly', 0.0)
    mx = x0 - d * px * (e - 0.5) * w0 * 0.06 - (x0 - cx * w0) * d * dz * e * 0.12
    my = y0 - d * py * (e - 0.5) * h0 * 0.06 - (y0 - cy * h0) * d * dz * e * 0.12
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def text_layer(spec, t, fonts):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
    for cap in spec.get('captions_fn', lambda t: [])(t):
        f = fonts[cap['font']]; x, y = cap['x'], cap['y']
        for item in cap['words']:   # [(word, t_on, color)]  -> line-wrapped
            pass
        line_h = f.size * cap.get('lead', 1.12); maxw = cap.get('maxw', W - 2 * x); lx, ly = 0, 0; pos = []
        for (w, ton, col) in cap['words']:
            ww = dr.textlength(w + ' ', font=f)
            if lx > 0 and lx + dr.textlength(w, font=f) > maxw: lx, ly = 0, ly + line_h
            pos.append((w, ton, col, lx, ly)); lx += ww
        lines = {}
        for p_ in pos: lines[p_[4]] = max(lines.get(p_[4], 0), p_[3] + dr.textlength(p_[0], font=f))
        for (w, ton, col, wx, wy) in pos:
            kk = min(1, max(0, (t - ton + 0.06) / 0.28));
            if kk <= 0: continue
            kk = 1 - (1 - kk) ** 3; off = (1 - kk) * f.size * 0.6
            bx = x + wx if cap.get('align') != 'center' else (W - lines[wy]) / 2 + wx
            a = int(255 * kk * cap.get('alpha', 1))
            if cap.get('shadow', True): dr.text((bx + 3, y + wy + off + 4), w, font=f, fill=(0, 0, 0, int(a * 0.55)))
            dr.text((bx, y + wy + off), w, font=f, fill=tuple(col[:3]) + (a,))
    for el in spec.get('overlay_fn', lambda t, dr, fonts: None)(t, dr, fonts) or []: pass
    return np.asarray(lay, np.float32) / 255.0

def render(spec, out):
    fonts = {k: ImageFont.truetype(v[0], v[1]) for k, v in spec['fonts'].items()}
    for sh in spec['shots']:
        if sh.get('img'):
            im = cv2.cvtColor(cv2.imread(sh['img']), cv2.COLOR_BGR2RGB); sh['_img'] = im.astype(np.float32)
            sh['_dep'] = depth_of(sh['img']).astype(np.float32)
            if sh['_dep'].shape != im.shape[:2]: sh['_dep'] = cv2.resize(sh['_dep'], (im.shape[1], im.shape[0]))
    dur = spec['duration']; n = int(dur * FPS); xf = spec.get('xfade', 0.45)
    ff = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', spec['audio'], '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                           '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(7)
    grain = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(12)]
    stills = [float(s) for s in os.environ.get('STILLS', '').split(',') if s]
    frames = [int(s * FPS) for s in stills] if stills else range(n)
    if stills: ff.stdin.close(); ff.kill(); outs = []
    for fi in frames:
        t = fi / FPS; acc = None
        for sh in spec['shots']:
            t0, t1 = sh['t'][0], sh['t'][1]
            if t < t0 - xf / 2 or t > t1 + xf / 2: continue
            k = min(1, max(0, (t - (t0 - xf / 2)) / ((t1 + xf / 2) - (t0 - xf / 2))))
            fr = shot_frame(sh, k, t) / 255.0 if sh.get('img') else np.zeros((H, W, 3), np.float32) + np.array(sh.get('color', [0.04, 0.04, 0.05]), np.float32)
            if sh.get('fx'): fr = sh['fx'](fr, t, k)
            a = min(1, max(0, (t - (t0 - xf / 2)) / xf)) if t0 > 0 else 1
            acc = fr if acc is None else acc * (1 - a) + fr * a
        x = grade((np.clip(acc, 0, 1) * 255).astype(np.uint8), spec['grade'])
        x = x + leak(t, spec['grade'].get('leak_color', [1.0, 0.6, 0.25]), spec['grade'].get('leak', 0.10))
        x = x * _VIG
        g = cv2.resize(grain[fi % 12], (W, H))[..., None]; x = x + g * spec['grade'].get('grain', 0.025)
        tl = text_layer(spec, t, fonts); x = x * (1 - tl[..., 3:]) + tl[..., :3] * tl[..., 3:]
        if spec.get('post'): x = spec['post'](x, t, fonts)
        fr8 = (np.clip(x, 0, 1) * 255).astype(np.uint8)
        if stills: outs.append(cv2.resize(fr8, (W // 3, H // 3))); continue
        ff.stdin.write(fr8.tobytes())
        if fi % 150 == 0: print(f'{fi}/{n}', flush=True)
    if stills: cv2.imwrite(out, cv2.cvtColor(np.hstack(outs), cv2.COLOR_RGB2BGR)); print('stills ->', out); return
    ff.stdin.close(); ff.wait(); print('->', out)

if __name__ == '__main__':
    sp = importlib.util.spec_from_file_location('spec', sys.argv[1]); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    render(m.SPEC, sys.argv[2])
