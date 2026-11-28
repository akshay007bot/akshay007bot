# -*- coding: utf-8 -*-
"""Render iOceane personal-brand proposals to HTML (then PDF via Playwright)."""
import base64, html, pathlib, sys
from content import *

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

def b64(p):
    return "data:image/png;base64," + base64.b64encode((ROOT / "assets" / p).read_bytes()).decode()

LOGO_DARK = b64("logo-black-crop.png")   # dark text — for light backgrounds
LOGO_LIGHT = b64("logo-white-crop.png")  # white text — for dark backgrounds

def inr(n):
    s = str(int(n)); last3, rest = s[-3:], s[:-3]
    parts = []
    while len(rest) > 2:
        parts.insert(0, rest[-2:]); rest = rest[:-2]
    if rest: parts.insert(0, rest)
    return "₹" + ",".join(parts + [last3]) if parts else "₹" + last3

e = html.escape

CSS = """
@page { size: A4; margin: 0; }
:root{--ink:#0A0F1E;--ink2:#1C2433;--muted:#5B6577;--line:#E3E8F0;--soft:#F3F6FA;--blue:#009FFF;--mint:#00FFAB;--mintd:#00B97C;--purple:#A855F7;}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;color:var(--ink);font-size:10pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact;background:#fff}
h1,h2,h3,.disp{font-family:Comfortaa,Inter,sans-serif;font-weight:700;letter-spacing:-.01em}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;padding:24mm 17mm 22mm}
.page:last-child{page-break-after:auto}
.bar{position:absolute;top:0;left:0;right:0;height:5px;display:flex}
.bar i{display:block;height:100%}
.bar i:nth-child(1){flex:6;background:var(--blue)}.bar i:nth-child(2){flex:3;background:var(--mint)}.bar i:nth-child(3){flex:1.4;background:var(--purple)}
.hdr{position:absolute;top:10mm;left:17mm;right:17mm;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:3mm}
.hdr img{height:15px}.hdr span{font-size:7.5pt;color:var(--muted)}
.ftr{position:absolute;bottom:9mm;left:17mm;right:17mm;display:flex;justify-content:space-between;font-size:7.5pt;color:var(--muted);border-top:1px solid var(--line);padding-top:2.5mm}
.ftr b{color:var(--ink);font-weight:600}
.eyebrow{font-size:7.5pt;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--blue)}
.sec{margin-top:8mm}
.sec:first-of-type{margin-top:4mm}
.sh{display:flex;align-items:baseline;gap:3mm;border-bottom:1px solid var(--line);padding-bottom:2mm;margin-bottom:4mm}
.sh .n{font-family:Comfortaa;font-weight:700;color:var(--blue);font-size:10pt}
.sh h2{font-size:17pt;font-weight:700}
.lead{font-size:11pt;color:var(--ink2);line-height:1.6}
p+p{margin-top:2.5mm}
.muted{color:var(--muted)}
.grid{display:grid;gap:3.5mm}
.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
.card{background:var(--soft);padding:4.5mm 4.5mm 5mm;border-top:3px solid var(--blue)}
.card.m{border-top-color:var(--mintd)}.card.p{border-top-color:var(--purple)}
.card .k{font-size:7pt;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--blue);margin-bottom:1.5mm}
.card.m .k{color:var(--mintd)}.card.p .k{color:var(--purple)}
.card h3{font-size:11.5pt;margin-bottom:1.5mm;line-height:1.3}
.card p{font-size:9pt;color:var(--muted);line-height:1.5}
table{width:100%;border-collapse:collapse;font-size:9pt}
th{background:var(--ink);color:#fff;font-size:7pt;letter-spacing:.18em;text-transform:uppercase;text-align:left;padding:2.6mm 3mm;font-weight:700}
td{padding:2.05mm 3mm;border-bottom:1px solid var(--line);vertical-align:top}
td.r,th.r{text-align:right}
td.num{font-family:Inter;font-weight:700;color:var(--blue);text-align:right;white-space:nowrap}
tr.grp td:first-child{font-family:Comfortaa;font-weight:700;font-size:10pt;border-left:3px solid var(--blue);background:var(--soft)}
.tile{background:var(--ink);color:#fff;padding:5mm}
.tile .k{font-size:7pt;letter-spacing:.18em;text-transform:uppercase;color:var(--mint);font-weight:700}
.tile .v{font-family:Inter;font-weight:700;font-size:19pt;margin:1.5mm 0 .5mm;letter-spacing:-.02em}
.tile .s{font-size:8pt;color:#AEB7C7}
.tile.hl{background:linear-gradient(135deg,#0070C9,#009FFF)}
.tile.hl .k{color:#CFFFEF}.tile.hl .s{color:#E2F3FF}
.pill{display:inline-block;font-size:6.8pt;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:1mm 2.2mm;border-radius:20px;background:#E6F5FF;color:#0070C9}
.pill.m{background:#DFFBEF;color:#007A52}.pill.p{background:#F3E8FF;color:#7E22CE}
ul.dots{list-style:none}
ul.dots li{position:relative;padding-left:4.5mm;margin:1.3mm 0;font-size:9.2pt}
ul.dots li:before{content:"";position:absolute;left:0;top:1.9mm;width:1.9mm;height:1.9mm;border-radius:50%;background:var(--mintd)}
.note{font-size:8pt;color:var(--muted);font-style:italic;margin-top:2.5mm}
.callout{border-left:3px solid var(--mintd);background:#F2FCF8;padding:3.5mm 4.5mm;font-size:9.4pt;margin-top:4mm}
/* cover */
.cover{background:var(--ink);color:#fff;padding:0}
.cover .glow{position:absolute;right:-60mm;top:40mm;width:190mm;height:190mm;border-radius:50%;background:radial-gradient(circle,rgba(0,159,255,.38),rgba(0,255,171,.10) 45%,rgba(10,15,30,0) 70%)}
.cover .rings{position:absolute;right:14mm;top:58mm;width:110mm;height:110mm}
.cover .inner{position:absolute;inset:0;padding:22mm 20mm}
.cover .logo{height:30px}
.cover .tag{position:absolute;top:24mm;right:20mm;font-size:7.5pt;letter-spacing:.3em;color:#8C96AB;font-weight:700}
.cover .title{position:absolute;top:112mm;left:20mm;right:20mm;border-left:4px solid var(--blue);padding-left:8mm}
.cover h1{font-size:38pt;line-height:1.08;margin:3mm 0 4mm}
.cover h1 span{background:linear-gradient(90deg,#009FFF,#00FFAB);-webkit-background-clip:text;color:transparent}
.cover .sub{font-size:11.5pt;color:#B9C2D3;max-width:130mm}
.cover .for{position:absolute;top:196mm;left:20mm;right:20mm}
.cover .for .name{font-family:Comfortaa;font-size:22pt;font-weight:700;margin-top:2mm}
.cover .for .role{font-size:9.5pt;color:#9AA4B8;margin-top:1mm}
.cover .meta{position:absolute;bottom:22mm;left:20mm;right:20mm;display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #2A3347;padding-top:5mm;font-size:9pt}
.cover .meta .k{font-size:6.8pt;letter-spacing:.2em;color:#7F8AA0;font-weight:700;margin-bottom:1.2mm}
.cover .meta b{font-weight:600}
.cover .meta span{color:#9AA4B8}
/* flow */
.flow{display:grid;grid-template-columns:1fr 6mm 1fr 6mm 1fr;align-items:stretch}
.flow .arr{display:flex;align-items:center;justify-content:center;color:var(--blue);font-weight:700}
/* packages */
.pkg{border:1px solid var(--line);padding:5mm;position:relative;display:flex;flex-direction:column}
.pkg.rec{border:2px solid var(--blue);box-shadow:0 6px 22px rgba(0,159,255,.15)}
.pkg .nm{font-family:Comfortaa;font-weight:700;font-size:14pt;margin:2mm 0 1mm}
.pkg .pr{font-weight:700;font-size:18pt;letter-spacing:-.02em}
.pkg .pr small{font-size:8pt;color:var(--muted);font-weight:500}
.pkg .was{font-size:8pt;color:var(--muted)}
.pkg .was s{color:#9AA3B2}
.pkg ul{margin-top:3mm;flex:1}
.pkg .fit{font-size:8pt;color:var(--muted);border-top:1px solid var(--line);padding-top:2.5mm;margin-top:3mm}
/* roadmap */
.road{display:grid;grid-template-columns:repeat(4,1fr);gap:0;position:relative}
.road .st{padding:0 3mm 0 0}
.road .dot{width:9px;height:9px;border-radius:50%;background:var(--blue);box-shadow:0 0 0 4px #DDF1FF;margin:0 0 3mm}
.road .line{position:absolute;top:4px;left:0;right:0;height:1px;background:linear-gradient(90deg,var(--blue),var(--mint),var(--purple));z-index:-1}
.road .when{font-size:7pt;letter-spacing:.16em;text-transform:uppercase;font-weight:700;color:var(--blue)}
.road h3{font-size:11pt;margin:1mm 0 1.5mm}
/* stats */
.stat{padding:4mm 0;border-top:2px solid var(--ink)}
.stat .v{font-family:Comfortaa;font-weight:700;font-size:17pt;background:linear-gradient(90deg,#009FFF,#00B97C);-webkit-background-clip:text;color:transparent}
.stat p{font-size:8.6pt;color:var(--muted);margin-top:1mm}
ol.terms{padding-left:5mm;font-size:8.6pt;color:var(--ink2)}
ol.terms li{margin:1.4mm 0;padding-left:1mm}
.sig{display:grid;grid-template-columns:1fr 1fr;gap:12mm;margin-top:6mm}
.sig .k{font-size:7pt;letter-spacing:.18em;font-weight:700;color:var(--blue);text-transform:uppercase;margin-bottom:12mm}
.sig .ln{border-bottom:1px solid #9AA3B2;margin-bottom:1.5mm;height:10mm}
.sig small{font-size:8pt;color:var(--muted)}
.cta{background:var(--ink);color:#fff;padding:9mm 9mm 8mm;position:relative;overflow:hidden}
.cta:after{content:"";position:absolute;right:-30mm;top:-30mm;width:90mm;height:90mm;border-radius:50%;background:radial-gradient(circle,rgba(0,159,255,.45),rgba(0,255,171,.08) 55%,transparent 70%)}
.cta h2{font-size:22pt;line-height:1.15;position:relative;z-index:1}
.cta h2 span{background:linear-gradient(90deg,#009FFF,#00FFAB);-webkit-background-clip:text;color:transparent}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:5mm;margin-top:6mm;position:relative;z-index:1}
.steps div{border-top:1px solid #39435A;padding-top:3mm}
.steps .n{font-family:Comfortaa;font-weight:700;color:var(--mint);font-size:13pt}
.steps p{font-size:9pt;color:#C9D1DF;margin-top:1mm}
.svc{display:grid;grid-template-columns:34mm 1fr;border-top:1px solid var(--line);padding:3.6mm 0}
.svc .nm .n{font-family:Comfortaa;font-weight:700;color:var(--blue);font-size:9pt}
.svc .nm h3{font-size:12pt;margin-top:.5mm}
.svc dl{display:grid;grid-template-columns:22mm 1fr;row-gap:1.2mm;font-size:8.9pt}
.svc dt{font-size:6.8pt;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);padding-top:.6mm}
.svc dd{color:var(--ink2)}
"""

