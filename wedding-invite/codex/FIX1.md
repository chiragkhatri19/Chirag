# Codex fix round 1

Use the same setup, style rules, QC loop and `generate.py` as `PROMPT.md`. Fix only the four items below,
overwrite the files in `wedding-invite/codex/out/`, update `qc_log.json`, `windows.json` and `contact_sheet.jpg`,
then commit and push.

## 1. `E03_ring_ceremony`: regenerate fully

Reference images:
- Attach `refs/groom_headshot.png`, `refs/bride_headshot.png`, `out/01_anchor_couple.png` and
  `out/E01_ganesh_sthapana.png` for the faces and the style.
- **Do not attach `refs/pose_ring.png`.** Its bride has the wrong, slimmer face. Describe the outfit
  in text only.

Prompt: keep the E03 scene from `PROMPT.md` (dusk rooftop terrace, fairy lights, rose arch, violet sky,
he slips a ring onto her finger and both laugh). Outfits: groom in a midnight-blue velvet bandhgala with
gold embroidery and black trousers; bride in a blush-pink and champagne sequinned lehenga with a sheer
dupatta and a diamond choker. Add:

> The bride's face must match bride_headshot.png exactly: soft round face, full cheeks, wide softly
> rounded jaw, thick straight dark-brown eyebrows, wide smile showing teeth. Do NOT slim, narrow or
> lengthen her face. Her hair is in a low bun with a few loose strands, as in 01_anchor_couple. The top
> 35% of the image is calm sky only. The couple fills about 45% of the image height.

## 2. `E04_carnival`: regenerate fully

Reference images:
- Use the same face and style references as E03.
- **Do not attach `refs/pose_carnival.png`.** Its bride has the wrong face. Describe the outfit in text.

Prompt: keep the E04 scene from `PROMPT.md` (morning lawn, canopies, balloons, bunting, game stalls, an
anchor's microphone stand). Groom in a turquoise and orange printed short kurta and white pants,
holding a scorecard. Bride in a mustard-yellow and pink printed co-ord kurta set, holding a small gold
trophy at chest height. Both are laughing. Add the same bride-face paragraph as E03, then:

> The top 40% of the image is empty sky only: no branches, garlands or bunting in the top corners.
> Every head and the trophy stay below 42% of the image height. The couple fills about 45% of the
> image height.

## 3. `E06_sangeet`: masked inpaint of one hand only

Call `images.edit` on the existing `out/E06_sangeet.png` with a mask over the bride's raised hand only
(about x 800–960, y 580–780; find the exact region before masking). Prompt:

> Bride's raised right hand in a graceful open dance mudra, palm out, five separate slender fingers,
> thumb clearly visible, no crossed or merged fingers. Match the surrounding painting exactly.

Everything outside the mask must stay pixel-identical.

## 4. `P_panorama`: repair the two seams with masked inpainting (no pillars)

1. Start from the original `out/P_panorama.png`, not `P_panorama_fixed.png`, and delete
   `P_panorama_fixed.png`.
2. For each segment join (near x≈934 and x≈3676), cut a 1024×1536 window centred on the join.
3. Mask a 320 px-wide vertical band centred on the join and run `images.edit` with:

   > Continue the sandstone haveli wall seamlessly through the masked band. The carved quatrefoil frieze
   > band and the plinth moulding must continue at exactly the same heights as on both unmasked sides.
   > The dusty ground must match the same tone and texture, with no light haze. Add no pillar, column or
   > new object.

4. Paste the result back.
5. Also remove the whitish haze on the ground around x 3700–4100, y > 1250, with the same masked method.
6. To the left of the day-3 window, make sure there is a plain smooth plaster panel at least 260 px
   wide and 500 px tall, completely clear of objects. This is `monogram_end`.

QC: there must be no visible seam at 100% zoom, and the frieze and plinth lines must run continuously
across both joins. Re-measure `windows.json`. Set `monogram_start` to the plain panel at the left
(about x 240–480, y 600–1050) and `monogram_end` to the new panel. Do not cover any green window.
