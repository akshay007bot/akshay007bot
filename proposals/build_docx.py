# -*- coding: utf-8 -*-
"""Editable DOCX version of the iOceane proposals (same content as the PDF)."""
import pathlib
from docx import Document
from docx.shared import Pt, RGBColor, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from content import *
from build_html import inr

ROOT = pathlib.Path(__file__).parent
BLUE, INK, MUTED, MINT = RGBColor(0, 0x9F, 0xFF), RGBColor(0x0A, 0x0F, 0x1E), RGBColor(0x5B, 0x65, 0x77), RGBColor(0, 0xB9, 0x7C)

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), hexcolor); tcPr.append(s)

def run(p, text, bold=False, size=None, color=None, font=None, italic=False):
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color
    if font: r.font.name = font; r._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    return r

def H(doc, n, text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(14); p.paragraph_format.space_after = Pt(6)
    if n: run(p, f"{n}  ", True, 11, BLUE, "Comfortaa")
    run(p, text, True, 16, INK, "Comfortaa")

def H3(doc, text):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(8)
    run(p, text, True, 11.5, INK, "Comfortaa")

def P(doc, text, **kw):
    p = doc.add_paragraph(); run(p, text, **kw); return p

def bullets(doc, items):
    for x in items:
        p = doc.add_paragraph(style="List Bullet"); run(p, x, size=9.5)

def table(doc, header, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(header)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; shade(c, "0A0F1E"); c.text = ""
        run(c.paragraphs[0], h.upper(), True, 7.5, RGBColor(255, 255, 255))
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = ""; run(cells[i].paragraphs[0], str(v), size=9, bold=(i == 0))
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Mm(w)
    doc.add_paragraph()
    return t

def build(key):
    c = CLIENTS[key]
    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Mm(297), Mm(210)
    sec.left_margin = sec.right_margin = Mm(18); sec.top_margin = sec.bottom_margin = Mm(18)
    st = doc.styles["Normal"]; st.font.name = "Inter"; st.font.size = Pt(10)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Inter")

    hp = sec.header.paragraphs[0]; hp.add_run().add_picture(str(ROOT / "assets/logo-black-crop.png"), height=Mm(4.5))
    run(hp, f"\t\tPersonal Brand Partnership · {c['full']}", size=7.5, color=MUTED)
    fp = sec.footer.paragraphs[0]
    run(fp, f"iOceane · {AGENCY['phone']} · {AGENCY['email']} · {AGENCY['web']} · {AGENCY['city']}", size=7.5, color=MUTED)

    # cover
    doc.add_paragraph().add_run().add_picture(str(ROOT / "assets/logo-black-crop.png"), height=Mm(10))
    for _ in range(5): doc.add_paragraph()
    P(doc, "PERSONAL BRAND PROPOSAL", bold=True, size=8, color=BLUE)
    P(doc, "Personal Brand Partnership", bold=True, size=32, color=INK, font="Comfortaa")
    P(doc, "Strategy, studio content, podcasts and stages, done for you so people know the person behind the businesses.", size=11, color=MUTED)
    for _ in range(4): doc.add_paragraph()
    P(doc, "PREPARED FOR", bold=True, size=8, color=MUTED)
    P(doc, c["full"], bold=True, size=20, font="Comfortaa")
    P(doc, c["role"], size=9.5, color=MUTED)
    doc.add_paragraph()
    table(doc, ["Prepared by", "Date", "Contact"], [["iOceane, Bengaluru", f"{DATE} · {VALID}", f"{AGENCY['email']} · {AGENCY['phone']}"]])
    doc.add_page_break()

    H(doc, "01", "Introduction")
    P(doc, f"Dear {c['first']},", bold=True)
    P(doc, f"Thank you for the conversation and for considering iOceane to build your personal brand. {c['hook']}")
    P(doc, "This proposal sets out what we will do, how we will work with you, what you will receive every month and what it costs, including the video shoots and podcast production we will handle for you.")
    P(doc, "Warm regards,\nTeam iOceane", color=BLUE, bold=True)

    H(doc, "02", "Executive summary")
    P(doc, c["summary"])
    table(doc, ["The goal", "The approach", "Your time"], [["Be known for who you are", "Credibility first. Fame follows.", "A few hours a month"]])
    H3(doc, "Investment at a glance")
    table(doc, ["Item", "Billing", "Amount"], [
        ["Brand Foundation", "One-time (waived on a 6-month term)", inr(FOUNDATION)],
        ["Personal brand retainer", "Monthly", inr(RETAINER)],
        ["Growth package (recommended)", "Monthly · retainer + shoot + podcast", inr(PACKAGES[1]["price"])]])
    P(doc, "All fees exclusive of 18% GST.", italic=True, size=8.5, color=MUTED)

    H(doc, "03", f"Understanding you, {c['first']}")
    P(doc, f"You have already built {c['ventures']}. The next thing to build is your name, because people trust people before they trust institutions.")
    table(doc, ["What we know", ""], c["facts"], [35, 139])
    H3(doc, "Who needs to know you")
    table(doc, ["Audience", "Why it matters"], c["audiences"], [45, 129])

    H(doc, "04", "The challenge")
    table(doc, ["Challenge", "What it means"], c["challenges"], [50, 124])
    H(doc, "05", "The opportunity")
    table(doc, ["Opportunity", "Why now"], c["opportunities"], [50, 124])

    H(doc, "06", "Strategy")
    H3(doc, "The goal: be known for who you are")
    table(doc, ["Your values", "Your vision", "Your nature"], [["What you stand for, in business, in your field and in life.", "Where you are taking your industry, and why.", "How you think, how you work and how you treat people."]])
    H3(doc, "The path: credibility first, fame follows")
    table(doc, ["Step", "Focus", "What happens"], [
        ["1 · Months 1–3", "Build credibility", "You show up every week with real substance. People start to trust you."],
        ["2 · Months 4–6", "Grow your reach", "Bigger podcasts, bigger stages, more people."],
        ["3 · Ongoing", "Compound", "Every talk and episode feeds new content and new invitations."]])
    H3(doc, "Your content pillars")
    table(doc, ["Pillar", "Theme", "What you’ll talk about"], c["pillars"], [30, 45, 99])

    H(doc, "07", "Proposed solution: three ways you show up")
    for s in SERVICES:
        what = c["stages"] if s.get("stages") else s["what"]
        H3(doc, f"{s['n']}  {s['name']}")
        table(doc, ["", ""], [["What", what], ["Why", s["why"]], ["How", s["how"]], ["Deliverables", s["out"]], ["We measure", s["kpi"]]], [30, 144])
    P(doc, "Every conversation and every talk is cut into short videos, so one hour of your time becomes weeks of content.", bold=True)
    H3(doc, "Where you’ll show up")
    table(doc, ["Platform", "Role", "Purpose"], c["platforms"], [28, 30, 116])

    H(doc, "08", "Detailed scope of work · every month")
    rows = [[g if i == 0 else "", d, q] for g, items in MONTHLY_SCOPE for i, (d, q) in enumerate(items)]
    table(doc, ["Area", "Deliverable", "Per month"], rows, [30, 120, 24])
    table(doc, ["01 · Plan", "02 · Shoot", "03 · Post & grow"], [["We pick the month’s topics together and write the hooks.", "One studio shoot and one podcast shoot. We bring crew, set and prompts.", "Editing, 24–28 posts, replies and outreach."]])
    P(doc, "Your time: roughly 6–8 hours a month.", size=9, color=MUTED)

    H(doc, "09", "Video shoots & podcast production")
    extra = f" {c['uk_note']}" if c.get("uk_note") else ""
    P(doc, f"We handle every shoot end to end: brief, script prompts, studio booking, crew, cameras, lighting, sound, teleprompter, direction on the day, editing and posting. You arrive and speak. On-location shoots can happen at {c['location_note']}.{extra}")
    table(doc, ["Production", "What’s included", "Market rate*", "iOceane"], [[n, d, m, f"{inr(p)} {u}"] for n, d, m, p, u in RATE_CARD], [36, 80, 32, 26])
    H3(doc, "Optional add-ons")
    table(doc, ["Add-on", "Price", "Unit"], [[n, inr(p), u] for n, p, u in ADD_ONS], [110, 32, 32])
    P(doc, "*Indicative Bengaluru/India market rates from public studio and production-house listings, November 2026. Studio rentals: ₹999–₹9,000/hr. Multi-camera video podcasts: ₹10,000–₹30,000+ per episode. Production-house shoots: ₹40,000 to ₹1.2–3.5 lakh. All iOceane prices are estimates, include crew, equipment, studio and editing, and are confirmed per shoot brief.", italic=True, size=8, color=MUTED)

    H(doc, "10", "Investment")
    H3(doc, f"Brand Foundation · {inr(FOUNDATION)} one-time (waived on a 6-month agreement)")
    bullets(doc, FOUNDATION_ITEMS)
    H3(doc, f"Personal brand management retainer · {inr(RETAINER)} / month")
    bullets(doc, ["Personal brand strategy & monthly planning", "24–28 posts a month across platforms", "Posting, community and account management", "Podcast, creator & event outreach", "One podcast shoot coordinated each month", "Weekly snapshots & monthly report"])
    H3(doc, "Monthly packages · retainer + production")
    table(doc, ["Package", "Price / month", "Includes", "Best for"], [[f"{p['name']} ({p['tag']})", inr(p["price"]) + (f"\n(separately {inr(p['list'])})" if p["list"] else ""), "\n".join("• " + x for x in p["items"]), p["fit"]] for p in PACKAGES], [30, 30, 70, 44])
    H3(doc, "Payment milestones")
    table(doc, ["Milestone", "When", "Amount"], [
        ["Brand Foundation", "On signing (waived on a 6-month term)", inr(FOUNDATION)],
        ["Month 1 package", "On signing, before the first shoot is booked", "As chosen"],
        ["Months 2 onward", "In advance, by the 5th of each month", "As chosen"],
        ["One-off shoots & add-ons", "50% at booking · 50% on delivery", "As quoted"]])

    H(doc, "11", "Timeline & milestones · first 6 months")
    table(doc, ["When", "Phase", "Milestones"], [[w, t, "\n".join("• " + x for x in xs)] for w, t, xs in ROADMAP], [28, 36, 110])
    H(doc, "12", "Expected outcomes & KPIs")
    table(doc, ["Area", "What we track", "Target", "Type"], KPIS, [26, 58, 64, 26])
    P(doc, "Commitments are what iOceane delivers. Tracked metrics are baselined in week 2, and numeric targets are set with you after the first month of real data. Goals depend partly on third parties.", italic=True, size=8.5, color=MUTED)
    P(doc, "What success looks like at month 6: a recognisable, consistent presence on Instagram and LinkedIn, six podcast conversations on record, your first talks delivered, a tested talk ready for a TEDx application, and inbound invitations that come to you by name.", bold=True, size=9.5)

    H(doc, "13", "Why iOceane")
    table(doc, ["Proof", ""], WHY, [34, 140])
    bullets(doc, ["One team: strategy, scripting, shooting, editing, posting and outreach in one place.", "Founder-first: a fixed monthly rhythm built around your calendar.", "Transparent: fixed monthly deliverables, market-benchmarked shoot rates, weekly reporting."])

    H(doc, "14", "Terms & conditions")
    for i, x in enumerate(TERMS, 1):
        p = doc.add_paragraph(style="List Number"); run(p, x, size=9)

    H(doc, "15", f"Next steps · Let’s build your name, {c['first']}.")
    table(doc, ["01", "02", "03"], [["Choose your package: Essential, Growth or Signature.", "One sit-down to understand you (2–3 hours).", "Your first shoot, within 3 weeks of signing."]])

    H(doc, "16", "Acceptance")
    P(doc, "By signing below, both parties agree to the scope, pricing and terms in this proposal.")
    table(doc, ["Selection", "Tick"], [[f"{p['name']} · {inr(p['price'])} / month", "☐"] for p in PACKAGES] + [["Term: 3 months ☐   6 months ☐ (Brand Foundation waived)", ""]], [150, 24])
    table(doc, [f"For {c['full']}", "For iOceane"], [["\n\nName & signature", "\n\nName & signature"], ["\nDate", "\nDate"]])
    P(doc, f"{AGENCY['phone']} · {AGENCY['email']} · {AGENCY['address']}", size=8.5, color=MUTED)

    out = ROOT / "output" / f"iOceane-Proposal-{c['slug']}.docx"
    doc.save(out); return out

if __name__ == "__main__":
    for k in CLIENTS: print(build(k))
