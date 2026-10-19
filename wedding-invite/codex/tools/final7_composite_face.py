import argparse
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis


def image_read(path):
    raw = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def image_write(path, image):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = path.suffix or ".png"
    ok, data = cv2.imencode(ext, image)
    if not ok:
        raise ValueError(f"Could not encode image: {path}")
    data.tofile(str(path))


def unit(vector):
    vector = np.asarray(vector, dtype=np.float32)
    return vector / max(float(np.linalg.norm(vector)), 1e-8)


def reference_embedding(app, ref_dir, person):
    vectors = []
    for i in range(1, 4):
        path = Path(ref_dir) / f"{person}_photo_{i}.jpg"
        faces = app.get(image_read(path))
        if not faces:
            raise RuntimeError(f"No face detected in official reference {path}")
        face = max(faces, key=lambda f: float((f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])))
        vectors.append(face.normed_embedding)
    direct = unit(np.mean(vectors, axis=0))
    for path in sorted((Path(ref_dir) / "real").glob("couple_*.jpg")):
        faces = app.get(image_read(path))
        if faces:
            face = max(faces, key=lambda f: float(np.dot(unit(f.normed_embedding), direct)))
            vectors.append(face.normed_embedding)
    return unit(np.mean(vectors, axis=0))


def choose_face(app, image, prototype):
    faces = app.get(image)
    if not faces:
        raise RuntimeError("No face detected in face crop")
    return max(faces, key=lambda f: float(np.dot(unit(f.normed_embedding), prototype)))


def main():
    parser = argparse.ArgumentParser(description="Align and feather-composite a 1024px identity face repaint.")
    parser.add_argument("--base", required=True, help="Original full scene PNG")
    parser.add_argument("--target-crop", required=True, help="1024x1024 Lanczos crop from the original scene")
    parser.add_argument("--edit", required=True, help="ImageGen face repaint corresponding to target-crop")
    parser.add_argument("--person", choices=("groom", "bride"), required=True)
    parser.add_argument("--ref-dir", required=True, help="Directory containing the official *_photo_1..3.jpg files")
    parser.add_argument("--box", nargs=4, type=int, required=True, metavar=("X1", "Y1", "X2", "Y2"),
                        help="Square target-crop bounds in original scene coordinates")
    parser.add_argument("--out", required=True, help="Output full scene PNG")
    parser.add_argument("--feather", type=float, default=24.0, help="Gaussian feather radius in 1024px crop space")
    args = parser.parse_args()

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    prototype = reference_embedding(app, args.ref_dir, args.person)
    base = image_read(args.base)
    target = image_read(args.target_crop)
    edited = image_read(args.edit)
    if target.shape[:2] != (1024, 1024):
        raise ValueError(f"Target crop must be 1024x1024, got {target.shape[1]}x{target.shape[0]}")
    x1, y1, x2, y2 = args.box
    side = x2 - x1
    if side != y2 - y1 or side <= 0 or x1 < 0 or y1 < 0 or x2 > base.shape[1] or y2 > base.shape[0]:
        raise ValueError("The supplied box must be an in-bounds square")

    target_face = choose_face(app, target, prototype)
    edited_face = choose_face(app, edited, prototype)
    transform, _ = cv2.estimateAffinePartial2D(
        np.asarray(edited_face.kps, dtype=np.float32),
        np.asarray(target_face.kps, dtype=np.float32),
        method=cv2.LMEDS,
    )
    if transform is None:
        raise RuntimeError("Could not align edited face landmarks to target landmarks")
    aligned = cv2.warpAffine(edited, transform, (1024, 1024), flags=cv2.INTER_LANCZOS4,
                             borderMode=cv2.BORDER_REFLECT_101)

    bbox = np.asarray(target_face.bbox, dtype=np.float32)
    center = ((bbox[:2] + bbox[2:]) * 0.5)
    bw, bh = float(bbox[2] - bbox[0]), float(bbox[3] - bbox[1])
    scale = 1024.0 / side
    cx, cy = int(round(center[0] * scale)), int(round(center[1] * scale))
    rx, ry = int(round(bw * 0.62 * scale)), int(round(bh * 0.70 * scale))
    mask = np.zeros((1024, 1024), dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), (max(1, rx), max(1, ry)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (0, 0), args.feather)

    # Match broad skin tone in LAB while preserving local painted texture.
    core = (mask > 220)
    base_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
    edit_lab = cv2.cvtColor(aligned, cv2.COLOR_BGR2LAB).astype(np.float32)
    if np.count_nonzero(core) > 100:
        for channel in range(3):
            src = edit_lab[:, :, channel][core]
            dst = base_lab[:, :, channel][core]
            src_std = max(float(src.std()), 1.0)
            dst_std = float(dst.std())
            gain = np.clip(dst_std / src_std, 0.80, 1.25)
            edit_lab[:, :, channel] = (edit_lab[:, :, channel] - float(src.mean())) * gain + float(dst.mean())
    aligned = cv2.cvtColor(np.clip(edit_lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)

    patch = cv2.resize(aligned, (side, side), interpolation=cv2.INTER_LANCZOS4)
    alpha = cv2.resize(mask, (side, side), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    alpha = alpha[:, :, None]
    destination = base[y1:y2, x1:x2].astype(np.float32)
    base[y1:y2, x1:x2] = np.clip(patch.astype(np.float32) * alpha + destination * (1.0 - alpha), 0, 255).astype(np.uint8)
    image_write(args.out, base)
    print({"person": args.person, "bbox_crop": [round(float(v), 2) for v in bbox],
           "landmark_similarity": round(float(np.linalg.norm(transform[:, :2])), 4),
           "mask_feather": args.feather, "output": str(args.out)})


if __name__ == "__main__":
    main()
