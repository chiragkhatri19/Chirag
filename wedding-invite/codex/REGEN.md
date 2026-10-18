# Codex brief: regenerate every image of the couple with true likeness

**This replaces `FIX1.md` and `FIX2.md`.** Work fully autonomously and do not ask questions. Generate, check,
regenerate and save everything in one run, then commit and push.

## Tooling: use your built-in image generation, not the OpenAI API

- **Create and edit every image with your own built-in image generation / image editing tool.**
  - **Do NOT** use an `OPENAI_API_KEY`.
  - **Do NOT** call the OpenAI Images API.
  - **Do NOT** write a script that calls any external image API.
  - **Ignore** the API instructions in section 0 of `PROMPT.md`.
- **Reference images:** attach them directly to the image tool. Wherever this brief says "attach", it means give these files to your image tool as references.
- **Edits with a mask:** use the tool's edit or inpaint mode on the source image. If the tool cannot take a mask:
  1. Edit the cropped region.
  2. Composite it back yourself in Python with Pillow/OpenCV, using a feathered mask.
- **Sizes and transparency:** after generating, save every result as a PNG at the size this brief asks for (resize or crop with Pillow if needed). For cut-outs that need a transparent background:
  1. Generate on a plain flat background (pure white, or pure chroma green if white appears in the figure).
  2. Remove the background in Python, for example with `rembg`, or by chroma key plus edge decontamination.
- **Local Python is fine** for detection, cropping, upscaling, masks, compositing, face-ID QC and contact sheets. Install what you need with pip.
- **Visual QC:** look at the images yourself.

## Why the earlier images failed (do not repeat these mistakes)

The client says none of the generated images look like them. There were three causes:
1. **Wrong references.** Faces were taken from AI-made images (`groom_headshot.png`, `bride_headshot.png`,
   `pose_*.png`). Each generation copied the previous one's errors, so the faces drifted further every round.
2. **Faces too small.** In a full scene each face is only about 80–110 px wide, and at that size no image model
   can render a real likeness.
3. **Weak QC.** A vision model "scoring" likeness passed faces that people would never recognise.

The fixes below handle each of these.

## Rule 1: only real photos define the faces

Use only these files for faces:

| File | Who | Notes |
|---|---|---|
| `refs/bride_photo_1.jpg`, `bride_photo_2.jpg`, `bride_photo_3.jpg` | Bride (Konika) | Real close-up selfies. **The best source for her face.** |
| `refs/groom_photo_1.jpg`, `groom_photo_2.jpg`, `groom_photo_3.jpg` | Groom (Veeral) | Real face crops. **The best source for his face.** |
| `refs/real/couple_*.jpg` (7 photos) | Both | Real full photos of the couple together. Use them for body proportions, height difference, how they stand together, and the groom's hair. |

**Never attach** `bride_headshot.png`, `groom_headshot.png`, any `pose_*.png`, or any earlier file in `out/`
(except the new character sheets made in Step 1).

Selfies are mirror images. The bride's mole is **on her right cheek, just beside her right nostril**. In a
non-mirrored painting where she faces the viewer, it appears on the **viewer's left**.

### Who they are

**Groom, Veeral, 28:**
- Long, narrow face, high cheekbones, strong angular jaw.
- Dense, full black beard with a sharp, clean cheek line, joined to a full moustache, slightly fuller at the chin.
- Heavy, straight, thick dark eyebrows.
- Deep-set, slightly hooded dark-brown eyes.
- Straight nose.
- Thick black hair in a tall, textured, upswept quiff with short sides. It is NOT curly, NOT a fringe, NOT messy.
- Wheatish skin.
- Usually a calm, confident half-smile.

**Bride, Konika, 27:**
- Oval face, softly defined chin, gently full cheeks, long forehead.
- **Thick, dark, strongly arched eyebrows** with full inner heads.
- Large, wide-set, dark-brown almond eyes with long lashes.
- Straight nose with a softly rounded tip.
- **A small dark mole beside her right nostril.**
- Medium pink lips, usually a soft closed-lip smile.
- Fair-wheatish skin.
- Dark hair, centre-parted and pulled back smoothly.

