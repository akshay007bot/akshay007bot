# MR Communications: cinematic 2.5-D reel from the site's real product photos. Render: python tools/cine.py brand-reels/cine/mrcomm.py out.mp4
import json, math, numpy as np, cv2
R = 'brand-reels/mrcomm-reel/'
VO = {v['bar']: v for v in json.load(open(R + 'vo.json'))}
WHITE, AMBER, MUTED = (248, 248, 248), (252, 159, 48), (150, 154, 160)
HI = {'you', 'twenty', 'years.', 'Two-way', 'radios.', 'Push', 'nationwide.', 'Encrypted', 'cameras.', 'press', 'talk.', 'thousand', 'signal', 'follows.', 'support.', 'team', 'communicates.'}
YY, XX = np.mgrid[0:1920, 0:1080].astype(np.float32)
IMG = R + 'assets/img/'
LABEL = {2: 'CH 01 · TWO-WAY RADIOS', 3: 'CH 02 · PUSH-TO-TALK · 4G/5G', 4: 'CH 03 · BODY CAMERAS · AES-256', 5: 'CH 04 · LICENSE-FREE', 6: '1000+ DEVICES DEPLOYED', 7: 'SECURITY · EVENTS · CONSTRUCTION', 8: 'SALES · RENTAL · PROGRAMMING · AMC'}

