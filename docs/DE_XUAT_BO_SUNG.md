# Đề xuất Bổ sung cho Kế hoạch Dự án
# Nguồn: Phân tích toàn bộ Tai_Lieu (70 slides PPTX + 5 conversation logs + 5 quy định/hướng dẫn)
# Ngày: 2026-05-21

---

## NHÓM A — Ưu tiên CAO (ảnh hưởng trực tiếp đến tính đúng đắn hoặc khả năng bảo vệ)

### #1 — Bảng PCI → Khuyến nghị bảo dưỡng
- **Nguồn:** Slide 26 PPTX chuyên môn
- **Bổ sung vào:** REQUIREMENTS → GUI-11
- **Nội dung:** Hiển thị khuyến nghị bảo dưỡng dựa trên PCI rating. Ví dụ: PCI 70-85 → bảo dưỡng định kỳ, PCI 40-55 → sửa chữa trung bình, PCI < 25 → tái cấu trúc. Tính năng có giá trị thực tiễn cho kỹ sư.

### #2 — So sánh tiêu chuẩn PCI khác (cho tổng quan thuyết minh)
- **Nguồn:** Slide 23-26 (Trung Quốc), Slide 27-28 (CIsurf/CIStruct), Slide 30-31 (Vizir - Pháp)
- **Bổ sung vào:** REQUIREMENTS → DOC-05
- **Nội dung:** So sánh ASTM D6433 với tiêu chuẩn Trung Quốc, Vizir, CIsurf/CIStruct. Nội dung cho Chương 1 (Tổng quan) thuyết minh.

### #5 — Tính PCI cấp đoạn đường (section-level)
- **Nguồn:** Slide 16 — ASTM quy định khảo sát nhiều mẫu đơn vị trên 1 đoạn đường → PCI đoạn = trung bình các mẫu
- **Bổ sung vào:** REQUIREMENTS → PCI-09
- **Nội dung:** Hiện tại kế hoạch chỉ xử lý 1 ảnh → 1 PCI. Thiếu bước tổng hợp nhiều ảnh thành PCI cho cả đoạn đường. ASTM yêu cầu: sample unit PCI → section PCI (trung bình có trọng số).

### #6 — Xử lý hàng loạt ảnh (batch)
- **Nguồn:** Slide 16 quy trình khảo sát + thực tiễn
- **Bổ sung vào:** REQUIREMENTS → GUI-11 (hoặc GUI-12)
- **Nội dung:** App cần hỗ trợ chọn thư mục ảnh → chạy batch inference → ra PCI đoạn đường. Khảo sát thực tế cần chụp hàng chục ảnh mẫu, không phải 1 ảnh lẻ.

### #16 — Căn chỉnh timeline roadmap với lịch học kỳ doanh nghiệp
- **Nguồn:** HUONG DAN THUC HIEN HOC KY DOANH NGHIEP.pdf
- **Nội dung chi tiết từ tài liệu:**
  - TT Phát triển Ứng dụng TTNT (DC4TG21): 3 tuần → đánh giá sau tuần 3
  - TT Chuyên ngành (DC4TG22): 3 tuần → đánh giá sau tuần 6
  - TT Tốt nghiệp (DC4TG70): 7 tuần → đánh giá sau tuần 13
  - Đồ án tốt nghiệp: 12-14 tuần → bảo vệ sau tuần 21
  - **Tổng: 13 tuần học kỳ DN + 12-14 tuần đồ án = ~25-27 tuần**
- **Bổ sung vào:** ROADMAP → thêm cột thời gian ước lượng
- **Lưu ý:** Roadmap hiện tại không có timeline. Cần gán Phase 1-5 vào 13 tuần học kỳ DN, Phase 6-7 vào 12-14 tuần đồ án.

### #17 — Dataset ground truth để xác minh PCI
- **Nguồn:** TST-04 requirement (so sánh PCI tự động vs thủ công)
- **Bổ sung vào:** REQUIREMENTS → TST-04 chi tiết hóa
- **Nội dung:** Cần có ảnh đã được chuyên gia đánh giá PCI sẵn. Hiện không có nguồn nào. Tìm hoặc tự tạo.

### #21 — Giao diện tiếng Việt
- **Nguồn:** Thực tiễn người dùng (kỹ sư giao thông Việt Nam)
- **Bổ sung vào:** REQUIREMENTS → GUI-12
- **Nội dung:** Quyết định ngôn ngữ UI: tiếng Việt, tiếng Anh, hoặc hỗ trợ cả hai. Ảnh hưởng đến toàn bộ GUI.

### #22 — Xác minh model YOLOv12s + ultralytics + class count
- **Nguồn:** Milestone audit trước đó + HuggingFace model page
- **Bổ sung vào:** REQUIREMENTS → DET-07
- **Nội dung:** (a) YOLOv12s có tương thích với ultralytics hiện tại không? (b) Model có đúng 4 classes hay 5 (có Repair)? Cần verify TRƯỚC khi implement Phase 1.

