# ROADMAP.md — Pavement PCI Thesis (v2 — Pretrained Weights Strategy)

## Milestone: V1.0 — MVP Detection + PCI (T1)

---

### Phase 1: Setup & Pretrained Model Integration
**Status:** next
**Goal:** Thiết lập môi trường, tải pretrained YOLOv12s, export ONNX, test inference
**Requirements:** DET-01, DET-02, DET-03, DET-04, DET-05, DET-06
**Mode:** mvp

- Setup Python venv + dependencies (ultralytics, onnxruntime-directml, supervision, opencv)
- Download yolo12s_seed0_best.pt từ HuggingFace (SreekarAditya/yolo-rdd2022-benchmark)
- Export .pt → ONNX (640x640, opset 12, Dynamic batch=False)
- Build detector module: load ONNX + DirectML provider, preprocess, postprocess
- Test inference trên 20 ảnh mẫu → validate detection output
- Supervision BoxAnnotator + LabelAnnotator cho visualization
- Benchmark: inference time, RAM usage trên Intel HD 4400

**Success Criteria:**
1. YOLOv12s ONNX loads và inference thành công qua DirectML
2. Detect 4 classes (D00, D10, D20, D40) với confidence ≥ 0.15
3. Inference ≤ 200ms/frame trên DirectML
4. RAM ≤ 150MB khi chạy inference đơn

---

### Phase 2: PCI Calculation Engine (ASTM D6433)
**Status:** pending
**Goal:** Implement PCI calculation theo chuẩn ASTM D6433 với bbox proxy
**Requirements:** PCI-01, PCI-02, PCI-03, PCI-04, PCI-05, PCI-06
**Depends on:** Phase 1

- Implement damage density calculation (bbox area / sample unit area)
- Implement deduct value curves cho 4 loại distress (D00, D10, D20, D40) theo ASTM D6433
- Implement CDV (Corrected Deduct Value) calculation
- Implement PCI = 100 - CDV
- PCI rating classification (0-100 → Good/Satisfactory/Fair/Poor/Very Poor/Failed)
- Damage summary table: count, density, deduct value per class
- Unit tests cho PCI engine với known values

**Success Criteria:**
1. PCI engine tính đúng với test cases từ ASTM D6433 examples
2. Damage density tính chính xác từ bounding boxes
3. PCI rating phân loại đúng 6 mức
4. Unit tests pass 100%

---

### Phase 3: Desktop App Core (GUI)
**Status:** pending
**Goal:** Xây dựng giao diện PySide6 Fluent Design, tích hợp detection + PCI
**Requirements:** VIS-01, VIS-02, VIS-03, GUI-01, GUI-02, GUI-03, GUI-04, GUI-05, GUI-06
**Depends on:** Phase 2

- PySide6 main window với Fluent-style QSS theme (dark + light)
- Image viewer widget (zoom, pan, fit-to-window)
- File open dialog (jpg, png, bmp)
- Menu bar, toolbar, status bar
- "Run Detection" action → load image → inference → annotate → display
- PCI panel: gauge chart + damage summary table
- Settings dialog (model path, confidence threshold, sample unit size)
- Dark/Light theme toggle
- Wire detector + PCI engine vào GUI

**Success Criteria:**
1. GUI hiển thị ảnh + annotated bounding boxes + labels
2. PCI panel hiển thị điểm số + bảng tổng hợp
3. Theme toggle hoạt động
4. Settings lưu được model path + confidence threshold

---

### Phase 4: FastSAM Segmentation Integration (T2)
**Status:** pending
**Goal:** Thêm FastSAM cho segmentation chính xác, nâng cấp PCI từ bbox→mask
**Requirements:** SEG-01, SEG-02, SEG-03, SEG-04, SEG-05
**Depends on:** Phase 3

- Download FastSAM-s weights
- Build FastSAM inference module (bbox-prompted segmentation)
- Pipeline: YOLOv12s detect → crop bbox → FastSAM segment → precise mask
- IoU matching giữa detection và segmentation
- Cập nhật PCI engine: tính damage area từ mask thay bbox
- So sánh PCI từ bbox proxy vs segmentation mask
- Toggle trong GUI: "Use Segmentation" checkbox

**Success Criteria:**
1. FastSAM segment chính xác trong detected bounding boxes
2. Damage area từ mask khác biệt đáng kể so với bbox (đặc biệt D00)
3. PCI từ mask chính xác hơn bbox proxy
4. Toggle segmentation trong GUI hoạt động

---

### Phase 5: Video Processing & Advanced GUI
**Status:** pending
**Goal:** Xử lý video, xuất báo cáo, hoàn thiện GUI
**Requirements:** VID-01, VID-02, VID-03, VID-04, VID-05, GUI-07, GUI-08, GUI-09, GUI-10
**Depends on:** Phase 4

- Video loader (OpenCV): mp4, avi
- Frame extraction + batch inference (detection + segmentation)
- ffmpeg H.264 encoding cho output video
- Progress bar khi xử lý video
- PCI time-series chart (PCI theo frame)
- Video player widget với timeline scrubber
- Side-by-side view (original | annotated)
- Damage heatmap overlay
- PDF report generation (PCI report + annotated images)

**Success Criteria:**
1. Video processing chạy ổn định, progress bar cập nhật realtime
2. Output video có annotation + H.264 encoding
3. PCI chart hiển thị xu hướng theo thời gian
4. PDF report chứa PCI score + annotated images + damage summary

---

### Phase 6: End-to-End Segmentation Training (T3 — Optional)
**Status:** pending
**Goal:** Train YOLOv12s-seg trên Colab cho end-to-end detection+segmentation
**Requirements:** TRN-01, TRN-02, TRN-03, TRN-04, TRN-05
**Depends on:** Phase 5

- Tải Kaggle dataset RDD2022 YOLO CrackScan v2 (đã convert sẵn YOLO format)
- Tạo Colab notebook train YOLOv12s-seg
- Train trên Colab GPU (Tesla T4)
- Target mAP50-seg ≥ 0.50
- Export best.pt → ONNX (DirectML compatible)
- So sánh 3 phương pháp: bbox proxy vs FastSAM vs end-to-end seg
- Tích hợp vào app: chọn segmentation mode (bbox/FastSAM/end-to-end)

**Success Criteria:**
1. YOLOv12s-seg train thành công, mAP50-seg ≥ 0.50
2. ONNX export chạy được trên DirectML
3. Bảng so sánh 3 phương pháp có số liệu cụ thể
4. App hỗ trợ chọn segmentation mode

---

### Phase 7: Testing, Evaluation & Thesis Documentation
**Status:** pending
**Goal:** Kiểm thử toàn diện, viết thuyết minh, chuẩn bị bảo vệ
**Requirements:** TST-01, TST-02, TST-03, TST-04, DOC-01, DOC-02, DOC-03, DOC-04
**Depends on:** Phase 6

- Unit tests cho PCI engine (ASTM D6433 logic, edge cases)
- Integration tests cho full pipeline (image → detection → seg → PCI → report)
- Benchmark inference speed: CPU vs DirectML, 1 model vs 2 models
- So sánh PCI tự động vs đánh giá thủ công (nếu có ground truth)
- Viết quyển thuyết minh đồ án (3 chương)
- Tạo slide bảo vệ (PowerPoint)
- Quay video demo hoàn chỉnh
- README + hướng dẫn cài đặt

**Success Criteria:**
1. Tất cả unit tests + integration tests pass
2. Inference benchmark có số liệu cụ thể
3. Thuyết minh hoàn chỉnh 3 chương
4. Slide + video demo sẵn sàng cho bảo vệ
