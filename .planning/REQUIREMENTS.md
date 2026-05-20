# Requirements: Hệ thống Đánh giá Hư hỏng Mặt đường

**Defined:** 2026-05-21
**Core Value:** Phát hiện hư hỏng chính xác + tính PCI chuẩn ASTM D6433

## V1 Requirements (MVP — T1: Detection + Bbox Proxy)

### Detection & Classification

- [ ] **DET-01**: Load pretrained YOLOv12s model (yolo12s_seed0_best.pt) từ HuggingFace
- [ ] **DET-02**: Export .pt → ONNX format cho ONNX Runtime inference
- [ ] **DET-03**: Inference ONNX Runtime + DirectML (Intel HD 4400) trên ảnh tĩnh
- [ ] **DET-04**: Phát hiện 4 lớp hư hỏng: D00 (longitudinal), D10 (transverse), D20 (alligator), D40 (pothole)
- [ ] **DET-05**: Confidence threshold mặc định 0.15 (theo benchmark recommendation)
- [ ] **DET-06**: Hiển thị bounding boxes + class labels + confidence scores trên ảnh

### PCI Calculation (Bbox Proxy — T1)

- [ ] **PCI-01**: Tính damage density = bbox area / sample unit area cho từng loại hư hỏng
- [ ] **PCI-02**: Ánh xạ damage density → deduct value theo ASTM D6433 curves (4 loại distress)
- [ ] **PCI-03**: Tính Corrected Deduct Value (CDV) dựa trên số deduct values > 2
- [ ] **PCI-04**: Tính PCI = 100 - CDV cho từng sample unit
- [ ] **PCI-05**: Phân loại PCI rating (Good/Satisfactory/Fair/Poor/Very Poor/Failed)
- [ ] **PCI-06**: Hiển thị bảng tổng hợp: damage count, density, deduct value, PCI theo loại

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

### Advanced GUI

- [ ] **GUI-07**: Video player widget với timeline scrubber
- [ ] **GUI-08**: Side-by-side view (original vs annotated)
- [ ] **GUI-09**: Damage heatmap overlay
- [ ] **GUI-10**: Export báo cáo PDF (PCI report + annotated images)

---

## V3 Requirements (Tối ưu — T3: End-to-End Segmentation)

### Model Training (Colab — Optional)

- [ ] **TRN-01**: Tải Kaggle dataset RDD2022 YOLO CrackScan v2 (đã convert sẵn)
- [ ] **TRN-02**: Train YOLOv12s-seg trên Colab GPU dùng pre-converted dataset
- [ ] **TRN-03**: Đạt mAP50-seg ≥ 0.50 trên val set
- [ ] **TRN-04**: Export best.pt → ONNX (DirectML compatible)
- [ ] **TRN-05**: So sánh 3 phương pháp: bbox proxy vs FastSAM vs end-to-end seg

### Testing & Evaluation

- [ ] **TST-01**: Unit tests cho PCI engine (ASTM D6433 logic)
- [ ] **TST-02**: Integration tests cho full pipeline
- [ ] **TST-03**: Benchmark inference speed (CPU vs DirectML)
- [ ] **TST-04**: So sánh PCI tự động vs đánh giá thủ công (sai số ≤ 5 điểm)

### Thesis Documentation

- [ ] **DOC-01**: Quyển thuyết minh đồ án (3 chương)
- [ ] **DOC-02**: Slide bảo vệ (PowerPoint)
- [ ] **DOC-03**: Video demo hoàn chỉnh
- [ ] **DOC-04**: README + hướng dẫn cài đặt

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
| PCI-01 | Phase 2 | Pending |
| PCI-02 | Phase 2 | Pending |
| PCI-03 | Phase 2 | Pending |
| PCI-04 | Phase 2 | Pending |
| PCI-05 | Phase 2 | Pending |
| PCI-06 | Phase 2 | Pending |
| VIS-01 | Phase 3 | Pending |
| VIS-02 | Phase 3 | Pending |
| VIS-03 | Phase 3 | Pending |
| GUI-01 | Phase 3 | Pending |
| GUI-02 | Phase 3 | Pending |
| GUI-03 | Phase 3 | Pending |
| GUI-04 | Phase 3 | Pending |
| GUI-05 | Phase 3 | Pending |
| GUI-06 | Phase 3 | Pending |
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
| GUI-07 | Phase 5 | Pending |
| GUI-08 | Phase 5 | Pending |
| GUI-09 | Phase 5 | Pending |
| GUI-10 | Phase 5 | Pending |
| TRN-01 | Phase 6 | Pending |
| TRN-02 | Phase 6 | Pending |
| TRN-03 | Phase 6 | Pending |
| TRN-04 | Phase 6 | Pending |
| TRN-05 | Phase 6 | Pending |
| TST-01 | Phase 7 | Pending |
| TST-02 | Phase 7 | Pending |
| TST-03 | Phase 7 | Pending |
| TST-04 | Phase 7 | Pending |
| DOC-01 | Phase 7 | Pending |
| DOC-02 | Phase 7 | Pending |
| DOC-03 | Phase 7 | Pending |
| DOC-04 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 18 total
- v2 requirements: 10 total
- v3 requirements: 9 total
- Mapped to phases: 37
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-21*
*Last updated: 2026-05-21 after strategy pivot*
