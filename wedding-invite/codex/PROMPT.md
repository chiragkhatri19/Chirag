# Codex brief: generate all artwork for the "Veeral weds Konika" invite

You are generating every illustration for an animated 9:16 Rajasthani wedding-invite video. Another
tool animates these images later (camera pans, zooms, parallax, banner unroll), so **each image must
be a clean, separate asset**. Work fully autonomously. Do not stop to ask questions. Generate, check,
regenerate and save everything in one run.

---------------------------------------------------------------------------------------------------

## 0. Setup

1. The reference images are in `wedding-invite/codex/refs/` (see section 2). Read all of them first.
2. Write a Python script `wedding-invite/codex/generate.py` that uses the official `openai` Python SDK
   and the environment variable `OPENAI_API_KEY`.
   - Use the newest GPT image model available to the key: try `gpt-image-1.5`, then `gpt-image-1`.
   - Call **`client.images.edit`** whenever a job lists reference images, passing all of them in
     `image=[...]`. Use `images.generate` only for jobs with no references.
   - Always set `quality="high"`, `input_fidelity="high"` (keeps faces accurate), `output_format="png"`.
   - Use `background="transparent"` for CUT-OUT jobs, and `background="opaque"` for SCENE and
     PANORAMA jobs.
   - Size: `1024x1536` portrait unless a job says otherwise.
3. Save every final image to `wedding-invite/codex/out/<job_id>.png`, with exactly the job ids below.
4. Install anything you need (`pip install openai pillow numpy`). If a call fails with a rate-limit or
   server error, wait and retry. Never skip a job.

## 1. The couple (keep this identical in every image)

- **Groom: Veeral.** Indian man, late 20s, fair-wheatish skin. Thick, voluminous, swept-up black
  hair with a slight side quiff. Well-groomed full black beard, short on the cheeks and fuller on the
  chin, with a moustache joined to the beard. Thick straight eyebrows, warm brown eyes, confident
  gentle smile.
- **Bride: Konika.** Indian woman, late 20s, fair skin, soft round face with full cheeks, softly
  rounded jawline. Thick dark-brown eyebrows, large brown eyes, warm wide smile showing teeth. Dark
  brown hair.
- **Faces must be an exact, instantly recognisable likeness of the headshots in `refs/`.** Never
  beautify, slim, age, lighten or westernise them. Match face shape, eye shape, eyebrows, nose, lips,
  smile, beard and hairline. If a face drifts from the headshot, regenerate.

## 2. Reference files (already in `wedding-invite/codex/refs/`)

| file | what it is | how to use it |
|------|------------|---------------|
| `groom_headshot.png` | realistic close-up of the groom | face likeness, every job with the groom |
| `bride_headshot.png` | realistic close-up of the bride | face likeness, every job with the bride |
| `pose_traditional.png` … `pose_phera.png` | earlier illustrations of each outfit and pose | outfit, pose and jewellery reference for the job with the same name |
| `style_street.jpg`, `style_banner.jpg`, `style_window.jpg`, `style_scene_night.jpg`, `style_scene_day.jpg` | frames from the reference reel | **art style reference only.** Copy the painting technique, palette and texture, never the exact content |

Attach **both headshots plus the matching `pose_*.png`** to every job that shows the couple. Attach
the relevant `style_*.jpg` to every job. Once `01_anchor_couple` passes QC, also attach
`out/01_anchor_couple.png` to every later job that shows the couple.

## 3. Art style (identical for every image)

> Hand-painted gouache and watercolour illustration in the style of a contemporary Indian-miniature-
> inspired luxury wedding invite, as in the `style_*.jpg` frames. Use a warm sandstone and ochre palette
> with marigold orange, deep vermilion red, indigo, teal and soft green accents. Visible handmade-paper
> grain and soft dry-brush textures, gentle painterly shading, warm diffused Rajasthani daylight (or
> warm lamp light at night). Details are rich but soft: carved stone, jharokhas, wooden doors, marigold
> garlands, brass. Nothing glossy, nothing 3D-rendered, nothing photographic.

The couple, when present:
- Drawn in the same gouache style, as charming **subtle caricatures**: heads about 15% larger than
  natural, elegant natural bodies, never chibi, with exact facial likeness.
- Full figures, faces clearly visible and unobstructed (no veil over the face, no sehra over the face).
  Joyful, natural expressions.

General rules:
- **No text, letters, numbers, logos or watermarks anywhere** (the video adds all text later).
- Correct anatomy: five fingers per hand, no extra or merged limbs.
- Cut-out jobs: transparent background, no ground shadow, nothing cropped, at least 40 px margin.

## 4. Jobs

### 4A. Characters

