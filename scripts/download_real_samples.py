"""Download real road damage images from HuggingFace for testing."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from huggingface_hub import hf_hub_download, list_repo_files

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPO = "Programmer-RD-AI/road-issues-detection-dataset"
SAMPLE_DIR = PROJECT_ROOT / "data" / "samples"
TEMP_DIR = PROJECT_ROOT / "data" / "_temp_hf"


def download_real_samples() -> None:
    """Download a few real road damage images from HuggingFace."""
    print(f"Listing files from {REPO}...")
    all_files = list_repo_files(REPO, repo_type="dataset")

    # Select images: potholes + damaged roads
    pothole = [f for f in all_files if "Pothole" in f and f.endswith((".jpg", ".png"))][:3]
    damaged = [f for f in all_files if "Damaged Road" in f and f.endswith((".jpg", ".png"))][:3]

    to_download = pothole + damaged
    print(f"Found {len(pothole)} pothole, {len(damaged)} damaged road images")

    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    for i, f in enumerate(to_download):
        fname = Path(f).name
        try:
            path = hf_hub_download(
                repo_id=REPO, filename=f, repo_type="dataset", local_dir=str(TEMP_DIR)
            )
            dest = SAMPLE_DIR / f"real_damage_{i+1:02d}_{fname}"
            shutil.copy2(path, dest)
            print(f"  Saved: {dest.name}")
        except Exception as e:
            print(f"  Failed {fname}: {e}")

    # Cleanup temp
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    print(f"\nDone! Real images in {SAMPLE_DIR}")


if __name__ == "__main__":
    download_real_samples()