**Never:** a round baby face, pencil-thin brows, a doll nose, westernised features, beautified or slimmed faces, or closed eyes (unless a scene note says so).

**Together:** he is about one head taller than her.

## Rule 2: build a character sheet first, then use it everywhere

### Step 1: character sheets (do these first, and loop until they pass)

**`CS_groom`** (1536×1024): a painted character model sheet of Veeral, plain warm-ivory background, no text.
- **Five head studies in a row:** front neutral, front smiling, three-quarter left, three-quarter right, profile.
- **Below them:** one full-body standing pose in an ivory bandhgala.
- **Refs:** all three groom photos and all 7 couple photos.

**`CS_bride`** (1536×1024): the same layout for Konika, in an emerald lehenga.
- **Refs:** all three bride photos and all 7 couple photos.

**Style for both:** the gouache style described in section 3 of `PROMPT.md`, with subtle caricature proportions (heads about 12% larger than natural) and exact likeness.

**QC for the sheets:**
1. Run the face-ID check (Rule 4) on every head on the sheet.
2. Each head must reach the threshold.
3. Regenerate up to 8 times and keep the best attempt.

The approved sheets are the identity anchors for every image that follows.

### Step 2: the images to regenerate

For every image below, attach:
- the two character sheets,
- the 3 photos of each person,
- and 2–3 of the `refs/real/couple_*.jpg` photos that best match the pose.

Generate in portrait 2:3 at the highest quality and resolution your image tool offers. Then save each result as 1024×1536.

**Composition:** the couple fills about 45% of the image height, full figure, in the lower half. The top 35% is
calm sky, canopy or plain wall, kept clear for text. No text anywhere in the image.

Keep each scene's setting from `PROMPT.md` section 4D. The outfits, poses and expressions are:

| Job | Outfits | Pose and expression (vary the head angle every time) |
|---|---|---|
| `01_anchor_couple` (cut-out, transparent) | ivory bandhgala with gold zig-zag; emerald lehenga, kundan choker, maang tikka, low bun | standing close, her hand on his chest, both smiling at the viewer, both waving with the free hand |
| `E01_ganesh_sthapana` | saffron silk kurta, cream dhoti, maroon stole; red-yellow bandhej saree | three-quarter view toward the Ganesha idol, folded hands, **eyes open** looking at the idol, serene smiles; she holds a puja thali |
| `E02_mayra_swagat` | maroon bandhgala over cream kurta; rani-pink poshak, odhni on the back of her head | turned toward relatives arriving on the left, he with a hand on his heart, she with folded hands, warm smiles |
| `E03_ring_ceremony` | midnight-blue velvet bandhgala; blush-pink and champagne lehenga, hair in a low bun | facing each other in three-quarter view, he slips the ring on her finger, both looking at the ring, she laughing |
| `E04_carnival` | turquoise and orange printed short kurta; mustard and pink co-ord kurta set | she holds up a small gold trophy and laughs, he holds a scorecard with raised brows in mock disbelief; heads below 42% of image height |
| `E05_bandoli` | mustard Jodhpuri bandhgala with leheriya safa (face fully visible); pink and orange leheriya saree | folk dance, his arm raised, looking over his shoulder at her; she claps with a big grin |
| `E06_sangeet` | black sherwani with silver embroidery; purple and magenta mirror-work lehenga | he holds her raised hand as she twirls, she looks back at the viewer smiling; five clear fingers on each hand |
| `E07_ghadi_vinayak` | cream kurta, maroon stole; maroon saree with pallu over her head (face visible) | seated side by side lighting a diya together, faces lit warmly from below, eyes looking down at the flame |
| `E08_haldi_janeu` | yellow dhoti, white janeu thread across his chest, marigold garland; yellow floral lehenga | seated on patlas, she smears haldi on his cheek and grins, he laughs with eyes squeezed shut |
| `E09_baraat` | groom alone: ivory and gold sherwani, red safa with kalgi, pearls, on a decorated white mare facing right | head turned three-quarters toward the viewer, chin up, proud smile, one hand raised |
| `E10_mangal_phera` | ivory sherwani with red safa; red bridal lehenga, dupatta on the back of her head, kundan jewellery, red chooda | walking around the havan fire in side view, gathbandhan knot, he glances back at her, she smiles shyly with eyes open |