def page(inner, c, title="Personal Brand Partnership"):
    return f"""<section class="page"><div class="bar"><i></i><i></i><i></i></div>
<div class="hdr"><img src="{LOGO_DARK}" alt="iOceane"><span>{e(title)} · {e(c['full'])}</span></div>
{inner}
<div class="ftr"><span><b>iOceane</b> · {AGENCY['phone']} · {AGENCY['email']} · {AGENCY['web']} · {AGENCY['city']}</span><span>Page {{PN}}</span></div></section>"""

def sec(n, title, body, cls="sec"):
    num = f'<span class="n">{n}</span>' if n else ''
    return f'<div class="{cls}"><div class="sh">{num}<h2>{e(title)}</h2></div>{body}</div>'

RINGS = """<svg class="rings" viewBox="0 0 200 200" fill="none"><g stroke="#2E5B8A" stroke-width=".6">
<circle cx="100" cy="100" r="96" opacity=".5"/><circle cx="100" cy="100" r="70" opacity=".7"/><circle cx="100" cy="100" r="44"/></g>
<g stroke="#2E5B8A" stroke-width=".5" opacity=".6"><path d="M100 4V196M4 100H196M32 32l136 136M168 32L32 168"/></g>
<circle cx="100" cy="100" r="10" fill="url(#g)"/><circle cx="100" cy="4" r="3" fill="#009FFF"/><circle cx="196" cy="100" r="3" fill="#00FFAB"/>
<circle cx="168" cy="168" r="2.4" fill="#A855F7"/><circle cx="4" cy="100" r="2.4" fill="#009FFF"/><circle cx="32" cy="32" r="2" fill="#00FFAB"/>
<defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#009FFF"/><stop offset="1" stop-color="#00FFAB"/></linearGradient></defs></svg>"""

