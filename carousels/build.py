"""Builds 4 branded Instagram carousels (1080x1350) as HTML; render.js screenshots them to PNG."""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))
A = 'assets/'
FONTS = """
@font-face{font-family:Corm;src:url(assets/fonts/cormorant-garamond-latin-500-normal.woff2);font-weight:500}
@font-face{font-family:Corm;src:url(assets/fonts/cormorant-garamond-latin-600-normal.woff2);font-weight:600}
@font-face{font-family:Corm;src:url(assets/fonts/cormorant-garamond-latin-500-italic.woff2);font-weight:500;font-style:italic}
@font-face{font-family:Geist;src:url(assets/fonts/geist-sans-latin-400-normal.woff2);font-weight:400}
@font-face{font-family:Geist;src:url(assets/fonts/geist-sans-latin-600-normal.woff2);font-weight:600}
@font-face{font-family:Geist;src:url(assets/fonts/geist-sans-latin-800-normal.woff2);font-weight:800}
@font-face{font-family:Play;src:url(assets/fonts/playfair-display-latin-600-normal.woff2);font-weight:600}
@font-face{font-family:Play;src:url(assets/fonts/playfair-display-latin-700-normal.woff2);font-weight:700}
@font-face{font-family:Play;src:url(assets/fonts/playfair-display-latin-600-italic.woff2);font-weight:600;font-style:italic}
@font-face{font-family:Comf;src:url(assets/fonts/comfortaa-latin-500-normal.woff2);font-weight:500}
@font-face{font-family:Comf;src:url(assets/fonts/comfortaa-latin-700-normal.woff2);font-weight:700}
@font-face{font-family:Int;src:url(assets/fonts/inter-latin-400-normal.woff2);font-weight:400}
@font-face{font-family:Int;src:url(assets/fonts/inter-latin-600-normal.woff2);font-weight:600}
@font-face{font-family:Int;src:url(assets/fonts/inter-latin-800-normal.woff2);font-weight:800}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
.s{position:relative;width:1080px;height:1350px;overflow:hidden}
.abs{position:absolute}
"""

def page(css, body):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{FONTS}{css}</style></head><body><div class='s'>{body}</div></body></html>"

# ---------------------------------------------------------------- iOceane
IOC_CSS = """
.s{background:#070d1c;color:#fff;font-family:Int}
.glow{position:absolute;inset:0;background:radial-gradient(700px 520px at 85% 8%,rgba(60,131,246,.38),transparent 70%),radial-gradient(640px 520px at 0% 100%,rgba(20,184,166,.28),transparent 70%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:54px 54px;mask-image:radial-gradient(circle at 50% 40%,#000 30%,transparent 80%)}
.logo{position:absolute;left:76px;top:60px;height:84px}
.pg{position:absolute;right:80px;top:88px;font:600 24px Int;color:#8fa0bf;letter-spacing:3px}
.g{background:linear-gradient(90deg,#3c83f6,#14b8a6);-webkit-background-clip:text;color:transparent}
.h{font-family:Comf;font-weight:700;line-height:1.08;letter-spacing:-1px}
.tag{display:inline-flex;align-items:center;gap:14px;padding:14px 26px;border:1px solid rgba(255,255,255,.18);border-radius:99px;background:rgba(255,255,255,.05);font:600 24px Int;color:#cfe0ff;letter-spacing:2px}
.tag i{width:12px;height:12px;border-radius:6px;background:linear-gradient(90deg,#3c83f6,#14b8a6)}
.p{font:400 34px/1.5 Int;color:#b6c2d9}
.swipe{position:absolute;left:80px;bottom:76px;font:600 26px Int;color:#8fa0bf;letter-spacing:3px}
.swipe b{color:#14b8a6}
.bar{position:absolute;left:0;right:0;bottom:0;height:10px;background:linear-gradient(90deg,#3c83f6,#14b8a6)}
.card{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:30px}
"""
def ioc(n, tot, inner, swipe=True):
    sw = "<div class='swipe'>SWIPE <b>→</b></div>" if swipe else ""
    return page(IOC_CSS, f"<div class='glow'></div><div class='grid'></div><img class='logo' src='{A}ioc_logo-white.png'><div class='pg'>{n:02d} / {tot:02d}</div>{inner}{sw}<div class='bar'></div>")

