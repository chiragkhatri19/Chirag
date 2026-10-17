# Codex fix round 1: new bride face, redo the anchor and all ten event scenes, repair the street

Use the same setup and QC loop as `PROMPT.md`, with the changes below. Overwrite the files in
`wedding-invite/codex/out/`, update `qc_log.json`, `windows.json` and `contact_sheet.jpg`, then commit and push.

## Step 0: rebuild the bride's face (do this first)

The client says the bride's face is wrong everywhere. Three **real photos** of her are now in
`refs/bride_photo_1.jpg`, `bride_photo_2.jpg` and `bride_photo_3.jpg`. They are the only source of
truth for her face. Section 1 of `PROMPT.md` has the corrected description: oval face, strongly arched
thick eyebrows, wide-set large eyes, a small mole on her right cheek beside the nose, and centre-parted
hair pulled back. **Never use `refs/bride_headshot.png` again.**

**Regenerate `01_anchor_couple`.** Call `images.edit` on the current `out/01_anchor_couple.png` with a
mask covering only the bride's head and neck. Attach the three bride photos as references. Prompt:

> Repaint only the bride's face and head so she is an exact, instantly recognisable likeness of the
> woman in the three attached photos: oval face, softly defined chin, thick strongly arched dark
> eyebrows, large wide-set dark-brown eyes, straight nose, the small mole on her right cheek beside
> the nose, and a gentle closed-lip smile. Hair centre-parted and pulled back into a low bun, with the
> same maang tikka and jhumkas. Keep the exact same painted gouache illustration style, line quality,
> lighting and subtle caricature proportions as the rest of the image. Change nothing outside the mask.

QC: compare the bride against all three photos. She must score 9 or more for likeness, including the
mole and the brows. The groom and everything else must stay pixel-identical. Save it over
`out/01_anchor_couple.png`, then use this new version as the master for every E-job below.

## Why the scenes are redone

The client approved the **style of `out/01_anchor_couple.png`** (and, from now on, its new bride). All ten event scenes (E01–E10) are rejected,
for three reasons:
- **The old `pose_*.png` references dragged in the wrong look.** They pulled faces toward the earlier,
  wrong likeness, especially the bride, and toward a glossy, photo-filter rendering.
- **Every face has the same frozen front-facing pose and smile.** It looks like the same head pasted
  into each scene.
- **The couple is too large** (about 63% of the image height) and too saturated against the soft
  gouache backgrounds.

## New rules for every E-job

1. **References:**
   - Attach ONLY `refs/groom_headshot.png`, `refs/bride_photo_1.jpg`, `refs/bride_photo_2.jpg`,
     `refs/bride_photo_3.jpg`, the new `out/01_anchor_couple.png`,
     and one `refs/style_scene_day.jpg` or `refs/style_scene_night.jpg` (whichever matches the time).
   - **Never attach any `pose_*.png`.** Describe the outfits in words only (given below).
2. **`01_anchor_couple.png` is the master.** Draw the couple exactly as in that image: same faces, same
   painting technique, same line quality, same skin rendering, same subtle caricature proportions.
   Every scene must look like the same artist drew it on the same day.
3. **Vary the face posture in every scene.** Each scene below gives the head angle, gaze and
   expression for both people. Follow it exactly. No two scenes may share the same head angle plus
   expression, and **no scene may copy 01's front-facing waving pose**. Likeness must hold in every
   angle: three-quarter, profile-leaning, looking down, laughing, eyes closed.
4. The couple fills about **40–45% of the image height**, full figure, in the lower half. **The top 35%
   is calm sky, canopy or plain wall** for text. No heads, hands or props up there.
5. Colour: soft and slightly muted, to sit naturally inside the gouache background. Use the same warm
   light as the scene, no glossy highlights, and a little paper grain over the figures too.
6. Bride's face (repeat this in every prompt):
   > Her face must match the three attached bride photos and the bride in 01_anchor_couple.png exactly:
   > oval face, softly defined chin, thick strongly arched dark eyebrows, large wide-set dark-brown eyes,
   > straight nose, the small mole on her right cheek beside the nose. Do not beautify, slim or change her face.

## The ten scenes (keep each scene's setting from `PROMPT.md`; outfits, poses and faces as below)

`E01_ganesh_sthapana` (midday, haveli courtyard, Ganesha idol on a red chowki):
- Groom: saffron silk kurta, cream dhoti, maroon-gold stole, red tilak.
- Bride: red-and-yellow bandhej saree, gold temple jewellery, gajra in her bun.
- Pose: both shown in profile-leaning three-quarter view, **facing the idol**, with folded hands.
- Faces: eyes softly closed in prayer, a gentle serene smile. She holds a small puja thali in one hand.

`E02_mayra_swagat` (late afternoon, decorated haveli entrance, gift trays and relatives behind):
- Groom: maroon silk bandhgala over a cream kurta.
- Bride: rani-pink Rajputi poshak with gota-patti, odhni on the back of her head.
- Pose and faces: both **turned toward the arriving relatives on the left**, heads slightly bowed in
  respect. He has his hand on his heart, she has folded hands. Warm, welcoming smiles, eyes looking
  left, not at the viewer.

