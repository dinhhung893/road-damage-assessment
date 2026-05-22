# Phase 4: FastSAM Segmentation Integration (T2) - Context

**Gathered:** 2026-05-23
**Status:** Ready for planning

<domain>
## Phase Boundary

**In scope:**
- Load FastSAM-s and FastSAM-x models (configurable, s is default)
- Bbox-prompted segmentation: crop detected bbox → FastSAM → precise mask
- Pass mask area to PCI engine (replacing bbox proxy when mask available)
- Display mask overlay on annotated image (Supervision MaskAnnotator)
- Auto-download FastSAM checkpoints (extend download_model.py)
- Run segmentation always when model is available (no toggle checkbox)
- Fallback to bbox proxy when model not available

**Out of scope:**
- End-to-end segmentation model training (Phase 6)
- Video segmentation (Phase 5)
- PCI comparison report bbox vs mask (Phase 7a — SEG-05)
- Mask geometry analysis (crack width, pothole diameter)

</domain>

<decisions>
## Implementation Decisions

### Model Choice
- **D-16:** FastSAM-s mặc định + FastSAM-x configurable qua Settings. Tải cả hai checkpoints (23MB + 126MB).
- **D-17:** Tự động tải FastSAM checkpoints, mở rộng `scripts/download_model.py`. Source: HuggingFace hoặc GitHub release.

### Pipeline Architecture
- **D-18:** Sequential per-bbox — crop từng detected bbox → chạy FastSAM trên từng crop → gộp kết quả. Đơn giản, dễ debug. Chậm hơn full-image prompt nhưng rõ ràng hơn.
- **D-19:** Mở rộng `Detection` dataclass thêm `mask_pixels: int = 0` và `mask_area_sqft: float = 0.0`. PCI engine kiểm tra: có mask → dùng mask area, không có → dùng bbox proxy + correction. Không đổi API `calculate_pci()`.

### GUI Integration
- **D-20:** Luôn chạy segmentation nếu model có sẵn. Không toggle checkbox. Nếu model không tải → fallback bbox proxy tự động (người dùng không cần quyết định).
- **D-21:** Hiển thị mask overlay màu semi-transparent trên ảnh, dùng Supervision `MaskAnnotator`. Mỗi loại hư hỏng màu khác (D00=red, D10=orange, D20=yellow, D40=purple).

### PCI Engine Changes
- **D-22:** Mask thay bbox khi có sẵn. Bỏ bbox correction khi có mask (mask area chính xác hơn). Không so sánh tự động bbox vs mask PCI. So sánh cho thesis (SEG-05) làm thủ công hoặc Phase 7a.
- **D-23:** Severity vẫn density-based — chỉ thay bbox area bằng mask area. Đơn giản, nhất quán với ASTM quy trình. Không dùng mask geometry cho severity.

### Claude's Discretion
- FastSAM inference implementation details (preprocessing, postprocessing)
- IoU threshold for matching segments to detections
- Mask pixel → area conversion (pixel count × resolution)
- Error handling when FastSAM produces empty mask for a bbox
- Batch mode progress reporting with 2-model pipeline

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### FastSAM
- FastSAM paper: https://arxiv.org/abs/2306.12276
- FastSAM GitHub: https://github.com/CASIA-IVA-Lab/FastSAM
- FastSAM checkpoints: HuggingFace (xtuner/FASTSAM-s, xtuner/FASTSAM-x) or GitHub releases

### Project Data
- `data/pci_astm_d6433.json` — Deduct value curves, CDV correction, severity assignment, rating scale
- `config/default.json` — App config including model paths, confidence, sample unit area

### Existing Engine Code
- `src/engine/detector.py` — RoadDamageDetector, Detection/DetectionResult dataclasses, CLASS_CODE_MAP
- `src/engine/pci.py` — PCIEngine, DamageRecord, BBOX_CORRECTION_FACTORS, calculate_pci()
- `src/utils/config.py` — load_config()/save_config() for JSON persistence
- `src/utils/logging_setup.py` — get_logger() with rotating file handler

### GUI Code
- `src/ui/main_window.py` — MainWindow, batch processing, image display
- `src/ui/workers.py` — DetectionWorker, BatchDetectionWorker (QThread)
- `src/ui/widgets/pci_gauge.py` — PCIGaugeWidget
- `src/ui/strings.py` — Vietnamese/English string constants

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `Detection` dataclass: Will be extended with mask fields (mask_pixels, mask_area_sqft)
- `RoadDamageDetector.detect()`: Returns DetectionResult with pci_detections list — segmentation runs AFTER this
- `PCIEngine.calculate_pci()`: Accepts detection list — will auto-detect mask vs bbox area
- `DetectionWorker(QThread)`: Will need to add FastSAM inference step after detection
- `BatchDetectionWorker(QThread)`: Same — add segmentation step
- `supervision` library: Already installed, has MaskAnnotator for mask overlay rendering
- `scripts/download_model.py`: Will be extended to download FastSAM checkpoints

### Established Patterns
- Lazy model loading: Detector uses lazy load — FastSAM should follow same pattern
- QThread + signals/slots: Detection runs in worker thread — segmentation adds to same pipeline
- Config JSON persistence: Model paths stored in config/default.json
- Bbox correction factors: `BBOX_CORRECTION_FACTORS` in pci.py — bypassed when mask available

### Integration Points
- `DetectionResult.pci_detections` → list of Detection objects → FastSAM processes each bbox
- `Detection.mask_area_sqft` → PCI engine reads this instead of bbox area
- `DetectionWorker.detection_finished` signal → may need to add segmentation step before emitting
- Image annotation: Currently uses Supervision BoxAnnotator + LabelAnnotator → add MaskAnnotator

</code_context>

<specifics>
## Specific Ideas

- FastSAM-s checkpoint: `FastSAM-s.pt` (~23MB) — YOLOv8s-seg backbone
- FastSAM-x checkpoint: `FastSAM-x.pt` (~126MB) — YOLOv8x-seg backbone
- Mask colors per class: D00=red, D10=orange, D20=yellow, D40=purple (consistent with bbox colors)
- Sequential pipeline: detect (~900ms) + N × segment (~500-800ms each) → total ~1.4-1.7s for 1 detection
- Batch mode: Each image takes longer but pipeline is same per-image pattern

</specifics>

<deferred>
## Deferred Ideas

1. **Full-image prompt segmentation** — Faster than per-bbox but more complex IoU matching. Could be Phase 4+ optimization.
2. **Mask geometry analysis** — Measure crack width / pothole diameter from mask for more accurate severity. Complex, deferred.
3. **Automatic bbox vs mask PCI comparison** — SEG-05 requirement, deferred to Phase 7a for thesis comparison table.
4. **Segmentation toggle checkbox** — User chose "always run if model available" instead. Could add later if performance is an issue.

</deferred>

---

*Phase: 04-FastSAM-Segmentation*
*Context gathered: 2026-05-23*
