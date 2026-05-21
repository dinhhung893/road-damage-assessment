# Phase 1: Setup & Pretrained Model Integration - Research

**Date:** 2026-05-21
**Status:** Complete

## Key Findings

### 1. Model Download Mechanism (DET-08)

**Finding:** ultralytics does NOT support loading models directly from HuggingFace Hub via `YOLO("repo_id")`. Must use `huggingface_hub.hf_hub_download()` to download .pt file first, then load with `YOLO(local_path)`.

**Recommended approach:**
```python
from huggingface_hub import hf_hub_download
from ultralytics import YOLO

# Download from HuggingFace
pt_path = hf_hub_download(
    repo_id="SreekarAditya/yolo-rdd2022-benchmark",
    filename="yolo-rdd2022-benchmark/yolo12s_seed0_best.pt",
    local_dir="models"
)
model = YOLO(pt_path)
```

**Alternative repo:** `rezzzq/yolo12s-road-damage-rdd2022` — simpler path structure, includes usage instructions.

### 2. ONNX Export (DET-02)

**Finding:** Export is straightforward via ultralytics API:
```python
model.export(
    format="onnx",
    opset=12,
    dynamic=False,     # Fixed batch size for DirectML
    simplify=True,     # Simplify ONNX graph
    half=False,        # FP32 for Intel HD 4400 compatibility
    imgsz=640          # Standard YOLO input size
)
```

**Output:** `.pt` → `.onnx` in same directory. Can verify with `onnxruntime.InferenceSession()`.

**Decision:** Export at setup time (not ship pre-exported). Reason: ensures compatibility with current onnxruntime version, allows debug if export fails.

### 3. ONNX Runtime + DirectML (DET-03)

**Finding:** Provider name is `"DmlExecutionProvider"`. Fallback to `"CPUExecutionProvider"` is built-in.

```python
import onnxruntime as ort

providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
session = ort.InferenceSession("model.onnx", providers=providers)
```

**EP Fail Recovery:** If DirectML fails during `session.run()`, ONNX Runtime automatically falls back to CPU. No manual try/except needed for per-inference fallback.

**Startup detection:** Check if DML is actually being used:
```python
active_providers = session.get_providers()
# ["DmlExecutionProvider", "CPUExecutionProvider"] if DML available
# ["CPUExecutionProvider"] if DML not available
```

**Decision:** Log which provider is active at startup. Show warning (not silent) if DML unavailable — user needs to know for performance expectations.

### 4. YOLO ONNX Preprocessing

**Standard pipeline:**
1. Read image with OpenCV (BGR)
2. Letterbox resize to 640x640 (maintain aspect ratio, pad with gray)
3. Convert BGR→RGB
4. Normalize to [0,1] (divide by 255.0)
5. Transpose HWC→CHW
6. Add batch dimension: (1, 3, 640, 640)
7. Convert to float32

**Postprocessing:** Parse YOLO output → extract boxes, scores, class_ids → apply NMS → filter by confidence threshold.

### 5. Supervision Library

**Usage for annotation:**
```python
import supervision as sv
from ultralytics import YOLO

results = model(image)
detections = sv.Detections.from_ultralytics(results[0])
annotator = sv.BoxAnnotator()
annotated = annotator.annotate(scene=image.copy(), detections=detections)
label_annotator = sv.LabelAnnotator()
annotated = label_annotator.annotate(scene=annotated, detections=detections, labels=labels)
```

### 6. requirements.txt Updates

**Current issues:**
- `torch>=2.0.0` — NOT needed for ONNX Runtime inference (saves ~2GB install)
- No version pinning — risk of API breakage

**Recommended:**
```
ultralytics>=8.1.0,<9.0.0
onnxruntime-directml>=1.18.0,<2.0.0
supervision>=0.25.0,<1.0.0
opencv-python>=4.9.0,<5.0.0
numpy>=1.26.0,<2.0.0
Pillow>=10.0.0,<11.0.0
matplotlib>=3.8.0,<4.0.0
huggingface-hub>=0.23.0,<1.0.0
PySide6>=6.7.0,<7.0.0
pytest>=8.0.0,<9.0.0
```

Note: `ultralytics` pulls `torch` as dependency. To avoid this, use `pip install ultralytics --no-deps` + install only needed deps. OR accept torch install (needed for export step only). **Decision: Accept torch install** — export requires it, and it's only ~2GB one-time.

### 7. YOLOv12s Class Verification (DET-07)

**RDD2022 has 4 classes (D00, D10, D20, D40)** in the benchmark repo. The `rezzzq` repo mentions 5 classes (includes "Repair"). Need to verify at runtime which model outputs which classes.

**Verification script:**
```python
model = YOLO(pt_path)
print(f"Model names: {model.names}")  # {0: 'D00', 1: 'D10', ...}
print(f"Number of classes: {len(model.names)}")
```

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| YOLOv12s not compatible with current ultralytics | Low | Verify first (DET-07), pin version |
| ONNX export fails on YOLOv12s | Low | Test export immediately after download |
| DirectML not available on target machine | Medium | Fallback CPU + warning at startup |
| Model returns 5 classes instead of 4 | Medium | Verify model.names at runtime, handle Repair class |
| ultralytics API changes break code | Medium | Pin version in requirements.txt |

---

*Research completed: 2026-05-21*