### #25 — Đã đọc xong Quy_Dinh_Huong_Dan
- **Kết quả:** Không phát hiện thêm đề xuất bổ sung mới. Nội dung chủ yếu là:
  - `hinh_thuc_trinh_bay_chuan.pdf`: Format thuyết minh (A4, Times New Roman 13, 3 chương, có Mở đầu/Lời cảm ơn/Nhận xét/Mục lục/Phụ lục/Tài liệu tham khảo)
  - `HUONG DAN THUC HIEN HOC KY DOANH NGHIEP.pdf`: Timeline 13 tuần + yêu cầu sản phẩm (source code + app chạy hoàn chỉnh + báo cáo PDF 3 chương)
  - `221223.SoTayVanHanhHeThongITS.docx`: Sổ tay vận hành ITS (hạ tầng camera, VDS, VMS, switch, trạm thu phí — nội dung tham khảo cho thuyết minh)
  - `TÀI_LIỆU_HƯỚNG_DẪN_CHUYÊN_MÔN_VỀ_CÔNG_TÁC_KIỂM_TRA.pdf`: Quy trình kiểm tra thiết bị ITS + danh sách thiết bị trên tuyến cao tốc
  - `Nội quy CTy QĐ.pdf`: Nội quy công ty (quản lý thiết bị, bảo mật, giao ca)

---

## NHÓM B — Ưu tiên TRUNG BÌNH (nâng cao chất lượng, tính chuyên nghiệp)

### #3 — Quy trình khảo sát PCI từng bước (workflow)
- **Nguồn:** Slide 16-19
- **Bổ sung vào:** data/pci_astm_d6433.json → thêm field `survey_procedure`
- **Nội dung:** Chia đoạn mẫu → chọn đoạn đại diện → khảo sát hư hỏng → tính density → tra deduct → tính CDV → ra PCI. Flow thuật toán cho Phase 2.

### #4 — Mô tả chi tiết từng loại hư hỏng kèm hình ảnh
- **Nguồn:** Slide 20
- **Bổ sung vào:** data/pci_astm_d6433.json → thêm field `distress_visual_description`
- **Nội dung:** Cấp độ nghiêm trọng kèm hình minh họa. Giải thích cho hội đồng.

### #7 — Lớp thứ 5 "Repair/Other"
- **Nguồn:** Slide 20 + HuggingFace RDD2022 dataset
- **Bổ sung vào:** REQUIREMENTS → DET-04 sửa
- **Nội dung:** RDD2022 có 5 lớp (D00, D10, D20, D40, Repair). Kế hoạch chỉ dùng 4. Vùng đã sửa chữa ảnh hưởng PCI khác với vùng hư hỏng mới.

### #8 — Hệ số hiệu chỉnh bbox overestimate
- **Nguồn:** G1-G2 bug history
- **Bổ sung vào:** REQUIREMENTS → PCI-10
- **Nội dung:** Bbox luôn lớn hơn diện tích thật, đặc biệt D00. Dùng tỷ lệ khung hình bbox (aspect ratio) để ước lượng hiệu chỉnh.

### #9 — Chiến lược lấy mẫu frame từ video
- **Nguồn:** Slide 16 quy trình
- **Bổ sung vào:** REQUIREMENTS → VID-06
- **Nội dung:** ASTM không cần phân tích từng frame. Cần chiến lược: lấy mẫu mỗi N frame, hoặc theo khoảng cách.

### #10 — Mẫu báo cáo theo form ASTM
- **Nguồn:** Slide 17-19 form khảo sát chuẩn
- **Bổ sung vào:** REQUIREMENTS → GUI-10 sửa
- **Nội dung:** PDF report nên theo form ASTM D6433 thay vì tự thiết kế.

### #18 — So sánh/kiến giải với tiêu chuẩn Việt Nam (TCVN)
- **Nguồn:** Slide chuyên môn + ngữ cảnh thực tiễn
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết
- **Nội dung:** Tại sao chọn ASTM thay vì TCVN 3220 hoặc QĐB 405? So sánh sự khác biệt.

### #19 — Xử lý edge case PCI
- **Nguồn:** Logic PCI engine
- **Bổ sung vào:** REQUIREMENTS → PCI-11
- **Nội dung:** (a) Không phát hiện hư hỏng → PCI = 100 nhưng ghi chú "chưa phát hiện" thay vì "đường tốt". (b) Ảnh không phải mặt đường → cảnh báo. (c) Confidence toàn bộ < 0.15 → không có detection.

