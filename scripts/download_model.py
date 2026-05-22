"""Auto-download pretrained model weights from HuggingFace.

Downloads:
- YOLOv12s detection weights from SreekarAditya/yolo-rdd2022-benchmark
- FastSAM-s segmentation weights from Uminosachi/FastSAM
- FastSAM-x segmentation weights from Uminosatchi/FastSAM (optional)

Usage:
    python scripts/download_model.py          # download all
    python scripts/download_model.py --fastsam-only  # FastSAM only
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from huggingface_hub import hf_hub_download

REPO_ID = "SreekarAditya/yolo-rdd2022-benchmark"
FILENAME = "yolo-rdd2022-benchmark/yolo12s_seed0_best.pt"
LOCAL_DIR = str(_PROJECT_ROOT / "models")

# Actual model class names (verified from download)
MODEL_CLASSES = {
    0: "longitudinal_crack",  # D00
    1: "transverse_crack",     # D10
    2: "alligator_crack",      # D20
    3: "pothole",              # D40
}

# ASTM D6433 short codes for PCI mapping
CLASS_CODE_MAP = {
    "longitudinal_crack": "D00",
    "transverse_crack": "D10",
    "alligator_crack": "D20",
    "pothole": "D40",
}

REPAIR_CLASS_NAMES = {"repair", "other"}


def download_model() -> Path:
    """Download YOLOv12s weights from HuggingFace. Returns local path."""
    print(f"Downloading from {REPO_ID}...")
    pt_path = hf_hub_download(
        repo_id=REPO_ID,
        filename=FILENAME,
        local_dir=LOCAL_DIR,
    )
    print(f"Downloaded: {pt_path}")
    return Path(pt_path)


def verify_model(pt_path: Path) -> dict:
    """Verify model loads and check class names. Returns model info dict."""
    from ultralytics import YOLO

    model = YOLO(str(pt_path))
    names = model.names
    num_classes = len(names)

    info = {
        "path": str(pt_path),
        "num_classes": num_classes,
        "names": names,
        "has_repair": any(
            v.lower() in REPAIR_CLASS_NAMES for v in names.values()
        ),
    }

    print(f"\nModel verification:")
    print(f"  Classes: {names}")
    print(f"  Count: {num_classes}")
    print(f"  Has Repair class: {info['has_repair']}")

    # Check if classes match expected
    if names == MODEL_CLASSES:
        print("  ✓ Classes match expected RDD2022 (4 classes)")
    elif num_classes == 5 and info["has_repair"]:
        print("  ✓ 5 classes detected (4 damage + Repair)")
        print("  → Repair class will be excluded from PCI calculation")
    else:
        print(f"  ⚠ Unexpected class mapping: {names}")
        print(f"  Expected: {MODEL_CLASSES}")

    return info


# --- FastSAM checkpoints ---

FASTSAM_REPOS = {
    "FastSAM-s.pt": "Uminosachi/FastSAM",
    "FastSAM-x.pt": "Uminosachi/FastSAM",
}


def download_fastsam(variant: str = "both") -> list[Path]:
    """Download FastSAM checkpoint(s) from HuggingFace.

    Args:
        variant: "s", "x", or "both"

    Returns:
        List of downloaded file paths.
    """
    targets = []
    if variant in ("s", "both"):
        targets.append("FastSAM-s.pt")
    if variant in ("x", "both"):
        targets.append("FastSAM-x.pt")

    downloaded = []
    for filename in targets:
        repo_id = FASTSAM_REPOS[filename]
        local_path = _PROJECT_ROOT / "models" / filename
        if local_path.exists():
            print(f"Already exists: {local_path}")
            downloaded.append(local_path)
            continue

        print(f"Downloading {filename} from {repo_id}...")
        pt_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(_PROJECT_ROOT / "models"),
        )
        print(f"Downloaded: {pt_path}")
        downloaded.append(Path(pt_path))

    return downloaded


def verify_fastsam(pt_path: Path) -> dict:
    """Verify FastSAM model loads. Returns model info dict."""
    from ultralytics import FastSAM

    model = FastSAM(str(pt_path))
    info = {
        "path": str(pt_path),
        "task": model.task,
    }
    print(f"  FastSAM verification: {info}")
    return info


if __name__ == "__main__":
    fastsam_only = "--fastsam-only" in sys.argv

    if not fastsam_only:
        pt_path = download_model()
        verify_model(pt_path)

    paths = download_fastsam()
    for p in paths:
        verify_fastsam(p)
