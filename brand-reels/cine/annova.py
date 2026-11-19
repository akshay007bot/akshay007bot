# ANNOVA 360: cinematic 2.5-D reel from the studio's real photos. Render: python tools/cine.py brand-reels/cine/annova.py out.mp4
import json, numpy as np, cv2
R = 'brand-reels/annova-reel/'
VO = {v['bar']: v for v in json.load(open(R + 'vo.json'))}
CREAM, GOLD, MUTED = (243, 241, 238), (206, 163, 89), (175, 178, 184)
HI = {'sketch.', 'approve...', 'get.', 'handoffs.', 'budget.', 'Whitefield.', 'commercial', 'finish.', 'key.', 'consultation.'}
BP = cv2.cvtColor(cv2.imread(R + 'assets/img/blueprint.png', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA).astype(np.float32) / 255.0
YY, XX = np.mgrid[0:1920, 0:1080].astype(np.float32)

def vo_words(bar): return [(w['w'], w['t'], GOLD if w['w'] in HI else CREAM) for w in VO[bar]['words']]
def blueprint_draw(fr, t, k):          # gold line drawing revealed in a sweeping diagonal
    reveal = np.clip(((t + 0.9) * 1.25 - (XX / 1080 * 0.6 + YY / 1920 * 0.9)) * 3, 0, 1)[..., None]
    base = np.zeros_like(fr) + np.array([0.05, 0.05, 0.05], np.float32)
    grid = ((XX % 60 < 1.2) | (YY % 60 < 1.2)).astype(np.float32)[..., None] * 0.04
    return base + grid * np.array([0.8, 0.64, 0.35]) + BP[..., :3] * BP[..., 3:] * reveal * 1.4
def blueprint_fade(fr, t, k):          # first moments of the real villa: lines dissolve away
    a = max(0.0, 1 - (t - 3.0) / 1.6)
    return fr * (0.35 + 0.65 * (1 - a)) + BP[..., :3] * BP[..., 3:] * a * 1.2

def captions(t):
    bar = min(9, int(t // 3)); out = []
    if bar in VO and bar != 9:
        out.append({'font': 'disp', 'x': 80, 'y': 230, 'words': vo_words(bar), 'maxw': 920})
    lab = {5: ('LUXURY APARTMENTS', 'Ankuraa Lotus', 'Whitefield · 2022'), 6: ('COMMERCIAL', 'Venus Communiti', 'Co-Work, Co-Live & Café · Bengaluru'),
           7: ('RESIDENTIAL', 'Family Residence', 'Contemporary · Bengaluru')}.get(bar)
    if lab:
        t0 = bar * 3 + 0.5
        out += [{'font': 'ui', 'x': 80, 'y': 1500, 'words': [(lab[0], t0, GOLD)]}, {'font': 'disp2', 'x': 80, 'y': 1545, 'words': [(lab[1], t0 + 0.15, CREAM)]},
                {'font': 'ui', 'x': 80, 'y': 1640, 'words': [(lab[2], t0 + 0.3, MUTED)]}]
    if bar == 9:
        out += [{'font': 'disp', 'x': 80, 'y': 820, 'align': 'center', 'words': vo_words(9)},
                {'font': 'ui', 'x': 80, 'y': 1090, 'align': 'center', 'words': [('BOOK  A  CONSULTATION', 28.0, GOLD)]},
                {'font': 'disp2', 'x': 80, 'y': 1230, 'align': 'center', 'words': [('+91 88610 35808', 28.3, CREAM)]},
                {'font': 'ui', 'x': 80, 'y': 1330, 'align': 'center', 'words': [('ANNOVA360.COM  ·  EST. 2014', 28.5, MUTED)]}]
    return out

LOGO = cv2.cvtColor(cv2.imread(R + 'assets/img/annova-logo.png', cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGBA)[140:771, 366:1208].astype(np.float32) / 255.0
LOGO = cv2.resize(LOGO, (560, int(560 * LOGO.shape[0] / LOGO.shape[1])))
def post(x, t, fonts):
    # gold gradient legibility band behind top captions
    a = np.clip(1 - YY / 860, 0, 1)[..., None] ** 1.1 * 0.93
    x = x * (1 - a) + a * 0.02
    if t > 26.6:
        k = min(1, (t - 26.6) / 0.6); h, w = LOGO.shape[:2]; y0, x0 = 330, (1080 - w) // 2
        x[y0:y0 + h, x0:x0 + w] = x[y0:y0 + h, x0:x0 + w] * (1 - LOGO[..., 3:] * k) + LOGO[..., :3] * LOGO[..., 3:] * k
        if t > 27.9:   # thin gold rules framing the call to action
            kb = min(1, (t - 27.9) / 0.4); w2 = int(240 * kb); x[1050:1052, 540 - w2:540 + w2] = [0.81, 0.64, 0.35]; x[1152:1154, 540 - w2:540 + w2] = [0.81, 0.64, 0.35]
    # gentle lower shade for project captions
    b = np.clip((YY - 1300) / 620, 0, 1)[..., None] * 0.7; return x * (1 - b) + b * 0.02

SPEC = {
    'duration': 30, 'audio': 'brand-reels/cine/annova_audio.wav', 'xfade': 0.5,
    'fonts': {'disp': (R + 'fonts/display.ttf', 96), 'disp2': (R + 'fonts/display.ttf', 74), 'ui': (R + 'fonts/ui.ttf', 26)},
    'grade': {'contrast': 1.12, 'shadow': [-0.01, 0.02, 0.05], 'high': [0.07, 0.04, -0.03], 'sat': 0.92, 'bloom': 0.8, 'leak': 0.09, 'leak_color': [1.0, 0.65, 0.3], 'grain': 0.03},
    'captions_fn': captions, 'post': post,
    'shots': [
        {'t': (0, 3), 'img': None, 'fx': blueprint_draw},
        {'t': (3, 6), 'img': R + 'assets/img/villa_9x16.jpg', 'c0': (0.5, 0.5), 'c1': (0.52, 0.52), 'z0': 1.0, 'z1': 1.08, 'par': (0.6, 0.2), 'dolly': 0.8, 'fx': blueprint_fade},
        {'t': (6, 9), 'img': R + 'assets/img/hero-villa.jpg', 'c0': (0.42, 0.5), 'c1': (0.6, 0.48), 'z0': 1.05, 'z1': 1.12, 'par': (1.4, 0.2), 'dolly': 0.5},
        {'t': (9, 12), 'img': R + 'assets/img/hero-villa.jpg', 'c0': (0.55, 0.52), 'c1': (0.58, 0.55), 'z0': 1.7, 'z1': 2.1, 'par': (0.8, 0.3), 'dolly': 1.0},
        {'t': (12, 15), 'img': R + 'assets/img/hero-villa.jpg', 'c0': (0.5, 0.85), 'c1': (0.5, 0.45), 'z0': 1.3, 'z1': 1.25, 'par': (0.3, 1.2), 'dolly': 0.4},
        {'t': (15, 18), 'img': R + 'assets/img/proj-ankuraa-lotus-exterior.jpg', 'c0': (0.55, 0.7), 'c1': (0.58, 0.35), 'z0': 1.05, 'z1': 1.12, 'par': (0.8, 1.4), 'dolly': 0.6},
        {'t': (18, 21), 'img': R + 'assets/img/proj-venus-exterior.jpg', 'c0': (0.5, 0.6), 'c1': (0.5, 0.45), 'z0': 1.0, 'z1': 1.15, 'par': (0.6, 0.6), 'dolly': 1.0},
        {'t': (21, 24), 'img': R + 'assets/img/proj-residence-living.jpg', 'c0': (0.42, 0.5), 'c1': (0.55, 0.5), 'z0': 1.05, 'z1': 1.18, 'par': (1.2, 0.2), 'dolly': 0.8},
        {'t': (24, 27), 'img': R + 'assets/img/hero-villa.jpg', 'c0': (0.55, 0.5), 'c1': (0.5, 0.5), 'z0': 1.35, 'z1': 1.0, 'par': (0.8, 0.3), 'dolly': -0.6},
        {'t': (27, 30), 'img': R + 'assets/img/hero-villa.jpg', 'c0': (0.5, 0.5), 'c1': (0.52, 0.5), 'z0': 1.0, 'z1': 1.05, 'par': (0.3, 0.1), 'fx': lambda fr, t, k: fr * 0.22},
    ],
}
