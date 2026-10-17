# Veeral weds Konika: Rajasthani wedding invite video

`veeral-weds-konika-invite.mp4` is a 1080×1920 (9:16) video at 30 fps, about 72 s long, with a synthesized background score.

## Story

1. **A painted Rajasthani street.** The camera opens on a gold V&K monogram under "॥ श्री गणेशाय नमः ॥", with puppets swaying in the foreground and a cycle-rickshaw rolling past.
2. **The invitation.** An elder at his window unrolls a long cloth banner that reads श्री गणेशाय नमः, then the blessings, चि. वीरल संग सौ. कां. कोनिका, the dates and the venue.
3. **The couple's entry.** Veeral and Konika step out of the haveli doorway.
4. **Three days through three windows.** For each day, the camera pans to that day's window, shows the day card, then flies through the window into its events. Each event is its own painted scene, with the event name, time and venue. Between events the camera passes behind a pillar or drape, or through flowers or a burst of petals. After the last event the camera pulls back out to the street.
   - Day 1: गणेश स्थापना, मायरा स्वागत, रिंग सेरेमनी
   - Day 2: कार्निवल, बंदोली, संगीत संध्या, घड़ी विनायक
   - Day 3: हल्दी एवं जनेऊ, बारात प्रस्थान, मंगल फेरा
5. **Finale.** The couple waits at the palace gate under "आपके आगमन की प्रतीक्षा में", with the venue रुणिचा धाम, बालोतरा (राजस्थान).

## Files

| Path | What it is |
|------|------------|
| `index.html` | The whole animation, driven by `seek(t)`. Text, times and venue are in `DAYS` / `EVENTS` / `VENUE` near the top. |
| `assets/v2/` | Web-ready artwork made from `codex/out` by `tools/prep_assets.py` (the green day windows are keyed out). |
| `codex/` | The image-generation brief (`PROMPT.md`, `FIX1.md`), the reference images and the raw generated artwork. |
| `tools/render.mjs` | Frame-by-frame renderer (headless Chromium + ffmpeg). |
| `tools/render-reel.mjs` | Renderer for the short save-the-date teaser. |
| `reel-cards.html` | Botanical-paper “SAVE / THE DATE” card version of the teaser. |
| `tools/make_music.py` | Synthesized score: tanpura, santoor and dholak, with bells on each day change. |
| `index_v1.html` | The first, code-drawn version (kept for reference). |

## Save-the-date reel

`veeral-konika-save-the-date.mp4` is a 16-second vertical teaser built from the invite's gouache
artwork. It reveals Veeral and Konika, the dates (19–21 November 2026), and venue (Runicha Dham,
Balotra, Rajasthan), then closes on the mangal-phera scene. Re-render it with:

```bash
NODE_PATH=$(npm root -g) node tools/render-reel.mjs veeral-konika-save-the-date.mp4
```

The deterministic motion/layout source is `reel.html`; `tools/render-reel.mjs` captures it at 30 fps
and adds a short fade on the invite's existing instrumental score.

`veeral-konika-save-the-date-cards.mp4` is a second, playful 10-second treatment inspired by the
paper-and-card reveal format. On a light botanical background, Konika holds “SAVE” and Veeral holds
“ME!”; the joke then resolves to their names, date and venue. Re-render it with:

```bash
NODE_PATH=$(npm root -g) node tools/render-reel.mjs veeral-konika-save-the-date-cards.mp4 --page reel-cards.html
```

## Editing text, times or colours

All content lives in `index.html`, in the `DAYS` and `EVENTS` arrays near the top of the script. Open `index.html` in a browser to preview it live, then tap to play it with music.

## Re-rendering

```bash
python3 tools/prep_assets.py                       # after changing anything in codex/out
python3 tools/make_music.py /tmp/music.wav 71.65 4.6 4.6,19.4,34.45,52.9,65.75 \
  && ffmpeg -y -i /tmp/music.wav -c:a aac -b:a 192k assets/music.m4a
NODE_PATH=$(npm root -g) node tools/render.mjs video veeral-weds-konika-invite.mp4 --audio assets/music.m4a
NODE_PATH=$(npm root -g) node tools/render.mjs stills /tmp/stills 10 22 70   # single frames
```

If you change any timings, print `window.__TL` in the page to get the new day-change times for the music bells.
