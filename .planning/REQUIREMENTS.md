# Requirements: Hệ thống Đánh giá Hư hỏng Mặt đường

**Defined:** 2026-05-21
**Core Value:** Phát hiện hư hỏng chính xác + tính PCI chuẩn ASTM D6433

## V1 Requirements (MVP — T1: Detection + Bbox Proxy)

### Detection & Classification

- [ ] **DET-01**: Load pretrained YOLOv12s model (yolo12s_seed0_best.pt) từ HuggingFace
- [ ] **DET-02**: Export .pt → ONNX format cho ONNX Runtime inference
- [ ] **DET-03**: Inference ONNX Runtime + DirectML (Intel HD 4400) trên ảnh tĩnh
- [ ] **DET-04**: Phát hiện 4 lớp hư hỏng: D00 (longitudinal), D10 (transverse), D20 (alligator), D40 (pothole). Xử lý lớp Repair/Other nếu model trả về (không tính vào PCI)
- [ ] **DET-05**: Confidence threshold mặc định 0.15 (theo benchmark recommendation)
- [ ] **DET-06**: Hiển thị bounding boxes + class labels + confidence scores trên ảnh
- [ ] **DET-07**: Verify model trước khi implement: (a) YOLOv12s tương thích ultralytics hiện tại, (b) class count đúng (4 hay 5), (c) ONNX export thành công
- [ ] **DET-08**: Script tự động tải model từ HuggingFace (huggingface_hub hoặc ultralytics built-in), không manual download

### PCI Calculation (Bbox Proxy — T1)

- [ ] **PCI-01**: Tính damage density = bbox area / sample unit area cho từng loại hư hỏng
- [ ] **PCI-02**: Ánh xạ damage density → deduct value theo ASTM D6433 curves (4 loại distress)
- [ ] **PCI-03**: Tính Corrected Deduct Value (CDV) dựa trên số deduct values > 2
- [ ] **PCI-04**: Tính PCI = 100 - CDV cho từng sample unit
- [ ] **PCI-05**: Phân loại PCI rating (Good/Satisfactory/Fair/Poor/Very Poor/Failed)
- [ ] **PCI-06**: Hiển thị bảng tổng hợp: damage count, density, deduct value, PCI theo loại
- [ ] **PCI-07**: Trích xuất deduct value curves từ slide chuyên môn PPTX (Slide 17-22) → data/pci_astm_d6433.json, verify với bản chính thức ASTM D6433-07
- [ ] **PCI-08**: Gán mức độ nghiêm trọng (severity) tự động dựa trên damage density khi chỉ có bounding box (không có segmentation mask)
- [ ] **PCI-09**: Tính PCI cấp đoạn đường (section-level): trung bình có trọng số PCI các sample unit trên cùng đoạn đường
- [ ] **PCI-10**: Hệ số hiệu chỉnh bbox overestimate — dùng aspect ratio của bbox để ước lượng diện tích thật (đặc biệt D00: vết nứt dài+hẹp)
- [ ] **PCI-11**: Xử lý edge case: (a) 0 detection → PCI=100 + ghi chú "chưa phát hiện hư hỏng", (b) ảnh không phải mặt đường → cảnh báo, (c) toàn bộ confidence < threshold
- [ ] **PCI-12**: Hỗ trợ chuyển đổi đơn vị: nhập diện tích mẫu theo m², tự chuyển sang ft² để tra deduct curves, hiển thị kết quả theo cả 2 đơn vị

### Visualization

- [ ] **VIS-01**: Annotate ảnh với bounding boxes, labels, confidence (Supervision)
- [ ] **VIS-02**: Damage summary table (count + area per class)
- [ ] **VIS-03**: PCI gauge/bar chart hiển thị điểm số

### Desktop GUI

- [ ] **GUI-01**: PySide6 main window với Fluent-style QSS theme
- [ ] **GUI-02**: Image viewer widget (zoom, pan, fit-to-window)
- [ ] **GUI-03**: File open dialog (image files: jpg, png, bmp)
- [ ] **GUI-04**: Menu bar, toolbar, status bar cơ bản
- [ ] **GUI-05**: Dark/Light theme toggle
- [ ] **GUI-06**: Settings dialog (model path, confidence threshold, sample unit size)
- [ ] **GUI-11**: Hiển thị khuyến nghị bảo dưỡng dựa trên PCI rating (từ Slide 26 PPTX) + hỗ trợ xử lý hàng loạt ảnh (batch) → ra PCI đoạn đường
- [ ] **GUI-12**: Giao diện tiếng Việt (ngôn ngữ chính), hỗ trợ tiếng Anh (optional)
- [ ] **GUI-13**: Xuất kết quả detection + PCI ra CSV/Excel để phân tích, vẽ biểu đồ, đưa vào thuyết minh
- [ ] **GUI-14**: Lưu trữ cấu hình bằng JSON file (không dùng QSettings registry), nhất quán cross-platform

