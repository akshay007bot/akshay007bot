# -*- coding: utf-8 -*-
"""Shared + per-client content for iOceane personal-brand proposals."""

DATE = "28 November 2026"
VALID = "Valid for 30 days"
AGENCY = {
    "name": "iOceane",
    "email": "info@ioceane.com",
    "phone": "+91 90199 31101",
    "web": "ioceane.com",
    "city": "Domlur, Bengaluru",
    "address": "1st Floor, B-179, Amarjyoti Layout, Domlur, Bengaluru 560071",
}

# ---------------------------------------------------------------- pricing
RETAINER = 50000
FOUNDATION = 25000

# Video production rate card: (name, what's included, market benchmark, iOceane price, unit)
RATE_CARD = [
    ("Studio content shoot · Half day",
     "4 hours in studio · 2 × 4K cameras · lighting · lapel + shotgun mics · teleprompter · crew of 3 · 1 set change. Yields 10–12 short videos.",
     "Studio ₹1,500–9,000/hr + crew ₹15,000–40,000/day", 25000, "per shoot"),
    ("Studio content shoot · Full day",
     "8 hours · 3 cameras incl. cinema camera · 2 sets / looks · on-set director · behind-the-scenes stills. Yields 20+ short videos + 1 long-form piece.",
     "₹40,000–1,20,000+ per shoot day", 45000, "per shoot"),
    ("On-location shoot · Full day",
     "Your office, campus or site in Bengaluru · cinema camera + gimbal · 2-person lighting & sound crew · b-roll of people and places.",
     "₹40,000–1,20,000+ per shoot day", 55000, "per shoot"),
    ("Video podcast · produced by iOceane",
     "Up to 90 min recording · 3 × 4K cameras · studio & set · audio mastering · full-episode edit · thumbnail · 6–8 short clips.",
     "₹10,000–30,000+ per episode", 30000, "per episode"),
    ("Event / stage coverage",
     "Half day · 2 cameras + direct audio feed from the stage · vertical clips cut from your talk.",
     "₹15,000–40,000 per day", 20000, "per event"),
]
ADD_ONS = [
    ("Professional grooming / make-up artist", 5000, "per shoot"),
    ("Drone footage (where legally permitted)", 8000, "per shoot"),
    ("Crew on a guest podcast (BTS + vertical clips)", 10000, "per session"),
    ("Additional long-form edit (up to 30 min)", 6000, "per video"),
    ("Professional portrait photo session (15 edited images)", 15000, "one-time"),
]

PACKAGES = [
    {
        "name": "Essential",
        "tag": "Start steady",
        "price": 75000,
        "list": None,
        "items": [
            "Personal brand management retainer",
            "1 half-day studio shoot / month",
            "Guest-podcast & event pitching",
            "24–28 posts / month",
        ],
        "fit": "Best if your calendar is tight and you want a consistent, credible presence.",
    },
    {
        "name": "Growth",
        "tag": "Recommended",
        "price": 110000,
        "list": 125000,
        "items": [
            "Personal brand management retainer",
            "1 full-day studio shoot / month",
            "1 video podcast / month, produced by iOceane",
            "Guest-podcast & event pitching",
            "24–28 posts / month + 1 long-form episode",
        ],
        "fit": "One shoot day and one podcast give you a full month of content.",
    },
    {
        "name": "Signature",
        "tag": "Fastest reach",
        "price": 135000,
        "list": 150000,
        "items": [
            "Everything in Growth",
            "1 event / stage coverage per month",
            "Grooming artist on every shoot",
            "Priority TEDx & keynote pitching",
            "Quarterly on-location shoot in place of one studio day",
        ],
        "fit": "For when the stage and speaking track is a priority this year.",
    },
]

MARKET_SOURCES = [
    ("Content Studio – multi-camera video podcast cost guide (₹10k–30k+/episode)", "https://contentstudio.co.in/blog/podcast-cost-gurugram"),
    ("Dr. Bomb podcast studio – ₹1,499–2,499/hr", "https://www.barchart.com/story/news/1411410/dr-bomb-introduces-a-modern-podcast-studio-in-india-with-fully-equipped-setups-starting-at-rs1-499-per-hour"),
    ("Bengaluru corporate video pricing – ₹40k single-camera to ₹1.2L–3.5L typical", "https://beverlyboy.com/bengaluru-videographer-services/"),
    ("IndiaMART videography listings – ₹10k–40k per day", "https://m.indiamart.com/impcat/videography-services.html"),
]

