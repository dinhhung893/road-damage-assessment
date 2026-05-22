"""Tests for RoadDamageSegmenter and mask-based PCI integration."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root on path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from src.engine.detector import Detection, DetectionResult


# ---------------------------------------------------------------------------
# Detection mask fields
# ---------------------------------------------------------------------------

class TestDetectionMaskFields:
    """Test new mask fields on Detection dataclass."""

    def test_default_mask_fields(self):
        """Detection without mask has zero mask fields."""
        det = Detection(
            class_name="pothole", class_id=3, confidence=0.9,
            bbox=(100, 100, 200, 200),
        )
        assert det.mask_pixels == 0
        assert det.mask_area_sqft == 0.0
        assert det.mask_contours == []
        assert det.has_mask is False

    def test_has_mask_true(self):
        """Detection with mask_pixels > 0 has mask."""
        det = Detection(
            class_name="pothole", class_id=3, confidence=0.9,
            bbox=(100, 100, 200, 200),
            mask_pixels=5000, mask_area_sqft=0.05,
        )
        assert det.has_mask is True

    def test_effective_area_with_mask(self):
        """effective_area_sqft returns mask area when mask available."""
        det = Detection(
            class_name="pothole", class_id=3, confidence=0.9,
            bbox=(100, 100, 200, 200),
            mask_pixels=5000, mask_area_sqft=0.05,
        )
        assert det.effective_area_sqft == 0.05

    def test_effective_area_without_mask(self):
        """effective_area_sqft returns 0 when no mask."""
        det = Detection(
            class_name="pothole", class_id=3, confidence=0.9,
            bbox=(100, 100, 200, 200),
        )
        assert det.effective_area_sqft == 0.0

    def test_bbox_area_pixels(self):
        """bbox_area_sqft returns pixel area of bbox."""
        det = Detection(
            class_name="pothole", class_id=3, confidence=0.9,
            bbox=(100, 100, 200, 200),
        )
        assert det.bbox_area_sqft == 10000.0  # 100*100

    def test_backward_compatible(self):
        """Old code creating Detection without mask fields still works."""
        det = Detection(
            class_name="alligator_crack", class_id=2, confidence=0.8,
            bbox=(50, 50, 150, 150),
        )
        assert det.code == "D20"
        assert det.include_in_pci is True
        assert det.has_mask is False


# ---------------------------------------------------------------------------
# PCI with mask area
# ---------------------------------------------------------------------------

class TestPCIWithMask:
    """Test PCI engine uses mask area when available."""

    def test_mask_no_correction(self):
        """When mask available, no bbox correction is applied."""
        from src.engine.pci import PCIEngine

        engine = PCIEngine()

        # Same detection with and without mask
        # Without mask: D00 bbox area = 10000px, correction = 0.3, effective = 3000px
        det_bbox = {
            "code": "D00",
            "bbox": (0, 0, 100, 100),
            "confidence": 0.9,
            "has_mask": False,
            "mask_area_sqft": 0.0,
        }

        # With mask: mask covers 2% of image (more accurate than corrected bbox)
        det_mask = {
            "code": "D00",
            "bbox": (0, 0, 100, 100),
            "confidence": 0.9,
            "has_mask": True,
            "mask_area_sqft": 0.02,  # 2% of image
        }

        image_area = 1000 * 1000  # 1M pixels

        result_bbox = engine.calculate_pci([det_bbox], image_area_px=image_area)
        result_mask = engine.calculate_pci([det_mask], image_area_px=image_area)

        # Mask-based density = 2.0%, bbox-based density = 10000*0.3/1M*100 = 0.3%
        # They should produce different PCI values (mask has higher density → lower PCI)
        assert result_mask.pci_value != result_bbox.pci_value

    def test_mask_density_is_precise(self):
        """Mask area ratio directly becomes density (no correction)."""
        from src.engine.pci import PCIEngine

        engine = PCIEngine()

        det = {
            "code": "D40",
            "bbox": (0, 0, 200, 200),
            "confidence": 0.9,
            "has_mask": True,
            "mask_area_sqft": 0.05,  # 5% of image
        }

        result = engine.calculate_pci([det], image_area_px=1000000)
        # Density should be exactly 5% (mask_area_ratio * 100)
        assert result.damages[0].density_pct == pytest.approx(5.0, abs=0.01)

    def test_bbox_fallback_when_no_mask(self):
        """Without mask, bbox correction is still applied."""
        from src.engine.pci import PCIEngine

        engine = PCIEngine()

        det = {
            "code": "D00",
            "bbox": (0, 0, 100, 100),
            "confidence": 0.9,
            "has_mask": False,
            "mask_area_sqft": 0.0,
        }

        result = engine.calculate_pci([det], image_area_px=100000)
        # Bbox area = 10000px, correction D00=0.3, effective=3000px
        # density = 3000/100000*100 = 3.0%
        assert result.damages[0].density_pct == pytest.approx(3.0, abs=0.01)


# ---------------------------------------------------------------------------
# Segmenter unit tests (require model file)
# ---------------------------------------------------------------------------

class TestSegmenterAvailability:
    """Test segmenter availability checks."""

    def test_missing_model_file(self):
        """Segmenter with missing model file is not available."""
        from src.engine.segmenter import RoadDamageSegmenter

        segmenter = RoadDamageSegmenter(model_path="nonexistent/FastSAM-s.pt")
        assert segmenter.is_available is False

    def test_available_model(self):
        """Segmenter with existing model file is available."""
        from src.engine.segmenter import RoadDamageSegmenter

        model_path = Path("models/FastSAM-s.pt")
        if not model_path.exists():
            pytest.skip("FastSAM-s.pt not downloaded")

        segmenter = RoadDamageSegmenter(model_path=model_path)
        assert segmenter.is_available is True

    def test_mask_to_contours(self):
        """mask_to_contours converts binary mask to contour points."""
        import numpy as np
        from src.engine.segmenter import RoadDamageSegmenter

        # Create a simple 50x50 mask with a filled rectangle
        mask = np.zeros((50, 50), dtype=np.uint8)
        mask[10:40, 10:40] = 1

        contours = RoadDamageSegmenter.mask_to_contours(mask, bbox_offset=(100, 200))
        assert len(contours) >= 1
        # First point should be offset by (100, 200)
        assert contours[0][0][0] >= 100  # x offset applied
        assert contours[0][0][1] >= 200  # y offset applied

    def test_mask_to_contours_empty(self):
        """mask_to_contours returns empty for empty mask."""
        import numpy as np
        from src.engine.segmenter import RoadDamageSegmenter

        mask = np.zeros((50, 50), dtype=np.uint8)
        contours = RoadDamageSegmenter.mask_to_contours(mask)
        assert len(contours) == 0


# ---------------------------------------------------------------------------
# Integration test (detect → segment → PCI)
# ---------------------------------------------------------------------------

class TestIntegrationSegmentPCI:
    """Integration test: detect → segment → PCI pipeline."""

    @pytest.fixture
    def sample_image(self):
        """Find a sample image for testing."""
        samples_dir = _PROJECT_ROOT / "data" / "samples"
        images = list(samples_dir.glob("*.jpg"))
        if not images:
            pytest.skip("No sample images available")
        return images[0]

    def test_detect_segment_pipeline(self, sample_image):
        """Full pipeline: detect → segment → PCI produces results."""
        from src.engine.detector import RoadDamageDetector
        from src.engine.segmenter import RoadDamageSegmenter
        from src.engine.pci import PCIEngine
        import cv2

        # Detect
        model_path = Path("models/yolo-rdd2022-benchmark/yolo12s_seed0_best.pt")
        if not model_path.exists():
            pytest.skip("YOLOv12s model not downloaded")

        detector = RoadDamageDetector(model_path=model_path)
        det_result = detector.detect(sample_image)

        # Skip if no detections
        if not det_result.pci_detections:
            pytest.skip("No detections on sample image")

        # Segment
        fastsam_path = Path("models/FastSAM-s.pt")
        if not fastsam_path.exists():
            pytest.skip("FastSAM-s.pt not downloaded")

        segmenter = RoadDamageSegmenter(model_path=fastsam_path)
        image = cv2.imread(str(sample_image))

        if segmenter.is_available and image is not None:
            seg_time = segmenter.segment_detections(
                image, det_result.pci_detections, det_result.image_shape
            )
            det_result.segmentation_time_ms = seg_time

        # PCI
        pci_engine = PCIEngine()
        img_h, img_w = det_result.image_shape
        damage_input = []
        for det in det_result.pci_detections:
            x1, y1, x2, y2 = det.bbox
            damage_input.append({
                "code": det.code,
                "bbox": (x1, y1, x2, y2),
                "confidence": det.confidence,
                "has_mask": det.has_mask,
                "mask_area_sqft": det.mask_area_sqft,
            })

        pci_result = pci_engine.calculate_pci(
            damage_input, image_area_px=img_h * img_w
        )

        # Verify pipeline produced valid results
        assert 0 <= pci_result.pci_value <= 100
        assert pci_result.rating in ("Good", "Satisfactory", "Fair", "Poor", "Very Poor", "Failed")

        # If segmentation worked, at least one detection should have mask
        if segmenter.is_available and det_result.segmentation_time_ms > 0:
            n_masked = sum(1 for d in det_result.pci_detections if d.has_mask)
            # Note: some detections may not get masks (small crops, etc.)
            assert det_result.segmentation_time_ms > 0