def ioc_slides():
    T = 6; S = []
    S.append(ioc(1, T, """
      <div class='abs' style='left:80px;top:250px;right:80px'>
        <div class='tag'><i></i>SEO &amp; AI SEARCH</div>
        <div class='h' style='font-size:104px;margin-top:46px'>Your customers stopped Googling.</div>
        <div class='h g' style='font-size:104px;margin-top:20px'>They're asking ChatGPT.</div>
        <div class='p' style='margin-top:48px;font-size:38px'>Is your brand in the answer?</div>
      </div>
      <div class='abs card' style='left:80px;right:80px;bottom:170px;padding:30px 38px;display:flex;gap:22px;align-items:center'>
        <div style='width:58px;height:58px;border-radius:29px;background:linear-gradient(135deg,#3c83f6,#14b8a6);flex:none'></div>
        <div style='font:400 30px Int;color:#dbe6ff'>“Best digital marketing agency in Bangalore?”<span style='color:#14b8a6'> ▍</span></div>
      </div>"""))
    S.append(ioc(2, T, """
      <div class='abs' style='left:80px;top:230px;right:80px'>
        <div class='h' style='font-size:84px'>Search has <span class='g'>changed.</span></div>
        <div class='p' style='margin-top:30px'>People still search. But now they also ask AI assistants for answers and recommendations.</div>
      </div>
      <div class='abs' style='left:80px;right:80px;top:700px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:26px'>
        <div class='card' style='padding:44px 30px;text-align:center'><div class='h' style='font-size:52px'>Google</div><div class='p' style='font-size:26px;margin-top:12px'>Search results</div></div>
        <div class='card' style='padding:44px 30px;text-align:center;border-color:rgba(20,184,166,.6)'><div class='h g' style='font-size:52px'>ChatGPT</div><div class='p' style='font-size:26px;margin-top:12px'>AI answers</div></div>
        <div class='card' style='padding:44px 30px;text-align:center'><div class='h' style='font-size:52px'>Gemini</div><div class='p' style='font-size:26px;margin-top:12px'>AI overviews</div></div>
      </div>
      <div class='abs p' style='left:80px;right:80px;top:1010px;font-size:32px'>Your brand needs to show up <b style='color:#fff'>everywhere</b> they look.</div>"""))
    S.append(ioc(3, T, """
      <div class='abs' style='left:80px;right:80px;top:330px;text-align:left'>
        <div class='h' style='font-size:124px;line-height:1.02'>If AI doesn't <span class='g'>know</span> you,</div>
        <div class='h' style='font-size:124px;line-height:1.02;margin-top:30px;color:#8fa0bf'>it can't <span style='color:#fff'>recommend</span> you.</div>
      </div>
      <div class='abs' style='left:80px;top:1010px;width:140px;height:6px;background:linear-gradient(90deg,#3c83f6,#14b8a6)'></div>"""))
    S.append(ioc(4, T, """
      <div class='abs' style='left:80px;top:230px;right:80px'>
        <div class='tag'><i></i>HOW iOCEANE HELPS</div>
        <div class='h' style='font-size:80px;margin-top:36px'>Get found on Google <span class='g'>and</span> in AI answers.</div>
      </div>
      <div class='abs' style='left:80px;right:80px;top:640px;display:flex;flex-direction:column;gap:24px'>
        <div class='card' style='padding:34px 40px;display:flex;gap:30px;align-items:center'><div class='h g' style='font-size:58px;width:90px'>01</div><div><div style='font:800 34px Int'>On-page SEO</div><div class='p' style='font-size:27px'>Pages structured to rank higher</div></div></div>
        <div class='card' style='padding:34px 40px;display:flex;gap:30px;align-items:center'><div class='h g' style='font-size:58px;width:90px'>02</div><div><div style='font:800 34px Int'>AI-ready content</div><div class='p' style='font-size:27px'>Clear answers AI assistants can understand</div></div></div>
        <div class='card' style='padding:34px 40px;display:flex;gap:30px;align-items:center'><div class='h g' style='font-size:58px;width:90px'>03</div><div><div style='font:800 34px Int'>Brand authority</div><div class='p' style='font-size:27px'>Signals that build trust with search &amp; AI</div></div></div>
      </div>"""))
    S.append(ioc(5, T, """
      <div class='abs' style='left:80px;top:230px;right:80px'>
        <div class='tag'><i></i>REAL METRICS · REAL CLIENTS</div>
        <div class='h' style='font-size:80px;margin-top:36px'>Results that <span class='g'>speak.</span></div>
      </div>
      <div class='abs' style='left:80px;right:80px;top:560px;display:flex;flex-direction:column;gap:26px'>
        <div class='card' style='padding:40px 46px;display:flex;justify-content:space-between;align-items:center'><div class='p' style='font-size:34px'>Impressions</div><div class='h g' style='font-size:110px'>954K+</div></div>
        <div class='card' style='padding:40px 46px;display:flex;justify-content:space-between;align-items:center'><div class='p' style='font-size:34px'>Clicks delivered</div><div class='h' style='font-size:110px'>10.6K</div></div>
        <div class='card' style='padding:40px 46px;display:flex;justify-content:space-between;align-items:center;border-color:rgba(20,184,166,.6)'><div class='p' style='font-size:34px'>Organic growth</div><div class='h g' style='font-size:110px'>78%</div></div>
      </div>"""))
    S.append(ioc(6, T, """
      <div class='abs' style='left:80px;right:80px;top:300px;text-align:center'>
        <div class='h' style='font-size:96px'>Rank higher.</div>
        <div class='h' style='font-size:96px;margin-top:10px'>Get found.</div>
        <div class='h g' style='font-size:96px;margin-top:10px'>Grow faster.</div>
        <div class='p' style='margin-top:44px'>150+ projects · 15+ years · 98% client satisfaction</div>
        <div style='display:inline-block;margin-top:70px;padding:34px 64px;border-radius:99px;background:linear-gradient(90deg,#3c83f6,#14b8a6);font:800 38px Int;box-shadow:0 20px 60px rgba(20,184,166,.35)'>Book a free strategy call →</div>
        <div style='margin-top:56px;font:600 34px Int;color:#dbe6ff;letter-spacing:2px'>ioceane.com &nbsp;·&nbsp; +91 90199 31101</div>
      </div>""", swipe=False))
    return S

