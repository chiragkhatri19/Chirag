# Codex brief: the final 7 scenes plus the couple cut-out (true likeness)

**This brief replaces `PROMPT.md` sections 1 and 4, and `FIX1.md`, `FIX2.md` and `REGEN.md`.** It is self-contained: do
not read those files. Work fully autonomously and do not ask questions. Generate, check, regenerate and save
everything in one run, then commit and push.

The invite has been cut down from 10 event scenes to **7 slides**, several of which now cover two or three events. Only
**10 images** are needed:
- 2 character sheets (identity anchors, not used in the video);
- 1 couple cut-out;
- 7 scenes.

## 0. Setup and tooling

- **Branch:** `git pull` on branch `claude/veeral-konika-wedding-invite-pbr9tf` first.
- **Where to write:** only inside `wedding-invite/codex/out/`, plus any helper scripts you write in `wedding-invite/codex/tools/`. Do not touch `index.html`, `tools/`, `assets/` or the videos.
- **Image tool:**
  - Create and edit every image with **your own built-in image generation / image editing tool**.
  - **Do NOT** use an `OPENAI_API_KEY`, call the OpenAI Images API, or write scripts that call any external image API.
  - Attach reference images directly to the image tool.
- **Masked edits:** use the tool's edit or inpaint mode. If it cannot take a mask:
  1. Edit a crop.
  2. Composite it back in Python (Pillow/OpenCV) with a feathered mask.
- **Local Python** is fine for detection, cropping, upscaling, masks, compositing, background removal (`rembg`), face-ID QC and contact sheets. Install what you need with pip.
- **Size:** generate portrait 2:3 at the highest quality your tool offers, then save as **1024×1536 PNG** (except the character sheets, which are **1536×1024**).
- **Speed:** stop at the first attempt that passes QC. Never regenerate an image that already passes.

## 1. Faces: only real photos define them

Use **only** these files for faces (in `wedding-invite/codex/refs/`):

| Files | Who | Use |
|---|---|---|
| `bride_photo_1.jpg`, `bride_photo_2.jpg`, `bride_photo_3.jpg` | Bride, Konika | Real close-ups. The best source for her face. |
| `groom_photo_1.jpg`, `groom_photo_2.jpg`, `groom_photo_3.jpg` | Groom, Veeral | Real face crops. The best source for his face. |
| `real/couple_*.jpg` (7 photos) | Both | Real full photos: body proportions, height difference, how they stand, the groom's hair. |

**Never attach** `bride_headshot.png`, `groom_headshot.png`, any `pose_*.png`, or any older image in `out/`. They are AI-made and carry the wrong faces.

**Groom, Veeral, 28:**
- Long, narrow face, high cheekbones, strong angular jaw.
- Dense full black beard with a sharp, clean cheek line, joined to a full moustache.
- Heavy, straight, thick dark brows; deep-set, slightly hooded dark-brown eyes; straight nose.
- Thick black hair in a tall, textured, upswept quiff with short sides. It is NOT curly, NOT a fringe.
- Wheatish skin; a calm, confident half-smile.

**Bride, Konika, 27:**
- Oval face, softly defined chin, gently full cheeks, long forehead.
- **Thick, dark, strongly arched brows** with full inner heads.
- Large, wide-set, dark-brown almond eyes with long lashes; straight nose with a softly rounded tip.
- **A small dark mole beside her right nostril.** It is on the viewer's left when she faces the viewer.
- Medium pink lips, usually a soft closed-lip smile; fair-wheatish skin.
- Dark hair, centre-parted and pulled back smoothly.

**Never:** a round baby face, pencil-thin brows, a doll nose, westernised or beautified faces, or closed eyes.

**Together:** he is about one head taller than her.

## 2. Art style (identical for every image)

> Hand-painted gouache and watercolour illustration, in the style of a contemporary luxury Indian wedding invite
> inspired by Rajasthani miniatures. Warm sandstone and ochre palette with marigold orange, deep vermilion red,
> indigo, teal and soft green accents. Visible handmade-paper grain, soft dry-brush texture and gentle painterly
> shading; warm Rajasthani daylight, or warm lamp and diya light at night. Rich but soft detail: carved stone,
> jharokhas, wooden doors, marigold garlands, brass. Nothing glossy, 3D-rendered or photographic.

Match the existing art. Attach `refs/style_scene_day.jpg` or `refs/style_scene_night.jpg` (whichever fits) as a style reference, for style only and never for faces.