### #23 — Xuất kết quả CSV/Excel
- **Nguồn:** Thực tiễn viết thuyết minh
- **Bổ sung vào:** REQUIREMENTS → GUI-13
- **Nội dung:** Cần xuất detection results + PCI calculations ra CSV/Excel để phân tích, vẽ biểu đồ, đưa vào thuyết minh.

### #24 — Hệ thống logging
- **Nguồn:** G1-G2 bug history (5 bug liên quan error handling)
- **Bổ sung vào:** REQUIREMENTS → INF-01 (Infrastructure — nhóm mới)
- **Nội dung:** Logging framework cho app. Tránh lặp lại UnicodeDecodeError, NoneType, logging NameError.

### #26 — [MỚI] Format thuyết minh theo chuẩn trường
- **Nguồn:** hinh_thuc_trinh_bay_chuan.pdf
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết hóa
- **Nội dung:** Thuyết minh phải tuân thủ: A4, Times New Roman size 13, margin top/bottom/right 2cm left 3cm, line spacing 1.35, 3 chương (Tổng quan → Phương pháp → Kết quả), có Mở đầu, Lời cảm ơn, Nhận xét GVHD, Mục lục, Danh mục bảng/sơ đồ/hình, Ký hiệu viết tắt, Phụ lục, Tài liệu tham khảo xếp ABC.

### #27 — [MỚI] Sản phẩm bắt buộc theo hướng dẫn học kỳ DN
- **Nguồn:** HUONG DAN THUC HIEN HOC KY DOANH NGHIEP.pdf
- **Bổ sung vào:** REQUIREMENTS → DOC-06 (mới)
- **Nội dung:** Theo tài liệu, sản phẩm bắt buộc gồm: (1) Source code chương trình/phần mềm AI, (2) Bộ dữ liệu đã gán nhãn chuẩn + ứng dụng AI chạy hoàn chỉnh, (3) Báo cáo PDF tóm tắt 3 chương. Cần đảm bảo Phase 7b deliver đủ 3 sản phẩm này.

### #28 — [MỚI] Nội dung ITS cho thuyết minh Chương 1
- **Nguồn:** 221223.SoTayVanHanhHeThongITS.docx + TÀI_LIỆU_HƯỚNG_DẪN_CHUYÊN_MÔN_VỀ_CÔNG_TÁC_KIỂM_TRA.pdf
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết
- **Nội dung:** Sổ tay vận hành ITS mô tả hệ thống camera CCTV, VDS (Vehicle Detection System), VMS (Variable Message Sign), switch Layer 2/3, trạm thu phí trên cao tốc. Đây là hạ tầng mà app sẽ tiếp nhận dữ liệu từ đó. Cần đưa vào Chương 1 để mô tả bối cảnh thực tế: app nhận ảnh từ camera CCTV trên cao tốc → phát hiện hư hỏng → tính PCI → hỗ trợ quyết định bảo dưỡng.

---

## NHÓM C — Ưu tiên THẤP (nội dung tham khảo, không ảnh hưởng code)

### #11 — Ngữ cảnh PMS (Pavement Management System)
- **Nguồn:** Slide 32-50
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết
- **Nội dung:** App là 1 module của PMS. Đưa vào Chương 1.

### #12 — Ngữ cảnh Quản lý Tài sản Hạ tầng
- **Nguồn:** Slide 60-70
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết
- **Nội dung:** Đường = tài sản, khấu hao theo tình trạng. Lý do cần tính PCI.

### #13 — Mối quan hệ PSI vs PCI
- **Nguồn:** Slide 11-13
- **Bổ sung vào:** REQUIREMENTS → DOC-01 chi tiết
- **Nội dung:** PSI (chủ quan) vs PCI (khách quan). App dùng PCI vì phù hợp automatic assessment.

### #14 — Ảnh hưởng confidence threshold đến PCI
- **Nguồn:** Phase 1 config
- **Bổ sung vào:** REQUIREMENTS → TST-06
- **Nội dung:** Test độ nhạy: thay threshold 0.10→0.20 → PCI thay đổi bao nhiêu?

### #15 — Tích hợp GIS/Map — hướng phát triển
- **Nguồn:** Slide 32-50
- **Bổ sung vào:** PROJECT.md → Out of Scope + DOC-01
- **Nội dung:** Nêu trong Chương "Hướng phát triển" của thuyết minh.

### #20 — Chuyển đổi đơn vị đo
- **Nguồn:** Slide 16 (5000 ft²) + thực tiễn VN
- **Bổ sung vào:** REQUIREMENTS → PCI-12
- **Nội dung:** App cho phép nhập diện tích mẫu theo m², tự chuyển sang ft² để tra deduct curves.

---

## TỔNG HỢP