# ---------------------------------------------------------------- VedRxTours
VED_CSS = """
.s{background:#f6f3ec;color:#0f1729;font-family:Int}
.logo{position:absolute;left:80px;top:70px;height:66px}
.pg{position:absolute;right:80px;top:92px;font:600 24px Int;color:#128271;letter-spacing:3px}
.h{font-family:Play;font-weight:700;line-height:1.08}
.it{font-family:Play;font-style:italic;font-weight:600;color:#128271}
.k{font:600 24px Int;letter-spacing:5px;color:#128271}
.p{font:400 33px/1.55 Int;color:#475569}
.ph{position:absolute;overflow:hidden;border-radius:40px}
.ph img{width:100%;height:100%;object-fit:cover}
.swipe{position:absolute;right:80px;bottom:70px;font:600 26px Int;color:#128271;letter-spacing:3px}
.step{position:absolute;left:80px;top:250px;font-family:Play;font-weight:700;font-size:300px;line-height:.8;color:transparent;-webkit-text-stroke:3px #128271;opacity:.9}
.leaf{position:absolute;border-radius:0 100% 0 100%;background:#128271}
"""
def ved(n, tot, inner, swipe=True, dark=False):
    sw = "<div class='swipe'>SWIPE →</div>" if swipe else ""
    logo = 'ved_logo-light.png' if dark else 'ved_logo.png'
    st = "<style>.s{background:#0f1729;color:#fff}.p{color:#cbd5e1}.pg,.swipe{color:#5eead4}</style>" if dark else ""
    return page(VED_CSS, f"{st}{inner}<img class='logo' src='{A}{logo}'><div class='pg'>{n:02d} / {tot:02d}</div>{sw}")