---

## V2 Requirements (Nâng cấp — T2: + FastSAM Segmentation)

### Segmentation

- [ ] **SEG-01**: Load FastSAM-s model cho instance segmentation
- [ ] **SEG-02**: Bbox-prompted segmentation: crop detected bbox → FastSAM → precise mask
- [ ] **SEG-03**: IoU matching giữa YOLOv12s detections và FastSAM segments
- [ ] **SEG-04**: Tính damage area từ segmentation mask (thay bbox proxy)
- [ ] **SEG-05**: So sánh PCI tính từ bbox proxy vs segmentation mask

### Video Processing

- [ ] **VID-01**: Xử lý video input (mp4, avi)
- [ ] **VID-02**: Frame extraction + batch inference (detection + segmentation)
- [ ] **VID-03**: Export video đã annotate (H.264 via ffmpeg)
- [ ] **VID-04**: Progress bar khi xử lý video
- [ ] **VID-05**: PCI time-series chart cho video (PCI theo frame)
- [ ] **VID-06**: Chiến lược lấy mẫu frame từ video (mỗi N frame hoặc theo khoảng cách) thay vì xử lý tất cả, phù hợp quy trình khảo sát ASTM

### Advanced GUI

- [ ] **GUI-07**: Video player widget với timeline scrubber
- [ ] **GUI-08**: Side-by-side view (original vs annotated)
- [ ] **GUI-09**: Damage heatmap overlay
- [ ] **GUI-10**: Export báo cáo PDF theo form ASTM D6433 (PCI report + annotated images + damage summary)

---

## V3 Requirements (Tối ưu — T3: End-to-End Segmentation)

### Model Training (Colab — Optional)

- [ ] **TRN-01**: Tải Kaggle dataset RDD2022 YOLO CrackScan v2 (đã convert sẵn)
- [ ] **TRN-02**: Train YOLOv12s-seg trên Colab GPU dùng pre-converted dataset
- [ ] **TRN-03**: Đạt mAP50-seg ≥ 0.50 trên val set
- [ ] **TRN-04**: Export best.pt → ONNX (DirectML compatible)
- [ ] **TRN-05**: So sánh 3 phương pháp: bbox proxy vs FastSAM vs end-to-end seg

### Infrastructure

- [ ] **INF-01**: Hệ thống logging framework (tránh lặp lỗi UnicodeDecodeError, NoneType, logging NameError từ G1-G2)
- [ ] **INF-02**: Đóng gói app thành .exe standalone bằng PyInstaller cho demo bảo vệ
- [ ] **INF-03**: Tuyển chọn bộ ảnh demo: đủ 4 loại hư hỏng + ảnh đường tốt + ảnh có PCI known
- [ ] **INF-04**: Dọn dẹp code cũ (Gradio era) + update requirements.txt trước Phase 1
- [ ] **INF-05**: Pin dependency versions trong requirements.txt (ultralytics>=8.1,<9.0, onnxruntime-directml, v.v.)
- [ ] **INF-06**: Quản lý thư mục output: outputs/images/, outputs/reports/, outputs/videos/ + quy tắc đặt tên (timestamp_PCI) + nút "Open Output Folder"

### Testing & Evaluation

- [ ] **TST-01**: Unit tests cho PCI engine (ASTM D6433 logic)
- [ ] **TST-02**: Integration tests cho full pipeline
- [ ] **TST-03**: Benchmark inference speed (CPU vs DirectML)
- [ ] **TST-04**: So sánh PCI tự động vs đánh giá thủ công (sai số ≤ 5 điểm) — cần tìm hoặc tạo bộ ảnh có ground truth PCI từ chuyên gia
- [ ] **TST-05**: Verify PCI engine với test cases từ slide chuyên môn PPTX (Slide 17-22)
- [ ] **TST-06**: Test độ nhạy PCI theo confidence threshold (0.10→0.20), ghi nhận tác động vào thuyết minh

### Thesis Documentation