The couple:
- Subtle caricatures: heads about 12% larger than natural, elegant natural bodies, never chibi, **exact likeness**.
- Full figures; faces clearly visible and unobstructed (no veil or sehra over the face).
- Vary the head angle between images.

Rules for every image:
- **No text, letters, numbers, logos or watermarks.**
- Five fingers per hand; no extra or merged limbs.

## 3. Step 1: character sheets (do these first)

- **`CS_groom.png`** (1536×1024): a painted model sheet of Veeral on a plain warm-ivory background, no text. Five head studies in a row (front neutral, front smiling, three-quarter left, three-quarter right, profile), and below them one full-body standing pose in an ivory bandhgala. **Attach:** all 3 groom photos and all 7 couple photos.
- **`CS_bride.png`** (1536×1024): the same layout for Konika, in an emerald lehenga. **Attach:** all 3 bride photos and all 7 couple photos.

Run the face-ID check (section 6) on every head. **At most 4 attempts per sheet;** keep the best. These sheets are the identity anchors for everything that follows.

## 4. Step 2: the 8 images for the video

For every image, attach:
- both character sheets;
- the 3 photos of each person who appears;
- 2–3 `refs/real/couple_*.jpg` photos that best match the pose;
- the matching style reference.

**Scene composition (all 7 scenes):**
- Opaque 1024×1536.
- **The top of the image is a calm text zone**, because the event names, times and venue are written there. Over the full width it holds only soft, low-contrast sky, plain wall or plain fabric: no domes, chhatris, canopies, flower garlands, lit stone, balconies or other high-detail elements.
  - `E01_ganesh_sthapana` and `E06_sangeet` (they list two or three events): the **top 42%** (to y ≈ 645).
  - All other scenes: the **top 36%** (to y ≈ 553).
- The people stand in the lower 60%, full figure, about 45% of the image height.
- The scene's subject (Ganesha idol, ring, trophy, mare, fire) must also sit below the text zone.

**Overwrite these files in `out/`.** Keep the exact names, because the video pipeline reads them.

| File | Slide (events it covers) | Setting | Outfits | Pose and expression |
|---|---|---|---|---|
| `01_anchor_couple.png` | Couple entry and finale. **Cut-out on a transparent background**, nothing cropped, at least 40 px margin, no ground shadow. | none | ivory bandhgala with gold zig-zag embroidery, ivory churidar, cream mojari; emerald silk lehenga with gold zari border, kundan choker, maang tikka, low bun | standing close, her hand on his chest, both smiling at the viewer, both waving with the free hand |
| `E01_ganesh_sthapana.png` | **Ganesh Sthapana + Mayra Swagat** (day 1) | Midday haveli courtyard. **Lord Ganesha is the hero:** a large, ornate, gold-and-vermilion Ganesha idol, about 30% of the image height, on a red-draped, marigold-decked chowki under a small mandap, centre-right, with diyas and a brass kalash. In the soft background, a few relatives arrive through a carved gate carrying gift trays covered in red cloth (the Mayra), painted small and loose, faces simple. | saffron silk kurta, cream dhoti, maroon stole; red-and-yellow bandhej saree | The couple stands to the left in three-quarter view, turned toward Ganesha, **inviting him**: he in a welcoming namaste; she offering a puja thali with a lit diya. Eyes open, looking at the idol, serene smiles. |
| `E03_ring_ceremony.png` | **Ring Ceremony** (day 1, evening) | Dusk rooftop terrace with fairy lights, lanterns, a rose arch and a violet sky. | midnight-blue velvet bandhgala; blush-pink and champagne lehenga, low bun | Facing each other in three-quarter view; he slips the ring onto her finger; both look at the ring; she laughs. |
| `E04_carnival.png` | **Carnival** (day 2, morning): a hosted fun-and-games event | Bright morning lawn with colourful canopies, balloons, bunting, game stalls (ring toss, tin-can stack) and an anchor's microphone stand. | turquoise and orange printed short kurta; mustard and pink kurta set | She holds up a small gold trophy and laughs; he holds a scorecard with raised brows in mock disbelief. |
| `E06_sangeet.png` | **Bandoli + Sangeet Sandhya + Ghadi Vinayak** (day 2, evening to midnight). One Sangeet picture represents all three. | Night palace courtyard: chandeliers, ivory drapes, candles and a row of diyas along the floor edge, a wooden dance floor, a starry indigo sky. | black sherwani with silver embroidery; purple and magenta mirror-work lehenga | He holds her raised hand as she twirls; she looks back at the viewer, smiling; five clear fingers on each hand. |
| `E08_haldi_janeu.png` | **Haldi + Janeu** (day 3, morning). Haldi is the main picture. | Sunny courtyard hung with yellow marigold curtains, brass urlis of turmeric, low wooden patlas. | yellow dhoti, **white janeu thread across his bare chest**, marigold garland; yellow floral lehenga with flower jewellery | Seated on patlas; she smears haldi on his cheek and grins; he laughs, eyes squeezed shut; haldi on both cheeks. |
| `E09_baraat.png` | **Baraat Prasthan + Bandoli** (day 3, afternoon). **The groom alone**, no bride. | Outside a palace gate, with a brass band, colourful umbrellas and marigold arches. | ivory and gold sherwani, red safa with kalgi, pearl strings; **face fully visible**, no sehra over it | On a decorated white mare facing right; head turned three-quarters toward the viewer, chin up, proud smile, one hand raised. |
| `E10_mangal_phera.png` | **Mangal Phera** (day 3, night) | Night, under a red-and-gold mandap with a marigold canopy, a havan kund fire, diyas. | ivory sherwani with red safa; red bridal lehenga, dupatta on the back of her head (face visible), kundan jewellery, red chooda | Walking around the fire in side view, joined by the gathbandhan knot; he glances back at her; she smiles shyly, eyes open. |

