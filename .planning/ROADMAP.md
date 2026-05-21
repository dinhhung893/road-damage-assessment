# ROADMAP.md — Pavement PCI Thesis (v2.1 — Pretrained Weights + ASTM Data Sourced)

## Milestone: V1.0 — MVP Detection + PCI (T1)

---

### Phase 1: Setup & Pretrained Model Integration
**Status:** next
**Goal:** Thiết lập môi trường, tải pretrained YOLOv12s, export ONNX, test inference
**Requirements:** DET-01, DET-02, DET-03, DET-04, DET-05, DET-06, DET-07, DET-08, INF-01, INF-03, INF-04, INF-05
**Mode:** mvp
**Est. Time:** 1.5 tuần (trong 13 tuần học kỳ DN)

- Setup Python venv + dependencies (ultralytics, onnxruntime-directml, supervision, opencv) — pin versions trong requirements.txt
- Dọn dẹp code cũ (Gradio era) + update requirements.txt
- Verify model YOLOv12s: (a) tương thích ultralytics, (b) class count đúng, (c) ONNX export thành công
- Script tự động tải model từ HuggingFace (huggingface_hub)
- Download yolo12s_seed0_best.pt từ HuggingFace (SreekarAditya/yolo-rdd2022-benchmark)
- Export .pt → ONNX (640x640, opset 12, Dynamic batch=False)
- Build detector module: load ONNX + DirectML provider (fallback CPU nếu DirectML không khả dụng), preprocess, postprocess
- Tuyển chọn bộ ảnh demo: đủ 4 loại hư hỏng + ảnh đường tốt + ảnh có PCI known
- Setup logging framework (tránh lặp lỗi G1-G2)
- Test inference trên 20 ảnh mẫu → validate detection output
- Supervision BoxAnnotator + LabelAnnotator cho visualization
- Benchmark: inference time, RAM usage trên Intel HD 4400

**Success Criteria:**
1. YOLOv12s ONNX loads và inference thành công qua DirectML
2. Detect 4 classes (D00, D10, D20, D40) với confidence ≥ 0.15
3. Inference ≤ 200ms/frame trên DirectML
4. RAM ≤ 150MB khi chạy inference đơn

---

### Phase 2: PCI Calculation Engine (ASTM D6433) — ƯU TIÊN CAO NHẤT
**Status:** pending
**Goal:** Implement PCI calculation theo chuẩn ASTM D6433 với bbox proxy, dùng deduct value curves đã trích xuất từ slide chuyên môn
**Requirements:** PCI-01, PCI-02, PCI-03, PCI-04, PCI-05, PCI-06, PCI-07, PCI-08, PCI-09, PCI-10, PCI-11, PCI-12
**Depends on:** Phase 1
**Priority:** CAO NHẤT — PCI là xương sống đồ án, phải hoàn thiện và test kỹ TRƯỚC khi chạm vào GUI
**Est. Time:** 1.5 tuần

- Load deduct value curves từ `data/pci_astm_d6433.json` (đã trích xuất từ Slide 17-22 PPTX chuyên môn)
- Implement damage density calculation (bbox area / sample unit area) — hỗ trợ cả ft² và m²
- Implement deduct value lookup: density → deduct value (nội suy tuyến tính từ curves)
- Implement CDV (Corrected Deduct Value) calculation từ q và TDV
- Implement PCI = 100 - CDV cho từng sample unit
- Implement PCI cấp đoạn đường (section-level): trung bình có trọng số các sample unit
- Implement severity assignment dựa trên density (khi chỉ có bbox, không có mask)
- Implement bbox overestimate correction (aspect ratio heuristic, đặc biệt D00)
- Implement edge case handling: 0 detection, non-pavement, low confidence
- PCI rating classification (0-100 → Good/Satisfactory/Fair/Poor/Very Poor/Failed) + khuyến nghị bảo dưỡng
- Damage summary table: count, density, deduct value, PCI per class
- Unit tests cho PCI engine với known values từ ASTM D6433 examples
- Verify deduct value curves với bản chính thức ASTM D6433-07

**Success Criteria:**
1. PCI engine tính đúng với test cases từ ASTM D6433 examples
2. Damage density tính chính xác từ bounding boxes
3. PCI rating phân loại đúng 6 mức
4. Deduct value curves đã verify với bản chính thức ASTM D6433-07
5. Unit tests pass 100% — KHÔNG bắt đầu Phase 3 nếu chưa pass
6. Edge cases xử lý đúng (0 detection, non-pavement)
7. Bbox overestimate correction hoạt động cho D00

---

