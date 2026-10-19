import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "refs"
OUT = ROOT / "out"
CROPS = OUT / "_tmp_refs" / "final7_face_crops"
FILES = {
    "01_anchor_couple": ["groom", "bride"],
    "E01_ganesh_sthapana": ["groom", "bride"],
    "E03_ring_ceremony": ["groom", "bride"],
    "E04_carnival": ["groom", "bride"],
    "E06_sangeet": ["groom", "bride"],
    "E08_haldi_janeu": ["groom"],
    "E09_baraat": ["groom"],
    "E10_mangal_phera": ["groom", "bride"],
}


def read(path):
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Cannot read {path}")
    return image


def unit(v):
    v = np.asarray(v, dtype=np.float32)
    return v / max(float(np.linalg.norm(v)), 1e-8)


def sim(a, b):
    return float(np.dot(unit(a), unit(b)))


def ref_vector(app, person):
    vectors = []
    for i in range(1, 4):
        path = REFS / f"{person}_photo_{i}.jpg"
        faces = app.get(read(path))
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]))
        vectors.append(face.normed_embedding)
    direct = unit(np.mean(vectors, axis=0))
    for path in sorted((REFS / "real").glob("couple_*.jpg")):
        faces = app.get(read(path))
        if faces:
            vectors.append(max(faces, key=lambda f: sim(f.normed_embedding, direct)).normed_embedding)
    return unit(np.mean(vectors, axis=0))


def main():
    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    refs = {p: ref_vector(app, p) for p in ("groom", "bride")}
    thresholds = {}
    sheet_scores = {}
    for person in ("groom", "bride"):
        faces = app.get(read(OUT / f"CS_{person}.png"))
        head_faces = sorted(faces, key=lambda f: (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1]), reverse=True)[:5]
        candidates = sorted((sim(f.normed_embedding, refs[person]) for f in head_faces), reverse=True)
        if len(candidates) < 5:
            raise RuntimeError(f"Expected five {person} head studies, detected {len(candidates)}")
        sheet_scores[person] = [round(v, 6) for v in candidates]
        thresholds[person] = max(0.30, min(candidates) - 0.05)

    records = {}
    CROPS.mkdir(parents=True, exist_ok=True)
    for name, people in FILES.items():
        path = OUT / f"{name}.png"
        image = read(path)
        faces = app.get(image)
        pool = list(faces)
        rec = {"attempt_count": 1, "attempts": [], "faces": {}}
        for person in people:
            if not pool:
                raise RuntimeError(f"No distinct detected face remains for {person} in {path}")
            face = max(pool, key=lambda f: (sim(f.normed_embedding, refs[person]),
                                           0.015 * np.log1p(max(1.0, (f.bbox[2]-f.bbox[0])*(f.bbox[3]-f.bbox[1])))))
            pool = [candidate for candidate in pool if candidate is not face]
            other = "bride" if person == "groom" else "groom"
            score = sim(face.normed_embedding, refs[person])
            wrong = sim(face.normed_embedding, refs[other])
            x1, y1, x2, y2 = [int(round(float(x))) for x in face.bbox]
            h, w = image.shape[:2]
            side = max(32, int(round(2.2 * (y2-y1))))
            cx, cy = (x1+x2)//2, (y1+y2)//2
            left = min(max(0, cx-side//2), max(0,w-side)); top = min(max(0,cy-side//2), max(0,h-side))
            crop = cv2.cvtColor(image[top:min(h,top+side), left:min(w,left+side)], cv2.COLOR_BGR2RGB)
            if crop.size:
                pil = Image.fromarray(crop).resize((3*max(crop.shape[1],crop.shape[0]),)*2, Image.Resampling.LANCZOS)
                pil.save(CROPS / f"{name}__{person}.png")
            rec["faces"][person] = {
                "similarity": round(score, 6),
                "wrong_person_similarity": round(wrong, 6),
                "threshold": round(thresholds[person], 6),
                "pass": bool(score >= thresholds[person] and score > wrong),
                "bbox": [round(float(v), 2) for v in face.bbox],
                "det_score": round(float(face.det_score), 6),
                "attempt_count": 1,
            }
        rec["attempts"].append({"pass": all(f["pass"] for f in rec["faces"].values()),
                               "scores": {p: f["similarity"] for p, f in rec["faces"].items()}})
        records[name] = rec

    result = {
        "method": "InsightFace buffalo_l ArcFace cosine similarity; prototype is normalized mean of three official portraits plus closest matching detected face from each of seven refs/real/couple_*.jpg photos.",
        "sheet_baseline": sheet_scores,
        "S_sheet": {p: min(v) for p, v in sheet_scores.items()},
        "thresholds": {p: round(v, 6) for p, v in thresholds.items()},
        "images": records,
    }
    (OUT / "_tmp_refs" / "final7_numeric_qc.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