# ---------------------------------------------------------------- clients
CLIENTS = {
    "ravi": {
        "slug": "Ravi-Venkatesh",
        "first": "Ravi",
        "full": "Ravi Venkatesh",
        "role": "Founder, ClobData (UK) · Pragnajanya International School (India)",
        "ventures": "ClobData in the UK and Pragnajanya International School in India",
        "hook": "People know your company and your school. It’s time they know you.",
        "hook_a": "People know your company and your school.",
        "hook_b": "It’s time they know you.",
        "summary": (
            "You have built a technology business in the UK and a school in India. "
            "Both carry your work, but not yet your name. This proposal sets out how iOceane will "
            "turn your thinking on AI, data and education into a consistent, credible personal brand on "
            "Instagram and LinkedIn. We start with your own studio content, then add podcasts and "
            "stages. We plan, shoot, edit, post and pitch. Your part is a few hours a month."
        ),
        "facts": [
            ("Ventures", "ClobData (UK technology company) and Pragnajanya International School (India)."),
            ("Territory", "Education, AI and data. You work across two countries."),
            ("Goal", "To be known for your values, your vision and your nature, not only through your institutions."),
        ],
        "audiences": [
            ("Parents & students", "Want to trust the person behind the school they choose."),
            ("Education leaders", "Look for practitioners with a clear view on AI in learning."),
            ("Business & tech peers", "Check LinkedIn before they partner with ClobData, hire from it or invest in it."),
            ("Hosts & organisers", "Need speakers with a clear point of view on AI and education."),
        ],
        "challenges": [
            ("Your name trails your institutions", "Trust sits with ClobData and Pragnajanya. A founder’s face and voice is what makes people choose them over the alternatives."),
            ("Time is your scarcest asset", "Running two organisations in two countries leaves little room to plan, film and post every week."),
            ("Two audiences, one voice", "Parents on Instagram and tech leaders on LinkedIn need different formats of the same ideas."),
            ("Credibility without hype", "Education is a trust category. Loud tactics or stunts would cost more than they earn."),
        ],
        "opportunities": [
            ("AI in education is a live conversation", "Few people can speak from inside both a tech company and a school. That combination is your edge."),
            ("Founder-led content earns trust", "Real people get more reach than logos on both Instagram and LinkedIn."),
            ("One hour → weeks of content", "A single shoot or podcast, edited well, feeds Instagram, LinkedIn and YouTube for a month."),
            ("Stages compound", "Education events, school and university talks build the track record a TEDx stage expects."),
        ],
        "pillars": [
            ("Your vision", "AI in education", "How AI will change the way children learn, and what Pragnajanya is doing about it."),
            ("Your expertise", "Tech and data", "What running a UK tech company has taught you about data, AI and business."),
            ("Your nature", "Two countries, one journey", "Building in the UK and in India: the lessons, the mistakes, the people."),
            ("Your values", "What you stand for", "Your take on education, family, community and giving back."),
        ],
        "platforms": [
            ("Instagram", "Main platform", "Where parents, students and the public meet you. Short videos from your shoots and podcasts, school life and your story."),
            ("LinkedIn", "Main platform", "Where business and education leaders check you out. Your thinking on AI, data and education, in your voice."),
            ("YouTube", "Library", "Full podcast episodes and talks plus Shorts, so your best thinking can be found in search for years."),
        ],
        "stages": "Education and technology events, school and university talks, then a TEDx stage when the time is right.",
        "location_note": "Pragnajanya campus or ClobData office",
        "uk_note": "Shoots while you are in the UK can be arranged with a partner crew and quoted separately.",
        "theme": {"accent": "#009FFF"},
    },
    "vicky": {
        "slug": "Vicky-Sujani",
        "first": "Vicky",
        "full": "Vicky Sujani",
        "role": "Founder, Kohinoor Business Park · Matrix Technologies",
        "ventures": "Kohinoor Business Park and Matrix Technologies",
        "hook": "People know your businesses. It’s time they know you.",
        "hook_a": "People know your businesses.",
        "hook_b": "It’s time they know you.",
        "summary": (
            "You have built Kohinoor Business Park and Matrix Technologies. People know the businesses "
            "but not yet the person who built them. This proposal sets out how iOceane will build your "
            "personal brand around real substance: the decisions behind Kohinoor, the fight against fake "
            "products at Matrix, and how you lead. It runs on Instagram and LinkedIn, then moves to podcasts "
            "and industry stages. We plan, shoot, edit, post and pitch. Your part is a few hours a month."
        ),
        "facts": [
            ("Ventures", "Kohinoor Business Park and Matrix Technologies."),
            ("Territory", "Real estate, manufacturing, brand protection and leadership."),
            ("Goal", "To be known for your values, your vision and your nature, not only through your companies."),
        ],
        "audiences": [
            ("Business owners & tenants", "Want to know who stands behind Kohinoor before they commit."),
            ("Brands & manufacturers", "Need a trusted expert on product authenticity and anti-counterfeiting."),
            ("Industry & investors", "Check LinkedIn to judge your leadership and track record."),
            ("Hosts & organisers", "Look for founders with real-world lessons for panels and talks."),
        ],
        "challenges": [
            ("Your name trails your businesses", "Kohinoor and Matrix are known. The founder behind them is the part of the story that is still missing."),
            ("Time is your scarcest asset", "Running two companies leaves little room to plan, film and post every week."),
            ("Two very different worlds", "Real estate and anti-counterfeiting technology need one clear story that ties them together: trust."),
            ("Credibility without hype", "Your buyers are serious decision-makers. Stunts and trends would cost more than they earn."),
        ],
        "opportunities": [
            ("Trust is your common thread", "A business park and an authenticity company both sell trust. That is a strong, ownable theme for you."),
            ("Founder-led content earns trust", "Real people get more reach than logos on both Instagram and LinkedIn."),
            ("One hour → weeks of content", "A single shoot or podcast, edited well, feeds Instagram, LinkedIn and YouTube for a month."),
            ("Stages compound", "Industry panels and college talks build the track record a TEDx stage expects."),
        ],
        "pillars": [
            ("Your vision", "Building Kohinoor", "The park, the big decisions and the people behind it."),
            ("Your expertise", "Trust and authenticity", "How fake products hurt brands, and how Matrix fights them."),
            ("Your nature", "Lessons from two companies", "What running two businesses has taught you, mistakes included."),
            ("Your values", "What you stand for", "Your take on business, family and doing things the right way."),
        ],
        "platforms": [
            ("Instagram", "Main platform", "Where people meet you. Short videos from your shoots and podcasts, behind the scenes, and your story."),
            ("LinkedIn", "Main platform", "Where business people check you out. Your thinking on real estate, manufacturing and leadership, in your voice."),
            ("YouTube", "Library", "Full podcast episodes and talks plus Shorts, so your best thinking can be found in search for years."),
        ],
        "stages": "Industry panels and college talks first, then a TEDx stage when the time is right.",
        "location_note": "Kohinoor Business Park or the Matrix facility",
        "uk_note": None,
        "theme": {"accent": "#009FFF"},
    },
}

