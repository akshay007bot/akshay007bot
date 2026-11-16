# iOceane promo video

A 55-second, 1920×1080 brand promo for iOceane, built with Remotion using
[claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit).

- **Final video:** `out/ioceane-promo.mp4` (normalised to -14 LUFS)
- **Storyboard:** `out/storyboard.png`
- **Scenes:** hook → "We Build Brands That Dominate" → 6 services → SEO results → stats → client logos → CTA
- **Voiceover:** Kokoro TTS (`af_heart` voice), one WAV per scene in `public/audio/s1–s7.wav`
- **Music:** original synthesised ambient bed, `public/audio/music.wav`

## Edit & re-render

```bash
npm install
npx remotion studio            # live preview
npx remotion render src/index.ts IoceanePromo out/ioceane-promo.mp4
```

Copy, stats and timings are all in `src/Promo.tsx` (`SCENES` holds each scene's length in frames at 30 fps).
`remotion.config.ts` points at `/opt/pw-browsers/chromium`; remove that line to use Remotion's own Chrome locally.
