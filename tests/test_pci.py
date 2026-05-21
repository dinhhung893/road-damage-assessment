"""Tests for PCI calculation engine — ASTM D6433."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.pci import (
    BBOX_CORRECTION_FACTORS,
    DamageRecord,
    PCIEngine,
    PCIResult,
)


# ── Fixtures ──


@pytest.fixture
def engine() -> PCIEngine:
    """Create PCIEngine with default data file."""
    return PCIEngine()


@pytest.fixture
def engine_no_correction() -> PCIEngine:
    """PCIEngine with bbox correction disabled for density tests."""
    return PCIEngine()


# ── Interpolation Tests ──


class TestInterpolation:
    """Tests for linear interpolation on curves."""

    def test_exact_point(self, engine: PCIEngine) -> None:
        """Interpolation at exact curve point returns exact value."""
        curve = [[0, 0], [10, 20], [20, 40]]
        assert engine.interpolate_curve(curve, 10) == 20.0

    def test_midpoint(self, engine: PCIEngine) -> None:
        """Interpolation at midpoint between two points."""
        curve = [[0, 0], [10, 20]]
        assert engine.interpolate_curve(curve, 5) == pytest.approx(10.0)

    def test_clamp_low(self, engine: PCIEngine) -> None:
        """Value below curve range is clamped to first point."""
        curve = [[5, 10], [10, 20]]
        assert engine.interpolate_curve(curve, 0) == 10.0

    def test_clamp_high(self, engine: PCIEngine) -> None:
        """Value above curve range is clamped to last point."""
        curve = [[0, 0], [10, 20]]
        assert engine.interpolate_curve(curve, 100) == 20.0

    def test_empty_curve(self, engine: PCIEngine) -> None:
        """Empty curve returns 0."""
        assert engine.interpolate_curve([], 5) == 0.0

    def test_single_point(self, engine: PCIEngine) -> None:
        """Single-point curve returns that value."""
        assert engine.interpolate_curve([[5, 10]], 5) == 10.0


# ── Severity Assignment Tests ──


class TestSeverityAssignment:
    """Tests for severity level assignment based on density."""

    def test_d00_low(self, engine: PCIEngine) -> None:
        """D00 with density <= 2% is Low."""
        assert engine.assign_severity("D00", 1.0) == "Low"

    def test_d00_medium(self, engine: PCIEngine) -> None:
        """D00 with density 2-10% is Medium."""
        assert engine.assign_severity("D00", 5.0) == "Medium"

    def test_d00_high(self, engine: PCIEngine) -> None:
        """D00 with density > 10% is High."""
        assert engine.assign_severity("D00", 15.0) == "High"

    def test_d20_low(self, engine: PCIEngine) -> None:
        """D20 with density <= 5% is Low."""
        assert engine.assign_severity("D20", 3.0) == "Low"

    def test_d20_medium(self, engine: PCIEngine) -> None:
        """D20 with density 5-20% is Medium."""
        assert engine.assign_severity("D20", 10.0) == "Medium"

    def test_d20_high(self, engine: PCIEngine) -> None:
        """D20 with density > 20% is High."""
        assert engine.assign_severity("D20", 25.0) == "High"

    def test_d40_boundary(self, engine: PCIEngine) -> None:
        """D40 severity boundaries: Low <= 1%, Medium <= 5%, High > 5%."""
        assert engine.assign_severity("D40", 0.5) == "Low"
        assert engine.assign_severity("D40", 3.0) == "Medium"
        assert engine.assign_severity("D40", 10.0) == "High"

    def test_unknown_code(self, engine: PCIEngine) -> None:
        """Unknown damage code defaults to Low severity."""
        assert engine.assign_severity("D99", 50.0) == "Low"

    def test_zero_density(self, engine: PCIEngine) -> None:
        """Zero density is always Low."""
        assert engine.assign_severity("D00", 0.0) == "Low"
        assert engine.assign_severity("D40", 0.0) == "Low"


# ── Deduct Value Lookup Tests ──


class TestDeductValueLookup:
    """Tests for deduct value lookup from curves."""

    def test_zero_density(self, engine: PCIEngine) -> None:
        """Zero density gives zero deduct value."""
        assert engine.lookup_deduct_value("D00", "Low", 0.0) == 0.0
        assert engine.lookup_deduct_value("D40", "High", 0.0) == 0.0

    def test_exact_curve_point(self, engine: PCIEngine) -> None:
        """Exact curve point returns exact value."""
        # D00 Low: [1, 10]
        assert engine.lookup_deduct_value("D00", "Low", 1.0) == pytest.approx(10.0)

    def test_interpolated_value(self, engine: PCIEngine) -> None:
        """Interpolated value between curve points."""
        # D00 Low: [0.5, 5] → [1, 10], midpoint at 0.75 → 7.5
        dv = engine.lookup_deduct_value("D00", "Low", 0.75)
        assert dv == pytest.approx(7.5)

    def test_high_severity_higher_dv(self, engine: PCIEngine) -> None:
        """High severity gives higher deduct value than Low at same density."""
        dv_low = engine.lookup_deduct_value("D20", "Low", 5.0)
        dv_high = engine.lookup_deduct_value("D20", "High", 5.0)
        assert dv_high > dv_low

    def test_d40_high_at_50pct(self, engine: PCIEngine) -> None:
        """D40 High at 50% density should be 97 (from curve)."""
        assert engine.lookup_deduct_value("D40", "High", 50.0) == pytest.approx(97.0)


# ── CDV Calculation Tests ──


class TestCDVCalculation:
    """Tests for Corrected Deduct Value calculation."""

    def test_empty_deduct_values(self, engine: PCIEngine) -> None:
        """Empty deduct values → CDV = 0."""
        cdv, q, tdv = engine.calculate_cdv([])
        assert cdv == 0.0
        assert q == 0
        assert tdv == 0.0

    def test_single_dv_le2(self, engine: PCIEngine) -> None:
        """Single DV <= 2: q=0, CDV = TDV."""
        cdv, q, tdv = engine.calculate_cdv([1.5])
        assert q == 0
        assert cdv == pytest.approx(1.5)

    def test_single_dv_gt2(self, engine: PCIEngine) -> None:
        """Single DV > 2: q=1, CDV = TDV (q <= 1 rule)."""
        cdv, q, tdv = engine.calculate_cdv([10.0])
        assert q == 1
        assert cdv == pytest.approx(10.0)

    def test_two_dvs_both_gt2(self, engine: PCIEngine) -> None:
        """Two DVs > 2: q=2, CDV from correction curve."""
        cdv, q, tdv = engine.calculate_cdv([15.0, 20.0])
        assert q == 2
        assert tdv == pytest.approx(35.0)
        # q2 curve at TDV=35: interpolate between [35,28] and [40,32]
        # Expected: 28 + (35-35)/(40-35) * (32-28) = 28.0
        assert cdv == pytest.approx(28.0, abs=0.5)

    def test_mixed_dvs(self, engine: PCIEngine) -> None:
        """Mix of DVs > 2 and <= 2."""
        cdv, q, tdv = engine.calculate_cdv([1.0, 15.0, 20.0, 0.5])
        assert q == 2  # Only 15 and 20 are > 2
        assert tdv == pytest.approx(36.5)


# ── PCI Rating Classification Tests ──


class TestRatingClassification:
    """Tests for PCI rating classification."""

    def test_good(self) -> None:
        assert PCIEngine.classify_rating(100) == "Good"
        assert PCIEngine.classify_rating(85) == "Good"

    def test_satisfactory(self) -> None:
        assert PCIEngine.classify_rating(70) == "Satisfactory"
        assert PCIEngine.classify_rating(84) == "Satisfactory"

    def test_fair(self) -> None:
        assert PCIEngine.classify_rating(55) == "Fair"
        assert PCIEngine.classify_rating(69) == "Fair"

    def test_poor(self) -> None:
        assert PCIEngine.classify_rating(40) == "Poor"
        assert PCIEngine.classify_rating(54) == "Poor"

    def test_very_poor(self) -> None:
        assert PCIEngine.classify_rating(25) == "Very Poor"
        assert PCIEngine.classify_rating(39) == "Very Poor"

    def test_failed(self) -> None:
        assert PCIEngine.classify_rating(0) == "Failed"
        assert PCIEngine.classify_rating(24) == "Failed"


# ── Full PCI Calculation Tests ──


class TestCalculatePCI:
    """Tests for full PCI calculation pipeline."""

    def test_no_detections(self, engine: PCIEngine) -> None:
        """No detections → PCI = 100 (Good)."""
        result = engine.calculate_pci([], image_area_px=307200)
        assert result.pci_value == 100.0
        assert result.rating == "Good"

    def test_zero_image_area(self, engine: PCIEngine) -> None:
        """Zero image area → PCI = 100 (cannot calculate)."""
        result = engine.calculate_pci(
            [{"code": "D40", "bbox": (100, 100, 200, 200), "confidence": 0.8}],
            image_area_px=0,
        )
        assert result.pci_value == 100.0

    def test_single_pothole(self, engine: PCIEngine) -> None:
        """Single pothole detection → PCI < 100."""
        # 640x640 image, pothole bbox 50x50 pixels
        image_area = 640 * 640
        result = engine.calculate_pci(
            [{"code": "D40", "bbox": (300, 300, 350, 350), "confidence": 0.8}],
            image_area_px=image_area,
        )
        assert result.pci_value < 100.0
        assert result.pci_value > 0.0
        assert len(result.damages) == 1
        assert result.damages[0].code == "D40"

    def test_bbox_correction_reduces_density(self, engine: PCIEngine) -> None:
        """Bbox correction should reduce density for D00/D10."""
        image_area = 640 * 640
        bbox = (100, 200, 500, 220)  # Wide bbox for longitudinal crack

        result_corrected = engine.calculate_pci(
            [{"code": "D00", "bbox": bbox, "confidence": 0.9}],
            image_area_px=image_area,
            apply_bbox_correction=True,
        )

        result_uncorrected = engine.calculate_pci(
            [{"code": "D00", "bbox": bbox, "confidence": 0.9}],
            image_area_px=image_area,
            apply_bbox_correction=False,
        )

        # Corrected should have lower density (and likely higher PCI)
        assert result_corrected.damages[0].density_pct < result_uncorrected.damages[0].density_pct

    def test_multiple_damages(self, engine: PCIEngine) -> None:
        """Multiple damage types → lower PCI than single damage."""
        image_area = 640 * 640
        single = engine.calculate_pci(
            [{"code": "D40", "bbox": (300, 300, 350, 350), "confidence": 0.8}],
            image_area_px=image_area,
        )
        multiple = engine.calculate_pci(
            [
                {"code": "D40", "bbox": (300, 300, 350, 350), "confidence": 0.8},
                {"code": "D00", "bbox": (50, 200, 550, 220), "confidence": 0.7},
            ],
            image_area_px=image_area,
        )
        assert multiple.pci_value <= single.pci_value

    def test_pci_never_negative(self, engine: PCIEngine) -> None:
        """PCI should never go below 0."""
        image_area = 640 * 640
        # Very large damages
        result = engine.calculate_pci(
            [
                {"code": "D20", "bbox": (0, 0, 640, 640), "confidence": 0.9},
                {"code": "D40", "bbox": (0, 0, 640, 640), "confidence": 0.9},
            ],
            image_area_px=image_area,
        )
        assert result.pci_value >= 0.0


# ── Section PCI Tests ──


class TestSectionPCI:
    """Tests for section-level PCI calculation."""

    def test_empty_section(self, engine: PCIEngine) -> None:
        """Empty section → PCI = 100."""
        result = engine.calculate_section_pci([])
        assert result["section_pci"] == 100.0

    def test_single_unit(self, engine: PCIEngine) -> None:
        """Single unit section → section PCI = unit PCI."""
        unit = PCIResult(pci_value=75.0, rating="Satisfactory")
        result = engine.calculate_section_pci([unit])
        assert result["section_pci"] == 75.0

    def test_multiple_units(self, engine: PCIEngine) -> None:
        """Multiple units → average PCI."""
        units = [
            PCIResult(pci_value=80.0, rating="Satisfactory"),
            PCIResult(pci_value=60.0, rating="Fair"),
        ]
        result = engine.calculate_section_pci(units)
        assert result["section_pci"] == 70.0
        assert result["rating"] == "Satisfactory"


# ── DamageRecord Tests ──


class TestDamageRecord:
    """Tests for DamageRecord dataclass."""

    def test_valid_severity(self) -> None:
        """Valid severity levels accepted."""
        for sev in ("Low", "Medium", "High"):
            rec = DamageRecord(code="D00", severity=sev, density_pct=5.0)
            assert rec.severity == sev

    def test_invalid_severity(self) -> None:
        """Invalid severity raises ValueError."""
        with pytest.raises(ValueError, match="Invalid severity"):
            DamageRecord(code="D00", severity="Critical", density_pct=5.0)


# ── Integration: Detector → PCI ──


class TestDetectorToPCI:
    """Integration test: detector output → PCI calculation."""

    def test_detection_to_pci(self, engine: PCIEngine) -> None:
        """Convert Detection objects to PCI input and calculate."""
        # Simulate detector output for a 640x640 image with one pothole
        detections = [
            {
                "code": "D40",
                "bbox": (428, 273, 477, 306),
                "confidence": 0.65,
            }
        ]
        image_area = 640 * 640

        result = engine.calculate_pci(detections, image_area_px=image_area)

        assert result.pci_value < 100.0
        assert result.pci_value > 0.0
        assert result.rating in ("Good", "Satisfactory", "Fair", "Poor", "Very Poor", "Failed")
        assert len(result.damages) == 1
        assert result.damages[0].code == "D40"
        assert result.cdv > 0.0
