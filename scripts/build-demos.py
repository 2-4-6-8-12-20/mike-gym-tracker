#!/usr/bin/env python3
"""Build small looping form GIFs from Everkinetic drawings (CC BY-SA 3.0).

Source files are the two-pose diagrams Everkinetic published and that
Wikimedia Commons hosts. This script rasterizes them, trims shared
whitespace, and writes a two- or three-frame GIF per exercise id.

Changes from the originals: white background, scaled to a 340px square,
whitespace cropped, poses held ~2s and looped. No pose was redrawn.
"""

import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media"
CACHE = Path("/tmp/ek")
UA = "mike-gym-tracker/1.0 (CC BY-SA form demos; attribution in README)"
SIZE = 340
WHITE = (255, 255, 255)
HOLD_MS = 2000

# exercise id -> Wikimedia Commons filenames, in pose order.
# Notes in index.html explain when a drawing is the closest standard movement.
SOURCES = {
    "a1": ["Incline chest press 1.svg", "Incline chest press 2.svg"],
    "a2": ["Seated shoulder press machine 1.svg", "Seated shoulder press machine 2.svg"],
    "a3": ["Butterfly machine 1.svg", "Butterfly machine 2.svg"],
    "a4": ["Lateral dumbbell raises 1.svg", "Lateral dumbbell raises 2.svg"],
    "a5": ["Triceps pushdown with cable 1.svg", "Triceps pushdown with cable 2.svg"],
    "a6": ["Close triceps pushup 1.svg", "Close triceps pushup 2.svg"],
    "a8": ["Cable crossover 1.svg", "Cable crossover 2.svg"],
    "b1": ["T bar rows 1.svg", "T bar rows 2.svg"],
    "b2": ["Underhand pull down 1.svg", "Underhand pull down 2.svg"],
    "b3": ["Reverse grips bent over barbell rows 1.svg", "Reverse grips bent over barbell rows 2.svg"],
    "b4": ["Dumbbell-shrugs-1.png", "Dumbbell-shrugs-2.png"],
    "b5": ["Alternating hammer curl with dumbbell 1.svg", "Alternating hammer curl with dumbbell 2.svg"],
    "b6": ["Standing one arm bicep curl with cable 1.svg", "Standing one arm bicep curl with cable 2.svg"],
    "b7": ["Seated cable rows 1.svg", "Seated cable rows 2.svg"],
    "b8": ["Straight arm push down 1.svg", "Straight arm push down 2.svg"],
    "b9": ["One arm preacher curl with dumbbell 1.svg", "One arm preacher curl with dumbbell 2.svg"],
    "c1": ["Front cable raises 1.svg", "Front cable raises 2.svg"],
    "c2": ["Lateral dumbbell raises 1.svg", "Lateral dumbbell raises 2.svg"],
    "c3": ["Seated rear lateral cable raise 1.svg", "Seated rear lateral cable raise 2.svg"],
    "c4": ["Alternating bicep curl with dumbbell 1.svg", "Alternating bicep curl with dumbbell 2.svg"],
    "c5": ["Lying triceps extension with dumbbells 1.svg", "Lying triceps extension with dumbbells 2.svg"],
    "c6": ["Decline crunch 1.svg", "Decline crunch 2.svg"],
    "c7": ["One arm low pulley triceps extension with cable 1.svg", "One arm low pulley triceps extension with cable 2.svg"],
    "d1": ["Romanian dead lift 1.svg", "Romanian dead lift 2.svg"],
    "d2": ["Seated leg curl 1.svg", "Seated leg curl 2.svg"],
    "d3": ["Leg-press-1-1024x670.png", "Leg-press-2-1024x670.png"],
    "d4": ["Step ups with dumbbells 1.svg", "Step ups with dumbbells 2.svg", "Step ups with dumbbells 3.svg"],
    "d5": ["Standing calf raises using machine 1.svg", "Standing calf raises using machine 2.svg"],
    "d6": ["Hip adduction 1.svg", "Hip adduction 2.svg"],
}


def is_svg(path: Path) -> bool:
    head = path.read_bytes()[:300].lower()
    return b"<svg" in head or head.startswith(b"<?xml")


