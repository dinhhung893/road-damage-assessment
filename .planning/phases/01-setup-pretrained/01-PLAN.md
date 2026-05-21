# Phase 1: Setup & Pretrained Model Integration - Plan

**Phase:** 01
**Status:** Planned
**Requirements:** DET-01~08, INF-01, INF-03~05
**Depends on:** None (first phase)
**Est. Time:** 1.5 tuần

---

## Task Overview

| Task | Type | Requirements | Priority | Est. |
|------|------|-------------|----------|------|
| T1: Dọn dẹp code cũ + tạo cấu trúc mới | infra | INF-04 | [BLOCKING] | 30min |
| T2: Update requirements.txt + tạo venv | infra | INF-05, INF-01 | [BLOCKING] | 30min |
| T3: Script tải model tự động | code | DET-08, DET-07 | [BLOCKING] | 1h |
| T4: Verify model + export ONNX | code | DET-01, DET-02, DET-07 | high | 1h |
| T5: Build detector module (ONNX Runtime) | code | DET-03, DET-04, DET-05 | high | 2h |
| T6: Tuyển chọn ảnh demo | data | INF-03 | medium | 30min |
| T7: Test inference + visualization | code | DET-06 | high | 1h |
| T8: Benchmark + validation | test | DET-01~06 | high | 1h |

---

## T1: Dọn dẹp code cũ + tạo cấu trúc mới [BLOCKING]

**Requirement:** INF-04
**Context decision:** D-01~04 (dọn dẹp triệt để, cấu trúc module chức năng, dọn trước implement)

### Steps
1. Xóa `notebooks/01_prepare_dataset.ipynb` (Colab crash, không dùng)
2. Xóa toàn bộ nội dung `src/engine/`, `src/ui/`, `src/utils/` (chỉ __init__.py trống)
3. Tạo cấu trúc mới:
   ```
   src/
   ├── __init__.py
   ├── engine/
   │   ├── __init__.py
   │   ├── detector.py      # ONNX Runtime inference
   │   └── pci.py            # PCI calculation (Phase 2)
   ├── utils/
   │   ├── __init__.py
   │   ├── config.py         # JSON config loader/saver
   │   ├── logging_setup.py  # Logging framework
   │   └── io.py             # File I/O helpers
   └── ui/
       ├── __init__.py
       ├── main_window.py     # PySide6 main window (Phase 3)
       └── widgets/           # Custom widgets (Phase 3)
   ```
4. Tạo `outputs/` cấu trúc con: `outputs/images/`, `outputs/reports/`, `outputs/videos/`
5. Tạo `.gitkeep` trong `outputs/` subdirs

### Files Modified
- DELETE: `notebooks/01_prepare_dataset.ipynb`
- DELETE: `src/engine/__init__.py` (old)
- DELETE: `src/ui/__init__.py` (old)
- DELETE: `src/utils/__init__.py` (old)
- CREATE: `src/engine/__init__.py` (new)
- CREATE: `src/engine/detector.py` (stub)
- CREATE: `src/engine/pci.py` (stub)
- CREATE: `src/utils/__init__.py` (new)
- CREATE: `src/utils/config.py` (stub)
- CREATE: `src/utils/logging_setup.py` (stub)
- CREATE: `src/utils/io.py` (stub)
- CREATE: `src/ui/__init__.py` (new)
- CREATE: `outputs/images/.gitkeep`
- CREATE: `outputs/reports/.gitkeep`
- CREATE: `outputs/videos/.gitkeep`

### Exit Criteria
- [ ] `notebooks/01_prepare_dataset.ipynb` đã xóa
- [ ] Cấu trúc src/ mới đã tạo với stub files
- [ ] `outputs/` có cấu trúc con

---

## T2: Update requirements.txt + tạo venv [BLOCKING]

**Requirements:** INF-05, INF-01
**Context decision:** D-05 (bỏ torch khỏi requirements, pin versions)

### Steps
1. Update `requirements.txt` với pinned versions:
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
   Note: `torch` sẽ được cài tự động qua ultralytics dependency (cần cho export)
2. Tạo Python venv: `python -m venv .venv`
3. Activate + install: `pip install -r requirements.txt`
4. Implement `src/utils/logging_setup.py` — structured logging framework:
   - Log format: `[%(asctime)s] %(levelname)s %(name)s: %(message)s`
   - Log file: `outputs/app.log` (rotating, 5MB max, 3 backups)
   - Console handler: INFO level
   - File handler: DEBUG level
   - Helper: `get_logger(name)` trả về configured logger

### Files Modified
- EDIT: `requirements.txt`
- EDIT: `src/utils/logging_setup.py` (implement, không còn stub)

### Exit Criteria
- [ ] `requirements.txt` đã update với pinned versions, không có `torch` riêng
- [ ] venv tạo thành công, `pip install -r requirements.txt` pass
- [ ] `logging_setup.py` implement xong, test được `get_logger()`

