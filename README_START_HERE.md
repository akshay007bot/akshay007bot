# Creative Studio Kit: start here

Everything from this project in one folder: brand reels, carousels, voice-over tools and the
open-source AI studio. It works **without GitHub**. Unzip it, open the folder in Claude Code, and ask.

## 1. One-time setup (new computer)

Install these four things:

| Tool | Mac | Windows | Why |
|---|---|---|---|
| Node.js 20+ | nodejs.org | nodejs.org | renders reels and carousels |
| ffmpeg | `brew install ffmpeg` | `winget install ffmpeg` | video encoding |
| uv (Python) | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `winget install astral-sh.uv` | music, beats, voice |
| Claude Code | claude.com/claude-code (desktop app or CLI) | same | does the work |

Then, inside the unzipped folder:

```bash
bash tools/setup.sh          # installs Playwright + Chromium for rendering
```
(Windows without bash: `cd brand-reels`, `npm install`, `npx playwright install chromium`.)

## 2. Open it in Claude Code

Open **this folder** as the project (Claude desktop: "Open folder"; CLI: `cd` here and run `claude`).
Claude reads `CLAUDE.md` automatically and finds the reel skill in `.claude/skills/motion-reel`,
so it already knows the workflow and the clients' feedback.

## 3. What to ask

**Cinematic reel or ad**
> Make a 30 s cinematic 9:16 brand reel for https://example.com with a natural voice-over.
> A new hook every 3 seconds, B-roll matching the text, CTA at the end.

Claude will: pull the site's real screenshots, photos, logo, fonts and colours → make music on a
beat grid → show you a shot list to approve → animate → review it itself → render a 60 fps MP4.

**Carousel**
> Make a 10-slide Instagram carousel for https://example.com in its brand colours, using only the
> site's real content. Render with brand-reels/carousels/render.mjs.

**Voice-over only**
```bash
uv run tools/tts_kokoro.py my_script.json my_voice af_heart
```
Voices: `af_heart` (warm female, default), `af_bella`, `am_michael` (male), `bf_emma` (UK female), `bm_george` (UK male).

## 4. Where things are

| Folder | Contents |
|---|---|
| `brand-reels/vedrx/deliver/` | Ved Rx Tours reel (MP4 + poster) |
| `brand-reels/vedrx/` | that reel's source: `film.js`, `audio/`, `docs/shotlist.md` |
| `brand-reels/carousels/` | iOceane, MR Communications, ANNOVA 360, VedRx carousels + `Brand_Carousels.zip` |
| `brand-reels/vedrx-carousel/v2/` | VedRx carousel v2 (with the client's latest changes) |
| `video/out/` | racing explainer videos (Kannada + English) |
| `Open-Higgsfield-AI/` | open-source AI image/video studio (needs a Muapi.ai API key) |
| `.claude/skills/motion-reel/` | the cinematic reel pipeline |
| `tools/` | setup and voice-over scripts |

## 5. Re-render something that already exists

```bash
cd brand-reels
node carousels/render.mjs carousels/ioceane iOceane     # carousel → PNG + PDF (run from brand-reels)
node ../.claude/skills/motion-reel/scripts/render.mjs --film vedrx --format 9x16 --video-only
node ../.claude/skills/motion-reel/scripts/mix.mjs vedrx  # → out/vedrx/final.mp4
```

## 6. Optional: restore the git history

`akshay007bot_history.bundle` (if you downloaded it) holds every commit:
```bash
git clone akshay007bot_history.bundle my-project
```
