# Codex fix round 2: face-only repaints for likeness

Use the same setup as `PROMPT.md`. **Only the faces change.** Every pixel outside each head mask must stay
identical, including outfits, poses, backgrounds and composition. Overwrite the files in
`wedding-invite/codex/out/`, update `qc_log.json` and `contact_sheet.jpg`, then commit and push.

## Why

The client says the faces look off in many scenes. A design-panel audit scored the bride's likeness at
3–6/10 in most scenes and the groom's at 4–7/10. The groom is drawn curly and round-faced, but he really
has a straight, upswept quiff and a long, angular face.

## Face references: always attach all of them

- **Bride:** `refs/bride_photo_1.jpg`, `refs/bride_photo_2.jpg`, `refs/bride_photo_3.jpg` (real photos).
- **Groom:** `refs/groom_photo_1.jpg`, `refs/groom_photo_2.jpg`, `refs/groom_photo_3.jpg` (real photos), plus
  `refs/groom_headshot.png`.
- Never use `refs/bride_headshot.png` or any `pose_*.png`.

## Who they are

- **Bride (Konika):** 27-year-old North Indian woman. Slim **oval** face with a narrow, tapered jaw and a
  long forehead. **Thick dark eyebrows**, softly arched with full inner heads. Large, wide-set, dark-brown
  almond eyes, **always open**. Straight medium nose with a rounded tip. Natural medium pink lips. A
  **small dark mole just beside her right nostril** (on the viewer's left in the painting). Wheatish-fair
  skin. Dark hair, centre-parted and smoothly pulled back, with no loose curls.
  - **Not:** round cheeks, pencil-thin brows, a doll face, or closed eyes.
- **Groom (Veeral):** 28-year-old North Indian man. **Long, narrow face**, high cheekbones and a strong
  angular jaw. **Dense full black beard** with a sharp cheek line, joined to a full moustache. Heavy,
  straight dark brows. Deep-set, slightly hooded brown eyes. Straight nose. **Thick dark hair in a
  textured upswept quiff with short sides, not curly.** Medium wheatish skin.

## Method, for each head below

1. Build a mask from the head box: pad it by 15% and feather it by 12 px.
2. Call `images.edit` with the scene image, the mask and the references.
3. Prompt:

> Repaint only the masked head in exactly the same painted storybook-Rajasthani gouache style, lighting,
> head angle, pose and expression as the original. Make the face an exact, instantly recognisable
> likeness of the person in the attached real photos: [paste the bride or groom description above].
> Keep the jewellery, headwear (turban/safa, dupatta, maang tikka), outfit and background unchanged.
> [scene note]

4. **QC:** use the vision model to compare a 3× crop of the new head with the real photos. Score
   likeness 1–10, and accept only 9 or more. Also check that the rest of the image is unchanged (mean
   absolute difference outside the padded mask must be under 1). Allow up to 5 attempts and keep the
   best one.

Head boxes are in output-image pixels (x0, y0, x1, y1), for 1024×1536 images. Re-detect the face first if
the box looks off by more than about 20 px.

| Image | Groom box | Groom scene note | Bride box | Bride scene note |
|---|---|---|---|---|
| `01_anchor_couple` | 315,10,520,260 | smiling at viewer | 455,115,615,320 | smiling at viewer, low bun with maang tikka |
| `E01_ganesh_sthapana` | 318,745,420,860 | gentle prayerful smile, straight quiff (not curly) | 438,812,515,905 | **eyes open**, softly looking toward the idol |
| `E02_mayra_swagat` | 425,688,527,818 | warm welcoming smile | 548,722,648,838 | warm smile, odhni stays on the back of her head |
| `E03_ring_ceremony` | 395,660,500,765 | turn him slightly so a three-quarter face is visible, looking at the ring | 518,702,602,802 | **eyes open**, looking at the ring, laughing softly |
| `E04_carnival` | 375,648,472,772 | mock-disbelief raised brows | 543,733,632,842 | laughing, eyes open |
| `E05_bandoli` | 355,715,455,842 | festive grin, safa unchanged | 588,788,672,882 | big festive smile |
| `E06_sangeet` | 318,712,417,818 | smiling at her | 585,766,652,842 | bright smile looking over her shoulder, **thick brows, no glam makeup** |
| `E07_ghadi_vinayak` | 290,590,490,780 | calm, eyes looking down at the flame (eyes visible) | 505,650,665,840 | calm, looking down at the diya |
| `E08_haldi_janeu` | 338,632,502,812 | laughing, keep the haldi on his cheek | 573,668,722,852 | mischievous grin, eyes open, haldi on her cheek |
| `E09_baraat` | 425,625,530,745 | proud regal smile, safa unchanged, eyes fully open | none | |
| `E10_mangal_phera` | 583,618,692,772 | glancing back at her, eyes open | 353,662,447,782 | **eyes open**, shy smile, dupatta on her head |

Do the bride in `01_anchor_couple`, `E03`, `E06`, `E01` and `E10` first; they were scored worst.

## Deliverable

The 11 updated PNGs in `out/`, plus `qc_log.json` with a `fix2` entry per head, listing the final
likeness score and the number of attempts. In your final message, list every head with its score.

## Also: the street ground patch

`out/P_panorama.png` has a washed-out, smoother rectangle of ground with a hard vertical edge, at about
x 4060–4608, y 1190–1536. Fix it with a masked `images.edit` on a 1024×1536 window covering x 3584–4608.
Mask x 4040–4608, y 1180–1536, feathered by 30 px, and use this prompt:

> Seamless continuation of the surrounding painted sandstone street ground: same warm ochre tone, same
> wavy dry-brush sand texture and grain as the ground to the left, light from upper left. No smooth or light
> patch, no rectangular tone change, no edges. Gouache style matching the adjacent area. Add no objects.

**QC:** at 100% zoom there must be no visible edge or tone change, and the palace gate steps and door must be
untouched. Paste the result back into `P_panorama.png`.
