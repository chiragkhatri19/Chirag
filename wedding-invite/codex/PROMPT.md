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

## 3. Art style (identical for every image)

> Premium Indian wedding-invite caricature illustration, like the work of a professional 2D animation
> studio. Polished hand-painted digital illustration: clean confident ink linework (thin warm-brown
> lines, not black), soft cel shading with gentle painterly gradients, rich jewel colours, crisp
> detailed embroidery, zari and jewellery. Warm golden key light from the upper left and a soft warm rim
> light on the right. Faces drawn in the SAME painted style as the bodies, not photographic, but with
> exact likeness. Subtle caricature proportions: heads about 15% larger than natural, bodies natural
> and elegant (never chibi, never cartoonish). Expressions joyful and natural.

Rules for every CHARACTER image:
- Full figures, head to toe, nothing cropped, with at least 40 px of empty margin on all sides.
- Transparent background: no floor, no shadow, no backdrop, no props beyond those listed.
- No text, letters, logos or watermarks anywhere.
- Correct anatomy: five fingers per hand, no extra or merged limbs, natural hands holding props.
- Both faces clearly visible and unobstructed (no veil over the face, no sehra over the groom's face).
- Unless the job says otherwise, both look at the viewer.

## 4. Jobs

### CHARACTERS (transparent, 1024x1536 portrait unless noted)

`01_anchor_traditional`: **do this first; it is the style anchor.** Refs: both headshots +
`pose_traditional.png`. Groom in an ivory bandhgala sherwani with gold sequin zig-zag embroidery,
ivory churidar, cream embroidered mojari. Bride in an emerald-green silk lehenga with heavy gold zari
border and gold buttis, green dupatta over one shoulder, kundan choker, maang tikka, kundan jhumkas,
green and gold bangles, hair in a low bun. They stand close, her hand resting on his chest, both smiling.

`02_ganesh_sthapana`: refs: headshots + `pose_ganesh.png`. Groom in a saffron silk kurta with gold
border, cream dhoti, maroon and gold stole over one shoulder, red tilak. Bride in a red and yellow
Rajasthani bandhej silk saree with gold border, gold temple jewellery, gajra in her bun, red bindi.
Both stand with folded hands in namaste; the bride also holds a small gold puja thali with a lit diya.

`03_mayra_swagat`: refs: headshots + `pose_mayra.png`. Groom in a maroon silk bandhgala with gold
buttons over a cream kurta, cream churidar. Bride in a rani-pink Rajputi poshak with heavy gold
gota-patti, sheer pink odhni on the back of her head (face fully visible), borla, nath, kundan necklace.
Warm welcoming pose, standing close.

`04_ring_ceremony`: refs: headshots + `pose_ring.png`. Groom in a midnight-blue velvet bandhgala with
gold embroidery, black trousers, black shoes. Bride in a blush-pink and champagne sequinned lehenga
with a sheer dupatta, diamond choker and drop earrings, long open wavy hair. The groom slips a diamond
ring onto her finger; both look at each other, laughing, with faces in three-quarter view toward the viewer.

`05_carnival`: refs: headshots + `pose_carnival.png`. A fun games morning hosted by an anchor. Groom in
a turquoise and orange printed short kurta, white pants, white sneakers, sunglasses pushed up on his
head, holding a game scorecard and pointing at the bride in mock disbelief. Bride in a mustard-yellow
and pink printed co-ord kurta set with a light dupatta, oxidised statement earrings, high ponytail
with a flower, laughing, holding up a small gold winner's trophy. A few colourful balloons and a toy
microphone at their feet.

`06_bandoli`: refs: headshots + `pose_bandoli.png`. Groom in a mustard-yellow printed Jodhpuri bandhgala,
white churidar, colourful leheriya safa turban (face fully visible). Bride in a bright pink and orange
leheriya saree with gota border, gold jewellery, many bangles. Joyful folk-dance pose: groom with one
arm raised, bride clapping.

`07_sangeet`: refs: headshots + `pose_sangeet.png`. Groom in a black Indo-western sherwani with silver
embroidery and a magenta pocket square. Bride in a deep purple and magenta mirror-work lehenga with a
wide flared skirt, silver jhumkas, hair in a soft bun. Mid-dance: bride twirling with the lehenga
flaring, groom in a playful bhangra pose with one arm raised. Keep the whole skirt inside the frame.

`08_ghadi_vinayak`: refs: headshots + `pose_puja.png`. A calm midnight puja. Groom in a cream silk
kurta pyjama with a maroon and gold stole, red tilak. Bride in a maroon silk saree with a gold zari
border, gold jewellery, pallu over one shoulder, red bindi. Both with folded hands and calm devotional
smiles, a small brass diya on a short brass stand glowing in front of them.

`09_haldi_janeu`: refs: headshots + `01` style anchor. Groom in a yellow silk dhoti with a light
yellow angavastram, a white sacred janeu thread across his bare chest from the left shoulder, marigold
garland. Bride in a bright yellow floral lehenga with fresh marigold and jasmine flower jewellery.
Light turmeric smudges on their cheeks and arms, laughing together, standing side by side.

`10_baraat` (**landscape 1536x1024**): refs: groom headshot + `pose_baraat.png`. Groom alone in a regal
ivory and gold wedding sherwani, pearl mala, red and gold Rajasthani safa with a jewelled kalgi and
white feather, red velvet stole, holding a small sword, seated proudly on a decorated white mare with
a red and gold embroidered saddle cloth, gold and red bridle, tassels, bells and a red plume. Horse in
side view facing right, the whole horse visible including all hooves and the tail. The groom's face is
turned to the viewer and fully visible (no sehra).

`11_mangal_phera`: refs: headshots + `pose_phera.png`. Groom in the same ivory and gold wedding sherwani,
red and gold safa with kalgi, pearl mala, red stole. Bride in a classic red bridal lehenga with heavy
gold zardozi, red dupatta pinned on the back of her head (face fully visible), full bridal kundan
jewellery, nath, maang tikka, red and gold chooda, mehendi on her hands. The groom's stole is tied to
her dupatta in a gathbandhan knot. A small brass havan kund with a gentle fire stands in front of
their feet, with a few marigolds around it. Both look at the viewer.

`12_car` (**landscape 1536x1024**): refs: headshots + `01` style anchor. The couple in an open-top
vintage two-seater convertible, cream-white with gold trim and chrome, decorated with marigold
garlands and a floral bunch on the bonnet (no text, no number plate text). Groom driving in a cream
bandhgala, bride beside him in a pink-and-gold lehenga with her dupatta fluttering behind in the wind.
Both smile and wave at the viewer. Front three-quarter view facing left, the whole car including all
visible wheels inside the frame.

### BACKGROUNDS (opaque, 1024x1536 portrait, no people, no vehicles, no text)

`13_bg_street`: painted Rajasthani town street at golden hour, in the same illustration style.
Sandstone havelis with jharokha balconies on both sides, colourful bunting and marigold strings across
the street, a palace with domes on a hill in the far distance, the road running from the bottom centre
into the distance. Keep the lower-middle third of the road empty (a car is placed there later). Warm
ivory, maroon, marigold and gold palette.

`14_bg_venue_gate`: grand decorated wedding venue entrance at dusk: a tall carved sandstone gateway
with a big arch draped in marigold and rose garlands, hanging brass lanterns, fairy lights, a red
carpet from the bottom centre to the gate, diyas lining the path, a lit palace-like building behind.
Keep the lower-middle third clear for the car and couple.

`15_bg_card_wash`: soft ivory handmade-paper texture with flowing maroon and deep-red watercolour
washes entering from the top-right and bottom-left corners, scattered gold-leaf flecks, and a large
calm empty ivory area in the middle for text. No objects.

### ORNAMENTS (transparent, 1024x1536, one object per image, same painted style, no text)

`16_orn_lanterns`: two ornate brass Rajasthani lanterns with warm glowing light, hanging from fine
chains that start at the very top edge of the image.

`17_orn_floral_corner`: a lush corner cluster of marigolds, red and pink roses, jasmine and green
leaves, arranged to fit a top-left corner (flowers spilling toward the bottom-right).

`18_orn_marigold_garland`: one long horizontal marigold and mango-leaf toran garland with small brass
bells, spanning the full width, landscape 1536x1024.

`19_orn_diya`: a single brass diya on a small brass stand with a warm flame, centred.

## 5. Quality control (mandatory for every image; this is what makes it "perfect")

After generating each image, inspect it yourself. Use a GPT vision-capable model through the same
SDK, passing the generated image **and** the reference headshots. Score it 1–10 on:
1. **Likeness:** does each face match its headshot exactly?
2. **Style consistency** with `01_anchor_traditional` (after the anchor exists).
3. **Anatomy:** hands and fingers, limbs, proportions.
4. **Completeness:** whole figure or object inside the frame, nothing cropped.
5. **Cleanliness:** truly transparent background where required, no halo, no ground shadow, no text.
6. **Brief match:** outfits, colours, props and pose exactly as written.

Ask the vision model to return JSON: `{"scores": {...}, "defects": [...], "pass": true|false}`. An image
passes only if **every score is 9 or 10**. If it fails, regenerate with the defects appended to the
prompt as explicit corrections. Allow up to **5 attempts per job** and keep the best-scoring one.
Log every attempt and score to `wedding-invite/codex/out/qc_log.json`.

Then verify the files with Pillow:
- Character and ornament PNGs are RGBA, and the four corner pixels have alpha 0.
- Background PNGs are opaque RGB.
- Every image matches the size requested.

## 6. Deliverables

- `wedding-invite/codex/out/01_anchor_traditional.png` … `19_orn_diya.png` (19 files).
- `wedding-invite/codex/out/contact_sheet.jpg`: every output on one sheet, labelled with its job id.
- `wedding-invite/codex/out/qc_log.json`.
- `wedding-invite/codex/generate.py`: the script you used. It must not contain the API key.

Commit all of the above and push to the current branch. In your final message, list each job id
with its final QC scores and the number of attempts it took.
