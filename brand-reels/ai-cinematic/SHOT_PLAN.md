# AI cinematic reels: shot plan (ready for Kling)

Goal: 4 Instagram reels (9:16, ~30 s) that look like real cinema, not motion graphics.
Generate each shot with Kling (9:16, 5 s, highest quality), then cut them together with the
EXISTING voice-overs/music in `../<film>/audio/` and add brand text + logo overlays.
Every shot = one VO line (bar = 3 s): hold 3 s of each 5 s clip, use the extra for transitions.

Style for every prompt (append): `cinematic 35mm film look, shallow depth of field, anamorphic lens
flare, natural film grain, smooth gimbal camera move, photorealistic, 9:16 vertical`.
Rules: no real hospital/brand names or logos inside AI footage (we overlay the real ones), no text in
the generated video, no faces of real people, nothing that implies a medical outcome guarantee.
Voice-overs: reuse `vedrx-story`, `annova-3d`, `ioceane-split`, `mrcomm-city` (`audio/vo.wav`, `vo.json`).

## 1 · VedRx Tours (VO: vedrx-story)
| bar | VO | shot prompt |
|---|---|---|
| 0 | Meet Amara. She needed treatment, and answers. | A woman in her 30s sits by a window at night, her phone lighting her thoughtful face, city lights blurred behind, slow push-in |
| 1 | Then she found VedRx Tours. | Close-up of hands holding a smartphone, screen glow on face, she smiles softly, warm light |
| 2 | She shared her medical reports. | Top-down shot of medical reports and an X-ray on a wooden desk, a hand slides them into a folder, slow dolly |
| 3 | She compared hospitals in Bengaluru. | Aerial drone shot over a modern Bengaluru skyline at golden hour, glass hospital buildings among trees, slow forward glide |
| 4 | And got a personalized estimate. | A friendly coordinator at a bright desk turns a laptop toward the camera, soft daylight, shallow focus |
| 5 | Visa, travel and stay were coordinated. | Airplane window view above clouds at sunrise, wing glinting, gentle motion |
| 6 | In India, her care coordinator met her. | Airport arrivals hall, a coordinator in teal scrubs smiles and waves at a traveller with a suitcase, warm light |
| 7 | Her care was planned with the hospital's team. | Modern hospital consultation room, doctor and coordinator explaining a plan to a patient, bright clean light |
| 8 | Back home, she stays connected for follow-up. | Woman at home in morning sunlight on a video call on a laptop, relaxed and smiling |
| 9 | Your journey can start today. | Slow drone pull-back over a calm Bengaluru avenue lined with trees at sunset (end card overlays logo + phone) |
Overlay the site's disclaimer on the end card: "Illustrative story. Outcomes depend on individual circumstances."
Client rules: no Taj Mahal; show Bengaluru; IVF beyond Apollo (names only as text overlays).

## 2 · ANNOVA 360 (VO: annova-3d)
| bar | VO | shot prompt |
|---|---|---|
| 0 | It starts on paper. | Architect's hand drawing a modern villa floor plan with a fine pen on tracing paper, warm desk lamp, macro |
| 1 | Every line, approved by you. | A client's hand signs an architectural drawing, gold pen, shallow depth of field |
| 2 | Then we build it. Exactly. | Construction site of a modern concrete villa at dawn, slow crane-up past rebar and formwork |
| 3 | Architecture. Construction. | Low-angle shot of a minimalist concrete and glass facade, sunlight sweeping across it |
| 4 | Interiors. Turnkey delivery. | Slow dolly through a luxury living room with warm wood panelling and a statement pendant light |
| 5 | One team, from sketch to site. | Team of architects and site engineers reviewing drawings on a tablet at a construction site, golden hour |
| 6 | What you approve... | Night exterior of a luxury modern villa with infinity pool, warm interior glow, slow drone approach |
| 7 | is what you get. | Same villa, camera glides along the reflecting pool toward the glass living room |
| 8 | Signature spaces across Bengaluru. | Use the REAL project photos (Ankuraa Lotus, Venus Communiti, residence) with slow camera moves |
| 9 | Book a private consultation. | Hand turning a key in a modern wooden door, warm light (end card: logo, phone) |

## 3 · iOceane (VO: ioceane-split) · split screen: top = dull, bottom = premium
| bar | VO | top half prompt (dull, grey) | bottom half prompt (premium) |
|---|---|---|---|
| 0 | Same business. Two very different brands. | Plain empty shop counter under flat fluorescent light | Same counter styled beautifully, warm cinematic light, customers |
| 1 | One has a logo. One has an identity. | Generic printed paper sign taped to a wall | Glowing branded neon sign on a textured wall |
| 2 | One posts. One gets noticed. | Phone showing a dull scrolling feed, bored thumb | Creator filming a stylish reel with a ring light |
| 3 | One is hidden. One gets found. | Dim empty street at night | Busy lit-up storefront with a queue |
| 4 | One has a website. One converts. | Laptop with a loading spinner in a dark room | Laptop on a bright desk, a hand clicks "book" |
| 5 | One boosts posts. One runs campaigns. | Person shrugging at a phone | Marketing team at a big screen of rising charts |
| 6–9 | full screen | — | Agency team brainstorming in a modern office; brand screens; end card with iOceane logo + "Book Free Strategy Call" |

## 4 · MR Communications (VO: mrcomm-city)
| bar | VO | shot prompt |
|---|---|---|
| 0 | Every site needs a clear line. | Night city skyline, slow drone over rooftops, a red antenna light blinking |
| 1 | Construction crews. | Construction worker in a hard hat talking on a walkie-talkie, cranes behind, golden hour |
| 2 | Hotels and retail teams. | Hotel concierge in uniform speaking into an earpiece radio in a luxury lobby |
| 3 | Event crews and security. | Security staff with radios at a concert crowd, stage lights, night |
| 4 | Factories and warehouses. | Warehouse supervisor with a walkie-talkie between tall shelves, forklift passing |
| 5 | All connected by MR Communications. | Rooftop telecom antenna at dusk, signal light glowing, slow orbit |
| 6 | Radios, push to talk, and body cameras. | Use the REAL product photos (DMR radio, PoC device, body camera) with slow push-ins |
| 7 | Over a thousand devices deployed. | Rack of charging two-way radios with green LEDs in a dark room, slow slide |
| 8 | Twenty years of sales, rental and support. | Technician programming a radio on a workbench, warm light, macro |
| 9 | Upgrade the way your team communicates. | Hand pressing the push-to-talk button on a radio, close-up (end card: logo, phone) |

## Assembly (after clips are generated)
1. Download clips to `ai-cinematic/<brand>/clips/bar_00.mp4 … bar_09.mp4` (9:16).
2. Cut each to 3.0 s on the bar grid (`../<film>/beats.json`), 6-frame cross-dissolves only where motion matches.
3. Colour-grade per brand (VedRx teal/warm, ANNOVA gold/charcoal, iOceane blue/teal, MR amber/black).
4. Overlay: the VO words as large captions (brand fonts, same timing as `vo.json`), logo + CTA end card.
5. Audio: `../<film>/audio/mix.wav` (VO + music + SFX, already -14 LUFS).
