# Codex brief: generate all artwork for the "Veeral weds Konika" invite

You are generating every illustration for an animated 9:16 Rajasthani wedding-invite video. Another
tool animates these images later, so **each image must be a clean, separate asset**. Work fully
autonomously. Do not stop to ask questions. Generate, check, regenerate and save everything in one run.

---------------------------------------------------------------------------------------------------

## 0. Setup

1. The reference images are in `wedding-invite/codex/refs/` (see section 2). Read all of them first.
2. Write a Python script `wedding-invite/codex/generate.py` that uses the official `openai` Python SDK
   and the environment variable `OPENAI_API_KEY`.
   - Use the newest GPT image model available to the key: try `gpt-image-1.5`, then `gpt-image-1`.
   - Call **`client.images.edit`**, never `images.generate`, whenever a job lists reference images,
     so the faces and outfits follow the references. Pass all the job's reference files in `image=[...]`.
   - Always set `quality="high"`, `input_fidelity="high"` (keeps faces accurate), `output_format="png"`.
   - Use `background="transparent"` for every CHARACTER and ORNAMENT job, and `background="opaque"`
     for BACKGROUND jobs.
   - Size: `1024x1536` (portrait), or `1536x1024` where the job says landscape.
3. Save every final image to `wedding-invite/codex/out/<job_id>.png`, with exactly the job ids below.
4. Install anything you need (`pip install openai pillow numpy`). If a call fails with a
   rate-limit or server error, wait and retry. Never skip a job.

## 1. The couple (keep this identical in every image)

- **Groom: Veeral.** Indian man, late 20s, fair-wheatish skin. Thick, voluminous, swept-up black
  hair with a slight side quiff. Well-groomed full black beard, shaped short on the cheeks and
  fuller on the chin, with a moustache joined to the beard. Thick straight eyebrows, warm brown
  eyes, confident gentle smile.
- **Bride: Konika.** Indian woman, late 20s, fair skin, soft round face with full cheeks, softly
  rounded jawline. Thick dark-brown eyebrows, large brown eyes, warm wide smile showing teeth. Dark
  brown hair.
- **Faces must be an exact, instantly recognisable likeness of the headshots in `refs/`.** Never
  beautify, slim, age, lighten or westernise their faces. Match face shape, eye shape, eyebrows, nose,
  lips, smile, beard and hairline exactly. If a generated face drifts from the headshot, regenerate it.

## 2. Reference files (already in `wedding-invite/codex/refs/`)

| file | what it is | how to use it |
|------|------------|---------------|
| `groom_headshot.png` | realistic close-up of the groom | face likeness, every job with the groom |
| `bride_headshot.png` | realistic close-up of the bride | face likeness, every job with the bride |
| `pose_traditional.png` … `pose_phera.png` | earlier illustrations of each outfit and pose | outfit, pose and jewellery reference for the job with the same name |

Attach **both headshots plus the matching `pose_*.png`** (when one exists) to every character job.
After `01_anchor_traditional` is approved, also attach `out/01_anchor_traditional.png` to every later
character job as the **style anchor**, so all images look like one artist drew them.

## 3. Art style for the painted 2D half (section 4A–4C)

> Premium Indian wedding-invite caricature illustration, like the work of a professional 2D animation
> studio. Polished hand-painted digital illustration: clean confident ink linework (thin warm-brown
> lines, not black), soft cel shading with gentle painterly gradients, rich jewel colours, crisp
> detailed embroidery, zari and jewellery. Warm golden key light from the upper left and a soft warm rim
> light on the right. Faces drawn in the SAME painted style as the bodies, not photographic, but with
> exact likeness. Subtle caricature proportions: heads about 15% larger than natural, bodies natural
> and elegant (never chibi, never cartoonish). Expressions joyful and natural.

