import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from insightface.app import FaceAnalysis


def read_image(path):
    raw = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def unit(vector):
    vector = np.asarray(vector, dtype=np.float32)
    return vector / max(float(np.linalg.norm(vector)), 1e-8)


def similarity(a, b):
    return float(np.dot(unit(a), unit(b)))


def reference_vectors(app, refs):
    result = {}
    for person in ("groom", "bride"):
        vectors = []
        for i in range(1, 4):
            path = Path(refs) / f"{person}_photo_{i}.jpg"
            faces = app.get(read_image(path))
            if not faces:
                raise RuntimeError(f"No face detected in {path}")
            face = max(faces, key=lambda f: float((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])))
            vectors.append(face.normed_embedding)
        direct = unit(np.mean(vectors, axis=0))
        for path in sorted((Path(refs) / "real").glob("couple_*.jpg")):
            faces = app.get(read_image(path))
            if faces:
                face = max(faces, key=lambda f: similarity(f.normed_embedding, direct))
                vectors.append(face.normed_embedding)
        result[person] = unit(np.mean(vectors, axis=0))
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect scene faces and make 2.2x, 1024px crops for face repaint.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--refs", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--people", nargs="+", choices=("groom", "bride"), required=True)
    args = parser.parse_args()

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    prototypes = reference_vectors(app, args.refs)
    image = read_image(args.image)
    faces = app.get(image)
    if not faces:
        raise RuntimeError(f"No faces detected in {args.image}")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    h, w = image.shape[:2]
    used = set()
    records = []

    for person in args.people:
        available = [f for f in faces if id(f) not in used]
        face = max(available or faces, key=lambda f: similarity(f.normed_embedding, prototypes[person]))
        used.add(id(face))
        other = "bride" if person == "groom" else "groom"
        box = np.asarray(face.bbox, dtype=np.float32)
        face_height = float(box[3] - box[1])
        side = max(64, int(round(2.2 * face_height)))
        cx, cy = ((box[:2] + box[2:]) * 0.5).tolist()
        x1 = int(round(cx - side / 2)); y1 = int(round(cy - side / 2))
        x1 = min(max(0, x1), max(0, w - side)); y1 = min(max(0, y1), max(0, h - side))
        x2, y2 = x1 + side, y1 + side
        crop = image[y1:y2, x1:x2]
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        crop = Image.fromarray(crop).resize((1024, 1024), Image.Resampling.LANCZOS)
        path = out_dir / f"{args.prefix}__{person}_face_1024.png"
        crop.save(path)
        records.append({
            "person": person,
            "bbox": [round(float(v), 2) for v in box],
            "crop_box": [x1, y1, x2, y2],
            "crop_path": str(path),
            "similarity": round(similarity(face.normed_embedding, prototypes[person]), 6),
            "wrong_person_similarity": round(similarity(face.normed_embedding, prototypes[other]), 6),
            "det_score": round(float(face.det_score), 6),
            "face_count": len(faces),
        })
    print(records)


if __name__ == "__main__":
    main()
