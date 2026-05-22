# Phase 4: FastSAM Segmentation — Research

**Phase:** 04
**Date:** 2026-05-23

---

## FastSAM Overview

FastSAM (Fast Segment Anything Model) is based on YOLOv8-seg architecture. It performs instance segmentation by first running "everything" segmentation on the full image, then filtering results with prompts (bbox, point, text).

**Key finding:** FastSAM is built into `ultralytics` — no separate package needed.

```python
from ultralytics import FastSAM
model = FastSAM("FastSAM-s.pt")  # or "FastSAM-x.pt"
results = model(image, device="cpu", retina_masks=True, imgsz=1024, conf=0.4, iou=0.9)
```

## Bbox-Prompted Segmentation

Two approaches:

### Approach 1: Full-image then filter (FastSAMPrompt)
```python
from fastsam import FastSAM, FastSAMPrompt
model = FastSAM("FastSAM-s.pt")
everything_results = model(image, device="cpu", retina_masks=True, imgsz=1024)
prompt_process = FastSAMPrompt(image, everything_results, device="cpu")
# bbox in [x1, y1, x2, y2] format
ann = prompt_process.box_prompt(bboxes=[[x1, y1, x2, y2]])
```
- Runs FastSAM once on full image → filters with IoU matching
- Faster for multiple bboxes (1 inference per image)
- Requires FastSAMPrompt utility from FastSAM repo

### Approach 2: Crop + segment (our decision D-18)
```python
from ultralytics import FastSAM
model = FastSAM("FastSAM-s.pt")
# Crop bbox region from image
crop = image[y1:y2, x1:x2]
result = model(crop, device="cpu", retina_masks=True, imgsz=640)
masks = result[0].masks  # Masks object
```
- Simpler, no IoU matching needed
- Each bbox = 1 FastSAM inference
- Slower for many detections but more reliable

## Checkpoint Sources

| Model | Size | Source |
|-------|------|--------|
| FastSAM-s.pt | ~23MB | HuggingFace: Uminosachi/FastSAM |
| FastSAM-x.pt | ~126MB | HuggingFace: conrevo/Segment-Anything-A1111 |

Both also available via ultralytics auto-download if placed in correct directory.

## Inference Speed Estimates (i5-4300U CPU)

- YOLOv12s detection: ~900ms/image (benchmarked)
- FastSAM-s per crop (640px): estimated ~500-800ms
- FastSAM-x per crop (640px): estimated ~1500-3000ms
- Total per image (1 detection): ~1.4-1.7s with FastSAM-s

## Integration with Existing Code

### Detection → Segmentation Pipeline
Current: `RoadDamageDetector.detect()` → `DetectionResult.pci_detections`
New: After detect, iterate pci_detections → crop bbox → FastSAM → add mask data to Detection

### PCI Engine Integration
Current: `PCIEngine.calculate_pci()` uses `Detection.bbox` area with correction factors
New: If `Detection.mask_area_sqft > 0`, use mask area (no correction). Otherwise fallback to bbox.

### Supervision MaskAnnotator
`supervision` already installed (v0.28.0). Has `supervision.annotators.core.MaskAnnotator` for rendering semi-transparent mask overlays.

```python
import supervision as sv
mask_annotator = sv.MaskAnnotator()
annotated = mask_annotator.annotate(scene=image, detections=sv_detections)
```

## Risks

1. **CPU speed**: FastSAM-s adds ~500-800ms per detection. With 5+ detections, could be 3-4s total. Acceptable for thesis demo.
2. **Empty masks**: FastSAM may return no mask for small/ambiguous bboxes. Fallback to bbox area.
3. **Memory**: FastSAM model ~23MB in RAM. Total with YOLOv12s: ~42MB. Well within 300MB limit.
4. **FastSAMPrompt dependency**: If using crop approach (D-18), no need for FastSAMPrompt utility — simpler.

## Validation Architecture

Not applicable — Phase 4 is integration work, not a new algorithm. Validation is through existing PCI tests + visual inspection of mask overlays.