Rules for every 2D CHARACTER image (section 4A):
- Full figures, head to toe, nothing cropped, with at least 40 px of empty margin on all sides.
- Transparent background: no floor, no shadow, no backdrop, no props beyond those listed.
- No text, letters, logos or watermarks anywhere.
- Correct anatomy: five fingers per hand, no extra or merged limbs, natural hands holding props.
- Both faces clearly visible and unobstructed (no veil over the face, no sehra over the groom's face).
- Unless the job says otherwise, both look at the viewer.

## 4. Jobs

The video has two halves, so there are two looks:
- **Entry (painted 2D look):** the section 3 style. Jobs 01, 12–19.
- **Events (cinematic 3D look):** jobs E01–E10 and F1–F4, described below.

### 4A. PAINTED 2D CHARACTERS (transparent, 1024x1536 portrait unless noted)

`01_anchor_traditional`: **do this first; it is the style anchor for the 2D half.** Refs: both
headshots + `pose_traditional.png`. Groom in an ivory bandhgala sherwani with gold sequin zig-zag
embroidery, ivory churidar, cream embroidered mojari. Bride in an emerald-green silk lehenga with heavy
gold zari border and gold buttis, green dupatta over one shoulder, kundan choker, maang tikka, kundan
jhumkas, green and gold bangles, hair in a low bun. They stand close, her hand resting on his chest,
both smiling.

`12_car` (**landscape 1536x1024**): refs: headshots + `01` style anchor. The couple in an open-top
vintage two-seater convertible, cream-white with gold trim and chrome, decorated with marigold garlands
and a floral bunch on the bonnet (no text, no number plate text). Groom driving in a cream bandhgala,
bride beside him in a pink-and-gold lehenga with her dupatta fluttering behind in the wind. Both smile
and wave at the viewer. The car drives toward the viewer in a front three-quarter view; the whole car,
including all visible wheels, is inside the frame.

### 4B. PAINTED 2D ENTRY SCENE LAYERS (for parallax; same painted style, no people, no vehicles, no text)

The entry is a "driving through a Rajasthani town" shot. It is built from stacked layers that move at
different speeds, so each layer must line up when stacked and must work on its own.

`13a_street_far` (opaque, 1024x1536): golden-hour sky with soft clouds and a few birds, and a palace
with domes on a hill in the far distance, sitting in the lower half of the frame. Nothing else.

`13b_street_mid` (transparent, 1024x1536): two rows of sandstone havelis with jharokha balconies and
colourful doors, one row on the left side and one on the right, framing a central gap. The road runs
from the bottom centre into the distance. Everything above and between the buildings is transparent,
so the sky layer shows through.

`13c_street_near` (transparent, 1024x1536): only foreground decorations, namely strings of colourful
triangular bunting and marigold garlands crossing the top third of the frame, plus a few potted plants
and a hanging lantern at the far left and right edges. Everything else is transparent.

`14_bg_venue_gate` (opaque, 1024x1536): a grand decorated wedding-venue entrance at dusk. A tall carved
sandstone gateway with a big arch draped in marigold and rose garlands, hanging brass lanterns, fairy
lights, a red carpet from the bottom centre to the gate, diyas lining the path, a lit palace-like
building visible through the arch. Keep the lower-middle third clear (the car stops there).

### 4C. CARD ART (painted)

`15_bg_card_wash` (opaque, 1024x1536): soft ivory handmade-paper texture with flowing maroon and
deep-red watercolour washes entering from the top-right and bottom-left corners, scattered gold-leaf
flecks, and a large calm empty ivory area in the middle for text. No objects.

`16_orn_lanterns` (transparent, 1024x1536): two ornate brass Rajasthani lanterns with warm glowing
light, hanging from fine chains that start at the very top edge of the image.

`17_orn_floral_corner` (transparent, 1024x1536): a lush corner cluster of marigolds, red and pink
roses, jasmine and green leaves, arranged to fit a top-left corner (flowers spilling toward the
bottom-right).

`18_orn_marigold_garland` (transparent, **landscape 1536x1024**): one long horizontal marigold and
mango-leaf toran garland with small brass bells, spanning the full width.

`19_orn_diya` (transparent, 1024x1536): a single brass diya on a small brass stand with a warm flame,
centred.

### 4D. CINEMATIC 3D EVENT SCENES (opaque, 1024x1536 portrait)

Do `E01` first. Once it passes QC, attach `out/E01_ganesh_sthapana.png` to every later E- and F-job
as the **3D style anchor**, so all scenes look like one continuous venue rendered by one studio.

**Look for every E-job:** a premium cinematic 3D-rendered wedding-venue scene, like a high-end animated
film or a luxury 3D wedding-invite reel. Use soft global illumination, warm golden-hour or night
lighting as stated, shallow depth of field with creamy bokeh, and realistic flowers, fabric, brass and
sandstone. The setting is one Rajasthani palace-courtyard venue: carved sandstone, jharokhas, marigold
and rose decor, brass lanterns and diyas. Colours are ivory, maroon, marigold, rose pink and gold.

**The couple in each scene:**
- They appear as stylised 3D animated-film characters, with exact facial likeness to the headshots and
  heads about 10% larger than natural.
- They wear the outfit given for that scene, which follows the matching `pose_*.png`.
- Place them in the lower half of the frame, **full figure, faces clearly visible**, standing beside
  (not in front of) the signboard, at about 35–45% of the frame height.

**The signboard (critical):** every scene contains one decorated signboard that matches the event:
an easel, an arch panel, a framed board or a wall panel. Its **flat face is a blank rectangle filled
with pure chroma green #00FF00**, which the video tool replaces with the event text later. Rules:
- No text, letters or symbols on the board or anywhere else in the image.
- Flowers may frame the green face, but nothing may overlap it.
- The green face is a simple four-corner rectangle (perspective allowed), at least 40% of the image
  width, fully inside the frame, in the upper-middle area.

`E01_ganesh_sthapana`: midday. A marigold-decorated mandap with a beautiful Ganesha idol on a red-cloth
pedestal at the back. A carved brass-framed signboard on an easel stands at the front left, with the
green face. Outfits as in `pose_ganesh.png` (saffron kurta, cream dhoti, maroon stole; red-yellow
bandhej saree). Couple with folded hands, the bride holding a puja thali.

`E02_mayra_swagat`: late afternoon at a grand haveli doorway with a rangoli on the floor, a brass kalash,
and gift trays covered with red cloth. The signboard is a carved wooden panel beside the door. Outfits as
in `pose_mayra.png` (maroon bandhgala; rani-pink poshak, odhni on the back of her head). Welcoming pose.

`E03_ring_ceremony`: evening, under fairy lights, beside a rose-and-white-flower arch. The signboard is
a white framed easel with pink roses. Outfits as in `pose_ring.png` (navy velvet bandhgala; blush
lehenga, open wavy hair). The groom slips a ring onto her finger.

`E04_carnival`: bright morning on a lawn with colourful umbrellas, a balloon arch, bunting and small
game stalls (ring toss, tin-can stack), and an anchor's mic stand. The signboard is a playful painted
wooden board with balloons tied to it. Outfits as in `pose_carnival.png`. The bride holds a trophy and
the groom a scorecard, both laughing.

`E05_bandoli`: early evening on a festive street lane with strings of lights and marigolds overhead and a
dhol on a stand. The signboard is a decorated wooden stand covered in marigold strings. Outfits as in
`pose_bandoli.png` (mustard bandhgala with leheriya safa; leheriya saree). Folk-dance pose.

`E06_sangeet`: night, on a stage with a glittering fairy-light curtain, gold drapes, warm spotlights and
haze. The signboard is a large stage backdrop panel behind them and to one side. Outfits as in
`pose_sangeet.png` (black embroidered sherwani; purple-magenta mirror-work lehenga). Dancing.

`E07_ghadi_vinayak`: midnight. A small temple corner glowing with dozens of diyas and brass lamps,
under a starry sky. The signboard is a brass-framed panel on a carved stand. Outfits: groom in a cream
kurta with a maroon stole, bride in a maroon silk saree, as in `pose_puja.png`. Both with folded hands.

`E08_haldi_janeu`: sunny morning in a courtyard draped in yellow marigold curtains, with brass urlis
of turmeric paste and a low wooden patla. The signboard is a board made entirely of marigolds with
the green face in the middle. Outfits: groom in a yellow dhoti with a white janeu thread across his
chest and a marigold garland; bride in a yellow floral lehenga with flower jewellery. Laughing, with
turmeric on their cheeks.

`E09_baraat`: afternoon at the palace gate. The groom (alone) sits on a decorated white mare as in
`pose_baraat.png` (ivory sherwani, red safa with kalgi), facing right. Behind him are a brass band
with drums, colourful umbrellas and marigold arches. The signboard is a tall decorated arch panel at
the left.

`E10_mangal_phera`: night, inside a grand red-and-gold mandap with marigold and rose canopy, a brass
havan kund with fire in the centre, and petals in the air. The signboard is a green-leaf (betel-leaf)
wall panel at the back left with the green face. Outfits as in `pose_phera.png` (ivory sherwani and safa;
red bridal lehenga, dupatta on the back of her head). Gathbandhan knot, standing beside the fire.

### 4E. FOREGROUND TRANSITION LAYERS (transparent, 1024x1536, same 3D look, no text)

These pass in front of the camera to "wipe" between scenes, as in luxury 3D reels.

`F1_fg_curtain`: one tall sheer drape of maroon and gold fabric with a marigold tie-back, filling
the full height of the frame, hanging from the very top edge to the very bottom edge.

`F2_fg_pillar`: one carved sandstone palace pillar with floral garlands, filling the full height of
the frame and about 35% of its width.

`F3_fg_flowers`: a dense bunch of marigolds, roses and leaves, as if very close to the camera and
softly out of focus, filling the bottom 40% of the frame.

`F4_fg_petal_burst`: hundreds of falling rose and marigold petals at different sizes and depths, with
some large blurred petals near the camera, spread over the whole frame.

## 5. Quality control (mandatory for every image; this is what makes it "perfect")

After generating each image, inspect it yourself. Use a GPT vision-capable model through the same
SDK, passing the generated image **and** the reference headshots. Score it 1–10 on:
1. **Likeness:** does each face match its headshot exactly?
2. **Style consistency:** 2D jobs match `01_anchor_traditional`; E- and F-jobs match `E01_ganesh_sthapana`.
3. **Anatomy:** hands and fingers, limbs, proportions.
4. **Completeness:** whole figure or object inside the frame, nothing cropped.
5. **Cleanliness:** truly transparent background where required, no halo, no ground shadow, no text.
   For E-jobs: the chroma-green face is pure #00FF00, rectangular, unobstructed, at least 40% of the image
   width, and nothing else in the image is that green.
6. **Brief match:** outfits, colours, props and pose exactly as written.

Ask the vision model to return JSON: `{"scores": {...}, "defects": [...], "pass": true|false}`. An image
passes only if **every score is 9 or 10**. If it fails, regenerate with the defects appended to the
prompt as explicit corrections. Allow up to **5 attempts per job** and keep the best-scoring one.
Log every attempt and score to `wedding-invite/codex/out/qc_log.json`.

For every E-job, also detect the green face with numpy (pixels where G>200, R<80, B<80). Write its four
corner points (pixel coordinates, clockwise from top-left) to `wedding-invite/codex/out/boards.json` as
`{"E01_ganesh_sthapana": [[x,y],[x,y],[x,y],[x,y]], ...}`. If the region is not one clean four-sided
shape, the job fails QC.

Then verify the files with Pillow:
- Character, ornament, `13b`, `13c` and F-layer PNGs are RGBA, and the four corner pixels have alpha 0.
- Backgrounds (`13a`, `14`, `15`) and E-scenes are opaque RGB.
- Every image matches the size requested.

## 6. Deliverables

- `wedding-invite/codex/out/`: `01_anchor_traditional`, `12_car`, `13a_street_far`, `13b_street_mid`,
  `13c_street_near`, `14_bg_venue_gate`, `15_bg_card_wash`, `16`–`19` ornaments, `E01`–`E10`, and
  `F1`–`F4` (28 PNG files), plus `boards.json`.
- `wedding-invite/codex/out/contact_sheet.jpg`: every output on one sheet, labelled with its job id.
- `wedding-invite/codex/out/qc_log.json`.
- `wedding-invite/codex/generate.py`: the script you used. It must not contain the API key.

Commit all of the above and push to the current branch. In your final message, list each job id
with its final QC scores and the number of attempts it took.