## Rule 3: high-resolution face pass (this is what makes them look like them)

After each scene passes composition QC, refine every face separately at high resolution:

1. Detect each head with a face detector, for example `insightface` (`buffalo_l`) or `mediapipe`.
2. Crop a square around the head that is 2.2× the face height, centred on the face.
3. Upscale the crop to 1024×1024 (Lanczos).
4. Make a soft elliptical mask covering the face, hairline and ears, but not the headwear, jewellery or clothing. Feather it by 24 px.
5. Edit the 1024 crop with your image tool, inside the mask (see Tooling). Attach that person's 3 photos and their character sheet, with this prompt:

   > Repaint only the masked face as an exact, instantly recognisable likeness of the person in the attached real photos, in the same painted gouache style, lighting, head angle and expression as the surrounding image. [Paste that person's description from Rule 1.] Keep hair, headwear and jewellery unchanged.

6. Downscale the result and paste it back with the same feathered mask. Colour-match it to the surrounding skin in LAB.
7. Run the face-ID check (Rule 4). If it fails, repeat with a new seed, up to 6 times, and keep the best attempt.

## Rule 4: numeric face-ID QC (mandatory, no vision-model guesswork)

`pip install insightface onnxruntime opencv-python`, then use the ArcFace embeddings from `buffalo_l`.

**Reference embedding:** for each person, the mean embedding of their 3 photos plus their faces detected in the 7 `refs/real/couple_*.jpg` photos.

**Measure first:** compute the cosine similarity between each painted face and the reference.
- Painted faces score lower than photos, so first record the similarity of the approved character-sheet heads.
- Call the lowest of those `S_sheet`.

**Pass rule:**
- Every face in every scene needs a similarity of at least `max(0.30, S_sheet − 0.05)`.
- It must also pass your own visual check against the real photos. Every one of these distinctive features must be present:
  - **Groom:** upswept straight quiff, full beard with a sharp cheek line, heavy straight brows.
  - **Bride:** thick arched brows, oval face, the mole beside her right nostril (it may be hidden in profile).

**Wrong-person check:** also measure each groom face against the bride reference, and each bride face against the groom reference. Each face must be closer to the right person.

**Logging:** log every attempt's similarity scores to `out/qc_log.json` under `regen`.

## Rule 5: also fix the street ground patch

`out/P_panorama.png` has a washed-out, smoother rectangle of ground at about x 4060–4608, y 1190–1536.

1. Take a 1024×1536 window covering x 3584–4608.
2. Use a mask over x 4040–4608, y 1180–1536, feathered by 30 px.
3. Edit it with your image tool, inside the mask (see Tooling), using this prompt:

   > Seamless continuation of the surrounding painted sandstone street ground, same warm ochre tone, wavy dry-brush sand texture and grain as the ground to the left, light from upper left; no smooth or light patch, no rectangular tone change, no edges; add no objects.

4. Paste the result back. **Change nothing else in the panorama:** the window positions are used by the video.

**Do not regenerate** `02_rickshaw`, `03_puppets`, `B1_banner`, `F1`–`F4` or `P1`–`P5`. They contain no couple, and they are already approved.

## Deliverables

1. `out/CS_groom.png` and `out/CS_bride.png`.
2. The 11 couple images, overwritten in `out/`.
3. The fixed `out/P_panorama.png`.
4. `out/qc_log.json`, with a `regen` section listing every face's similarity and attempt count.
5. `out/faces_contact_sheet.jpg`. One row per image: each painted head cropped at 3×, placed next to the person's 3 real photos.
6. The updated `out/contact_sheet.jpg`.

Commit and push all of these. In your final message, list each face with its similarity score and `S_sheet`.
