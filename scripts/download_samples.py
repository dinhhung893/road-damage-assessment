"""Download sample road damage images from RDD2022 dataset on Kaggle.

Requires Kaggle API key (~/.kaggle/kaggle.json).
Downloads a small subset of test images for demo purposes.

Usage:
    python scripts/download_samples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

SAMPLE_DIR = _PROJECT_ROOT / "data" / "samples"
NUM_SAMPLES_PER_CLASS = 2


def download_samples() -> None:
    """Download sample images from RDD2022 Kaggle dataset."""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("kaggle package not installed. Install with: pip install kaggle")
        print("Also requires ~/.kaggle/kaggle.json API key")
        print("\nFalling back to manual download instructions:")
        print("1. Go to https://www.kaggle.com/datasets/aliabdelmenam/rdd-2022")
        print("2. Download test images")
        print("3. Extract to data/samples/")
        return

    api = KaggleApi()
    api.authenticate()

    dataset = "aliabdelmenam/rdd-2022"
    print(f"Downloading from Kaggle: {dataset}")

    # Download to temp, then cherry-pick sample images
    import zipfile
    import shutil

    temp_dir = _PROJECT_ROOT / "data" / "_temp_rdd2022"
    temp_dir.mkdir(parents=True, exist_ok=True)

    api.dataset_download_files(dataset, path=str(temp_dir), unzip=True)
    print("Download complete. Selecting sample images...")

    # Find test images
    test_dir = temp_dir / "RDD2022" / "test" / "images"
    if not test_dir.exists():
        # Try alternate structure
        for p in temp_dir.rglob("test"):
            if p.is_dir() and (p / "images").exists():
                test_dir = p / "images"
                break

    if not test_dir.exists():
        print(f"Could not find test images in {temp_dir}")
        print("Manual selection required.")
        return

    # Copy a selection of images
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    images = sorted(test_dir.glob("*.jpg")) + sorted(test_dir.glob("*.png"))

    # Take first 12 images as samples
    for i, img in enumerate(images[:12]):
        dest = SAMPLE_DIR / f"rdd2022_sample_{i+1:02d}{img.suffix}"
        shutil.copy2(img, dest)
        print(f"  Copied: {dest.name}")

    # Cleanup temp
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\nDone! {min(12, len(images))} sample images in {SAMPLE_DIR}")


if __name__ == "__main__":
    download_samples()
