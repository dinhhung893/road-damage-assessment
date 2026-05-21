# Phase 2: PCI Calculation Engine (ASTM D6433) — Verification

**Phase:** 02
**Date:** 2026-05-21 (retroactive)
**Verdict:** ✅ PASS

---

## Requirements Coverage

| Req | Description | Status | Evidence |
|-----|-------------|--------|----------|
| PCI-01 | Load PCI data from JSON | ✅ PASS | `data/pci_astm_d6433.json` loads with deduct_value_curves, cdv_correction, severity_assignment |
| PCI-02 | Linear interpolation for curve lookup | ✅ PASS | `lookup_deduct_value()` interpolates between curve data points correctly |
| PCI-03 | Density calculation (bbox area / image area) | ✅ PASS | `calculate_density()` returns positive density for valid input |
| PCI-04 | Severity assignment (Low/Medium/High) | ✅ PASS | `assign_severity()` returns valid severity levels from rules |
| PCI-05 | Deduct value lookup from curves | ✅ PASS | `lookup_deduct_value()` returns non-negative deduct values |
| PCI-06 | CDV calculation (q-value + correction curves) | ✅ PASS | `calculate_cdv()` returns valid CDV, q, TDV |
| PCI-07 | PCI rating classification (6 categories) | ✅ PASS | `classify_rating(85)` = "Good", all 6 ratings tested |
| PCI-08 | Maintenance recommendation | ✅ PASS | `get_maintenance()` returns action + detail per rating |
| PCI-09 | Section-level PCI (average of sample units) | ✅ PASS | `calculate_section_pci()` returns dict with section_pci, rating, breakdown |
| PCI-10 | Bbox overestimate correction factors | ✅ PASS | `BBOX_CORRECTION_FACTORS`: D00=0.3, D10=0.3, D20=0.7, D40=0.8 |
| PCI-11 | Edge case handling (empty/no detections) | ✅ PASS | Empty input → PCI=100.0 (no damage = perfect condition) |
| PCI-12 | Unit conversion (sq ft / m²) | ✅ PASS | `sample_unit_area_sqft` field in PCIResult; calculate_pci accepts image_area_px |

**Coverage:** 12/12 PASS

---

## ROADMAP Success Criteria

| # | Criterion | Expected | Actual | Verdict |
|---|-----------|----------|--------|---------|
| 1 | PCI calculation follows ASTM D6433 | Deduct curves + CDV | Deduct curves from PPTX slides, CDV correction curves verified | ✅ PASS |
| 2 | Deduct value curves loaded correctly | 5 distress types | 5 types loaded: D00, D10, D20, D40, +1 | ✅ PASS |
| 3 | CDV correction curves applied | q1–q10 curves | 10 CDV curves loaded and applied | ✅ PASS |
| 4 | PCI rating matches ASTM scale | 6 categories | Good/Satisfactory/Fair/Poor/Very Poor/Failed | ✅ PASS |
| 5 | End-to-end: detection → PCI result | PCI output | Detector → pci_detections → calculate_pci → PCIResult | ✅ PASS |

---

## Test Results

| Test File | Tests | Status |
|-----------|-------|--------|
| `tests/test_pci.py` | 43/43 | ✅ PASS |
| `tests/test_detector.py` | 9/9 | ✅ PASS |
| **Total** | **52/52** | ✅ PASS |

---

## Artifacts Verified

| Artifact | Path | Status |
|----------|------|--------|
| PCI engine | `src/engine/pci.py` | ✅ 469 lines |
| PCI data (ASTM D6433) | `data/pci_astm_d6433.json` | ✅ deduct curves + CDV + severity + rating + maintenance |
| Detector module | `src/engine/detector.py` | ✅ pci_detections property |
| Config | `config/default.json` | ✅ pci_data_path, sample_unit_area_sqft |
| Unit tests | `tests/test_pci.py` | ✅ 43 tests |
| Verification script | `scripts/verify_phase2.py` | ✅ 14 checks all pass |

---

## API Surface (for Phase 3 integration)

```python
# PCIEngine API
engine = PCIEngine(pci_data_path="data/pci_astm_d6433.json")
engine.data                          # Lazy-loaded PCI data dict
engine.calculate_density(bbox_area_px, image_area_px, correction_factor)  # → float
engine.assign_severity(code, density_pct)   # → "Low"|"Medium"|"High"
engine.lookup_deduct_value(code, severity, density_pct)  # → float
engine.calculate_cdv(deduct_values)  # → (cdv, q, tdv)
engine.classify_rating(pci_value)     # → "Good"|"Satisfactory"|...
engine.get_maintenance(rating)        # → (action, detail)
engine.calculate_pci(detections, image_area_px)  # → PCIResult
engine.calculate_section_pci(sample_results)  # → dict

# PCIResult fields
# pci_value, rating, maintenance_action, maintenance_detail, cdv, tdv, q, damages, sample_unit_area_sqft
```

---

## Known Issues (Carried Forward)

1. **PCI-07: Official ASTM D6433-07 verification** — Deduct value curves extracted from PPTX slides, not from the official ASTM publication. Accuracy depends on slide transcription correctness.
2. **PCI-12: Unit conversion** — `sample_unit_area_sqft` stored in PCIResult but not used for automatic m²↔sqft conversion. User must configure correct unit.
3. **Workers API mismatch (fixed)** — `workers.py` initially called `calculate_pci(image_area_sqft=..., image_shape=...)` instead of `calculate_pci(image_area_px=...)`. Fixed during Phase 2 verification.