Then run a composition check: text zone calm, full figures, correct outfits, hands correct, no text. **At most 3 attempts per image.**

## 5. Step 3: high-resolution face pass (this is what makes them look like them)

At a full-scene size a face is only about 100 px wide, and no model can render a likeness that small. So, for every face:
1. Detect each head with `insightface` (`buffalo_l`) or `mediapipe`.
2. Crop a square around it, 2.2× the face height, and upscale the crop to 1024×1024 (Lanczos).
3. Make a soft elliptical mask over the face, hairline and ears. Exclude headwear, jewellery and clothing. Feather it by 24 px.
4. Edit inside the mask with your image tool. Attach that person's 3 photos and their character sheet, with this prompt:

   > Repaint only the masked face as an exact, instantly recognisable likeness of the person in the attached real
   > photos, in the same painted gouache style, lighting, head angle and expression as the surrounding image.
   > [paste that person's description from section 1]. Keep hair, headwear and jewellery unchanged.

5. Downscale, paste back with the same feathered mask, and colour-match to the surrounding skin in LAB.
6. Run the face-ID check. **At most 3 attempts per face;** keep the best.

## 6. Face-ID QC (numeric, mandatory)

- **Setup:** `pip install insightface onnxruntime opencv-python`, and use ArcFace embeddings from `buffalo_l`.
- **Reference:** for each person, the mean embedding of their 3 photos plus their faces detected in the 7 couple photos.
- **Baseline:** the lowest similarity among the approved character-sheet heads is `S_sheet`.
- **Pass:** every scene face scores at least `max(0.30, S_sheet − 0.05)` **and** passes your own visual check:
  - Groom: upswept straight quiff, full beard with a sharp cheek line, heavy straight brows.
  - Bride: thick arched brows, oval face, the mole beside her right nostril (it may be hidden in profile).
- **Wrong-person check:** each face must be closer to the right person than to the other.
- **Log:** record every attempt's scores in `out/qc_log.json` under the key `final7`.

## 7. Do not touch

- `P_panorama.png`: the old street panorama stays as it is. Do not edit it.
- `02_rickshaw`, `03_puppets`, `B1_banner`, `F1`–`F4`, `P1`–`P5`: already approved.
- `E02_mayra_swagat`, `E05_bandoli`, `E07_ghadi_vinayak`: no longer used. Leave them and do not regenerate them.

## 8. Deliverables (commit and push all of them)

1. `out/CS_groom.png` and `out/CS_bride.png`.
2. The 8 images from section 4, overwritten in `out/` with the same names.
3. `out/faces_contact_sheet.jpg`: one row per image, with each painted head cropped at 3× next to that person's 3 real photos.
4. `out/contact_sheet.jpg`: the 8 images side by side.
5. `out/qc_log.json`, with the `final7` section.

Commit with a clear message and push to `claude/veeral-konika-wedding-invite-pbr9tf`. In your final message, list
every face with its similarity score, the attempt count and `S_sheet`.