---

## T3: Script tải model tự động [BLOCKING]

**Requirements:** DET-08, DET-07
**Research finding:** ultralytics không hỗ trợ `YOLO("repo_id")`, phải dùng `huggingface_hub`

### Steps
1. Tạo `scripts/download_model.py`:
   ```python
   """Auto-download YOLOv12s pretrained weights from HuggingFace."""
   from huggingface_hub import hf_hub_download
   import sys
   from pathlib import Path

   REPO_ID = "SreekarAditya/yolo-rdd2022-benchmark"
   FILENAME = "yolo-rdd2022-benchmark/yolo12s_seed0_best.pt"
   LOCAL_DIR = "models"

   def download_model():
       pt_path = hf_hub_download(
           repo_id=REPO_ID,
           filename=FILENAME,
           local_dir=LOCAL_DIR,
           local_dir_use_symlinks=False,
       )
       print(f"Downloaded: {pt_path}")
       return pt_path

   if __name__ == "__main__":
       download_model()
   ```
2. Verify model sau khi tải:
   ```python
   from ultralytics import YOLO
   model = YOLO(pt_path)
   print(f"Classes: {model.names}")
   print(f"Class count: {len(model.names)}")
   # Expected: {0: 'D00', 1: 'D10', 2: 'D20', 3: 'D40'} or 5 classes with Repair
   ```
3. Nếu model trả về 5 classes (có Repair), ghi nhận và xử lý trong detector:
   - Repair class → không tính vào PCI
   - Log warning cho user biết

### Files Modified
- CREATE: `scripts/download_model.py`
- CREATE: `models/.gitkeep` (trước khi download)

### Exit Criteria
- [ ] `scripts/download_model.py` chạy thành công
- [ ] `models/yolo12s_seed0_best.pt` tồn tại (~18.9MB)
- [ ] Model load được qua ultralytics
- [ ] Class count và names đã verify (4 hay 5 classes)

---

## T4: Verify model + export ONNX

**Requirements:** DET-01, DET-02, DET-07

### Steps
1. Load model với ultralytics, chạy inference test trên 1 ảnh:
   ```python
   from ultralytics import YOLO
   model = YOLO("models/yolo12s_seed0_best.pt")
   results = model("test_image.jpg", conf=0.15)
   ```
2. Export ONNX:
   ```python
   model.export(
       format="onnx",
       opset=12,
       dynamic=False,
       simplify=True,
       half=False,
       imgsz=640,
   )
   ```
3. Verify ONNX file:
   ```python
   import onnxruntime as ort
   session = ort.InferenceSession("models/yolo12s_seed0_best.onnx")
   print(f"Inputs: {session.get_inputs()}")
   print(f"Outputs: {session.get_outputs()}")
   print(f"Providers: {session.get_providers()}")
   ```
4. So sánh kết quả inference .pt vs .onnx trên cùng ảnh → sai số < 1%

### Files Modified
- CREATE: `models/yolo12s_seed0_best.onnx` (từ export)

### Exit Criteria
- [ ] ONNX export thành công, không lỗi
- [ ] ONNX file load được qua onnxruntime
- [ ] DirectML provider active (hoặc CPU fallback + warning)
- [ ] Kết quả .pt vs .onnx khớp (sai số < 1%)

---

## T5: Build detector module (ONNX Runtime)

**Requirements:** DET-03, DET-04, DET-05
**Research finding:** DmlExecutionProvider + CPUExecutionProvider fallback

### Steps
1. Implement `src/engine/detector.py`:
   - Class `RoadDamageDetector`:
     - `__init__(model_path, confidence=0.15, provider="auto")`
     - `_load_model()` → tạo ONNX InferenceSession
     - `_preprocess(image)` → letterbox 640x640, normalize, NCHW
     - `_postprocess(output)` → parse YOLO output, NMS, filter confidence
     - `detect(image_path)` → trả về list of Detection(name, confidence, bbox)
     - `detect_batch(image_paths)` → batch processing
   - Provider selection logic:
     ```python
     if provider == "auto":
         providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
     elif provider == "cpu":
         providers = ["CPUExecutionProvider"]
     session = ort.InferenceSession(model_path, providers=providers)
     active = session.get_providers()[0]
     if active == "CPUExecutionProvider":
         logger.warning("DirectML không khả dụng, dùng CPU. Inference sẽ chậm hơn.")
     ```
   - Repair class handling:
     ```python
     # Nếu model trả về class "Repair" (id=4), đánh dấu nhưng không tính PCI
     for det in detections:
         if det.name == "Repair":
             det.include_in_pci = False
     ```
2. Implement `src/utils/config.py`:
   - `load_config()` → đọc JSON config file
   - `save_config(config)` → ghi JSON config file
   - Default config: model_path, confidence, sample_unit_area, provider
