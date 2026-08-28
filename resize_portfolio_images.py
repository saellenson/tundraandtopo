"""
resize_portfolio_images.py

Generates web-ready versions of everything in your Portfolio folder:
  - thumbs/  small, fast-loading versions for the grid view (static images only)
  - full/    larger, higher-quality versions for the lightbox

Videos (.mp4) and GIFs are copied as-is into full/ (and thumbs/ for mp4, since the
grid plays them directly) rather than resized — resizing would break their animation.

All filenames are slugified (lowercase, hyphens, no spaces/punctuation) so they work
cleanly as URLs on the website, e.g. "40 Mile River, AK.jpg" -> "40-mile-river-ak.jpg"

HOW TO RUN:
1. Install Pillow if you don't have it:  pip install Pillow
2. Run:  python resize_portfolio_images.py
3. Match up the printed slug names with the "thumb"/"full" paths in index.html —
   rename either side if anything doesn't line up.
"""

import re
import shutil
from pathlib import Path
from PIL import Image

# ---- SETTINGS (edit these if you want) ----
SOURCE_FOLDER = Path(r"C:\Users\saellenson\OneDrive - Dewberry\Misc\Portfolio")
OUTPUT_FOLDER = SOURCE_FOLDER / "resized"

THUMB_MAX_DIMENSION = 1000   # grid thumbnails — small & fast
THUMB_QUALITY = 78

FULL_MAX_DIMENSION = 3200    # lightbox images — sharp, still web-reasonable
FULL_QUALITY = 90

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}
COPY_ONLY_EXTENSIONS = {".mp4", ".gif"}  # not resized — just slugified + copied


def slugify(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return re.sub(r"-+", "-", name).strip("-")


def save_version(img, max_dim, quality, out_path):
    ratio = min(1.0, max_dim / max(img.width, img.height))
    new_size = (int(img.width * ratio), int(img.height * ratio))
    resized = img.resize(new_size, Image.LANCZOS)
    resized.save(out_path, "JPEG", quality=quality, optimize=True)
    return new_size, out_path.stat().st_size / (1024 * 1024)


def main():
    if not SOURCE_FOLDER.exists():
        print(f"Folder not found: {SOURCE_FOLDER}")
        return

    thumbs_folder = OUTPUT_FOLDER / "thumbs"
    full_folder = OUTPUT_FOLDER / "full"
    thumbs_folder.mkdir(parents=True, exist_ok=True)
    full_folder.mkdir(parents=True, exist_ok=True)

    all_files = [f for f in SOURCE_FOLDER.iterdir() if f.is_file()]
    image_files = [f for f in all_files if f.suffix.lower() in IMAGE_EXTENSIONS]
    copy_files = [f for f in all_files if f.suffix.lower() in COPY_ONLY_EXTENSIONS]

    if not image_files and not copy_files:
        print(f"No image/video files found in {SOURCE_FOLDER}")
        return

    print(f"Found {len(image_files)} image(s) and {len(copy_files)} video/gif file(s).\n")

    for file in image_files:
        try:
            with Image.open(file) as img:
                img = img.convert("RGB")
                slug = slugify(file.stem) + ".jpg"

                thumb_size, thumb_mb = save_version(
                    img, THUMB_MAX_DIMENSION, THUMB_QUALITY, thumbs_folder / slug
                )
                full_size, full_mb = save_version(
                    img, FULL_MAX_DIMENSION, FULL_QUALITY, full_folder / slug
                )

                print(f"  {file.name}  ->  {slug}")
                print(f"    thumb: {thumb_size[0]}x{thumb_size[1]}  ({thumb_mb:.1f} MB)")
                print(f"    full:  {full_size[0]}x{full_size[1]}  ({full_mb:.1f} MB)")

        except Exception as e:
            print(f"  Failed on {file.name}: {e}")

    for file in copy_files:
        try:
            slug = slugify(file.stem) + file.suffix.lower()
            shutil.copy2(file, full_folder / slug)
            if file.suffix.lower() == ".mp4":
                shutil.copy2(file, thumbs_folder / slug)  # grid plays the mp4 directly
            print(f"  {file.name}  ->  {slug}  (copied, not resized)")
        except Exception as e:
            print(f"  Failed on {file.name}: {e}")

    print(f"\nDone. Upload the contents of:")
    print(f"  {thumbs_folder}  ->  your repo's images/thumbs/ folder")
    print(f"  {full_folder}    ->  your repo's images/full/ folder")


if __name__ == "__main__":
    main()
