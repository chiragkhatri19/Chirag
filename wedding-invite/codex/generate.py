"""Generate, assemble, and validate Veeral and Konika wedding-invite artwork.

Image-generation helpers use the official OpenAI Python SDK and read
OPENAI_API_KEY from the environment. This workspace's delivered images were
created with the Codex image-generation service because that key was absent;
the helper is retained so the SDK workflow can be rerun when a key is set.
"""

from __future__ import annotations

import base64
from contextlib import ExitStack
import json
import os
import sys
import time
from collections import deque
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError


HERE = Path(__file__).resolve().parent
REFS = HERE / "refs"
OUT = HERE / "out"
PORTRAIT = (1024, 1536)
PANEL_OVERLAP = 384
PANEL_APPEND = 640


def openai_client() -> OpenAI:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY in the environment before using SDK generation/QC.")
    return OpenAI()


def generate_image(prompt: str, destination: Path, references: list[Path] | None = None,
                   size: str = "1024x1536", transparent: bool = False) -> str:
    """Generate/edit one PNG; fall back from gpt-image-1.5 to gpt-image-1."""
    client = openai_client()
    references = references or []
    for model in ("gpt-image-1.5", "gpt-image-1"):
        for attempt in range(5):
            try:
                params = dict(model=model, prompt=prompt, size=size, quality="high",
                              output_format="png", background="transparent" if transparent else "opaque")
                if references:
                    with ExitStack() as stack:
                        params["image"] = [stack.enter_context(path.open("rb")) for path in references]
                        params["input_fidelity"] = "high"
                        result = client.images.edit(**params)
                else:
                    result = client.images.generate(**params)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(base64.b64decode(result.data[0].b64_json))
                return model
            except (RateLimitError, APIConnectionError) as exc:
                if attempt == 4:
                    raise
                time.sleep(min(60, 2 ** (attempt + 1)))
            except APIStatusError as exc:
                if exc.status_code in (408, 409, 429, 500, 502, 503, 504) and attempt < 4:
                    time.sleep(min(60, 2 ** (attempt + 1)))
                    continue
                break
    raise RuntimeError("Neither gpt-image-1.5 nor gpt-image-1 was available to this API key.")


def qc_with_vision(image_path: Path, prompt: str, references: list[Path] | None = None) -> dict:
    """Return structured vision QC from the SDK; all six scores must be >= 9."""
    client = openai_client()
    inputs = [image_path, *(references or [])]
    content = [{"type": "text", "text": prompt}]
    for path in inputs:
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        mime_type = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{data}"}})
    response = client.chat.completions.create(
        model=os.environ.get("OPENAI_VISION_MODEL", "gpt-4.1"),
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": content}],
        temperature=0,
    )
    result = json.loads(response.choices[0].message.content)
    result["pass"] = all(int(score) >= 9 for score in result.get("scores", {}).values())
    return result