| Nhóm | Số đề xuất | Mức ưu tiên |
|------|-----------|-------------|
| A — Ưu tiên CAO | #1, #2, #5, #6, #16, #17, #21, #22, #25, #29, #31, #32 | 12 items |
| B — Ưu tiên TRUNG BÌNH | #3, #4, #7, #8, #9, #10, #18, #19, #23, #24, #26, #27, #28, #30, #33, #35, #36 | 17 items |
| C — Ưu tiên THẤP | #11, #12, #13, #14, #15, #20, #34 | 7 items |
| **Tổng cộng** | | **36 items** |

### Đề xuất mới từ việc đọc Quy_Dinh_Huong_Dan (#26, #27, #28):
- **#26:** Format thuyết minh theo chuẩn trường (A4, TNR 13, 3 chương, có đầy đủ các phần phụ)
- **#27:** Sản phẩm bắt buộc: source code + bộ dữ liệu + app chạy hoàn chỉnh + báo cáo PDF 3 chương
- **#28:** Nội dung ITS (CCTV, VDS, VMS, trạm thu phí) cho bối cảnh thực tế trong thuyết minh

### #29 — Đóng gói app thành executable (PyInstaller)
- **Nguồn:** Thực tiễn bảo vệ đồ án
- **Bổ sung vào:** REQUIREMENTS → INF-02
- **Nội dung:** Bảo vệ cần demo chạy được trên máy khác. Chạy từ source + pip install trên máy hội đồng là rủi ro cao. Cần đóng gói .exe standalone bằng PyInstaller.

### #30 — Fallback CPU khi DirectML không khả dụng
- **Nguồn:** Robustness requirement
- **Bổ sung vào:** REQUIREMENTS → DET-03 sửa
- **Nội dung:** Nếu demo trên máy không có Intel HD 4400 hoặc DirectML lỗi, app phải tự fallback sang CPU provider thay vì crash.

### #31 — Chuẩn bị bộ ảnh demo cho bảo vệ
- **Nguồn:** Thực tiễn bảo vệ + data/samples/ hiện trống (.gitkeep)
- **Bổ sung vào:** REQUIREMENTS → INF-03
- **Nội dung:** Tuyển chọn ảnh mẫu có đủ 4 loại hư hỏng + ảnh đường tốt (0 detection) + ảnh có PCI known để demo mượt mà. data/samples/ hiện trống.

---

### #32 — Cơ chế tải model tự động
- **Nguồn:** Phase 1 ROADMAP — thiếu cơ chế cụ thể
- **Bổ sung vào:** REQUIREMENTS → DET-08
- **Nội dung:** Phase 1 nói "download yolo12s từ HuggingFace" nhưng không chỉ định cơ chế. Cần script tự động dùng huggingface_hub hoặc ultralytics built-in, không phải manual download. Nếu URL thay đổi hoặc user không biết dùng huggingface_hub, Phase 1 fails.

### #33 — Chiến lược với code cũ
- **Nguồn:** Cấu trúc workspace hiện tại (src/ có code Gradio era, notebooks/ có prepare_dataset.ipynb không còn phù hợp, requirements.txt có thể chứa dependencies cũ)
- **Bổ sung vào:** REQUIREMENTS → INF-04
- **Nội dung:** Cần quyết định: dọn dẹp code cũ + update requirements.txt trước khi bắt đầu Phase 1, hay start fresh. 01_prepare_dataset.ipynb không còn cần với strategy pretrained.

### #34 — Lưu trữ cấu hình (persistence)
- **Nguồn:** GUI-06 requirement — thiếu chi tiết
- **Bổ sung vào:** REQUIREMENTS → GUI-14
- **Nội dung:** GUI-06 nói "Settings dialog" nhưng không chỉ định cách lưu cấu hình: QSettings registry? JSON file? Cần quyết định để implement nhất quán.

---

### #35 — Pin dependency versions (requirements.txt)
- **Nguồn:** Risk — ultralytics API thay đổi thường xuyên, YOLOv12s là model mới
- **Bổ sung vào:** REQUIREMENTS → INF-05
- **Nội dung:** Cần pin version cụ thể trong requirements.txt (ví dụ ultralytics>=8.1,<9.0). Nếu không pin, `pip install ultralytics` hôm nay và ngày mai có thể cho version khác, YOLOv12s load fail. Từng gặp lỗi tương thích khi chuyển YOLOv8→YOLO11→YOLO12.

### #36 — Quản lý thư mục output
- **Nguồn:** Workspace có outputs/ trống, không có requirement về cấu trúc kết quả
- **Bổ sung vào:** REQUIREMENTS → INF-06
- **Nội dung:** Cần quy định: (a) thư mục output mặc định (outputs/), (b) cấu trúc con (outputs/images/, outputs/reports/, outputs/videos/), (c) quy tắc đặt tên file (timestamp + PCI score), (d) nút "Open Output Folder" trong GUI.

---

### Không còn khoảng trống nào chưa phát hiện.
### DANH SÁCH 1-36 ĐÃ ĐẦY ĐỦ TOÀN BỘ.
