"""Tests for detector module and config."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure project root on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import load_config, save_config
from src.engine.detector import (
    CLASS_CODE_MAP,
    PCI_EXCLUDED_NAMES,
    Detection,
    DetectionResult,
)


class TestConfig:
    """Tests for config loader/saver."""

    def test_load_defaults(self) -> None:
        """Config loads defaults when file missing."""
        config = load_config("/nonexistent/path.json")
        assert config["confidence"] == 0.15
        assert config["device"] == "cpu"
        assert config["language"] == "vi"

    def test_load_from_file(self) -> None:
        """Config loads and merges user values."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            json.dump({"confidence": 0.3, "device": "cuda"}, f)
            tmp = f.name

        config = load_config(tmp)
        assert config["confidence"] == 0.3
        assert config["device"] == "cuda"
        # Defaults still present
        assert config["language"] == "vi"
        Path(tmp).unlink()

    def test_save_and_reload(self) -> None:
        """Config saves and reloads correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_config.json"
            config = {"confidence": 0.5, "device": "cpu"}
            save_config(config, path)
            reloaded = load_config(path)
            assert reloaded["confidence"] == 0.5


class TestDetection:
    """Tests for Detection dataclass."""

    def test_detection_code_mapping(self) -> None:
        """Detection auto-maps class_name to ASTM code."""
        det = Detection(
            class_name="longitudinal_crack",
            class_id=0,
            confidence=0.9,
            bbox=(10, 20, 100, 200),
        )
        assert det.code == "D00"
        assert det.include_in_pci is True

    def test_all_damage_codes(self) -> None:
        """All 4 damage types map correctly."""
        for name, code in CLASS_CODE_MAP.items():
            det = Detection(
                class_name=name,
                class_id=0,
                confidence=0.5,
                bbox=(0, 0, 10, 10),
            )
            assert det.code == code

    def test_repair_class_excluded(self) -> None:
        """Repair class is excluded from PCI."""
        det = Detection(
            class_name="repair",
            class_id=4,
            confidence=0.8,
            bbox=(0, 0, 10, 10),
        )
        assert det.include_in_pci is False
        assert det.code == "UNKNOWN"

    def test_unknown_class(self) -> None:
        """Unknown class gets UNKNOWN code but included in PCI."""
        det = Detection(
            class_name="something_new",
            class_id=99,
            confidence=0.5,
            bbox=(0, 0, 10, 10),
        )
        assert det.code == "UNKNOWN"
        assert det.include_in_pci is True


class TestDetectionResult:
    """Tests for DetectionResult dataclass."""

    def test_pci_detections_filter(self) -> None:
        """pci_detections filters out Repair class."""
        result = DetectionResult(
            image_path="test.jpg",
            detections=[
                Detection("longitudinal_crack", 0, 0.9, (0, 0, 10, 10)),
                Detection("repair", 4, 0.8, (0, 0, 10, 10)),
                Detection("pothole", 3, 0.7, (0, 0, 10, 10)),
            ],
        )
        assert len(result.pci_detections) == 2
        assert len(result.detections) == 3

    def test_damage_types(self) -> None:
        """damage_types returns unique ASTM codes."""
        result = DetectionResult(
            image_path="test.jpg",
            detections=[
                Detection("longitudinal_crack", 0, 0.9, (0, 0, 10, 10)),
                Detection("longitudinal_crack", 0, 0.8, (0, 0, 20, 20)),
                Detection("pothole", 3, 0.7, (0, 0, 10, 10)),
            ],
        )
        assert result.damage_types == {"D00", "D40"}
