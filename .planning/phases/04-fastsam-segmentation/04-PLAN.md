# Phase 4: FastSAM Segmentation Integration (T2) — Plan

**Phase:** 04
**Status:** Planned
**Requirements:** SEG-01, SEG-02, SEG-03, SEG-04, SEG-05
**Depends on:** Phase 3 (✅ complete pending audit)
**Est. Time:** 2 tuần
**Mode:** mvp

---

## Task Overview

| Task | Type | Requirements | Priority | Est. |
|------|------|-------------|----------|------|
| T1: Install & verify FastSAM | infra | SEG-01 | [BLOCKING] | 30min |
| T2: Download FastSAM checkpoints | infra | SEG-01 | [BLOCKING] | 30min |
| T3: Segmentation module (src/engine/segmenter.py) | code | SEG-01, SEG-02 | [BLOCKING] | 2h |
| T4: Extend Detection dataclass with mask fields | code | SEG-04 | high | 30min |
| T5: Update PCI engine for mask area | code | SEG-04 | high | 1h |
| T6: Update DetectionWorker pipeline | code | SEG-02 | high | 1h |
| T7: Mask overlay visualization | code | SEG-03 | high | 1h |
| T8: Update batch worker for 2-model pipeline | code | SEG-02 | medium | 1h |
| T9: Config + Settings for FastSAM model path | code | SEG-01 | medium | 30min |
| T10: End-to-end test (detect → segment → PCI) | test | All | high | 1h |

---

## T1: Install & Verify FastSAM [BLOCKING]

**Requirement:** SEG-01
**Context decision:** D-16 (FastSAM-s default + FastSAM-x configurable)

### Steps
1. Verify `ultralytics` already includes FastSAM: `from ultralytics import FastSAM`
2. If not available, update ultralytics: `pip install ultralytics>=8.4.0`
3. Test: `FastSAM("FastSAM-s.pt")` loads and runs on a sample image
4. Verify `supervision` MaskAnnotator works: `sv.MaskAnnotator()`
5. Benchmark FastSAM-s inference time on CPU with sample crop

### Exit Criteria
- [ ] `from ultralytics import FastSAM` works
- [ ] FastSAM-s inference produces masks on test image
- [ ] MaskAnnotator renders semi-transparent overlay
- [ ] Benchmark: inference time recorded

---

## T2: Download FastSAM Checkpoints [BLOCKING]

**Requirement:** SEG-01
**Context decision:** D-17 (auto-download, extend download_model.py)

### Steps
1. Add FastSAM checkpoint URLs to `scripts/download_model.py`:
   - FastSAM-s.pt from HuggingFace (Uminosachi/FastSAM)
   - FastSAM-x.pt from HuggingFace (conrevo/Segment-Anything-A1111)
2. Download both to `models/` directory
3. Add `fastsam_model` and `fastsam_model_x` keys to `config/default.json`
4. Test: script downloads both checkpoints successfully

### Exit Criteria
- [ ] `models/FastSAM-s.pt` exists (~23MB)
- [ ] `models/FastSAM-x.pt` exists (~126MB)
- [ ] `config/default.json` has FastSAM model path entries

---

## T3: Segmentation Module (src/engine/segmenter.py) [BLOCKING]

**Requirement:** SEG-01, SEG-02
**Context decision:** D-18 (sequential per-bbox), D-16 (configurable model)

### Steps
1. Create `src/engine/segmenter.py` with `RoadDamageSegmenter` class
2. Lazy model loading (same pattern as `RoadDamageDetector`)
3. Method: `segment_bbox(image, bbox) -> np.ndarray` (binary mask)
4. Method: `segment_detections(image, detections) -> list[Detection]` (add mask to each Detection)
5. Handle edge cases:
   - FastSAM returns no mask → log warning, Detection.mask_pixels stays 0
   - Crop too small (< 32px) → skip segmentation, use bbox
   - Model not loaded → skip silently, return detections unchanged
6. Mask area calculation: `mask_pixels * (image_width * image_height / (image_rows * image_cols))` converted to sqft using config `sample_unit_area_sqft`

### Exit Criteria
- [ ] `RoadDamageSegmenter` class with lazy load
- [ ] `segment_bbox()` returns binary mask for a crop
- [ ] `segment_detections()` adds mask data to Detection objects
- [ ] Edge cases handled (no mask, small crop, no model)

---

## T4: Extend Detection Dataclass with Mask Fields

**Requirement:** SEG-04
**Context decision:** D-19 (extend Detection, not new dataclass)

### Steps
1. Add to `Detection` in `src/engine/detector.py`:
   - `mask_pixels: int = 0` — pixel count of segmentation mask
   - `mask_area_sqft: float = 0.0` — mask area in sq ft (computed from mask_pixels)
2. Add property `has_mask: bool` → `return self.mask_pixels > 0`
3. Add property `effective_area_sqft: float` → `return self.mask_area_sqft if self.has_mask else self.bbox_area_sqft`
4. Update existing tests to pass with new fields (default values = backward compatible)

### Exit Criteria
- [ ] `Detection.mask_pixels` and `Detection.mask_area_sqft` fields added
- [ ] `Detection.has_mask` property works
- [ ] `Detection.effective_area_sqft` returns mask or bbox area
- [ ] Existing tests still pass (52/52)

---

## T5: Update PCI Engine for Mask Area

**Requirement:** SEG-04
**Context decision:** D-22 (mask replaces bbox, no auto-compare), D-23 (density-based severity)

### Steps
1. In `PCIEngine.calculate_pci()`, check `detection.has_mask`:
   - If `has_mask`: use `detection.mask_area_sqft` for density, skip bbox correction
   - If not: use existing bbox area + correction factors (unchanged)
