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
4. **PCI:** ASTM D6433 standard (deduct value curves, CDV) — thay cho exponential decay tự chế
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
PCI:        ASTM D6433 (deduct value curves, CDV)
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

## Session Continuity
- Last action: Rewrote PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md (strategy pivot)
- Ready to: Execute Phase 1 (Setup & Pretrained Model Integration)
