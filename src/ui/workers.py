"""Background worker threads for detection and PCI calculation."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from src.utils.config import load_config
from src.utils.logging_setup import get_logger

logger = get_logger("workers")


class DetectionWorker(QThread):
    """Worker thread that runs detection + PCI calculation.

    Runs RoadDamageDetector.detect() and PCIEngine.calculate_pci()
    in a background thread to keep the GUI responsive.

    Signals:
        finished: Emitted with (pci_result, det_result) on success.
        error: Emitted with error message string on failure.
        status: Emitted with status message string during processing.
    """

    finished = Signal(object, object)  # (PCIResult, DetectionResult)
    error = Signal(str)
    status = Signal(str)

    def __init__(self, image_path: str | Path, parent=None) -> None:
        super().__init__(parent)
        self.image_path = Path(image_path)

    def run(self) -> None:
        """Execute detection + PCI in background thread."""
        try:
            config = load_config()

            # --- Detection ---
            self.status.emit(f"Loading model…")

            from src.engine.detector import RoadDamageDetector

            model_path = config.get("model_path", "models/yolo-rdd2022-benchmark/yolo12s_seed0_best.pt")
            confidence = config.get("confidence", 0.15)
            device = config.get("device", "cpu")

            detector = RoadDamageDetector(
                model_path=model_path,
                confidence=confidence,
                device=device,
            )

            self.status.emit(f"Detecting: {self.image_path.name}")
            det_result = detector.detect(self.image_path)

            # --- PCI Calculation ---
            if not det_result.pci_detections:
                # No PCI-relevant detections — return detection result with None PCI
                self.finished.emit(None, det_result)
                return

            self.status.emit("Calculating PCI…")

            from src.engine.pci import PCIEngine

            pci_data_path = config.get("pci_data_path", "data/pci_astm_d6433.json")
            sample_unit_area = config.get("sample_unit_area_sqft", 5000)

            pci_engine = PCIEngine(pci_data_path=pci_data_path)

            # Convert DetectionResult to PCI input format
            img_h, img_w = det_result.image_shape
            image_area_px = img_h * img_w

            # Build damage input list from detections
            damage_input = []
            for det in det_result.pci_detections:
                x1, y1, x2, y2 = det.bbox
                damage_input.append({
                    "code": det.code,
                    "bbox": (x1, y1, x2, y2),
                    "confidence": det.confidence,
                })

            pci_result = pci_engine.calculate_pci(
                damage_input,
                image_area_px=image_area_px,
            )

            self.finished.emit(pci_result, det_result)

        except FileNotFoundError as e:
            self.error.emit(str(e))
        except Exception as e:
            logger.error(f"DetectionWorker error: {e}", exc_info=True)
            self.error.emit(str(e))


class BatchDetectionWorker(QThread):
    """Worker thread for batch processing multiple images.

    Signals:
        image_finished: Emitted per image with (image_path, pci_result, det_result).
        progress: Emitted with (current_index, total_count, image_name).
        batch_finished: Emitted with list of (image_path, pci_result, det_result).
        error: Emitted with error message string.
        status: Emitted with status message string.
    """

    image_finished = Signal(str, object, object)  # (path, PCIResult, DetectionResult)
    progress = Signal(int, int, str)  # (current, total, name)
    batch_finished = Signal(list)  # [(path, PCIResult, DetectionResult), ...]
    error = Signal(str)
    status = Signal(str)

    def __init__(self, image_paths: list[str | Path], parent=None) -> None:
        super().__init__(parent)
        self.image_paths = [Path(p) for p in image_paths]

    def run(self) -> None:
        """Execute batch detection + PCI for all images."""
        try:
            config = load_config()

            from src.engine.detector import RoadDamageDetector
            from src.engine.pci import PCIEngine

            model_path = config.get("model_path", "models/yolo-rdd2022-benchmark/yolo12s_seed0_best.pt")
            confidence = config.get("confidence", 0.15)
            device = config.get("device", "cpu")
            pci_data_path = config.get("pci_data_path", "data/pci_astm_d6433.json")
            sample_unit_area = config.get("sample_unit_area_sqft", 5000)

            detector = RoadDamageDetector(
                model_path=model_path,
                confidence=confidence,
                device=device,
            )
            pci_engine = PCIEngine(pci_data_path=pci_data_path)

            total = len(self.image_paths)
            results = []

            for i, img_path in enumerate(self.image_paths):
                self.progress.emit(i + 1, total, img_path.name)
                self.status.emit(
                    get_string("msg_batch_progress", i=i + 1, n=total, name=img_path.name)
                )

                try:
                    det_result = detector.detect(img_path)

                    pci_result = None
                    if det_result.pci_detections:
                        damage_input = []
                        for det in det_result.pci_detections:
                            x1, y1, x2, y2 = det.bbox
                            damage_input.append({
                                "code": det.code,
                                "bbox": (x1, y1, x2, y2),
                                "confidence": det.confidence,
                            })

                        img_h, img_w = det_result.image_shape
                        pci_result = pci_engine.calculate_pci(
                            damage_input,
                            image_area_px=img_h * img_w,
                        )

                    results.append((str(img_path), pci_result, det_result))
                    self.image_finished.emit(str(img_path), pci_result, det_result)

                except Exception as e:
                    logger.error(f"Batch error on {img_path}: {e}")
                    results.append((str(img_path), None, None))

            self.batch_finished.emit(results)

        except Exception as e:
            logger.error(f"BatchDetectionWorker error: {e}", exc_info=True)
            self.error.emit(str(e))
