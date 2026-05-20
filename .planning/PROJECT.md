# Hệ thống Hỗ trợ Đánh giá Hư hỏng Mặt đường sử dụng Deep Learning

## What This Is

Desktop application hỗ trợ kỹ sư giao thông tự động phát hiện, phân loại hư hỏng mặt đường từ ảnh/video, tính toán chỉ số PCI (Pavement Condition Index) theo chuẩn ASTM D6433, và xuất báo cáo đánh giá. Sử dụng pretrained model YOLOv12s từ benchmark RDD2022 công khai trên HuggingFace — không cần tự train, chạy inference hoàn toàn local.

## Core Value

Phát hiện hư hỏng mặt đường chính xác + tính PCI chuẩn ASTM D6433 — nếu mọi thứ khác thất bại, detection + PCI phải hoạt động.

## Metadata
- **Tên đề tài:** Xây dựng hệ thống hỗ trợ đánh giá hư hỏng mặt đường sử dụng Deep Learning, tích hợp dự đoán chỉ số PCI
- **Loại dự án:** Đồ án tốt nghiệp (ĐH Công nghệ GTVT — Viện CN Đường sắt & GTVT — Trung tâm BIM & AI)
- **Ngày khởi tạo:** 2026-05-18
- **Ngày tái cấu trúc:** 2026-05-21 (chuyển sang pretrained weights)
- **Deadline bảo vệ:** Chưa xác định

## Requirements

### Validated

(NONE — ship to validate)

### Active

- [ ] Phát hiện + phân loại 4 lớp hư hỏng (D00, D10, D20, D40) từ ảnh tĩnh
- [ ] Segmentation vùng hư hỏng để đo diện tích chính xác
- [ ] Tính toán PCI theo chuẩn ASTM D6433 (deduct value curves, CDV)
- [ ] Trực quan hóa kết quả: annotated image, PCI chart, damage summary
- [ ] Xử lý video input, xuất video đã annotate
- [ ] Desktop GUI PySide6 + Fluent Design
- [ ] Xuất báo cáo đánh giá (PDF)
- [ ] Inference hoàn toàn local (ONNX Runtime + DirectML)

### Out of Scope

- Real-time webcam processing — không phải use case đồ án
- Mobile app — ngoài phạm vi
- Cloud deployment — chạy local
- 3D pavement reconstruction — quá phức tạp
- Tự train model từ đầu — dùng pretrained weights

## Context

### Tại sao thay đổi chiến lược
Tiến trình Colab bị gián đoạn do mất mạng. Chạy lại toàn bộ notebook (đặc biệt XML→YOLO conversion) quá tốn thời gian. Tìm thấy pretrained weights YOLOv12s trên HuggingFace (SreekarAditya/yolo-rdd2022-benchmark) — model #1 trên RDD2022 benchmark, mAP50=0.632, không cần tự train.

### Kiến trúc 3 tầng (tăng dần độ chính xác)

**T1 — MVP (bbox proxy):**
- YOLOv12s detection → bounding box → ước lượng diện tích hư hỏng → PCI
- Ưu điểm: nhanh, nhẹ, chạy ngay không cần Colab
- Nhược điểm: bbox overestimate diện tích, đặc biệt với vết nứt dọc (D00)

**T2 — Nâng cấp (+ FastSAM):**
- YOLOv12s detect → FastSAM segment trong từng bbox → mask chính xác → PCI
- Ưu điểm: diện tích chính xác hơn đáng kể
- Nhược điểm: thêm 1 model, chậm hơn một chút

**T3 — Tối ưu (end-to-end seg):**
- Train YOLOv12s-seg trên Colab dùng Kaggle dataset đã convert sẵn (RDD2022 YOLO CrackScan v2)
- Ưu điểm: 1 model duy nhất, detection+seg tích hợp, chính xác nhất
- Nhược điểm: cần Colab (nhưng nhanh hơn nhiều so với trước — dataset đã convert)

### Nguồn model
- **Detection:** `yolo12s_seed0_best.pt` từ SreekarAditya/yolo-rdd2022-benchmark (HuggingFace)
  - YOLOv12s, 18.9MB, mAP50=0.632 (seed 0), Friedman rank #1
  - 4 classes: D00 (longitudinal crack), D10 (transverse crack), D20 (alligator crack), D40 (pothole)
  - Optimal confidence: 0.15 (benchmark recommends 0.10–0.20)
  - License: CC BY 4.0
- **Segmentation (T2):** FastSAM-s (YOLOv8s-seg backbone, bbox-prompted)
- **Segmentation (T3):** YOLOv12s-seg trained on RDD2022 (Kaggle dataset)

## Constraints

- **Hardware:** Dell Latitude 3540, i5-4300U, 12GB RAM, Intel HD 4400 (DirectML)
- **RAM:** Ứng dụng ≤ 300MB khi chạy inference (2 models)
- **Inference:** ≤ 500ms/frame cho detection+segmentation
- **SSD:** Cài đặt ≤ 2GB (models + dependencies)
- **Offline:** Inference chạy local hoàn toàn, không cần internet

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Dùng pretrained YOLOv12s thay vì tự train YOLO11n-seg | Tránh mất thời gian Colab, model tốt hơn (mAP50 0.632 vs target 0.60) | — Pending |
| Kiến trúc 3 tầng (bbox→FastSAM→end-to-end) | MVP nhanh, cải tiến dần, không block | — Pending |
| PCI theo ASTM D6433 | Tiêu chuẩn quốc tế, có thể kiểm chứng, phù hợp đồ án | — Pending |
| Confidence threshold 0.15 | Benchmark chứng minh optimal 0.10–0.20 cho RDD2022 | — Pending |
| ONNX Runtime + DirectML | Tận dụng Intel HD 4400, chạy local, không cần PyTorch cho inference | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-21 after strategy pivot to pretrained weights*