def is_raster(path: Path) -> bool:
    head = path.read_bytes()[:8]
    return head.startswith(b"\x89PNG") or head.startswith(b"\xff\xd8") or head.startswith(b"GIF8")


def find_local(name: str):
    if not CACHE.exists():
        return None
    candidates = []
    for folder in (CACHE / "src", CACHE / "png", CACHE):
        if not folder.exists():
            continue
        candidates.extend([
            folder / name,
            folder / (name + ".thumb.png"),
            folder / (name + ".png"),
            folder / name.replace("/", "_"),
        ])
    for path in candidates:
        if path.exists() and path.stat().st_size > 400 and (is_svg(path) or is_raster(path)):
            return path
    return None


def download(name: str) -> Path:
    dest_dir = CACHE / "src"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=480"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if data[:20].lower().startswith(b"<!doctype") or data[:6].lower().startswith(b"<html"):
        raise RuntimeError("got HTML for " + name)
    dest.write_bytes(data)
    return dest


def on_white(im: Image.Image) -> Image.Image:
    if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, WHITE)
        bg.paste(rgba, mask=rgba.split()[-1])
        return bg
    return im.convert("RGB")


def load_frame(name: str) -> Image.Image:
    path = find_local(name) or download(name)
    if is_svg(path):
        png = CACHE / "raster" / (name + ".png")
        png.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call([
            "rsvg-convert", "-w", "520", "-h", "520", "-a", "-b", "white",
            "-o", str(png), str(path),
        ])
        im = Image.open(png)
    else:
        im = Image.open(path)
    im = on_white(im)
    im.thumbnail((520, 520), Image.Resampling.LANCZOS)
    return im


def content_bbox(im: Image.Image):
    # Near-white counts as background.
    diff = ImageChops.difference(im, Image.new("RGB", im.size, WHITE))
    gray = diff.convert("L")
    mask = gray.point(lambda p: 255 if p > 12 else 0)
    return mask.getbbox()


def normalize(frames):
    boxes = [content_bbox(im) for im in frames]
    if any(b is None for b in boxes):
        raise RuntimeError("blank frame")
    left = min(b[0] for b in boxes)
    top = min(b[1] for b in boxes)
    right = max(b[2] for b in boxes)
    bottom = max(b[3] for b in boxes)
    pad = 12
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(frames[0].width, right + pad)
    bottom = min(frames[0].height, bottom + pad)
    # Frames may differ in size before crop (png vs svg). Crop in each image's own space
    # only when sizes match; otherwise fit each full image.
    same = all(im.size == frames[0].size for im in frames)
    fitted = []
    for im in frames:
        if same:
            cropped = im.crop((left, top, right, bottom))
        else:
            box = content_bbox(im)
            cropped = im.crop((
                max(0, box[0] - pad),
                max(0, box[1] - pad),
                min(im.width, box[2] + pad),
                min(im.height, box[3] + pad),
            ))
        cropped.thumbnail((SIZE - 8, SIZE - 8), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (SIZE, SIZE), WHITE)
        canvas.paste(cropped, ((SIZE - cropped.width) // 2, (SIZE - cropped.height) // 2))
        fitted.append(canvas)
    return fitted


def save_gif(frames, dest: Path):
    combo = Image.new("RGB", (SIZE * len(frames), SIZE), WHITE)
    for i, frame in enumerate(frames):
        combo.paste(frame, (i * SIZE, 0))
    palette = combo.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    quantized = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    quantized[0].save(
        dest,
        save_all=True,
        append_images=quantized[1:],
        duration=HOLD_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    subprocess.check_call([
        "gifsicle", "-O3", "--colors", "32", "--no-warnings", "-o", str(dest), str(dest),
    ])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    selected = sys.argv[1:] or list(SOURCES)
    unknown = [ex_id for ex_id in selected if ex_id not in SOURCES]
    if unknown:
        raise SystemExit("unknown exercise id: " + ", ".join(unknown))
    for ex_id in selected:
        names = SOURCES[ex_id]
        frames = normalize([load_frame(name) for name in names])
        dest = OUT / f"{ex_id}.gif"
        save_gif(frames, dest)
        print(f"{ex_id}.gif  {dest.stat().st_size:6d}  poses={len(frames)}")


if __name__ == "__main__":
    main()