`01_anchor_couple` (cut-out): **do this first; it is the style anchor.** Refs: headshots +
`pose_traditional.png` + `style_street.jpg`. Groom in an ivory bandhgala sherwani with gold sequin
zig-zag embroidery, ivory churidar, cream mojari. Bride in an emerald-green silk lehenga with gold zari
border, green dupatta over one shoulder, kundan choker, maang tikka, jhumkas, green bangles, hair in a
low bun. They stand close and wave at the viewer, both smiling. This is the couple's entry on the street.

`02_rickshaw` (cut-out, **landscape 1536x1024**): ref: `style_street.jpg`. A man in a white kurta, green
dhoti and red Rajasthani turban pedals a colourful cycle-rickshaw with a painted green and pink canopy,
loaded with marigold baskets and oranges. Side view moving to the right, whole vehicle visible, wheels
complete.

`03_puppets` (cut-out): three strings of colourful Rajasthani kathputli puppets (red and gold costumes)
and two hanging marigold tassels. Each hangs from a thread that starts at the very top edge of the image.

### 4B. The street panorama (built by outpainting)

The opening is one long, continuous painted Rajasthani street, and the camera pans from left to right
along it. Build it as a **seamless panorama 1536 px tall and about 4600 px wide**, in five segments:
1. Generate segment 1 at `1024x1536`.
2. For each next segment, make a new 1024x1536 canvas. Place the rightmost 384 px of the panorama so
   far at its left edge, and leave the remaining 640 px transparent.
3. Call `images.edit` with that canvas and a mask so the model continues the street seamlessly into
   the empty area: same wall height, same horizon, same ground line, same light and palette.
4. Append the new 640 px.
5. Save each segment as `P1`…`P5`, and the stitched result as `P_panorama.png`.

The ground (a dusty street) runs along the bottom 20% of every segment, so the rickshaw and the couple
can be placed on it. Everything is in the reference reel's style, ref `style_street.jpg`.

- `P1`: an old sandstone haveli wall with carved jharokha balconies at the top, marigold and mango-leaf
  torans over two doorways, a fruit cart with oranges, marigold baskets on the ground, and a large
  **plain smooth plaster panel** in the middle of the wall (the gold V&K monogram is painted there later).
- `P2`: the wall continues. Upper centre: an open window with an elderly Rajasthani man in a white
  kurta, grey shawl and red turban, leaning on the sill and holding a wooden scroll rod with both hands.
  His face is gentle and simple, and he looks down at the street. Below his window, a large stretch of
  plain wall (a long cloth banner unrolls down over it later).
- `P3`: a grand carved wooden haveli doorway, decorated with marigold strings and a brass bell, its
  dark interior visible (the couple is placed standing in it later). Beside it, at mid-height, a large
  window **for Day 1**.
- `P4`: more wall with a shop front of colourful bangles and textiles, and hanging lanterns. A large
  window **for Day 2**.
- `P5`: the wall ends at a decorated palace gate with marigold drapes. Beside it, a large window **for
  Day 3**, and a second plain plaster panel for the closing monogram.

**Windows:** the three day-windows are big (about 420 px wide and 520 px tall) carved stone frames,
and their openings are filled with **pure chroma green #00FF00**. The video shows a scene through
each one and zooms through it. Nothing overlaps the green. No other window is green.

### 4C. Banner

`B1_banner` (cut-out, 1024x1536): ref: `style_banner.jpg`. A long hanging cloth banner of aged ivory
handmade paper or khadi, with a turned wooden rod across the top. Delicate watercolour marigold, rose
and leaf sprigs grow in the lower-left and right corners. Hand-torn edges, and a bottom fringe of
marigold-orange and red tassels. The middle 70% is completely empty for text. Hang it straight, front
view, filling most of the frame.

### 4D. Event scenes (opaque, 1024x1536), the views through the windows

Each event is one painted scene in the same gouache style, ref `style_scene_night.jpg` or
`style_scene_day.jpg` (whichever matches the time). **The top 35% of every scene is calm and empty** (sky,
plain wall or soft canopy) because the event name, date, time and venue are written there. The couple
stands in the lower half, full figure, about 40% of the image height, in the outfit given (follow the
matching `pose_*.png`), with faces exactly matching the headshots.

`E01_ganesh_sthapana`: midday in a haveli courtyard with a marigold-decorated mandap and a Ganesha idol
on a red-draped chowki. Couple per `pose_ganesh.png` (saffron kurta and cream dhoti; red-yellow
bandhej saree), with folded hands, the bride holding a puja thali.

`E02_mayra_swagat`: late afternoon at a decorated haveli entrance with a rangoli, a brass kalash, and
gift trays covered in red cloth, carried by relatives in the background (small, faces simple). Couple
per `pose_mayra.png`, welcoming.

`E03_ring_ceremony`: dusk on a rooftop terrace with fairy lights, lanterns and a rose arch, and a
violet sky. Couple per `pose_ring.png`; he slips a ring onto her finger and both laugh.