def _canvas_fit(image: Image.Image, size: tuple[int, int], *, transparent: bool) -> Image.Image:
    """Keep cut-outs proportional; fill opaque scene canvases to the required frame."""
    image = image.convert("RGBA" if transparent else "RGB")
    if not transparent:
        return image.resize(size, Image.Resampling.LANCZOS)
    contained = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.alpha_composite(contained, ((size[0] - contained.width) // 2,
                                       (size[1] - contained.height) // 2))
    return canvas


def normalize_assets() -> None:
    transparent_ids = {"01_anchor_couple", "02_rickshaw", "03_puppets", "B1_banner",
                       "F1_fg_drape", "F2_fg_pillar", "F3_fg_flowers", "F4_fg_petals"}
    for path in sorted(OUT.glob("*.png")):
        if path.name == "P_panorama.png":
            continue
        if path.stem == "02_rickshaw":
            target = (1536, 1024)
            with Image.open(path) as opened:
                image = opened.convert("RGBA")
                # Preserve complete wheels and create a genuine clear margin
                # around the landscape cut-out, even when the source fills frame.
                bbox = image.getchannel("A").getbbox()
                needs_margin = bbox is None or bbox[0] < 40 or bbox[1] < 40 or \
                    target[0] - bbox[2] < 40 or target[1] - bbox[3] < 40
                if needs_margin:
                    fitted = ImageOps.contain(image, (int(target[0] * 0.86), int(target[1] * 0.86)),
                                              method=Image.Resampling.LANCZOS)
                    canvas = Image.new("RGBA", target, (0, 0, 0, 0))
                    canvas.alpha_composite(fitted, ((target[0] - fitted.width) // 2,
                                                     (target[1] - fitted.height) // 2))
                else:
                    canvas = image
                canvas.save(path, format="PNG", optimize=True)
            continue
        else:
            target = PORTRAIT
        with Image.open(path) as opened:
            fixed = _canvas_fit(opened, target, transparent=path.stem in transparent_ids)
            fixed.save(path, format="PNG", optimize=True)


def stitch_panorama() -> Image.Image:
    panels = []
    for index in range(1, 6):
        path = OUT / f"P{index}.png"
        if not path.exists():
            raise FileNotFoundError(path)
        with Image.open(path) as image:
            panels.append(image.convert("RGB").resize(PORTRAIT, Image.Resampling.LANCZOS))

    seam_overlap = 32
    width = PORTRAIT[0] + 4 * (PORTRAIT[0] - seam_overlap)
    panorama = Image.new("RGB", (width, PORTRAIT[1]))
    panorama.paste(panels[0], (0, 0))
    for index, panel in enumerate(panels[1:], start=1):
        x = index * (PORTRAIT[0] - seam_overlap)
        prior = panorama.crop((x, 0, x + seam_overlap, PORTRAIT[1]))
        incoming = panel.crop((0, 0, seam_overlap, PORTRAIT[1]))
        ramp = np.linspace(0, 1, seam_overlap, dtype=np.float32)[None, :, None]
        blended = np.asarray(prior, dtype=np.float32) * (1 - ramp) + np.asarray(incoming, dtype=np.float32) * ramp
        panorama.paste(Image.fromarray(np.uint8(np.clip(blended, 0, 255))), (x, 0))
        panorama.paste(panel.crop((seam_overlap, 0, PORTRAIT[0], PORTRAIT[1])),
                       (x + seam_overlap, 0))
    # 4608 px is the requested approximate panorama width; this gentle uniform
    # horizontal reduction retains every panel and keeps all three windows whole.
    panorama = panorama.resize((4608, PORTRAIT[1]), Image.Resampling.LANCZOS)
    panorama.save(OUT / "P_panorama.png", optimize=True)
    return panorama


def green_components(image: Image.Image) -> list[tuple[int, int, int, int]]:
    rgb = np.asarray(image.convert("RGB"))
    mask = (rgb[:, :, 1] > 200) & (rgb[:, :, 0] < 80) & (rgb[:, :, 2] < 80)
    seen = np.zeros(mask.shape, dtype=bool)
    height, width = mask.shape
    components: list[tuple[int, int, int, int]] = []
    for sy, sx in np.argwhere(mask):
        sy, sx = int(sy), int(sx)
        if seen[sy, sx]:
            continue
        queue = deque([(sy, sx)])
        seen[sy, sx] = True
        min_x = max_x = sx
        min_y = max_y = sy
        count = 0
        while queue:
            y, x = queue.popleft()
            count += 1
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    queue.append((ny, nx))
        if count >= 5000:
            components.append((min_x, min_y, max_x + 1, max_y + 1))
    return sorted(components, key=lambda box: box[0])


def write_windows(panorama: Image.Image) -> dict:
    boxes = green_components(panorama)
    if len(boxes) != 3:
        raise RuntimeError(f"Expected exactly 3 connected chroma-green windows; found {len(boxes)}: {boxes}")

    def corners(box: tuple[int, int, int, int]) -> list[list[int]]:
        left, top, right, bottom = box
        return [[left, top], [right - 1, top], [right - 1, bottom - 1], [left, bottom - 1]]

    data = {f"day{i + 1}": corners(box) for i, box in enumerate(boxes)}
    # Approximate wall targets, in stitched panorama coordinates.
    data["monogram_start"] = [[280, 620], [700, 620], [700, 1170], [280, 1170]]
    data["monogram_end"] = [[3660, 370], [3870, 370], [3870, 910], [3660, 910]]
    data["banner_area"] = [[1020, 600], [1760, 600], [1760, 1190], [1020, 1190]]
    (OUT / "windows.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def contact_sheet() -> None:
    paths = [p for p in sorted(OUT.glob("*.png")) if p.name != "P_panorama.png"]
    paths.append(OUT / "P_panorama.png")
    cols, cell_w, cell_h, label_h = 4, 240, 300, 30
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * (cell_h + label_h)), (248, 244, 234))
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(paths):
        x, y = (i % cols) * cell_w, (i // cols) * (cell_h + label_h)
        with Image.open(path) as opened:
            thumb = ImageOps.contain(opened.convert("RGBA"), (cell_w - 12, cell_h - 12), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x + (cell_w - thumb.width) // 2, y + (cell_h - thumb.height) // 2), thumb)
        draw.text((x + 6, y + cell_h + 5), path.stem, fill=(48, 38, 28))
    sheet.save(OUT / "contact_sheet.jpg", quality=90, optimize=True)


def verify() -> dict:
    problems = []
    report = {}
    for path in sorted(OUT.glob("*.png")):
        with Image.open(path) as image:
            report[path.name] = {"size": list(image.size), "mode": image.mode}
            if path.stem in {"01_anchor_couple", "02_rickshaw", "03_puppets", "B1_banner", "F1_fg_drape",
                             "F2_fg_pillar", "F3_fg_flowers", "F4_fg_petals"}:
                target_size = (1536, 1024) if path.stem == "02_rickshaw" else PORTRAIT
                if image.size != target_size or image.mode != "RGBA":
                    problems.append(f"{path.name}: expected {target_size} RGBA, found {image.size}/{image.mode}")
                elif any(image.getpixel(point)[3] != 0 for point in ((0, 0), (image.width - 1, 0),
                                                                      (0, image.height - 1),
                                                                      (image.width - 1, image.height - 1))):
                    problems.append(f"{path.name}: transparent corners required")
            elif path.stem == "02_rickshaw":
                if image.size != (1536, 1024) or image.mode != "RGBA":
                    problems.append(f"{path.name}: expected landscape RGBA, found {image.size}/{image.mode}")
            elif path.stem.startswith("P") and path.stem != "P_panorama":
                if image.size != PORTRAIT or image.mode != "RGB":
                    problems.append(f"{path.name}: expected portrait opaque RGB")
            elif path.stem == "P_panorama":
                if image.size != (4608, 1536) or image.mode != "RGB":
                    problems.append(f"{path.name}: expected 4608x1536 opaque RGB, found {image.size}/{image.mode}")
            elif image.size != PORTRAIT or image.mode != "RGB":
                problems.append(f"{path.name}: expected portrait opaque RGB, found {image.size}/{image.mode}")
    (OUT / "size_report.json").write_text(json.dumps({"images": report, "problems": problems}, indent=2) + "\n",
                                             encoding="utf-8")
    if problems:
        raise RuntimeError("Output validation failed:\n" + "\n".join(problems))
    return report


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    normalize_assets()
    panorama = stitch_panorama()
    write_windows(panorama)
    contact_sheet()
    verify()
    print(f"Prepared outputs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