- [ ] **DOC-01**: Quyển thuyết minh đồ án (3 chương)
- [ ] **DOC-02**: Slide bảo vệ (PowerPoint)
- [ ] **DOC-03**: Video demo hoàn chỉnh
- [ ] **DOC-04**: README + hướng dẫn cài đặt
- [ ] **DOC-05**: So sánh ASTM D6433 với tiêu chuẩn Trung Quốc, Vizir (Pháp), CIsurf/CIStruct — nội dung Chương 1 tổng quan
- [ ] **DOC-06**: Đảm bảo 3 sản phẩm bắt buộc theo hướng dẫn học kỳ DN: (1) source code + app chạy hoàn chỉnh, (2) bộ dữ liệu đã gán nhãn, (3) báo cáo PDF 3 chương

---

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real-time webcam processing | Không phải use case đồ án |
| Mobile app | Ngoài phạm vi |
| Multi-camera support | Quá phức tạp |
| Cloud deployment | Chạy local |
| 3D pavement reconstruction | Quá phức tạp |
| Tự train detection model từ đầu | Dùng pretrained weights |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DET-01 | Phase 1 | Pending |
| DET-02 | Phase 1 | Pending |
| DET-03 | Phase 1 | Pending |
| DET-04 | Phase 1 | Pending |
| DET-05 | Phase 1 | Pending |
| DET-06 | Phase 1 | Pending |
| DET-07 | Phase 1 | Pending |
| DET-08 | Phase 1 | Pending |
| PCI-01 | Phase 2 | Pending |
| PCI-02 | Phase 2 | Pending |
| PCI-03 | Phase 2 | Pending |
| PCI-04 | Phase 2 | Pending |
| PCI-05 | Phase 2 | Pending |
| PCI-06 | Phase 2 | Pending |
| PCI-07 | Phase 2 | Pending |
| PCI-08 | Phase 2 | Pending |
| VIS-01 | Phase 3 | Pending |
| VIS-02 | Phase 3 | Pending |
| VIS-03 | Phase 3 | Pending |
| GUI-01 | Phase 3 | Pending |
| GUI-02 | Phase 3 | Pending |
| GUI-03 | Phase 3 | Pending |
| GUI-04 | Phase 3 | Pending |
| GUI-05 | Phase 3 | Pending |
| GUI-06 | Phase 3 | Pending |
| GUI-11 | Phase 3 | Pending |
| GUI-12 | Phase 3 | Pending |
| GUI-13 | Phase 3 | Pending |
| GUI-14 | Phase 3 | Pending |
| SEG-01 | Phase 4 | Pending |
| SEG-02 | Phase 4 | Pending |
| SEG-03 | Phase 4 | Pending |
| SEG-04 | Phase 4 | Pending |
| SEG-05 | Phase 4 | Pending |
| VID-01 | Phase 5 | Pending |
| VID-02 | Phase 5 | Pending |
| VID-03 | Phase 5 | Pending |
| VID-04 | Phase 5 | Pending |
| VID-05 | Phase 5 | Pending |
| VID-06 | Phase 5 | Pending |
| GUI-07 | Phase 5 | Pending |
| GUI-08 | Phase 5 | Pending |
| GUI-09 | Phase 5 | Pending |
| GUI-10 | Phase 5 | Pending |
| TRN-01 | Phase 6 | Pending |
| TRN-02 | Phase 6 | Pending |
| TRN-03 | Phase 6 | Pending |
| TRN-04 | Phase 6 | Pending |
| TRN-05 | Phase 6 | Pending |
| INF-01 | Phase 1 | Pending |
| INF-02 | Phase 7a | Pending |
| INF-03 | Phase 1 | Pending |
| INF-04 | Phase 1 | Pending |
| INF-05 | Phase 1 | Pending |
| INF-06 | Phase 3 | Pending |
| TST-01 | Phase 7a | Pending |
| TST-02 | Phase 7a | Pending |
| TST-03 | Phase 7a | Pending |
| PCI-09 | Phase 2 | Pending |
| PCI-10 | Phase 2 | Pending |
| PCI-11 | Phase 2 | Pending |
| PCI-12 | Phase 2 | Pending |
| TST-04 | Phase 7a | Pending |
| TST-05 | Phase 7a | Pending |
| TST-06 | Phase 7a | Pending |
| DOC-01 | Phase 7b | Pending |
| DOC-02 | Phase 7b | Pending |
| DOC-03 | Phase 7b | Pending |
| DOC-04 | Phase 7b | Pending |
| DOC-05 | Phase 7b | Pending |
| DOC-06 | Phase 7b | Pending |

**Coverage:**
- v1 requirements: 26 total
- v2 requirements: 13 total
- v3 requirements: 22 total
- Mapped to phases: 61
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-21*
*Last updated: 2026-05-21 after full Tai_Lieu analysis + 36 đề xuất bổ sung*
