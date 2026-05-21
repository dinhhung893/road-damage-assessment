# Phase 2: PCI Engine — Context (Retroactive)

**Phase:** 02
**Status:** ✅ Complete
**Date documented:** 2026-05-21 (retroactive, after implementation)

---

## Phase Boundary

**In scope:**
- PCI calculation engine per ASTM D6433 standard
- Deduct value curve lookup with linear interpolation
- CDV (Corrected Deduct Value) calculation
- Severity assignment from bounding box density proxy
- Bbox overestimate correction
- PCI rating classification + maintenance recommendation
- Section-level PCI (weighted average of sample units)
- Edge case handling (0 detections, zero image area)
- Comprehensive unit tests (43 test cases)

**Out of scope:**
- GUI display of PCI results (Phase 3)
- Segmentation mask-based density (Phase 4)
- Video frame PCI tracking (Phase 5)
- Batch PCI report export (Phase 3)

---

## Implementation Decisions

### D-01: Bbox Proxy for Damage Density
- **Decision:** Use bounding box area as proxy for damage area when no segmentation mask is available
- **Rationale:** YOLOv12s only outputs bboxes. FastSAM (Phase 4) will provide masks for more accurate density
- **Impact:** Density is overestimated → bbox correction factors applied to compensate

### D-02: Bbox Overestimate Correction Factors
- **Decision:** Apply fixed correction factors per damage type
- **Values:** D00=0.3, D10=0.3, D20=0.7, D40=0.8
- **Rationale:** Linear cracks (D00/D10) have bboxes much larger than actual crack width. Alligator cracking (D20) fills more of the bbox. Potholes (D40) fill bbox reasonably well
- **Alternative considered:** Aspect-ratio heuristic (rejected — too fragile for small detections)
- **Deferred:** Fine-tuning correction factors based on real RDD2022 validation data

### D-03: Severity Assignment from Density
- **Decision:** Assign severity (Low/Medium/High) based on damage density percentage thresholds from `severity_assignment` in data file
- **Rationale:** Without segmentation mask, cannot measure crack width or pothole depth directly. Density serves as proxy
- **Thresholds:** Defined in `data/pci_astm_d6433.json` → `severity_assignment` section

### D-04: Lazy Data Loading
- **Decision:** PCI data loaded lazily via `data` property, with `_ = self.data` guards in all methods that access internal dicts
- **Rationale:** Allows standalone method testing without requiring `calculate_pci()` entry point
- **Bug found & fixed:** Initial implementation missed lazy-load guards → 11 test failures in first run

### D-05: CDV Calculation — q ≤ 1 Rule
- **Decision:** When q (number of deduct values > 2) is ≤ 1, CDV = TDV directly (no correction curve lookup)
- **Rationale:** ASTM D6433-07 specifies this rule explicitly. Single damage type doesn't need multi-distress correction

### D-06: Section-Level PCI — Simple Average
- **Decision:** Section PCI = simple average of sample unit PCI values (equal weight)
- **Rationale:** MVP approach. Weighted average by area can be added later if needed
- **Deferred:** Area-weighted section PCI (PCI-09 requirement, non-blocking for Phase 2)

---

## Canonical References

1. **ASTM D6433-07** — Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys
2. **data/pci_astm_d6433.json** — Digitized deduct value curves, CDV correction, severity rules, rating scale, maintenance recommendations
3. **Tai_Lieu/Chuyen_Mon/Quan ly bao duong mat duong** — Slide 17-22 (deduct curves), Slide 21-22 (CDV), Slide 26 (maintenance)

---

## Existing Code Insights

- `src/engine/detector.py` — `RoadDamageDetector.detect()` returns `DetectionResult` with `pci_detections` list (excludes repair/other class). Each `Detection` has `.code`, `.bbox`, `.confidence`, `.class_id`
- `src/utils/config.py` — `load_config()` / `save_config()` for JSON config persistence
- `src/utils/logging_setup.py` — `get_logger()` with rotating file handler
- PCI data file path configured via `config/default.json` → `pci_data_path`

---

## Specific Ideas (Implemented)

1. **Damage aggregation by type+severity** — Group detections by (code, severity) before density calculation to avoid double-counting overlapping bboxes of same type
2. **PCI color property** — `PCIResult.pci_color` returns hex color matching rating for GUI gauge chart
3. **DamageRecord dataclass** — Full traceability from bbox → density → severity → deduct value → CDV → PCI

---

## Deferred Ideas

1. **Area-weighted section PCI** — Weight sample unit PCI by unit area (PCI-09)
2. **Confidence-weighted density** — Scale density by detection confidence (reduce impact of low-confidence detections)
3. **Deduct value curve verification** — Verify digitized curves against official ASTM D6433-07 document (ROADMAP success criterion #4)
4. **Non-pavement detection** — Filter out non-road images before PCI calculation (PCI-11 edge case)
5. **Unit conversion ft²↔m²** — Support both imperial and metric units (PCI-12)