def ved_steps(n, tot, num, title, text, bullets):
    lis = ''.join(f"<div style='display:flex;gap:20px;align-items:center;margin-top:22px'><div style='width:44px;height:44px;border-radius:22px;background:#128271;color:#fff;font:800 24px Int;display:flex;align-items:center;justify-content:center'>✓</div><div style='font:600 32px Int'>{b}</div></div>" for b in bullets)
    return ved(n, tot, f"""
      <div class='step'>{num}</div>
      <div class='abs' style='left:80px;right:80px;top:560px'>
        <div class='k'>STEP {num}</div>
        <div class='h' style='font-size:84px;margin-top:20px'>{title}</div>
        <div class='p' style='margin-top:26px'>{text}</div>
        <div style='margin-top:30px'>{lis}</div>
      </div>
      <div class='abs' style='left:80px;right:80px;bottom:140px;height:8px;border-radius:4px;background:#e2ddd0'><div style='width:{int(num)*25}%;height:100%;border-radius:4px;background:#128271'></div></div>""")

def ved_slides():
    T = 7; S = []
    S.append(ved(1, T, f"""
      <div class='ph' style='left:0;top:0;right:0;height:760px;border-radius:0 0 60px 60px'><img src='{A}ved_taj.jpg' style='object-position:50% 40%'></div>
      <div class='abs' style='left:0;right:0;top:0;height:260px;background:linear-gradient(#0f1729cc,transparent)'></div>
      <div class='abs' style='left:80px;right:80px;top:810px'>
        <div class='k'>MEDICAL CARE IN INDIA</div>
        <div class='h' style='font-size:90px;margin-top:18px'>Treatment in India, <span class='it'>without the stress.</span></div>
        <div class='p' style='margin-top:22px'>Here's how it works, in 4 simple steps.</div>
      </div>""", dark=False).replace(f"src='{A}ved_logo.png'", f"src='{A}ved_logo-light.png'").replace("<div class='pg'>", "<div class='pg' style='color:#fff'>"))
    S.append(ved_steps(2, T, '01', 'Tell us what you need', 'Share your medical needs and what matters to you.', ['Your reports & condition', 'Your preferences & budget']))
    S.append(ved_steps(3, T, '02', 'Explore your options', 'Discuss suitable hospitals and an individual care plan.', ['Leading hospitals across India', 'A plan built around you']))
    S.append(ved_steps(4, T, '03', 'Plan with confidence', 'Coordinate your documents, travel and accommodation.', ['Visa & travel guidance', 'Stay arranged near care']))
    S.append(ved_steps(5, T, '04', 'Care beyond arrival', 'Stay connected during treatment and follow-up.', ['A dedicated care coordinator', 'Follow-up after you fly home']))
    tr = ['Heart care', 'Bone &amp; joint', 'Cancer care', 'Brain &amp; spine', 'Fertility &amp; IVF', 'Dental care', 'Organ transplants', 'Cosmetic surgery']
    chips = ''.join(f"<div style='padding:26px 30px;border-radius:24px;background:#fff;border:2px solid #e7e1d3;font:600 32px Int;display:flex;gap:16px;align-items:center'><span style='width:14px;height:14px;border-radius:7px;background:#128271;flex:none'></span>{t}</div>" for t in tr)
    S.append(ved(6, T, f"""
      <div class='abs' style='left:80px;right:80px;top:240px'>
        <div class='k'>FIND YOUR PATH TO BETTER HEALTH</div>
        <div class='h' style='font-size:84px;margin-top:20px'>Care for what <span class='it'>matters to you.</span></div>
      </div>
      <div class='abs' style='left:80px;right:80px;top:590px;display:grid;grid-template-columns:1fr 1fr;gap:22px'>{chips}</div>"""))
    S.append(ved(7, T, f"""
      <div class='ph' style='left:80px;right:80px;top:200px;height:520px'><img src='{A}ved_consultation.jpg' style='object-position:65% 50%'></div>
      <div class='abs' style='left:80px;right:80px;top:780px;text-align:center'>
        <div class='h' style='font-size:76px'>You focus on getting better.</div>
        <div class='h it' style='font-size:76px;margin-top:6px'>We'll help with the journey.</div>
        <div style='display:inline-block;margin-top:46px;padding:30px 58px;border-radius:99px;background:linear-gradient(90deg,#128271,#0ea5e9);color:#fff;font:800 36px Int'>Get your treatment estimate →</div>
        <div style='margin-top:36px;font:600 32px Int;color:#5eead4'>vedrxtours.in &nbsp;·&nbsp; +91 95356 99931</div>
      </div>""", swipe=False, dark=True))
    return S

