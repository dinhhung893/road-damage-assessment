# Phase 2: PCI Calculation Engine (ASTM D6433) — Plan (Retroactive)

**Phase:** 02
**Status:** ✅ Complete
**Requirements:** PCI-01~12
**Depends on:** Phase 1
**Priority:** CAO NHẤT — PCI là xương sống đồ án
**Est. Time:** 1.5 tuần
**Mode:** mvp

---

## Task Overview

| Task | Type | Requirements | Priority | Est. | Status |
|------|------|-------------|----------|------|--------|
| T1: Load PCI data from JSON | code | PCI-01 | [BLOCKING] | 30min | ✅ |
| T2: Implement linear interpolation | code | PCI-02 | [BLOCKING] | 30min | ✅ |
| T3: Implement density calculation | code | PCI-03, PCI-12 | high | 30min | ✅ |
| T4: Implement severity assignment | code | PCI-04 | high | 30min | ✅ |
| T5: Implement deduct value lookup | code | PCI-05 | high | 30min | ✅ |
| T6: Implement CDV calculation | code | PCI-06 | high | 1h | ✅ |
| T7: Implement PCI rating + maintenance | code | PCI-07, PCI-08 | high | 30min | ✅ |
| T8: Implement bbox correction | code | PCI-10 | medium | 30min | ✅ |
| T9: Implement section-level PCI | code | PCI-09 | medium | 30min | ✅ |
| T10: Edge case handling | code | PCI-11 | medium | 30min | ✅ |
| T11: Comprehensive unit tests | test | PCI-01~12 | high | 2h | ✅ |
| T12: End-to-end integration test | test | PCI-01~12 | high | 30min | ✅ |

---

## T1: Load PCI Data from JSON [BLOCKING]

**Requirement:** PCI-01
**Context decision:** D-04 (lazy loading with property guard)

### Implementation
1. `PCIEngine.__init__()` — Accept `pci_data_path` and `sample_unit_area_sqft` params
2. `PCIEngine.data` property — Lazy-loads JSON on first access
3. `PCIEngine._load_data()` — Parses JSON into internal dicts: `_deduct_curves`, `_cdv_curves`, `_severity_rules`, `_rating_scale`, `_maintenance`, `_distress_mapping`
4. All methods that access internal dicts include `_ = self.data` guard

### Files Modified
- `src/engine/pci.py` — Full implementation

### Exit Criteria
- [x] PCI data loads without error
- [x] All 4 deduct curve types parsed (D00, D10, D20, D40)
- [x] All 10 CDV curves parsed (q1–q10)
- [x] Severity rules parsed for all 4 damage types
- [x] Lazy-load guard prevents empty-dict bugs

---

## T2: Implement Linear Interpolation [BLOCKING]

**Requirement:** PCI-02
**Context decision:** N/A (utility function)

### Implementation
1. `PCIEngine.interpolate_curve(curve, x)` — Static method
2. Clamp x to curve range [x_min, x_max]
3. Find bracketing points, compute linear interpolation
4. Handle edge cases: empty curve, single point, duplicate x values

### Exit Criteria
- [x] Exact curve point returns exact value
- [x] Midpoint interpolation is correct
- [x] Clamping works for out-of-range values
- [x] Empty curve returns 0.0

---

## T3: Implement Damage Density Calculation

**Requirement:** PCI-03, PCI-12

### Implementation
1. `PCIEngine.calculate_density(bbox_area_px, image_area_px, correction_factor)` 
2. Proportion = bbox_area_px / image_area_px
3. Apply correction_factor (1.0 = no correction)
4. density_pct = proportion × 100

### Exit Criteria
- [x] Density calculated correctly from pixel areas
- [x] Correction factor applied before density calculation
- [x] Zero image area returns 0.0

---

## T4: Implement Severity Assignment

**Requirement:** PCI-04
**Context decision:** D-03 (density as severity proxy)

### Implementation
1. `PCIEngine.assign_severity(code, density_pct)`
2. Look up severity rules from `_severity_rules[code]`
3. Compare density_pct against Low/Medium/High thresholds
4. Unknown code defaults to "Low"

### Exit Criteria
- [x] All 4 damage types assigned correct severity
- [x] Boundary values handled correctly
- [x] Unknown code defaults to Low

---

## T5: Implement Deduct Value Lookup

**Requirement:** PCI-05

### Implementation
1. `PCIEngine.lookup_deduct_value(code, severity, density_pct)`
2. Select curve from `_deduct_curves[code][severity]`
3. Interpolate using `interpolate_curve()`
4. Unknown code/severity returns 0.0

### Exit Criteria
- [x] Zero density returns zero deduct value
- [x] Exact curve points return exact values
- [x] Interpolated values are correct
- [x] Higher severity gives higher deduct value at same density

---

## T6: Implement CDV Calculation

**Requirement:** PCI-06
**Context decision:** D-05 (q ≤ 1 rule)

### Implementation
1. `PCIEngine.calculate_cdv(deduct_values)` → (CDV, q, TDV)
2. Count q = number of DV > 2
3. Calculate TDV = sum of all DVs
4. If q ≤ 1: CDV = TDV
5. If q > 1: look up CDV from `_cdv_curves[f"q{min(q,10)}"]` using TDV
6. Clamp q to max 10 (data limitation)

### Exit Criteria
- [x] Empty deduct values → CDV = 0
- [x] Single DV > 2 → q=1, CDV = TDV
- [x] Multiple DVs > 2 → CDV from correction curve
- [x] Mixed DVs (some ≤ 2) → q counts only > 2