# ---------------------------------------------------------------- shared sections
SERVICES = [
    {
        "n": "01", "name": "Your own content",
        "what": "Studio-quality videos of you speaking on your four pillars, cut into Reels, LinkedIn videos and Shorts.",
        "why": "Weekly, substantive content is what builds credibility. Your own content is the base of the brand.",
        "how": "Monthly topic sit-down → hooks & talking points written for you → teleprompter-assisted shoot → edit, captions, posting.",
        "out": "10–12 short videos, 8 LinkedIn posts, 4–6 carousels per month",
        "kpi": "Reach, watch time, saves & shares, profile visits",
    },
    {
        "n": "02", "name": "Podcasts",
        "what": "One podcast a month, either on our produced show or as a guest on other creators’ shows.",
        "why": "Long conversations show depth and character. Every episode reaches a new audience you can borrow.",
        "how": "We build your guest one-sheet, shortlist relevant hosts, pitch, prepare you, and handle logistics and clipping.",
        "out": "1 podcast / month + 6–8 clips from each",
        "kpi": "Episodes recorded, new followers from guest audiences",
    },
    {
        "n": "03", "name": "Events and stages",
        "stages": True,
        "what": "",
        "why": "Stages give a third-party stamp of credibility that no post can buy.",
        "how": "Speaker profile, talk topics, event shortlist, outreach to organisers, talk prep and coverage on the day.",
        "out": "4+ organiser pitches / month, talk clips",
        "kpi": "Invitations received, talks delivered, TEDx application",
    },
]

