"""Quick end-to-end test: detect → segment → PCI."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.detector import RoadDamageDetector
from src.engine.segmenter import RoadDamageSegmenter
from src.engine.pci import PCIEngine
import cv2

# Find a sample image with detections
samples = list(Path("data/samples").glob("real_damage_*.jpg"))
if not samples:
    print("No sample images found")
    sys.exit(1)

det = RoadDamageDetector()
seg = RoadDamageSegmenter()
pci = PCIEngine()

for img_path in samples:
    print(f"\n--- {img_path.name} ---")
    r = det.detect(img_path)
    print(f"  Detections: {len(r.pci_detections)}")
    if not r.pci_detections:
        print("  No PCI detections, skipping")
        continue

    for d in r.pci_detections:
        print(f"  {d.code} conf={d.confidence:.2f} bbox={d.bbox}")

    # Segment
    if seg.is_available:
        img = cv2.imread(str(img_path))
        t = seg.segment_detections(img, r.pci_detections, r.image_shape)
        r.segmentation_time_ms = t

        for d in r.pci_detections:
            print(f"  {d.code} mask_px={d.mask_pixels} ratio={d.mask_area_sqft:.4f} contours={len(d.mask_contours)}")
    else:
        print("  FastSAM not available")

    # PCI
    h, w = r.image_shape
    dmg = [{
        "code": d.code, "bbox": d.bbox, "confidence": d.confidence,
        "has_mask": d.has_mask, "mask_area_sqft": d.mask_area_sqft,
    } for d in r.pci_detections]
    res = pci.calculate_pci(dmg, image_area_px=h * w)
    print(f"  PCI={res.pci_value} ({res.rating})")
    print(f"  Detect: {r.inference_time_ms:.0f}ms, Segment: {r.segmentation_time_ms:.0f}ms")
