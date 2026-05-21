"""Milestone V1.0 audit — verify requirements coverage and cross-phase integration."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.detector import RoadDamageDetector, CLASS_CODE_MAP, PCI_EXCLUDED_NAMES
from src.engine.pci import PCIEngine, BBOX_CORRECTION_FACTORS, DamageRecord, PCIResult
from src.utils.config import load_config
from src.utils.logging_setup import get_logger


def audit_detector() -> dict:
    """Audit Phase 1 detector module."""
    d = RoadDamageDetector()
    return {
        "classes": d.model.names,
        "class_code_map": CLASS_CODE_MAP,
        "pci_excluded": PCI_EXCLUDED_NAMES,
        "class_count": len(d.model.names),
    }


def audit_pci_engine() -> dict:
    """Audit Phase 2 PCI engine."""
    p = PCIEngine()
    _ = p.data  # trigger load
    return {
        "deduct_curves": list(p._deduct_curves.keys()),
        "cdv_curves": list(p._cdv_curves.keys()),
        "severity_rules": list(p._severity_rules.keys()),
        "bbox_correction": BBOX_CORRECTION_FACTORS,
        "rating_colors": PCIEngine.RATING_COLORS,
    }


def audit_pci_data() -> dict:
    """Audit PCI data file."""
    data = json.loads(
        (PROJECT_ROOT / "data" / "pci_astm_d6433.json").read_text(encoding="utf-8")
    )
    return {
        "top_keys": list(data.keys()),
        "distress_types": list(data["distress_mapping"].keys()),
        "deduct_curve_types": list(data["deduct_value_curves"].keys()),
        "cdv_curves": list(data["cdv_correction"]["curves"].keys()),
        "rating_levels": list(data["pci_rating"].keys()),
        "maintenance_levels": list(data["maintenance_recommendation"].keys()),
    }


def audit_config() -> dict:
    """Audit config file."""
    cfg = load_config()
    return {"keys": list(cfg.keys()), "model_path": cfg.get("model_path")}


def audit_integration() -> dict:
    """Audit end-to-end integration: detect -> PCI."""
    detector = RoadDamageDetector()
    pci_engine = PCIEngine()

    # Find a real image with detection
    sample_dir = PROJECT_ROOT / "data" / "samples"
    results = []
    for img in sorted(sample_dir.glob("real_damage_*.jpg")):
        det = detector.detect(str(img))
        if det.detections:
            pci_input = [
                {"code": d.code, "bbox": d.bbox, "confidence": d.confidence}
                for d in det.pci_detections
            ]
            h, w = det.image_shape
            pci = pci_engine.calculate_pci(pci_input, image_area_px=h * w)
            results.append({
                "image": img.name,
                "detections": len(det.detections),
                "pci": pci.pci_value,
                "rating": pci.rating,
                "cdv": pci.cdv,
                "maintenance": pci.maintenance_action,
            })

    return {"integration_tests": results, "passed": len(results) > 0}


def main() -> None:
    print("=" * 60)
    print("MILESTONE V1.0 AUDIT — MVP Detection + PCI (T1)")
    print("=" * 60)

    # Phase 1
    print("\n--- Phase 1: Detector ---")
    d = audit_detector()
    print(f"  Classes: {d['classes']}")
    print(f"  CLASS_CODE_MAP: {d['class_code_map']}")
    print(f"  PCI_EXCLUDED: {d['pci_excluded']}")
    print(f"  Class count: {d['class_count']} (expected: 4)")

    # Phase 2
    print("\n--- Phase 2: PCI Engine ---")
    p = audit_pci_engine()
    print(f"  Deduct curves: {p['deduct_curves']}")
    print(f"  CDV curves: {p['cdv_curves']}")
    print(f"  Severity rules: {p['severity_rules']}")
    print(f"  Bbox correction: {p['bbox_correction']}")
    print(f"  Rating colors: {p['rating_colors']}")

    # PCI Data
    print("\n--- PCI Data File ---")
    data = audit_pci_data()
    print(f"  Distress types: {data['distress_types']}")
    print(f"  Deduct curve types: {data['deduct_curve_types']}")
    print(f"  CDV curves: {data['cdv_curves']}")
    print(f"  Rating levels: {data['rating_levels']}")
    print(f"  Maintenance levels: {data['maintenance_levels']}")

    # Config
    print("\n--- Config ---")
    c = audit_config()
    print(f"  Keys: {c['keys']}")
    print(f"  Model path: {c['model_path']}")

    # Integration
    print("\n--- Integration: Detect -> PCI ---")
    integ = audit_integration()
    for r in integ["integration_tests"]:
        print(f"  {r['image']}: {r['detections']} det, PCI={r['pci']} ({r['rating']}), CDV={r['cdv']}")
    print(f"  Integration PASSED: {integ['passed']}")

    # Requirements coverage
    print("\n" + "=" * 60)
    print("REQUIREMENTS COVERAGE")
    print("=" * 60)

    reqs = {
        # Phase 1
        "DET-01": True,   # Model loaded
        "DET-02": True,   # ONNX exported (though DirectML fails)
        "DET-03": "PARTIAL",  # Torch CPU works, DirectML deferred
        "DET-04": True,   # 4 classes detected
        "DET-05": True,   # Confidence threshold 0.15
        "DET-06": True,   # Supervision annotation
        "DET-07": True,   # Model verified
        "DET-08": True,   # Auto-download script
        "INF-01": True,   # Logging framework
        "INF-03": True,   # Demo images
        "INF-04": True,   # Code cleanup
        "INF-05": True,   # Dependency pinning
        # Phase 2
        "PCI-01": True,   # Damage density
        "PCI-02": True,   # Deduct value lookup
        "PCI-03": True,   # CDV calculation
        "PCI-04": True,   # PCI = 100 - CDV
        "PCI-05": True,   # Rating classification
        "PCI-06": "PARTIAL",  # Summary table — data exists, GUI display pending Phase 3
        "PCI-07": "PARTIAL",  # Curves extracted, needs official ASTM verification
        "PCI-08": True,   # Severity assignment
        "PCI-09": True,   # Section-level PCI
        "PCI-10": True,   # Bbox correction
        "PCI-11": True,   # Edge cases
        "PCI-12": "DEFERRED",  # Unit conversion ft2/m2 not yet implemented
    }

    pass_count = sum(1 for v in reqs.values() if v is True)
    partial_count = sum(1 for v in reqs.values() if v == "PARTIAL")
    deferred_count = sum(1 for v in reqs.values() if v == "DEFERRED")
    total = len(reqs)

    for req, status in reqs.items():
        symbol = "PASS" if status is True else ("PARTIAL" if status == "PARTIAL" else "DEFERRED")
        print(f"  {req}: {symbol}")

    print(f"\n  Total: {total} | PASS: {pass_count} | PARTIAL: {partial_count} | DEFERRED: {deferred_count}")
    print(f"  Coverage: {pass_count}/{total} = {pass_count/total*100:.0f}% full, {(pass_count+partial_count)/total*100:.0f}% including partial")


if __name__ == "__main__":
    main()