MONTHLY_SCOPE = [
    ("Strategy", [("Monthly planning sit-down (topics + hooks)", "1"), ("Content calendar & scripts / talking points", "1"), ("Monthly performance review call", "1")]),
    ("Content", [("Reels / short videos (IG, LinkedIn, YouTube Shorts)", "10–12"), ("LinkedIn thought-leadership posts", "8"), ("Instagram carousels & quote posts", "4–6"), ("Long-form video (podcast / talk) on YouTube", "1–2"), ("Instagram Stories", "12+")]),
    ("Community", [("Account management on all platforms", "✓"), ("Comment & DM replies (non-sensitive, on agreed guidelines)", "Daily"), ("Engagement with peers & target voices", "Weekly")]),
    ("Outreach", [("Podcast host & creator pitches", "4+"), ("Event & organiser pitches", "4+"), ("Podcast shoot coordinated", "1")]),
    ("Reporting", [("Weekly snapshot (WhatsApp / email)", "4"), ("Monthly report: growth, top content, next moves", "1")]),
]

FOUNDATION_ITEMS = [
    "Discovery sit-down (2–3 hrs) on your values, vision and nature",
    "Personal brand strategy document: positioning, voice, pillars, do’s & don’ts",
    "Audit and optimisation of Instagram, LinkedIn & YouTube profiles",
    "Bio, headline and featured-section copy",
    "Branded visual templates for posts, carousels & thumbnails",
    "Speaker & podcast-guest one-sheet (media kit)",
    "90-day content calendar",
]

ROADMAP = [
    ("Weeks 1–2", "Foundation", ["Discovery sit-down", "Profile audit & optimisation", "Strategy document signed off", "Speaker one-sheet ready"]),
    ("Weeks 3–4", "First shoot", ["First studio shoot", "First 8–10 posts live", "Podcast & event pitching begins", "Baseline metrics recorded"]),
    ("Months 2–3", "Build credibility", ["Weekly posting rhythm", "First podcasts recorded", "First talk invitations", "Format tuning from data"]),
    ("Months 4–6", "Grow reach", ["Larger podcasts & stages", "TEDx application with a tested talk", "Best formats scaled", "6-month review & plan"]),
]

KPIS = [
    ("Consistency", "Posts published vs plan", "24–28 every month", "Commitment"),
    ("Podcasts", "Episodes recorded", "1 / month · 6 by month 6", "Commitment"),
    ("Outreach", "Host & organiser pitches sent", "8+ / month", "Commitment"),
    ("Audience", "Followers, reach, engagement rate (IG + LinkedIn)", "Baseline in week 2; targets agreed after month 1", "Tracked"),
    ("Attention", "Watch time, saves, shares, profile visits", "Month-on-month growth", "Tracked"),
    ("Credibility", "Inbound invites, collaboration & press requests", "Logged and reported monthly", "Tracked"),
    ("Stages", "Talks delivered", "2–3 talks by month 6; TEDx application ready", "Goal"),
]

WHY = [
    ("16+ years", "of branding and digital marketing experience in Bengaluru."),
    ("120+ brands", "served across India, UAE, US and UK."),
    ("150+ projects", "delivered, from startups to enterprise brands."),
    ("In-house", "video production. Strategy, shoot, edit and posting by one team, with no hand-offs between agencies."),
]

TERMS = [
    "All fees are in INR and exclusive of 18% GST.",
    "Brand Foundation is billed on signing. It is waived on a 6-month agreement.",
    "Monthly retainer and production packages are billed in advance by the 5th of each month.",
    "One-off shoots and add-ons: 50% at booking, 50% on delivery.",
    "Minimum term of 3 months; 6 months recommended. Either party may end the agreement after that with 30 days’ written notice.",
    "Shoots rescheduled with less than 48 hours’ notice are charged at 50% of the shoot fee.",
    "Two rounds of revisions are included per content piece.",
    "Outstation travel, stay and venue fees for shoots outside Bengaluru are billed at actuals with prior approval.",
    "Paid promotion budgets, event registration fees and third-party podcast fees, if any, are not included.",
    "You own your accounts and all final content. iOceane keeps raw footage for 6 months and shows work only with your approval.",
    "We commit to effort, quality and deliverables. Follower counts, virality and selection by podcasts, events or TEDx depend on third parties and cannot be guaranteed.",
    "Video production prices are estimates based on November 2026 Bengaluru market rates and are confirmed per shoot brief.",
]