def vo_words(bar): return [(w['w'], w['t'], AMBER if w['w'] in HI else WHITE) for w in VO[bar]['words']]
def captions(t):
    bar = min(9, int(t // 3)); out = []
    if bar != 9: out.append({'font': 'disp', 'x': 80, 'y': 230, 'words': vo_words(bar), 'maxw': 920})
    if bar in LABEL: out.append({'font': 'mono', 'x': 84, 'y': 1660, 'words': [(LABEL[bar], bar * 3 + 0.35, AMBER)]})
    if bar == 1: out.append({'font': 'mono', 'x': 84, 'y': 1660, 'words': [('20 YEARS · SINCE 2006', 3.4, AMBER)]})
    if bar == 9:
        out += [{'font': 'disp', 'x': 80, 'y': 740, 'align': 'center', 'words': vo_words(9)},
                {'font': 'disp2', 'x': 80, 'y': 1092, 'align': 'center', 'words': [('+91 98450 47487', 27.9, AMBER)]},
                {'font': 'mono', 'x': 80, 'y': 1260, 'align': 'center', 'words': [('MRCOMMUNICATIONS.ORG', 28.3, WHITE)]}]
    return out

def static_burst(fr, t, k):            # radio static at the open and on each channel change
    bar_t = t % 3; a = max(0.0, 1 - bar_t / 0.18) if 6 <= t < 18 else (max(0.0, 1 - t / 1.0) if t < 3 else 0)
    if a <= 0: return fr
    rng = np.random.default_rng(int(t * 30)); n = rng.random((480, 270)).astype(np.float32)
    n = cv2.resize(n, (1080, 1920), interpolation=cv2.INTER_NEAREST)[..., None]
    return fr * (1 - a * 0.8) + n * a * 0.6
def rec_dot(fr, t, k):
    fr = static_burst(fr, t, k)
    if int(t * 2.5) % 2 == 0: m = ((XX - 960) ** 2 + (YY - 420) ** 2 < 18 ** 2)[..., None]; fr = np.where(m, np.array([1.0, 0.2, 0.15]), fr)
    return fr
LOGO = cv2.cvtColor(cv2.imread(IMG + 'logo-DCbxs-Mr.png', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)[170:600, 170:710].astype(np.float32) / 255.0
LOGO = cv2.resize(LOGO, (380, int(380 * LOGO.shape[0] / LOGO.shape[1])))
def post(x, t, fonts):
    a = np.clip(1 - YY / 860, 0, 1)[..., None] ** 1.1 * 0.93; x = x * (1 - a) + a * 0.01
    b = np.clip((YY - 1450) / 470, 0, 1)[..., None] * 0.75; x = x * (1 - b) + b * 0.01
    x = x * (1 - 0.06 * ((YY.astype(np.int32) // 2) % 2 == 0)[..., None])        # faint scan lines
    if t > 26.7:
        k = min(1, (t - 26.7) / 0.5); h, w = LOGO.shape[:2]; y0, x0 = 330, (1080 - w) // 2
        x[y0:y0 + h, x0:x0 + w] = x[y0:y0 + h, x0:x0 + w] * (1 - LOGO[..., 3:] * k) + LOGO[..., :3] * LOGO[..., 3:] * k
    if t > 27.7:   # amber frame around the phone number (text stays on top)
        kb = min(1, (t - 27.7) / 0.35); w2 = int(340 * kb)
        for yy in (1060, 1061, 1062, 1186, 1187, 1188): x[yy, 540 - w2:540 + w2] = [0.99, 0.62, 0.19]
    return x

SPEC = {
    'duration': 30, 'audio': 'brand-reels/cine/mrcomm_audio.wav', 'xfade': 0.35,
    'fonts': {'disp': (R + 'fonts/display.ttf', 84), 'disp2': (R + 'fonts/display.ttf', 60), 'mono': (R + 'fonts/ui.ttf', 26)},
    'grade': {'contrast': 1.18, 'shadow': [-0.01, 0.02, 0.06], 'high': [0.08, 0.04, -0.03], 'sat': 1.0, 'bloom': 0.9, 'leak': 0.10, 'leak_color': [1.0, 0.55, 0.15], 'grain': 0.035},
    'captions_fn': captions, 'post': post,
    'shots': [
        {'t': (0, 3), 'img': IMG + 'hero-radio.jpg', 'c0': (0.62, 0.45), 'c1': (0.6, 0.5), 'z0': 1.6, 'z1': 1.3, 'par': (0.8, 0.3), 'dolly': 0.8, 'fx': static_burst},
        {'t': (3, 6), 'img': IMG + 'hero-radio.jpg', 'c0': (0.55, 0.55), 'c1': (0.6, 0.5), 'z0': 1.1, 'z1': 1.2, 'par': (1.2, 0.3), 'dolly': 0.6},
        {'t': (6, 9), 'img': IMG + 'product-dmr.jpg', 'c0': (0.5, 0.5), 'c1': (0.5, 0.48), 'z0': 1.1, 'z1': 1.3, 'par': (0.8, 0.4), 'dolly': 1.0, 'fx': static_burst},
        {'t': (9, 12), 'img': IMG + 'product-poc.jpg', 'c0': (0.48, 0.55), 'c1': (0.52, 0.45), 'z0': 1.15, 'z1': 1.35, 'par': (0.8, 0.6), 'dolly': 1.0, 'fx': static_burst},
        {'t': (12, 15), 'img': IMG + 'product-bodycam.jpg', 'c0': (0.55, 0.5), 'c1': (0.5, 0.5), 'z0': 1.2, 'z1': 1.45, 'par': (1.0, 0.3), 'dolly': 1.0, 'fx': rec_dot},
        {'t': (15, 18), 'img': IMG + 'product-license.jpg', 'c0': (0.45, 0.5), 'c1': (0.55, 0.5), 'z0': 1.15, 'z1': 1.25, 'par': (1.4, 0.2), 'dolly': 0.6, 'fx': static_burst},
        {'t': (18, 21), 'img': IMG + 'hero-radio.jpg', 'c0': (0.7, 0.6), 'c1': (0.62, 0.4), 'z0': 1.8, 'z1': 1.5, 'par': (0.6, 1.0), 'dolly': 0.8},
        {'t': (21, 24), 'img': IMG + 'product-poc.jpg', 'c0': (0.5, 0.3), 'c1': (0.5, 0.6), 'z0': 1.6, 'z1': 1.4, 'par': (0.4, 1.2), 'dolly': 0.6},
        {'t': (24, 27), 'img': IMG + 'product-dmr.jpg', 'c0': (0.5, 0.65), 'c1': (0.5, 0.4), 'z0': 1.7, 'z1': 1.5, 'par': (0.6, 1.0), 'dolly': 0.6},
        {'t': (27, 30), 'img': IMG + 'hero-radio.jpg', 'c0': (0.6, 0.5), 'c1': (0.62, 0.5), 'z0': 1.2, 'z1': 1.25, 'par': (0.3, 0.1), 'fx': lambda fr, t, k: fr * 0.2},
    ],
}
