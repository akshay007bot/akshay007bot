# iOceane — 31s brand ad

**Deliverables** (`out/`)
- `ioceane_ad_16x9.mp4` — 1920×1080, YouTube / LinkedIn / website
- `ioceane_ad_9x16.mp4` — 1080×1920, Instagram Reels / Shorts / Stories / WhatsApp status

Both: 31 s, 30 fps, H.264 + AAC, loudness -14 LUFS (social standard).

**Brand system used** (pulled from ioceane.com): logo + crescent mark, ocean blue `#009FFF`, mint `#00FFAB`,
deep navy background, Comfortaa (headlines, matches logo) + Inter (body), line "make brands infinite",
the site's own service hero images, and facts as stated on the site (16+ years, 150+ projects, Bengaluru, free 30-min strategy call).

**Script / beats**
| Time | On screen | Voiceover |
|---|---|---|
| 0–4.5s | Most brands get seen. / Few get remembered. | same |
| 4.5–10s | Crescent mark, "An AI-driven creative agency", Creativity + AI + Strategy | At iOceane, we blend creativity, AI, and strategy to change that. |
| 10–15.5s | 5-cut montage: Branding, Websites, SEO & AI Search, Video, AI Automation | the service names |
| 15.5–18s | Everything your brand needs. Under one roof. | same |
| 18–22s | 16+ years, 150+ projects, Made in Bengaluru | Sixteen years. A hundred and fifty plus projects. |
| 22–31s | Logo, "Let's make your brand infinite.", CTA, ioceane.com · +91 90199 31101 | iOceane. Let's make your brand infinite. Book your free strategy call at ioceane.com. |

**Rebuild**: `python3 make_music.py 31 audio/music.wav`, `node render.js land` and `node render.js port` (Playwright), then the ffmpeg mix (VO delayed 0.5 s, music side-chain ducked, loudnorm -14 LUFS).

Voice: ElevenLabs "Prashant Nair – Warm Indian Narrator" (`audio/vo.mp3`). Music: original, synthesized in `make_music.py` (royalty-free).