### Phase 3: Desktop App Core (GUI)
**Status:** pending
**Goal:** Xây dựng giao diện PySide6 Fluent Design, tích hợp detection + PCI
**Requirements:** VIS-01, VIS-02, VIS-03, GUI-01, GUI-02, GUI-03, GUI-04, GUI-05, GUI-06, GUI-11, GUI-12, GUI-13, GUI-14, INF-06
**Depends on:** Phase 2 (CHỈ bắt đầu khi Phase 2 pass 100% tests)
**Est. Time:** 2 tuần

- PySide6 main window với Fluent-style QSS theme (dark + light) — giao diện tiếng Việt
- Image viewer widget (zoom, pan, fit-to-window)
- File open dialog (jpg, png, bmp) + thư mục ảnh (batch processing)
- Menu bar, toolbar, status bar
- "Run Detection" action → load image → inference → annotate → display
- PCI panel: gauge chart + damage summary table + khuyến nghị bảo dưỡng
- Settings dialog (model path, confidence threshold, sample unit size) — lưu JSON file
- Dark/Light theme toggle
- Xuất kết quả detection + PCI ra CSV/Excel
- Quản lý thư mục output: outputs/images/, outputs/reports/, outputs/videos/ + nút "Open Output Folder"
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
**Requirements:** VID-01, VID-02, VID-03, VID-04, VID-05, VID-06, GUI-07, GUI-08, GUI-09, GUI-10
**Depends on:** Phase 4
**Est. Time:** 2 tuần

- Video loader (OpenCV): mp4, avi
- Frame extraction + batch inference (detection + segmentation) — chiến lược lấy mẫu mỗi N frame
- ffmpeg H.264 encoding cho output video
- Progress bar khi xử lý video
- PCI time-series chart (PCI theo frame)
- Video player widget với timeline scrubber
- Side-by-side view (original | annotated)
- Damage heatmap overlay
- PDF report generation theo form ASTM D6433 (PCI report + annotated images + damage summary)

**Success Criteria:**
1. Video processing chạy ổn định, progress bar cập nhật realtime
2. Output video có annotation + H.264 encoding
3. PCI chart hiển thị xu hướng theo thời gian
4. PDF report chứa PCI score + annotated images + damage summary

---

### Phase 6: End-to-End Segmentation Training (T3 — Optional, KHÔNG block Phase 7)
**Status:** pending
**Goal:** Train YOLOv12s-seg trên Colab cho end-to-end detection+segmentation
**Requirements:** TRN-01, TRN-02, TRN-03, TRN-04, TRN-05
**Depends on:** Phase 5
**Note:** Phase này là điểm cộng, không bắt buộc. Phase 7a có thể bắt đầu mà không cần kết quả từ Phase 6.

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

### Phase 7a: Testing & Evaluation — KHÔNG phụ thuộc Phase 6
**Status:** pending
**Goal:** Kiểm thử toàn diện, benchmark, so sánh phương pháp
**Requirements:** TST-01, TST-02, TST-03, TST-04, TST-05, TST-06, INF-02
**Depends on:** Phase 5
**Est. Time:** 2 tuần

- Unit tests cho PCI engine (ASTM D6433 logic, edge cases)
- Integration tests cho full pipeline (image → detection → seg → PCI → report)
- Benchmark inference speed: CPU vs DirectML, 1 model vs 2 models
- So sánh PCI tự động vs đánh giá thủ công (nếu có ground truth)
- Verify PCI engine với test cases từ slide chuyên môn PPTX
- Test độ nhạy PCI theo confidence threshold (0.10→0.20)
- So sánh 2 phương pháp: bbox proxy vs FastSAM (nếu có Phase 6 thì thêm end-to-end)
- Đóng gói app thành .exe bằng PyInstaller

**Success Criteria:**
1. Tất cả unit tests + integration tests pass
2. Inference benchmark có số liệu cụ thể
3. PCI engine verify đúng với test cases từ tài liệu chuyên môn
4. Bảng so sánh ít nhất 2 phương pháp (bbox vs mask)

---

### Phase 7b: Thesis Documentation — Có thể dùng kết quả T3 nếu có
**Status:** pending
**Goal:** Viết thuyết minh, chuẩn bị bảo vệ
**Requirements:** DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DOC-06
**Depends on:** Phase 7a
**Est. Time:** 2 tuần

- Viết quyển thuyết minh đồ án (3 chương) theo format chuẩn trường (A4, TNR 13, 3 chương)
- So sánh ASTM D6433 với tiêu chuẩn Trung Quốc, Vizir, CIsurf — Chương 1 tổng quan
- Đảm bảo 3 sản phẩm bắt buộc: source code + app + báo cáo PDF
- Tạo slide bảo vệ (PowerPoint)
- Quay video demo hoàn chỉnh
- README + hướng dẫn cài đặt

**Success Criteria:**
1. Thuyết minh hoàn chỉnh 3 chương
2. Slide + video demo sẵn sàng cho bảo vệ
3. Nếu có kết quả Phase 6 → bổ sung bảng so sánh 3 phương pháp vào thuyết minh