# ---------------------------------------------------------------- MR Communications
MR_CSS = """
.s{background:#0b0b0c;color:#fafafa;font-family:Geist}
.logo{position:absolute;left:66px;top:46px;height:130px}
.pg{position:absolute;right:80px;top:96px;font:600 24px Geist;color:#8a8a8f;letter-spacing:4px}
.o{color:#F5A623}
.h{font:800 92px/1.02 Geist;letter-spacing:-3px}
.k{font:600 24px Geist;letter-spacing:6px;color:#F5A623}
.p{font:400 32px/1.5 Geist;color:#a1a1aa}
.ph{position:absolute;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover}
.line{position:absolute;left:80px;right:80px;height:1px;background:#2a2a2e}
.swipe{position:absolute;right:80px;bottom:70px;font:600 26px Geist;color:#F5A623;letter-spacing:4px}
.pill{display:inline-block;padding:12px 24px;border-radius:99px;border:1px solid #3a3a40;font:600 24px Geist;color:#e4e4e7;margin:0 12px 14px 0}
.big{position:absolute;right:50px;font:800 330px/1 Geist;color:transparent;-webkit-text-stroke:2px #2c2c30;letter-spacing:-10px}
"""
def mr(n, tot, inner, swipe=True):
    sw = "<div class='swipe'>SWIPE →</div>" if swipe else ""
    return page(MR_CSS, f"{inner}<img class='logo' src='{A}mrc_logo.png'><div class='pg'>{n:02d} / {tot:02d}</div>{sw}")

def mr_type(n, tot, num, kind, title, img, who, pts, note, pos='50% 50%'):
    pills = ''.join(f"<span class='pill'>{w}</span>" for w in who)
    li = ''.join(f"<div style='display:flex;gap:18px;margin-top:16px;font:400 31px Geist;color:#e4e4e7'><span class='o'>—</span>{x}</div>" for x in pts)
    return mr(n, tot, f"""
      <div class='ph' style='left:0;top:0;right:0;height:640px'><img src='{A}{img}' style='object-position:{pos}'></div>
      <div class='abs' style='left:0;right:0;top:380px;height:262px;background:linear-gradient(transparent,#0b0b0c)'></div>
      <div class='abs' style='left:0;right:0;top:0;height:220px;background:linear-gradient(#0b0b0cdd,transparent)'></div>
      <div class='big' style='top:520px'>{num}</div>
      <div class='abs' style='left:80px;right:80px;top:640px'>
        <div class='k'>TYPE {num} · {kind}</div>
        <div class='h' style='font-size:76px;margin-top:16px'>{title}</div>
        <div style='margin-top:26px'>{pills}</div>
        <div style='margin-top:8px'>{li}</div>
        <div style='margin-top:26px;font:600 26px Geist;color:#F5A623'>{note}</div>
      </div>""")

