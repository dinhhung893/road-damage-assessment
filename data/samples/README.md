# Data Samples — Road Damage Test Images

## Source
Synthetic images generated for pipeline verification (Phase 1).
Real RDD2022 images should be added via `scripts/download_samples.py` (requires Kaggle API key).

## Contents

| File | Description | Expected Detection |
|------|-------------|-------------------|
| `asphalt_clean_01.jpg` | Clean asphalt (no damage) | 0 detections |
| `asphalt_longitudinal_01.jpg` | Horizontal line (longitudinal crack) | D00 (may or may not detect — synthetic) |
| `asphalt_transverse_01.jpg` | Vertical line (transverse crack) | D10 (may or may not detect — synthetic) |
| `asphalt_alligator_01.jpg` | Grid pattern (alligator crack) | D20 (may or may not detect — synthetic) |
| `asphalt_pothole_01.jpg` | Dark circle (pothole) | D40 (may or may not detect — synthetic) |
| `asphalt_mixed_01.jpg` | Multiple damages | Mixed (may or may not detect — synthetic) |

## Note
These synthetic images are for **pipeline verification only** — confirming that the
detector loads, runs, and produces output. They are NOT representative of real
road damage and may not trigger detections.

For real-world testing, download RDD2022 test images:
```bash
pip install kaggle
python scripts/download_samples.py
```