`E03_ring_ceremony` (dusk rooftop, fairy lights, rose arch):
- Groom: midnight-blue velvet bandhgala, black trousers.
- Bride: blush-pink and champagne sequinned lehenga, diamond choker, hair in a low bun.
- Pose: **facing each other in profile.** He slips the ring onto her finger.
- Faces: both **look down at the ring**. She is laughing with her eyes squeezed happily; he has a
  shy grin.

`E04_carnival` (morning lawn, canopies, balloons, game stalls, an anchor's mic stand):
- Groom: turquoise and orange printed short kurta, white pants, holding a scorecard.
- Bride: mustard-yellow and pink printed co-ord set, holding a small gold trophy at chest height.
- Pose and faces: she is mid-celebration, head tilted back, **laughing open-mouthed** toward him. He
  looks at her in mock disbelief, eyebrows raised, one hand on his head. Three-quarter views.

`E05_bandoli` (early evening lane, string lights, a dholi with a dhol):
- Groom: mustard printed Jodhpuri bandhgala, white churidar, leheriya safa.
- Bride: pink and orange leheriya saree.
- Pose: mid folk-dance, **turned toward each other**. He has one arm up and his head turned over his
  shoulder toward her.
- Faces: she is clapping, head tilted to one side, smiling at him, with a big festive grin.

`E06_sangeet` (night palace courtyard, chandeliers, dance floor, starry sky):
- Groom: black Indo-western sherwani with silver embroidery.
- Bride: deep purple and magenta mirror-work lehenga.
- Pose: a ballroom-style twirl. **He holds her raised hand as she spins**, her skirt flaring.
- Faces: she is looking over her shoulder at the viewer with a bright smile; he looks at her, smiling.
- Hands must be perfect: five separate fingers each.

`E07_ghadi_vinayak` (midnight temple corner, many diyas, stars):
- Groom: cream kurta with a maroon stole.
- Bride: maroon silk saree, pallu over her head (face fully visible).
- Pose: **seated side by side** on a low wooden patla, lighting a diya together, one hand each on the lamp.
- Faces: looking down at the flame, calm and devotional, lit warmly from below.

`E08_haldi_janeu` (sunny courtyard with yellow marigold curtains, brass urlis of haldi):
- Groom: yellow dhoti, white janeu thread across his chest, marigold garland.
- Bride: yellow floral lehenga with flower jewellery.
- Pose: seated on patlas. **She playfully smears haldi on his cheek**; he scrunches his face and laughs
  with his eyes closed. She grins mischievously at him.
- Faces: haldi on both their cheeks.

`E09_baraat` (afternoon palace gate, brass band, umbrellas, marigold arches):
- Groom alone on a decorated white mare, in an ivory-and-gold sherwani with a red safa, kalgi and pearls.
- Pose and face: **chin up, proud regal smile**, head turned in three-quarter view toward the viewer,
  one hand raised in a greeting.

`E10_mangal_phera` (night mandap, marigold canopy, havan kund fire):
- Groom: ivory-and-gold sherwani, red safa.
- Bride: red bridal lehenga with dupatta on the back of her head, kundan bridal jewellery, red chooda.
- Pose: **walking around the fire in side profile**, she one step behind him, with the gathbandhan
  knot linking his stole to her dupatta.
- Faces: she looks down shyly with a soft smile; he glances back over his shoulder at her. Keep the
  fire clear of her lehenga.

## QC additions

On top of the QC in `PROMPT.md`, each E-job is checked on these points:
- **likeness to the groom headshot and the three bride photos, in the given angle**
- **match to `01_anchor_couple.png` style**
- **face posture differs from 01 and from every earlier E-job**: same angle plus same expression fails
- **the brief's specific pose and expression are followed**
- **top 35% is clear**

Every score must be 9 or more. Up to 5 attempts each.

## Street panorama: repair the two seams (no pillars)

1. Start from the original `out/P_panorama.png`.
2. For each segment join (near x≈934 and x≈3676), take a 1024×1536 window centred on it.
3. Mask a 320 px vertical band centred on the join, and run `images.edit` with:
   > Continue the sandstone haveli wall seamlessly through the masked band. The carved quatrefoil frieze
   > band and the plinth moulding continue at exactly the same heights as on both unmasked sides. The
   > dusty ground matches the same tone and texture with no light haze. Add no pillar, column or new object.
4. Paste the result back.
5. Remove the whitish ground haze around x 3700–4100, y > 1250 the same way.
6. To the left of the day-3 window, keep a plain smooth plaster panel at least 260 px wide and 500 px
   tall, completely clear (this is `monogram_end`).
7. Re-measure `windows.json`. Set `monogram_start` to the plain panel at about x 240–480, y 600–1050,
   and set `monogram_end` to the new panel.

QC: no visible seam at 100% zoom, frieze and plinth lines continuous across both joins, no green
window covered.