def mr_slides():
    T = 7; S = []
    S.append(mr(1, T, f"""
      <div class='ph' style='right:-260px;top:120px;width:820px;height:1230px'><img src='{A}mrc_hero-radio.jpg' style='object-position:30% 50%'></div>
      <div class='abs' style='left:0;top:0;width:900px;bottom:0;background:linear-gradient(90deg,#0b0b0c 62%,transparent)'></div>
      <div class='abs' style='left:80px;top:330px;width:660px'>
        <div class='k'>WALKIE-TALKIE BUYING GUIDE</div>
        <div class='h' style='margin-top:28px'><span class='o'>4</span> types of radios.</div>
        <div class='h' style='margin-top:12px;color:#a1a1aa'>Only <span style='color:#fafafa'>one</span> is right for you.</div>
        <div class='p' style='margin-top:40px;width:560px'>Swipe to find the one that fits your team.</div>
      </div>
      <div class='abs' style='left:80px;bottom:150px;width:120px;height:6px;background:#F5A623'></div>"""))
    S.append(mr_type(2, T, '01', 'LICENSE-FREE', 'No paperwork. Just press to talk.', 'mrc_product-license.jpg', ['Retail counters', 'Cafés', 'Small sites', 'Event crews'], ['Ready to use out of the box', 'Best for short-range teams'], 'NO LICENCE NEEDED', '50% 40%'))
    S.append(mr_type(3, T, '02', 'DMR DIGITAL', 'Crystal-clear, secure, built tough.', 'mrc_hero-radio.jpg', ['Security', 'Hotels', 'Factories', 'Construction'], ['Clear digital audio & encryption', 'GPS, IP-rated, MIL-STD tested'], 'REQUIRES A WPC LICENCE', '35% 40%'))
    S.append(mr_type(4, T, '03', 'PoC 4G/5G', 'Push-to-talk. Nationwide by design.', 'mrc_product-poc.jpg', ['Fleets', 'Logistics', 'Multi-city teams'], ['Works over the mobile network', 'AI noise cancellation'], 'RANGE BEYOND RADIO', '50% 35%'))
    S.append(mr_type(5, T, '04', 'BODY-WORN CAMERAS', 'Evidence-grade capture. Encrypted, always.', 'mrc_product-bodycam.jpg', ['Security', 'Enforcement', 'Patrols'], ['AES-256 encryption, IP68 rated', '4G/5G live streaming'], 'VIDEO YOU CAN RELY ON', '50% 50%'))
    S.append(mr(6, T, """
      <div class='abs' style='left:80px;right:80px;top:300px'>
        <div class='k'>STILL UNSURE?</div>
        <div class='h' style='margin-top:26px'>Tell us two things.</div>
        <div class='h o' style='margin-top:6px'>We'll do the rest.</div>
      </div>
      <div class='abs' style='left:80px;right:80px;top:700px;display:grid;grid-template-columns:1fr 1fr;gap:26px'>
        <div style='border:1px solid #2e2e33;border-radius:28px;padding:44px 40px;background:#121214'><div style='font:800 90px Geist' class='o'>1</div><div style='font:600 40px Geist;margin-top:10px'>Your site size</div></div>
        <div style='border:1px solid #2e2e33;border-radius:28px;padding:44px 40px;background:#121214'><div style='font:800 90px Geist' class='o'>2</div><div style='font:600 40px Geist;margin-top:10px'>Your team size</div></div>
      </div>
      <div class='abs p' style='left:80px;right:80px;top:1060px;font-size:34px'>→ We recommend the right model in <b style='color:#fafafa'>one working day.</b></div>"""))
    S.append(mr(7, T, f"""
      <div class='ph' style='left:0;right:0;top:0;height:1350px;opacity:.35'><img src='{A}mrc_product-dmr.jpg'></div>
      <div class='abs' style='inset:0;background:radial-gradient(circle at 50% 45%,rgba(11,11,12,.55),#0b0b0c 75%)'></div>
      <div class='abs' style='left:80px;right:80px;top:330px;text-align:center'>
        <div class='k'>SINCE 2006</div>
        <div class='h' style='margin-top:26px;font-size:96px'>Need radios<br>for your team?</div>
        <div style='margin-top:40px'><span class='pill'>Sales</span><span class='pill'>Rental</span><span class='pill'>Programming</span><span class='pill'>AMC</span></div>
        <div style='display:inline-block;margin-top:50px;padding:32px 60px;border-radius:99px;background:#F5A623;color:#0b0b0c;font:800 40px Geist'>WhatsApp +91 98450 47487</div>
        <div style='margin-top:40px;font:600 30px Geist;color:#a1a1aa'>20+ years · 1000+ devices deployed · 100% genuine</div>
        <div style='margin-top:14px;font:600 30px Geist;color:#fafafa'>mrcommunications.org</div>
      </div>""", swipe=False))
    return S

