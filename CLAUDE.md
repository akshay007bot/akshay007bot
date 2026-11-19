# Creative studio project: notes for Claude

This folder makes cinematic brand reels (9:16 videos) and Instagram carousels for clients.
No GitHub is needed; everything runs locally from this folder.

## Tools in this folder
- `.claude/skills/motion-reel/`: the reel pipeline (gather a site's real assets, beat grid + synthesized
  music, shot list, canvas film, critique loop, frame-exact render, SFX, -14 LUFS mix). Use it for
  any reel, ad, promo or launch video. `<skill>` in its docs = `.claude/skills/motion-reel`.
  Run its scripts from `brand-reels/` (the project folder that holds the films).
- `tools/tts_kokoro.py`: natural voice-over, offline and free: `uv run tools/tts_kokoro.py script.json out_dir af_heart`.
- `brand-reels/carousels/render.mjs <brand> <Name>`: renders a carousel's `carousel.html` to
  1080x1350 PNGs + PDF and reports any text that runs into the footer. `sheet.sh` makes a preview strip.
- First-time setup on a new machine: `bash tools/setup.sh`.

## What is here
- `brand-reels/vedrx/`: Ved Rx Tours 30 s reel (film.js, VO, music, deliver/ mp4).
- `brand-reels/vedrx-carousel/`: VedRx carousel v1 and v2 (v2 is current).
- `brand-reels/carousels/`: iOceane, MR Communications, ANNOVA 360 carousels (+ vedrx copy, zip).
- `video/`: Kannada / English racing explainer video.
- `Open-Higgsfield-AI/`: open-source AI image/video studio (needs a Muapi.ai key; `npm install`,
  `npm run build:packages`, `npm run dev`).

## House rules (clients are strict)
- Real assets only: screenshots, photos, logos and wording from the client's own website. Never invent
  claims, prices, stats, reviews or screens. Keep the site's own disclaimers on medical content.
- Match brand colours and fonts exactly (gather.mjs pulls them from the site).
- Reels: a new hook every ~3 s; the B-roll must show exactly what the text/voice says; CTA at the end.
- Check every frame/slide at full size before delivering; fix overflow and contrast first.

## Client feedback log: Ved Rx Tours (vedrxtours.in)
- Multiple hooks, one every 3 seconds, so viewers reach the CTA. B-roll must match the text.
- Show Bangalore hospitals (Manipal, SPARSH, Apollo, Fortis, Narayana, Aster CMI, Ramaiah ...).
- IVF: do not show only Apollo Fertility; include Cloudnine, Rainbow & BirthRight, SPARSH Women &
  Children, Columbia Asia / Manipal (all listed in the site's hospital directory).
- Do NOT use the Taj Mahal to represent India. Use hospitals / medical cities (210 listings, 48 cities).
- TODO: the reel (brand-reels/vedrx) still has a Taj scene and an Apollo-only IVF scene; update it.

## Next job: AI cinematic reels (in progress)
The user found the code-drawn reels too flat ("looks like ppt") and wants very high-end, cinematic
footage. Plan: generate real-looking shots with the Kling AI connector, then cut them with the existing
voice-overs. Full shot list and assembly steps: `brand-reels/ai-cinematic/SHOT_PLAN.md`.
Tell the user the total cost before generating; generate one test shot first and show it.
