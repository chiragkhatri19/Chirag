# Veeral weds Konika — Rajasthani wedding invite video

`veeral-weds-konika-invite.mp4`: 1080×1920 (9:16, ready for WhatsApp, Instagram or Status), 30 fps, about 94 s, with a synthesized background score.

## What's in the video

| # | Slide | Caricature |
|---|-------|-----------|
| 1 | Palace doors open → ॥ श्री गणेशाय नमः ॥ with the Vakratunda shloka | — |
| 2 | Title: शुभ विवाह · Veeral weds Konika, with elephants and a V&K crest | lehenga look |
| 3 | सादर आमंत्रण: चि. वीरल संग सौ. कां. कोनिका, 19–21 November 2026 | — |
| 4 | प्रथम दिवस: गुरुवार, 19 नवम्बर 2026 (day schedule) | library look |
| 5–7 | गणेश स्थापना (दोपहर 12:05) · मायरा स्वागत (शाम 4:15) · रिंग सेरेमनी (शाम 7:15) | library look |
| 8 | द्वितीय दिवस: शुक्रवार, 20 नवम्बर 2026 | garden look |
| 9–12 | कार्निवल (सुबह 8:00) · बंदोली (शाम 4:00) · संगीत संध्या (शाम 7:00) · घड़ी विनायक (रात 12:15) | garden look |
| 13 | तृतीय दिवस: शनिवार, 21 नवम्बर 2026 | lehenga look |
| 14–16 | हल्दी एवं जनेऊ (सुबह 8:00) · बारात प्रस्थान एवं बंदोली (दोपहर 3:00) · मंगल फेरा (रात्रि 7:21 – 9:34) | lehenga look |
| 17 | Finale: all three looks together, "आपके आगमन की प्रतीक्षा में" | all |

Each event slide has its own colour theme, an icon medallion (Ganesha, mayra gift thaal, rings, Ferris wheel, dhol, tabla, clock at 12:15, haldi bowl with janeu, safa, agni kund), and matching particles: marigold petals, rose petals, confetti, music notes, stars or embers.

## Editing text, times or colours

All content lives in `index.html`, in the `DAYS` and `EVENTS` arrays near the top of the script. Open `index.html` in a browser to preview it live, then tap to play it with music.

## Re-rendering

```bash
# video (headless Chromium + ffmpeg); about 4 minutes on 4 cores
NODE_PATH=$(npm root -g) node tools/render.mjs video veeral-weds-konika-invite.mp4 --audio assets/music.m4a
# single frames for checking
NODE_PATH=$(npm root -g) node tools/render.mjs stills /tmp/stills 11 29 83
# music
python3 tools/make_music.py /tmp/music.wav 93.8 && ffmpeg -y -i /tmp/music.wav -c:a aac -b:a 192k assets/music.m4a
```

## Caricatures

`assets/caricature_*.png` are generated from the couple's photos by `tools/cutout.mjs` (background removal) and `tools/make_caricatures.py`. The second script finds the faces, enlarges the heads with a smooth chin-anchored warp, then adds cel shading, soft ink lines and a white sticker outline. The original photos are not in this repository; see the docstring at the top of `make_caricatures.py` for how to run it. If you get hand-drawn caricatures from an artist, save them over these three PNGs (transparent background) and re-render.