---

## T7: Implement PCI Rating + Maintenance Recommendation

**Requirement:** PCI-07, PCI-08

### Implementation
1. `PCIEngine.classify_rating(pci_value)` — Static method, 6-level classification
2. `PCIEngine.get_maintenance(rating)` — Returns (action, detail) tuple
3. `PCIResult.pci_color` — Property returning hex color for rating

### Exit Criteria
- [x] All 6 rating levels classified correctly
- [x] Boundary values handled (85=Good, 84=Satisfactory, etc.)
- [x] Maintenance recommendation returned for each rating
- [x] Color hex codes match data file

---

## T8: Implement Bbox Overestimate Correction

**Requirement:** PCI-10
**Context decision:** D-02 (fixed correction factors)

### Implementation
1. `BBOX_CORRECTION_FACTORS` dict — D00=0.3, D10=0.3, D20=0.7, D40=0.8
2. Applied in `calculate_pci()` before density calculation
3. `apply_bbox_correction` parameter allows disabling for comparison

### Exit Criteria
- [x] Corrected density is lower than uncorrected for D00/D10
- [x] Correction factor can be disabled via parameter
- [x] Unknown damage type uses factor 1.0 (no correction)

---

## T9: Implement Section-Level PCI

**Requirement:** PCI-09
**Context decision:** D-06 (simple average)

### Implementation
1. `PCIEngine.calculate_section_pci(sample_results)` → dict
2. Section PCI = average of sample unit PCI values
3. Includes rating, maintenance, and per-unit breakdown

### Exit Criteria
- [x] Empty section → PCI = 100
- [x] Single unit → section PCI = unit PCI
- [x] Multiple units → average PCI with correct rating

---

## T10: Edge Case Handling

**Requirement:** PCI-11

### Implementation
1. No detections → PCI = 100 (Good), with maintenance recommendation
2. Zero image area → PCI = 100 (cannot calculate density)
3. Invalid severity → ValueError in DamageRecord.__post_init__
4. Unknown damage code → severity defaults to Low, deduct value = 0

### Exit Criteria
- [x] No detections handled gracefully
- [x] Zero image area handled gracefully
- [x] Invalid severity raises ValueError
- [x] Unknown damage code doesn't crash

---

## T11: Comprehensive Unit Tests

**Requirement:** PCI-01~12

### Test Suite: `tests/test_pci.py` (43 tests)

| Test Class | Count | Coverage |
|-----------|-------|----------|
| TestInterpolation | 6 | Exact, midpoint, clamp, empty, single |
| TestSeverityAssignment | 8 | D00/D20/D40 boundaries, unknown, zero |
| TestDeductValueLookup | 5 | Zero, exact, interpolated, severity comparison, D40@50% |
| TestCDVCalculation | 5 | Empty, single, two DVs, mixed, q≤1 rule |
| TestRatingClassification | 6 | All 6 levels + boundaries |
| TestCalculatePCI | 5 | No detections, zero area, single, correction, multiple, negative guard |
| TestSectionPCI | 3 | Empty, single, multiple units |
| TestDamageRecord | 2 | Valid/invalid severity |
| TestDetectorToPCI | 1 | End-to-end integration |

### Exit Criteria
- [x] 43/43 tests pass
- [x] All ASTM D6433 calculation steps covered
- [x] Edge cases tested
- [x] Integration with detector verified

---

## T12: End-to-End Integration Test

**Requirement:** PCI-01~12

### Implementation
1. Run `RoadDamageDetector.detect()` on real image
2. Convert detection output to PCI input format
3. Run `PCIEngine.calculate_pci()` with pixel-space data
4. Verify PCI value, rating, CDV, damages

### Verified Result
- Image: `real_damage_03` (640×640, 1 pothole D40)
- Detection: D40 bbox (428,273,477,306), confidence 0.65
- PCI: **92.2 (Good)**, CDV=7.8, q=1, TDV=7.8
- Maintenance: Bảo dưỡng định kỳ (routine maintenance)

### Exit Criteria
- [x] Detector output feeds directly into PCI engine
- [x] PCI value is reasonable for detected damage
- [x] Full pipeline: image → detect → PCI → rating → maintenance

---

## Success Criteria Verification

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | PCI engine tính đúng với test cases | ✅ | 43/43 tests pass |
| 2 | Damage density tính chính xác từ bboxes | ✅ | TestCalculatePCI covers this |
| 3 | PCI rating phân loại đúng 6 mức | ✅ | TestRatingClassification 6/6 |
| 4 | Deduct value curves đã verify với ASTM | ⚠️ | Marked as "needs verification" — deferred to pre-thesis |
| 5 | Unit tests pass 100% | ✅ | 52/52 total (9 detector + 43 PCI) |
| 6 | Edge cases xử lý đúng | ✅ | T10 tests pass |
| 7 | Bbox overestimate correction cho D00 | ✅ | test_bbox_correction_reduces_density |

**Gate: PASS** — Phase 3 may proceed (criterion #4 is non-blocking advisory)

---

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `src/engine/pci.py` | Created | 469 |
| `tests/test_pci.py` | Created | 280 |
| `.planning/ROADMAP.md` | Updated | Phase 2 status → next |
| `.planning/STATE.md` | Updated | Phase 2 info |

---

## Commits

- `9084ae9` — feat: Phase 2 PCI Engine - ASTM D6433 calculation