def build(key):
    global RETAINER, SHOOT_BUDGET
    c = CLIENTS[key]
    import content as _ct
    RETAINER = c.get("retainer", _ct.RETAINER)
    SHOOT_BUDGET = c.get("shoot_budget", _ct.SHOOT_BUDGET)
    pages = []

    # ---------- 1 cover
    pages.append(f"""<section class="page cover"><div class="glow"></div>{RINGS}<div class="inner">
<img class="logo" src="{LOGO_LIGHT}" alt="iOceane"><div class="tag">PROPOSAL</div>
<div class="title"><div class="eyebrow">Personal brand proposal</div>
<h1>Personal Brand<br><span>Partnership</span></h1>
<div class="sub">Strategy, studio content, podcasts and stages, done for you so people know the person behind the businesses.</div></div>
<div class="for"><div class="eyebrow" style="color:#7F8AA0">Prepared for</div><div class="name">{e(c['full'])}</div><div class="role">{e(c['role'])}</div></div>
<div class="meta"><div><div class="k">PREPARED BY</div><b>iOceane</b><br><span>Bengaluru, India</span></div>
<div><div class="k">DATE</div><b>{DATE}</b><br><span>{VALID}</span></div>
<div><div class="k">CONTACT</div><b>{AGENCY['email']}</b><br><span>{AGENCY['phone']}</span></div></div></div></section>""")

    # ---------- 2 intro + exec summary
    tiles = f"""<div class="grid g4" style="margin-top:4mm">
<div class="tile"><div class="k">One-time</div><div class="v">{inr(FOUNDATION)}</div><div class="s">Brand Foundation · waived on a 6-month term</div></div>
<div class="tile"><div class="k">Monthly retainer</div><div class="v">{inr(RETAINER)}</div><div class="s">Strategy, content, posting & outreach</div></div>
<div class="tile"><div class="k">Video shoots</div><div class="v">{inr(SHOOT_BUDGET)}</div><div class="s">Monthly budget · 1 content shoot + 1 podcast</div></div>
<div class="tile hl"><div class="k">Total monthly</div><div class="v">{inr(RETAINER+SHOOT_BUDGET)}</div><div class="s">Retainer + video shoots</div></div></div>
<p class="note">All fees exclusive of 18% GST.</p>"""
    body = sec("01", "Introduction", f"""<p class="lead"><b>Dear {e(c['first'])},</b></p>
<p class="lead">Thank you for the conversation and for considering iOceane to build your personal brand. {e(c['hook'])}</p>
<p>This proposal sets out what we will do, how we will work with you, what you will receive every month and what it costs, including the video shoots and podcast production we will handle for you.</p>
<p style="margin-top:3mm">Warm regards,<br><b style="font-family:Comfortaa;color:var(--blue)">Team iOceane</b></p>""")
    body += sec("02", "Executive summary", f"""<p>{e(c['summary'])}</p>
<div class="grid g3" style="margin-top:4mm">
<div class="card"><div class="k">The goal</div><h3>Be known for who you are</h3><p>Your values, vision and nature, shown well and shown often.</p></div>
<div class="card m"><div class="k">The approach</div><h3>Credibility first. Fame follows.</h3><p>Weekly substance first, then bigger podcasts and stages.</p></div>
<div class="card p"><div class="k">Your time</div><h3>A few hours a month</h3><p>One planning sit-down, one shoot, one podcast. We handle the rest.</p></div></div>
<h3 style="font-size:11pt;margin-top:6mm">Investment at a glance</h3>{tiles}""")
    pages.append(page(body, c))

    # ---------- 3 understanding
    facts = "".join(f"<tr><td style='width:32mm;font-weight:600'>{e(k)}</td><td>{e(v)}</td></tr>" for k, v in c["facts"])
    aud = "".join(f'<div class="card {["","m","p",""][i]}"><div class="k">Audience {i+1}</div><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(c["audiences"]))
    body = sec("03", f"Understanding you, {c['first']}", f"""<p class="lead">You have already built {e(c['ventures'])}. The next thing to build is your name, because people trust people before they trust institutions.</p>
<table style="margin-top:5mm"><tr><th colspan="2">What we know</th></tr>{facts}</table>
<h3 style="font-size:11pt;margin:6mm 0 3mm">Who needs to know you</h3><div class="grid g2">{aud}</div>
<div class="callout"><b>Week 1 deep-dive.</b> In our first sit-down we audit your current profiles, record baseline numbers and put your values, vision and nature into words. Everything we make comes from that.</div>""")
    pages.append(page(body, c))

    # ---------- 4 challenges & opportunities
    ch = "".join(f"<tr><td style='width:6mm' class='num'>{i+1:02d}</td><td><b>{e(a)}</b><br><span class='muted'>{e(b)}</span></td></tr>" for i, (a, b) in enumerate(c["challenges"]))
    op = "".join(f'<div class="card {["","m","p",""][i]}"><div class="k">Opportunity {i+1}</div><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(c["opportunities"]))
    body = sec("04", "The challenge", f"<table>{ch}</table>")
    body += sec("05", "The opportunity", f'<div class="grid g2">{op}</div>')
    pages.append(page(body, c))

    # ---------- 5 strategy
    goal = """<div class="grid g3"><div class="card"><div class="k">Your values</div><h3>What you stand for</h3><p>In business, in your field and in life.</p></div>
<div class="card m"><div class="k">Your vision</div><h3>Where you’re going</h3><p>Where you are taking your industry, and why.</p></div>
<div class="card p"><div class="k">Your nature</div><h3>How you are</h3><p>How you think, how you work and how you treat people.</p></div></div>"""
    flow = """<div class="flow" style="margin-top:4mm"><div class="card"><div class="k">Step 1 · Months 1–3</div><h3>Build credibility</h3><p>You show up every week with real substance: your work, your thinking, your experience. People start to trust you.</p></div>
<div class="arr">→</div><div class="card m"><div class="k">Step 2 · Months 4–6</div><h3>Grow your reach</h3><p>Bigger podcasts, bigger stages, more people. When a moment takes off, there is a real person behind it.</p></div>
<div class="arr">→</div><div class="card p"><div class="k">Step 3 · Ongoing</div><h3>Compound</h3><p>Every talk and episode feeds new content, new invitations and a stronger reputation.</p></div></div>
<p class="note" style="font-style:normal">No stunts. Just you, shown well and shown often.</p>"""
    pil = "".join(f'<div class="card {["","m","p",""][i]}"><div class="k">{e(a)}</div><h3>{e(b)}</h3><p>{e(d)}</p></div>' for i, (a, b, d) in enumerate(c["pillars"]))
    body = sec("06", "Strategy", f'<h3 style="font-size:11pt;margin-bottom:3mm">The goal: be known for who you are</h3>{goal}<h3 style="font-size:11pt;margin:6mm 0 0">The path: credibility first, fame follows</h3>{flow}')
    body += sec("", "Your content pillars", f'<p class="muted" style="margin-bottom:3mm">Four themes. Every post, podcast and talk maps to one of them.</p><div class="grid g4">{pil}</div>')
    pages.append(page(body, c))

    # ---------- 6 solutions
    svcs = ""
    for s in SERVICES:
        what = c["stages"] if s.get("stages") else s["what"]
        svcs += f"""<div class="svc"><div class="nm"><div class="n">{s['n']}</div><h3>{e(s['name'])}</h3></div><dl>
<dt>What</dt><dd>{e(what)}</dd><dt>Why</dt><dd>{e(s['why'])}</dd><dt>How</dt><dd>{e(s['how'])}</dd>
<dt>Deliverables</dt><dd><b>{e(s['out'])}</b></dd><dt>We measure</dt><dd>{e(s['kpi'])}</dd></dl></div>"""
    plats = "".join(f'<div class="card {["","m","p"][i]}"><div class="k">{e(t)}</div><h3>{e(n)}</h3><p>{e(d)}</p></div>' for i, (n, t, d) in enumerate(c["platforms"]))
    body = sec("07", "Proposed solution: three ways you show up", svcs + '<p class="callout" style="margin-top:2mm">Every conversation and every talk is cut into short videos, so <b>one hour of your time becomes weeks of content.</b></p>')
    body += sec("", "Where you’ll show up", f'<div class="grid g3">{plats}</div>')
    pages.append(page(body, c))

    # ---------- 7 scope
    rows = ""
    for g, items in MONTHLY_SCOPE:
        for i, (d, q) in enumerate(items):
            rows += f"<tr class='{'grp' if i==0 else ''}'><td style='width:34mm'>{e(g) if i==0 else ''}</td><td>{e(d)}</td><td class='num'>{e(q)}</td></tr>"
    month = """<div class="flow"><div class="card"><div class="k">01 · Plan</div><h3>We sit with you</h3><p>We pick the month’s topics together and write the hooks and talking points.</p></div><div class="arr">→</div>
<div class="card m"><div class="k">02 · Shoot</div><h3>You show up</h3><p>One studio shoot for your content and one podcast shoot. We bring crew, set and prompts.</p></div><div class="arr">→</div>
<div class="card p"><div class="k">03 · Post & grow</div><h3>We do the rest</h3><p>Editing, 24–28 posts, replies, and outreach to podcast hosts and event organisers.</p></div></div>"""
    body = sec("08", "Detailed scope of work · every month", f'<table><tr><th>Area</th><th>Deliverable</th><th class="r">Per month</th></tr>{rows}</table>')
    body += sec("", "One month with us", month + '<p class="note" style="font-style:normal"><b>Your time:</b> roughly 6–8 hours a month: a 1-hour planning call, one shoot, one podcast and quick approvals on WhatsApp.</p>')
    pages.append(page(body, c))

    # ---------- 9 investment
    fi = "".join(f"<li>{e(x)}</li>" for x in FOUNDATION_ITEMS)
    loc = f"Shoots happen in a Bengaluru studio or at {c['location_note']}."
    extra = f" {c['uk_note']}" if c.get("uk_note") else ""
    summ = f"""<table><tr><th>Item</th><th>Billing</th><th class="r">Amount</th></tr>
<tr><td><b>Brand Foundation</b><br><span class="muted">Strategy, profile set-up, templates · waived on a 6-month term</span></td><td style="white-space:nowrap">One-time</td><td class="num">{inr(FOUNDATION)}</td></tr>
<tr><td><b>Personal brand retainer</b><br><span class="muted">Strategy, 24–28 posts, account management, podcast & event outreach</span></td><td>Monthly</td><td class="num">{inr(RETAINER)}</td></tr>
<tr><td><b>Video shoot budget</b><br><span class="muted">{e(SHOOT_DESC)}</span></td><td>Monthly</td><td class="num">{inr(SHOOT_BUDGET)}</td></tr>
<tr><td style="background:var(--ink);color:#fff"><b>Total monthly investment</b></td><td style="background:var(--ink);color:#AEB7C7">Monthly</td><td class="num" style="background:var(--ink);color:var(--mint);font-size:12pt">{inr(RETAINER+SHOOT_BUDGET)}</td></tr></table>
<p class="note">All fees exclusive of 18% GST. {e(loc)}{e(extra)}</p>"""
    pay = f"""<table><tr><th>Milestone</th><th>When</th><th class="r">Amount</th></tr>
<tr><td>Brand Foundation</td><td>On signing (waived on a 6-month term)</td><td class="num">{inr(FOUNDATION)}</td></tr>
<tr><td>Month 1 retainer + shoot budget</td><td>On signing, before the first shoot</td><td class="num">{inr(RETAINER+SHOOT_BUDGET)}</td></tr>
<tr><td>Months 2 onward</td><td>In advance, by the 5th of each month</td><td class="num">{inr(RETAINER+SHOOT_BUDGET)}</td></tr></table>"""
    body = sec("09", "Investment", summ + f"""<div class="grid g2" style="gap:5mm;margin-top:5mm">
<div class="card"><div class="k">One-time · {inr(FOUNDATION)}</div><h3>Brand Foundation</h3><ul class="dots">{fi}</ul></div>
<div class="card m"><div class="k">Monthly · {inr(RETAINER)} + {inr(SHOOT_BUDGET)}</div><h3>Retainer & video shoots</h3><ul class="dots"><li>Monthly planning sit-down & scripts</li><li>1 studio content shoot / month</li><li>1 podcast shoot / month</li><li>Editing of all videos & clips</li><li>24–28 posts across platforms</li><li>Podcast, creator & event outreach</li><li>Weekly snapshots & monthly report</li></ul></div></div>""")
    body += sec("", "Payment milestones", pay)
    pages.append(page(body, c))

    # ---------- 10 timeline + KPIs
    rd = "".join(f'<div class="st"><div class="dot"></div><div class="when">{e(w)}</div><h3>{e(t)}</h3><ul class="dots">{"".join(f"<li>{e(x)}</li>" for x in xs)}</ul></div>' for w, t, xs in ROADMAP)
    kp = "".join(f"<tr><td style='width:24mm;font-weight:600'>{e(a)}</td><td>{e(b)}</td><td>{e(d)}</td><td class='r'><span class='pill {dict(Commitment='',Tracked='m',Goal='p')[t]}'>{t}</span></td></tr>" for a, b, d, t in KPIS)
    body = sec("10", "Timeline & milestones · first 6 months", f'<div class="road"><div class="line"></div>{rd}</div>')
    body += sec("11", "Expected outcomes & KPIs", f"""<table><tr><th>Area</th><th>What we track</th><th>Target</th><th class="r">Type</th></tr>{kp}</table>
<p class="note"><b>Commitments</b> are what iOceane delivers. <b>Tracked</b> metrics are baselined in week 2, and we set numeric targets with you after the first month of real data rather than promising numbers up front. <b>Goals</b> depend partly on third parties such as hosts, organisers and TEDx curators.</p>
<div class="callout"><b>What success looks like at month 6:</b> a recognisable, consistent presence on Instagram and LinkedIn, six podcast conversations on record, your first talks delivered, a tested talk ready for a TEDx application, and inbound invitations that come to you by name.</div>""")
    pages.append(page(body, c))

    # ---------- 11 why + terms
    st = "".join(f'<div class="stat"><div class="v">{e(a)}</div><p>{e(b)}</p></div>' for a, b in WHY)
    tm = "".join(f"<li>{e(x)}</li>" for x in TERMS)
    body = sec("12", "Why iOceane", f"""<div class="grid g4">{st}</div>
<div class="grid g3" style="margin-top:4mm"><div class="card"><div class="k">One team</div><h3>Strategy to screen</h3><p>Strategy, scripting, shooting, editing, posting and outreach in one place.</p></div>
<div class="card m"><div class="k">Founder-first</div><h3>Built around your time</h3><p>A fixed monthly rhythm that respects a founder’s calendar.</p></div>
<div class="card p"><div class="k">Transparent</div><h3>Clear deliverables</h3><p>Fixed monthly counts, market-benchmarked shoot rates, weekly reporting.</p></div></div>""")
    body += sec("13", "Terms & conditions", f'<ol class="terms">{tm}</ol>')
    pages.append(page(body, c))

    # ---------- 12 next steps + acceptance
    body = f"""<div class="sec" style="margin-top:4mm"><div class="cta"><div class="eyebrow" style="color:var(--mint)">14 · Next steps</div>
<h2 style="margin-top:3mm">Let’s build your name,<br><span>{e(c['first'])}.</span></h2>
<div class="steps"><div><div class="n">01</div><p><b style="color:#fff">Confirm the plan</b><br>Pick your term. Sign below or reply by email.</p></div>
<div><div class="n">02</div><p><b style="color:#fff">One sit-down to understand you</b><br>2–3 hours. Your values, vision and nature, put into words.</p></div>
<div><div class="n">03</div><p><b style="color:#fff">Your first shoot</b><br>Within 3 weeks of signing. First posts live the week after.</p></div></div></div></div>
<div class="sec"><div class="sh"><span class="n">15</span><h2>Acceptance</h2></div>
<p>By signing below, both parties agree to the scope, pricing and terms in this proposal.</p>
<table style="margin-top:4mm"><tr><th>Agreement</th><th class="r">Monthly</th></tr>
<tr><td>Personal brand retainer + video shoot budget</td><td class="num">{inr(RETAINER+SHOOT_BUDGET)}</td></tr>
<tr><td>Term: ☐ 3 months &nbsp;&nbsp; ☐ 6 months (Brand Foundation waived)</td><td></td></tr></table>
<div class="sig"><div><div class="k">For {e(c['full'])}</div><div class="ln"></div><small>Name & signature</small><div class="ln"></div><small>Date</small></div>
<div><div class="k">For iOceane</div><div class="ln"></div><small>Name & signature</small><div class="ln"></div><small>Date</small></div></div>
<p class="note" style="margin-top:8mm;font-style:normal">Questions? Call or WhatsApp <b>{AGENCY['phone']}</b> · <b>{AGENCY['email']}</b> · {AGENCY['address']}</p></div>"""
    pages.append(page(body, c))

    out = []
    for i, p in enumerate(pages, 1):
        out.append(p.replace("{PN}", f"{i:02d} / {len(pages):02d}"))
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>iOceane × {e(c['full'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>{''.join(out)}</body></html>"""
    path = OUT / f"iOceane-Proposal-{c['slug']}.html"
    path.write_text(doc, encoding="utf-8")
    return path

if __name__ == "__main__":
    for k in (sys.argv[1:] or CLIENTS):
        print(build(k))