2. In `_calculate_density()`, use `detection.effective_area_sqft` instead of raw bbox area
3. Skip `BBOX_CORRECTION_FACTORS` lookup when mask is available
4. Keep correction factors for bbox-only fallback
5. Add test cases: detection with mask → verify no correction applied

### Exit Criteria
- [ ] PCI uses mask area when available (no bbox correction)
- [ ] PCI falls back to bbox + correction when no mask
- [ ] New test cases for mask-based PCI pass
- [ ] All existing tests still pass (52/52)

---

## T6: Update DetectionWorker Pipeline

**Requirement:** SEG-02
**Context decision:** D-20 (always run if model available), D-18 (sequential per-bbox)

### Steps
1. In `src/ui/workers.py`, add `RoadDamageSegmenter` usage after detection:
   - After `detector.detect()` returns `DetectionResult`
   - If segmenter model is loaded: `segmenter.segment_detections(image, result.pci_detections)`
   - If not: skip (detections remain bbox-only)
2. Update `DetectionWorker.run()` to include segmentation step
3. Emit same `detection_finished` signal — Detection objects now have mask data
4. Log segmentation time separately from detection time

### Exit Criteria
- [ ] DetectionWorker runs detect → segment pipeline
- [ ] If segmenter unavailable, falls back to detect-only
- [ ] Segmentation time logged
- [ ] Signal format unchanged (backward compatible)

---

## T7: Mask Overlay Visualization

**Requirement:** SEG-03
**Context decision:** D-21 (MaskAnnotator, colored per class)

### Steps
1. In `src/ui/main_window.py`, add mask annotation step after bbox annotation:
   - Convert Detection masks to `supervision.Detections` format
   - Use `sv.MaskAnnotator()` with per-class colors
2. Define mask colors: D00=red, D10=orange, D20=yellow, D40=purple
3. Render masks semi-transparent (opacity ~0.3-0.4)
4. If no masks available (bbox-only), skip mask annotation (existing bbox display unchanged)

### Exit Criteria
- [ ] Segmentation masks rendered as colored semi-transparent overlays
- [ ] Each damage class has distinct color
- [ ] Bbox + label display still works alongside masks
- [ ] No masks → existing bbox-only display unchanged

---

## T8: Update Batch Worker for 2-Model Pipeline

**Requirement:** SEG-02
**Context decision:** D-20 (always run if model available)

### Steps
1. In `BatchDetectionWorker.run()`, add segmentation step after each image's detection
2. Same pattern as T6: if segmenter loaded, run `segment_detections()`
3. Log per-image: detection time + segmentation time
4. Progress bar accounts for longer per-image processing time

### Exit Criteria
- [ ] Batch worker runs detect → segment for each image
- [ ] Per-image timing includes both detection and segmentation
- [ ] Progress bar reflects actual processing time
- [ ] Fallback to detect-only if segmenter unavailable

---

## T9: Config + Settings for FastSAM Model Path

**Requirement:** SEG-01
**Context decision:** D-16 (configurable s/x), D-17 (auto-download)

### Steps
1. Add to `config/default.json`:
   - `fastsam_model`: "models/FastSAM-s.pt"
   - `fastsam_model_x`: "models/FastSAM-x.pt"
   - `fastsam_variant`: "s"  (or "x")
2. In `src/ui/settings_dialog.py`, add FastSAM model path setting + variant selector
3. Segmenter reads config on load to determine which model to use

### Exit Criteria
- [ ] Config has FastSAM model paths and variant setting
- [ ] Settings dialog allows changing FastSAM variant
- [ ] Segmenter loads correct model based on config

---

## T10: End-to-End Test (Detect → Segment → PCI)

**Requirement:** All (SEG-01~05)
**Priority:** High

### Steps
1. Create `tests/test_segmenter.py` with unit tests:
   - FastSAM model loads
   - segment_bbox returns mask for sample image
   - segment_detections adds mask to Detection objects
   - Edge cases: no mask, small crop, no model
2. Add integration test:
   - Load sample image → detect → segment → PCI
   - Verify PCI with mask differs from PCI with bbox
   - Verify mask area < bbox area (mask is more precise)
3. Run all tests: `pytest tests/ -v`

### Exit Criteria
- [ ] Unit tests for segmenter pass
- [ ] Integration test: detect → segment → PCI pipeline works
- [ ] PCI with mask ≠ PCI with bbox (expected: mask PCI usually higher, less overestimate)
- [ ] All 52+ tests pass

---

## Success Criteria (from ROADMAP.md)

1. FastSAM segments accurately within detected bounding boxes
2. Damage area from mask differs significantly from bbox (especially D00)
3. PCI from mask is more accurate than bbox proxy
4. Toggle segmentation in GUI works (D-20: always-on if model available, fallback if not)

---

## Files Modified

| File | Change |
|------|--------|
| `src/engine/segmenter.py` | NEW — RoadDamageSegmenter class |
| `src/engine/detector.py` | Add mask fields to Detection dataclass |
| `src/engine/pci.py` | Use mask area when available, skip correction |
| `src/ui/workers.py` | Add segmentation step to DetectionWorker + BatchWorker |
| `src/ui/main_window.py` | Add mask overlay rendering |
| `src/ui/settings_dialog.py` | Add FastSAM variant setting |
| `config/default.json` | Add FastSAM model paths + variant |
| `scripts/download_model.py` | Add FastSAM checkpoint downloads |
| `tests/test_segmenter.py` | NEW — segmenter unit + integration tests |
