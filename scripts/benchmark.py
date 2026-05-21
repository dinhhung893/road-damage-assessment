"""Phase 1 benchmark and validation script."""

from __future__ import annotations

import sys
import time
import tracemalloc
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.engine.detector import RoadDamageDetector


def benchmark() -> None:
    """Run benchmark on sample images."""
    detector = RoadDamageDetector()

    # Find a real image with detections
    test_img = PROJECT_ROOT / "data" / "samples" / "real_damage_03_100_jpg.rf.3caf197d115db938f70442b9cbefbe34.jpg"
    if not test_img.exists():
        # Fallback to any sample
        samples = sorted((PROJECT_ROOT / "data" / "samples").glob("*.jpg"))
        if not samples:
            print("No sample images found!")
            return
        test_img = samples[0]

    # Memory tracking
    tracemalloc.start()

    # Warmup
    _ = detector.detect(str(test_img))

    # Benchmark: 10 runs
    times = []
    for _ in range(10):
        t0 = time.perf_counter()
        result = detector.detect(str(test_img))
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    mean_t = sum(times) / len(times)
    std_t = (sum((t - mean_t) ** 2 for t in times) / len(times)) ** 0.5

    print("=== BENCHMARK RESULTS ===")
    print(f"Image: {test_img.name}")
    print(f"Image shape: {result.image_shape}")
    print(f"Detections: {len(result.detections)}")
    print(f"Inference times (10 runs):")
    print(f"  Mean: {mean_t:.0f} ms")
    print(f"  Min:  {min(times):.0f} ms")
    print(f"  Max:  {max(times):.0f} ms")
    print(f"  Std:  {std_t:.0f} ms")
    print(f"Memory:")
    print(f"  Current: {current / 1024 / 1024:.1f} MB")
    print(f"  Peak:    {peak / 1024 / 1024:.1f} MB")

    # Validation
    print()
    print("=== VALIDATION ===")
    print(f"Model classes: {detector.model.names}")
    print(f"Expected: 4 damage classes (D00, D10, D20, D40)")
    actual_count = len(detector.model.names)
    status = "PASS" if actual_count >= 4 else "FAIL"
    print(f"Class count: {actual_count} -> {status}")

    # Check all sample images
    print()
    print("=== ALL SAMPLES ===")
    for img in sorted((PROJECT_ROOT / "data" / "samples").glob("*.jpg")):
        r = detector.detect(str(img))
        dets = ", ".join(f"{d.code}({d.confidence:.0%})" for d in r.detections) or "none"
        print(f"  {img.name}: {len(r.detections)} det [{dets}] {r.inference_time_ms:.0f}ms")


if __name__ == "__main__":
    benchmark()