3. Write unit tests: `tests/test_detector.py`
   - Test preprocess shape (1, 3, 640, 640)
   - Test postprocess với mock output
   - Test provider fallback

### Files Modified
- EDIT: `src/engine/detector.py` (implement)
- EDIT: `src/utils/config.py` (implement)
- CREATE: `tests/test_detector.py`
- CREATE: `config/default.json` (default config)

### Exit Criteria
- [ ] `RoadDamageDetector` class hoàn chỉnh
- [ ] Preprocess → shape đúng (1, 3, 640, 640)
- [ ] DirectML fallback hoạt động + warning log
- [ ] Repair class được đánh dấu `include_in_pci=False`
- [ ] `config.py` đọc/ghi JSON thành công
- [ ] Unit tests pass

---

## T6: Tuyển chọn ảnh demo

**Requirement:** INF-03

### Steps
1. Tìm ảnh mẫu từ RDD2022 dataset (public online):
   - 2 ảnh có D00 (nứt dọc)
   - 2 ảnh có D10 (nứt ngang)
   - 2 ảnh có D20 (nứt da cá)
   - 2 ảnh có D40 (ổ gà)
   - 2 ảnh đường tốt (0 detection)
   - 2 ảnh có nhiều loại hư hỏng (mixed)
2. Lưu vào `data/samples/` với tên file mô tả:
   - `D00_longitudinal_01.jpg`
   - `D10_transverse_01.jpg`
   - `D20_alligator_01.jpg`
   - `D40_pothole_01.jpg`
   - `good_road_01.jpg`
   - `mixed_damage_01.jpg`
3. Tạo `data/samples/README.md` mô tả nguồn và nội dung

### Files Modified
- CREATE: `data/samples/*.jpg` (10-12 ảnh)
- CREATE: `data/samples/README.md`
- DELETE: `data/samples/.gitkeep`

### Exit Criteria
- [ ] Ít nhất 10 ảnh mẫu trong `data/samples/`
- [ ] Đủ 4 loại hư hỏng + ảnh đường tốt + ảnh mixed
- [ ] README.md có mô tả nguồn

---

## T7: Test inference + visualization

**Requirement:** DET-06

### Steps
1. Chạy inference trên tất cả ảnh demo:
   ```python
   from src.engine.detector import RoadDamageDetector
   import supervision as sv

   detector = RoadDamageDetector("models/yolo12s_seed0_best.onnx")
   for img_path in Path("data/samples").glob("*.jpg"):
       detections = detector.detect(str(img_path))
       # Annotate with supervision
       # Save to outputs/images/
   ```
2. Verify:
   - Ảnh có D00 → detect D00
   - Ảnh đường tốt → 0 detection
   - Bounding boxes + labels hiển thị đúng
3. Tạo annotated images trong `outputs/images/`

### Files Modified
- CREATE: `outputs/images/*.jpg` (annotated)

### Exit Criteria
- [ ] Inference chạy thành công trên tất cả ảnh demo
- [ ] Annotated images hiển thị đúng boxes + labels + confidence
- [ ] Ảnh đường tốt trả về 0 detection

---

## T8: Benchmark + validation

**Requirements:** DET-01~06 (success criteria verification)

### Steps
1. Benchmark inference speed:
   ```python
   import time
   times = []
   for _ in range(50):
       start = time.perf_counter()
       detector.detect("data/samples/D00_longitudinal_01.jpg")
       times.append(time.perf_counter() - start)
   avg_ms = sum(times) / len(times) * 1000
   print(f"Average inference: {avg_ms:.1f}ms")
   ```
2. Benchmark CPU vs DirectML (nếu cả 2 available)
3. Đo RAM usage: `psutil.Process().memory_info().rss / 1024 / 1024`
4. Verify success criteria:
   - [ ] YOLOv12s ONNX loads qua DirectML ✓
   - [ ] Detect 4 classes với confidence ≥ 0.15 ✓
   - [ ] Inference ≤ 200ms/frame trên DirectML ✓
   - [ ] RAM ≤ 150MB khi chạy inference đơn ✓

### Exit Criteria
- [ ] Benchmark report có số liệu cụ thể
- [ ] Tất cả success criteria pass

---

## Success Criteria (Phase 1 Complete)

1. YOLOv12s ONNX loads và inference thành công qua DirectML
2. Detect 4 classes (D00, D10, D20, D40) với confidence ≥ 0.15
3. Inference ≤ 200ms/frame trên DirectML
4. RAM ≤ 150MB khi chạy inference đơn
5. Edge case: Repair class handled nếu model trả về
6. DirectML fallback + warning hoạt động
7. Logging framework hoạt động
8. Bộ ảnh demo đầy đủ trong data/samples/
9. Code cũ đã dọn dẹp, cấu trúc mới sạch

---

*Plan created: 2026-05-21*
