# STATE.md — Project Memory

## Current State
- **Date:** 2026-05-21
- **Phase:** Phase 1 — Setup & Pretrained Model Integration (next)
- **Milestone:** V1.0 — MVP Detection + PCI (T1)
- **Next:** Execute Phase 1

## Key Decisions
1. **Detection:** YOLOv12s pretrained (yolo12s_seed0_best.pt) — mAP50=0.632, #1 on RDD2022 benchmark
2. **Segmentation (T2):** FastSAM-s — bbox-prompted, không cần train
3. **Segmentation (T3):** YOLOv12s-seg — train trên Colab dùng Kaggle dataset đã convert
4. **PCI:** ASTM D6433 standard (deduct value curves, CDV) — deduct value curves đã trích xuất từ slide chuyên môn PPTX (Slide 17-22) → data/pci_astm_d6433.json
5. **GUI:** PySide6 + QSS Fluent-style (giữ nguyên)
6. **Inference:** ONNX Runtime + DirectML (Intel HD 4400) — giữ nguyên
7. **Visualization:** Supervision (Roboflow) — giữ nguyên
8. **Confidence threshold:** 0.15 (benchmark recommends 0.10–0.20)

## Tech Stack
```
GUI:        PySide6 + QSS Fluent theme
Detection:  YOLOv12s (pretrained, HuggingFace)
Segmentation(T2): FastSAM-s
Segmentation(T3): YOLOv12s-seg (Colab trained)
Inference:  ONNX Runtime + DirectML (Intel HD 4400)
Vis:        Supervision (roboflow)
Video:      OpenCV + ffmpeg (H.264)
PCI:        ASTM D6433 (deduct value curves từ PPTX chuyên môn, CDV)
PCI Data:   data/pci_astm_d6433.json (deduct curves + CDV correction + severity assignment)
Dataset:    RDD2022 (47,420 images) — pretrained, không cần tải về local
```

## Hardware Profile
- Dell Latitude 3540
- Intel Core i5-4300U @ 1.90GHz (2C/4T)
- 12GB RAM
- Intel HD Graphics 4400 (DirectML capable)
- Windows 11 Pro 64-bit

## Model Sources
- **Detection weights:** https://huggingface.co/SreekarAditya/yolo-rdd2022-benchmark/blob/main/yolo-rdd2022-benchmark/yolo12s_seed0_best.pt
- **FastSAM weights:** TBD (Phase 4)
- **Kaggle dataset (T3):** https://www.kaggle.com/datasets/sreekaraditya/rdd2022-yolo-crackscan-v2

## PCI Data Source
- **Deduct value curves:** Trích xuất từ Tai_Lieu/Chuyen_Mon/Quan ly bao duong mat duong - Cac chi tieu danh gia (Slide 17-22)
- **CDV correction curves:** Từ cùng PPTX (Slide 21-22) + tham chiếu ASTM D6433-07
- **Data file:** data/pci_astm_d6433.json — chứa deduct curves, CDV correction, severity assignment, PCI rating scale, survey_procedure (9 bước ASTM), maintenance_recommendation (6 mức)
- **Status:** Đã số hóa, cần verify với bản chính thức ASTM D6433-07 trước khi dùng cho đồ án

## Requirements Update (36 đề xuất bổ sung)
- **Total requirements:** 61 (từ 40 ban đầu)
- **New groups:** Infrastructure (INF-01~06), PCI-09~12, DET-07~08, GUI-11~14, VID-06, TST-06, DOC-05~06
- **Source:** docs/DE_XUAT_BO_SUNG.md — phân tích toàn bộ Tai_Lieu (70 slides + 5 conversation logs + 5 quy định/hướng dẫn)
- **Key additions:** Section-level PCI, batch processing, Vietnamese UI, PyInstaller packaging, model verification, dependency pinning, output directory management

## Timeline (Học kỳ Doanh nghiệp)
- TT Phát triển Ứng dụng TTNT (DC4TG21): 3 tuần → đánh giá tuần 3
- TT Chuyên ngành (DC4TG22): 3 tuần → đánh giá tuần 6
- TT Tốt nghiệp (DC4TG70): 7 tuần → đánh giá tuần 13
- Đồ án tốt nghiệp: 12-14 tuần → bảo vệ tuần 21+
- **Phase 1-5:** fit vào 13 tuần học kỳ DN (1.5 + 1.5 + 2 + 2 + 2 = 9 tuần, dư 4 tuần buffer)
- **Phase 6:** optional, không block Phase 7
- **Phase 7a+7b:** 4 tuần (2+2), fit vào đồ án tốt nghiệp

## Session Continuity
- Last action: Bổ sung 36 đề xuất bổ sung vào REQUIREMENTS.md (61 requirements), ROADMAP.md (timeline + chi tiết), data file (survey_procedure + maintenance_recommendation)
- Ready to: Execute Phase 1 (Setup & Pretrained Model Integration)
- Key insight: PCI đã sai 3 lần liên tiếp (G1-G2) do tự chế công thức. Slide chuyên môn CÓ SẴN bảng deduct value curves từ đầu. Phase 2 phải hoàn thiện TRƯỚC Phase 3.
- Planning docs fully updated: REQUIREMENTS.md (v2), ROADMAP.md (v2.1 + timeline), STATE.md, PROJECT.md, data/pci_astm_d6433.json