# ---------------------------------------------------------------- ANNOVA 360
AN_CSS = """
.s{background:#0d0c0a;color:#f3efe6;font-family:Int}
.logo{position:absolute;left:50%;transform:translateX(-50%);top:46px;height:150px}
.pg{position:absolute;right:80px;top:96px;font:500 22px Int;color:#8c8270;letter-spacing:5px}
.gold{color:#C9A35B}
.h{font-family:Corm;font-weight:500;line-height:1.02}
.k{font:500 22px Int;letter-spacing:8px;color:#C9A35B}
.p{font:400 31px/1.6 Int;color:#b8b0a1}
.hair{position:absolute;height:1px;background:linear-gradient(90deg,transparent,#C9A35B,transparent)}
.num{font-family:Corm;font-weight:500;color:#C9A35B;line-height:.8}
.ph{position:absolute;overflow:hidden}
.ph img{width:100%;height:100%;object-fit:cover}
.swipe{position:absolute;left:50%;transform:translateX(-50%);bottom:64px;font:500 22px Int;color:#8c8270;letter-spacing:6px}
.frame{position:absolute;inset:36px;border:1px solid rgba(201,163,91,.35);pointer-events:none}
"""
def an(n, tot, inner, swipe=True):
    sw = "<div class='swipe'>SWIPE  →</div>" if swipe else ""
    return page(AN_CSS, f"{inner}<div class='frame'></div><img class='logo' src='{A}ann_annova-logo.png'><div class='pg'>{n:02d}/{tot:02d}</div>{sw}")

def an_commit(n, tot, num, title, text, img, pos='50% 50%'):
    return an(n, tot, f"""
      <div class='ph' style='left:36px;right:36px;bottom:36px;height:520px'><img src='{A}{img}' style='object-position:{pos}'></div>
      <div class='abs' style='left:36px;right:36px;bottom:36px;height:520px;background:linear-gradient(#0d0c0a 0%,rgba(13,12,10,.35) 45%,rgba(13,12,10,.15))'></div>
      <div class='abs' style='left:90px;right:90px;top:250px'>
        <div style='display:flex;align-items:flex-end;gap:30px'><div class='num' style='font-size:210px'>{num}</div><div class='k' style='padding-bottom:20px'>COMMITMENT</div></div>
        <div class='hair' style='left:0;right:0;top:auto;position:relative;margin:34px 0 34px'></div>
        <div class='h' style='font-size:84px'>{title}</div>
        <div class='p' style='margin-top:26px'>{text}</div>
      </div>""")