`E04_carnival`: bright morning on a lawn with colourful canopies, balloons, bunting and game stalls
(ring toss, tin cans), and an anchor's microphone stand. Couple per `pose_carnival.png`, laughing, with
trophy and scorecard.

`E05_bandoli`: early evening on a lane lit with strings of bulbs, a dholi playing a dhol and a few
dancing relatives in the background. Couple per `pose_bandoli.png`, dancing.

`E06_sangeet`: night in a palace courtyard with chandeliers, ivory drapes, candles and a wooden dance
floor under a starry indigo sky, as in `style_scene_night.jpg`. Couple per `pose_sangeet.png`, dancing.

`E07_ghadi_vinayak`: midnight at a small temple corner glowing with many diyas under stars. Couple per
`pose_puja.png` (cream kurta and maroon stole; maroon saree), folded hands.

`E08_haldi_janeu`: sunny morning in a courtyard hung with yellow marigold curtains, with brass urlis
of turmeric and a low wooden patla. Groom in a yellow dhoti with a white janeu thread across his chest
and a marigold garland; bride in a yellow floral lehenga with flower jewellery. Laughing, with turmeric
on their cheeks.

`E09_baraat`: afternoon outside a palace gate, with a brass band, colourful umbrellas and marigold arches.
The groom alone on a decorated white mare per `pose_baraat.png`, facing right, face visible.

`E10_mangal_phera`: night, under a red-and-gold mandap with a marigold canopy, a havan kund fire and
diyas, as in the wedding frame of `style_scene_day.jpg`, but at night. Couple per `pose_phera.png`, with
the gathbandhan knot, standing beside the fire.

### 4E. Foreground layers for transitions (cut-outs, 1024x1536, same gouache style)

These pass close in front of the camera to wipe between event scenes.

- `F1_fg_drape`: one tall drape of marigold-orange and red fabric with marigold strings, filling the
  full height of the frame.
- `F2_fg_pillar`: one carved sandstone pillar with a marigold garland, filling the full height of the
  frame and about 35% of its width.
- `F3_fg_flowers`: a dense bunch of marigolds, roses and leaves very close to the camera, filling the
  bottom 40% of the frame.
- `F4_fg_petals`: falling marigold and rose petals at many sizes, spread over the whole frame.

## 5. Quality control (mandatory for every image; this is what makes it "perfect")

After generating each image, inspect it yourself. Use a GPT vision-capable model through the same SDK,
passing the generated image, the reference headshots and the relevant `style_*.jpg`. Score it 1–10 on:
1. **Likeness:** each face matches its headshot exactly (skip for images with no couple).
2. **Style:** looks hand-painted gouache like the `style_*.jpg` frames and matches `01_anchor_couple`.
3. **Anatomy:** hands and fingers, limbs, proportions (the elder, the rickshaw man and the couple).
4. **Completeness:** the whole subject is inside the frame, nothing cropped. For scenes, the top 35%
   is empty enough for text.
5. **Cleanliness:** no text anywhere. Cut-outs are truly transparent with no halo or shadow. The
   panorama has no visible seams between segments.
6. **Brief match:** contents, outfits, colours and time of day exactly as written.

Ask the vision model to return JSON: `{"scores": {...}, "defects": [...], "pass": true|false}`. An image
passes only if **every score is 9 or 10**. If it fails, regenerate with the defects appended to the
prompt as explicit corrections. Allow up to **5 attempts per job** and keep the best one. Log every
attempt to `wedding-invite/codex/out/qc_log.json`.

Then, in code:
- For the panorama, find each day-window's green opening (pixels with G>200, R<80, B<80). Write the
  bounding boxes and four corners to `out/windows.json` as `{"day1": [[x,y]...4], "day2": ..., "day3": ...}`,
  with day1 being the leftmost. Also record the two plain monogram panels and the banner wall area
  below the elder (approximate boxes) in the same file as `"monogram_start"`, `"monogram_end"` and
  `"banner_area"`. If there are not exactly three clean green windows, regenerate the segment concerned.
- Verify cut-outs are RGBA with transparent corners, scenes and the panorama are opaque, and sizes
  are as requested.

## 6. Deliverables

- `wedding-invite/codex/out/`:
  - `01_anchor_couple`, `02_rickshaw`, `03_puppets`
  - `P1`–`P5` and `P_panorama`
  - `B1_banner`
  - `E01`–`E10`
  - `F1`–`F4`
  - `windows.json`
- `wedding-invite/codex/out/contact_sheet.jpg`: every output on one sheet, labelled.
- `wedding-invite/codex/out/qc_log.json`.
- `wedding-invite/codex/generate.py`: the script you used. It must not contain the API key.

Commit all of the above and push to the current branch. In your final message, list each job id with
its final QC scores and the number of attempts it took.
