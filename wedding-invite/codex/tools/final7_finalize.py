import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
TEMP = OUT / "_tmp_refs"
QC = json.loads((TEMP / "final7_numeric_qc.json").read_text(encoding="utf-8"))
NAMES = [
    "01_anchor_couple", "E01_ganesh_sthapana", "E03_ring_ceremony",
    "E04_carnival", "E06_sangeet", "E08_haldi_janeu", "E09_baraat",
    "E10_mangal_phera",
]
ATTEMPTS = {
    "01_anchor_couple": 1,
    "E01_ganesh_sthapana": 1,
    "E03_ring_ceremony": 2,
    "E04_carnival": 1,
    "E06_sangeet": 1,
    "E08_haldi_janeu": 4,
    "E09_baraat": 1,
    "E10_mangal_phera": 4,
}
APPROVAL = {
    "01_anchor_couple": "reviewed in the preceding task context",
    "E01_ganesh_sthapana": "user-approved",
    "E03_ring_ceremony": "user-approved after full-scene revision",
    "E04_carnival": "user-approved",
    "E06_sangeet": "user-approved",
    "E08_haldi_janeu": "user-approved solo-groom version with hands lowered",
    "E09_baraat": "user-approved",
    "E10_mangal_phera": "user-approved same-direction version; subsequent face-only full-scene edit was rejected and reverted",
}


def font(size=22):
    for candidate in ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def thumb(path, size, background=(246, 241, 230)):
    im = Image.open(path).convert("RGBA")
    im.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (*background, 255))
    canvas.alpha_composite(im, ((size[0]-im.width)//2, (size[1]-im.height)//2))
    return canvas.convert("RGB")


def make_contact():
    w, h, gap, label_h = 256, 384, 12, 34
    sheet = Image.new("RGB", (8*w+9*gap, h+label_h+2*gap), (244, 239, 228))
    draw = ImageDraw.Draw(sheet)
    f = font(17)
    for i, name in enumerate(NAMES):
        x = gap + i*(w+gap)
        sheet.paste(thumb(OUT / f"{name}.png", (w, h)), (x, gap))
        draw.text((x+4, h+gap+3), name, fill=(45, 38, 31), font=f)
    sheet.save(OUT / "contact_sheet.jpg", quality=94, subsampling=0)


def make_faces():
    rows = []
    for name in NAMES:
        for person in ("groom", "bride"):
            crop_path = TEMP / "final7_face_crops" / f"{name}__{person}.png"
            if not crop_path.exists():
                continue
            refs = [ROOT / "refs" / f"{person}_photo_{i}.jpg" for i in range(1, 4)]
            rows.append((name, person, crop_path, refs))
    cell_w, cell_h, label_h, gap = 270, 250, 28, 8
    canvas = Image.new("RGB", (gap+4*(cell_w+gap), gap+len(rows)*(cell_h+label_h+gap)), (247, 243, 235))
    d = ImageDraw.Draw(canvas)
    f = font(17)
    for row_i, (name, person, painted, refs) in enumerate(rows):
        y = gap + row_i*(cell_h+label_h+gap)
        d.text((gap, y), f"{name} — {person}", fill=(40, 34, 28), font=f)
        items = [painted] + refs
        for col, item in enumerate(items):
            x = gap + col*(cell_w+gap)
            canvas.paste(thumb(item, (cell_w, cell_h)), (x, y+label_h))
            if col == 0:
                caption = "Painted face (3× crop)"
            else:
                caption = f"Real photo {col}"
            d.text((x+4, y+label_h+cell_h-22), caption, fill=(255,255,255), font=font(15), stroke_width=2, stroke_fill=(20,20,20))
    canvas.save(OUT / "faces_contact_sheet.jpg", quality=93, subsampling=0)


def make_log():
    log_path = OUT / "qc_log.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
    images = {}
    for name, record in QC["images"].items():
        faces = {}
        for person, result in record["faces"].items():
            faces[person] = {
                "similarity": result["similarity"],
                "wrong_person_similarity": result["wrong_person_similarity"],
                "threshold": result["threshold"],
                "pass": result["pass"],
                "attempt_count": ATTEMPTS[name],
                "note": "final accepted image score; earlier user-reviewed variants were not numerically rescored",
            }
        images[name] = {
            "attempt_count": ATTEMPTS[name],
            "approved_by_user": APPROVAL[name],
            "faces": faces,
            "numeric_pass": all(item["pass"] for item in faces.values()),
        }
    log["final7"] = {
        "method": QC["method"],
        "S_sheet": QC["S_sheet"],
        "thresholds": QC["thresholds"],
        "character_sheet_head_scores": QC["sheet_baseline"],
        "images": images,
        "notes": [
            "All listed final scene images were reviewed and approved by the user, except the rejected E10 face-edit candidate, which was reverted.",
            "ArcFace threshold misses are retained as user-approved images and are reported rather than silently altered.",
            "No edits were made to P_panorama.png or other excluded assets.",
        ],
    }
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")


if __name__ == "__main__":
    make_contact()
    make_faces()
    make_log()
    print("Wrote contact_sheet.jpg, faces_contact_sheet.jpg, and final7 qc_log section")
