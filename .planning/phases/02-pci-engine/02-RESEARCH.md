# Phase 2: PCI Engine — Research (Retroactive)

**Phase:** 02
**Status:** ✅ Complete
**Date documented:** 2026-05-21 (retroactive)

---

## Research Findings

### R-01: ASTM D6433 PCI Calculation Procedure

The ASTM D6433-07 standard defines a 9-step procedure for calculating PCI:

1. **Divide road into sections** — Same construction, traffic, environment
2. **Select sample units** — Representative areas (~5000 ft² / 464.5 m²)
3. **Survey distresses** — Record type, severity, quantity per sample unit
4. **Calculate density** — Damage area / sample unit area × 100 (%)
5. **Look up deduct value** — From curves: density + severity → DV
6. **Calculate CDV** — Count q (DV > 2), sum TDV, look up CDV from correction table
7. **Calculate sample PCI** — PCI = 100 - CDV
8. **Calculate section PCI** — Weighted average of sample unit PCIs
9. **Classify rating** — 0-100 → Good/Satisfactory/Fair/Poor/Very Poor/Failed

**Key insight:** Steps 5-6 are the core algorithm. Deduct value curves are distress-type AND severity specific. CDV correction accounts for multiple concurrent distress types.

### R-02: Deduct Value Curves (Digitized from PPTX Slides 17-22)

Each curve maps density (%) → deduct value (0-100). Curves exist for:
- **D00/D10** (cracks): Low/Medium/High severity — 3 curves each
- **D20** (alligator): Low/Medium/High — 3 curves
- **D40** (pothole): Low/Medium/High — 3 curves

Total: 12 deduct value curves, each with 9 data points [[density, DV], ...]

**Interpolation method:** Linear interpolation between curve points. Clamp to curve range.

### R-03: CDV Correction Curves (Digitized from PPTX Slides 21-22)

CDV correction accounts for the fact that multiple distresses don't simply add up — there's a diminishing effect.

- **q** = number of deduct values > 2 (i.e., significant distresses)
- **TDV** = total of all deduct values
- **CDV** = looked up from correction curves indexed by q and TDV

Curves available: q1 through q10 (10 curves, 21 data points each)

**Special rule:** When q ≤ 1, CDV = TDV (no correction needed for single distress)

### R-04: Severity Assignment Without Segmentation Mask

ASTM D6433 defines severity by physical measurements (crack width, pothole depth). Without segmentation, we use **density as proxy**:

| Code | Low | Medium | High |
|------|-----|--------|------|
| D00  | ≤2% | ≤10% | >10% |
| D10  | ≤2% | ≤10% | >10% |
| D20  | ≤5% | ≤20% | >20% |
| D40  | ≤1% | ≤5% | >5% |

**Rationale:** Higher density implies more severe damage. Thresholds derived from ASTM severity descriptions and PPTX slide guidance.

### R-05: Bbox Overestimate Problem

YOLOv12s outputs bounding boxes, not segmentation masks. A thin longitudinal crack gets a wide bbox that greatly overestimates the actual crack area.

**Solution:** Apply per-type correction factors:
- D00/D10 (linear cracks): 0.3 — bbox is ~3x wider than actual crack
- D20 (alligator): 0.7 — fills bbox more completely
- D40 (pothole): 0.8 — nearly fills bbox

**Future improvement:** FastSAM segmentation (Phase 4) will provide pixel-accurate masks, eliminating the need for correction factors.

### R-06: PCI Rating Scale & Maintenance Recommendations

From ASTM D6433 + PPTX Slide 26:

| Rating | PCI Range | Color | Maintenance |
|--------|-----------|-------|-------------|
| Good | 85-100 | #2ecc71 | Routine maintenance |
| Satisfactory | 70-84 | #27ae60 | Preventive maintenance |
| Fair | 55-69 | #f1c40f | Corrective maintenance |
| Poor | 40-54 | #e67e22 | Major rehabilitation |
| Very Poor | 25-39 | #e74c3c | Reconstruction |
| Failed | 0-24 | #c0392b | New construction |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Deduct value curves not verified against official ASTM | Wrong PCI values | Mark as "needs verification" in data file; prioritize before thesis defense |
| Bbox correction factors are estimates | Over/under-correction | Document as heuristic; FastSAM (Phase 4) eliminates issue |
| Density proxy for severity is approximate | Misclassification | Acceptable for MVP; severity refinement in Phase 4 |
| CDV curves only go to q=10 | Unknown behavior for q>10 | Clamp to q10 curve; rare in practice (>10 concurrent distress types) |

---

## Key References

1. ASTM D6433-07 — Standard Practice for Roads and Parking Lots Pavement Condition Index Surveys
2. Tai_Lieu/Chuyen_Mon/Quan ly bao duong mat duong — Slides 17-22 (deduct curves), 21-22 (CDV), 26 (maintenance)
3. data/pci_astm_d6433.json — Digitized ASTM data (182 lines)
4. Shahin (2006) — Pavement Management for Airports, Roads, and Parking Lots (ASTM D6433 reference textbook)