def an_slides():
    T = 7; S = []
    S.append(an(1, T, f"""
      <div class='ph' style='inset:0'><img src='{A}ann_hero-villa.jpg' style='object-position:40% 50%'></div>
      <div class='abs' style='inset:0;background:linear-gradient(#0d0c0aee 0%,#0d0c0a88 40%,#0d0c0add 75%,#0d0c0a 100%)'></div>
      <div class='abs' style='left:90px;right:90px;top:430px;text-align:center'>
        <div class='k'>WHY ANNOVA 360</div>
        <div class='h' style='font-size:118px;margin-top:30px'>Five commitments.</div>
        <div class='h gold' style='font-size:118px;font-style:italic'>Zero surprises.</div>
        <div class='hair' style='left:30%;right:30%;position:relative;margin:46px auto'></div>
        <div class='p' style='font-size:34px'>The five promises most builders<br>won't put in writing.</div>
      </div>"""))
    S.append(an_commit(2, T, '01', 'What you approve is what you get.', 'Every material, finish and dimension is locked at design sign-off and delivered exactly as specced.', 'ann_proj-residence-living.jpg'))
    S.append(an_commit(3, T, '02', 'One design partner. Zero handoffs.', 'The same team that designs your space executes it, so nothing is lost between drawing and site.', 'ann_hero-villa.jpg', '30% 50%'))
    S.append(an_commit(4, T, '03', 'A client-embedded process.', 'Structured weekly walkthroughs and real-time decisions made with you, not around you.', 'ann_proj-venus-exterior.jpg', '50% 60%'))
    S.append(an_commit(5, T, '04', 'Spec-level documentation.', 'Every drawing, BOQ and material call-out is detailed to the tolerance of a build document.', 'ann_proj-ankuraa-lotus-exterior.jpg', '50% 40%'))
    S.append(an_commit(6, T, '05', 'Fixed scope, timeline and budget.', 'We commit to the scope, cost and schedule agreed at the start, and we deliver against it.', 'ann_proj-residence-living.jpg', '70% 50%'))
    S.append(an(7, T, f"""
      <div class='ph' style='inset:0;opacity:.45'><img src='{A}ann_proj-ankuraa-lotus-exterior.jpg'></div>
      <div class='abs' style='inset:0;background:radial-gradient(circle at 50% 50%,rgba(13,12,10,.6),#0d0c0a 78%)'></div>
      <div class='abs' style='left:90px;right:90px;top:420px;text-align:center'>
        <div class='k'>EST. 2014 · DESIGN · BUILD · DELIVER</div>
        <div class='h' style='font-size:104px;margin-top:34px'>Phase one is</div>
        <div class='h gold' style='font-size:104px;font-style:italic'>a conversation.</div>
        <div style='display:inline-block;margin-top:60px;padding:28px 60px;border:1px solid #C9A35B;color:#C9A35B;font:500 28px Int;letter-spacing:6px'>BOOK A PRIVATE CONSULTATION</div>
        <div style='margin-top:48px;font:500 28px Int;color:#b8b0a1;letter-spacing:3px'>annova360.com &nbsp;·&nbsp; +91 88610 35808</div>
      </div>""", swipe=False))
    return S

if __name__ == '__main__':
    out = os.path.join(HERE, 'html'); os.makedirs(out, exist_ok=True)
    jobs = []
    for brand, fn in (('ioceane', ioc_slides), ('vedrxtours', ved_slides), ('mr-communications', mr_slides), ('annova360', an_slides)):
        for i, h in enumerate(fn(), 1):
            name = f'{brand}-{i:02d}'
            open(os.path.join(HERE, f'{name}.html'), 'w').write(h)
            jobs.append(name)
    json.dump(jobs, open(os.path.join(HERE, 'html', 'jobs.json'), 'w'))
    print(len(jobs), 'slides')
