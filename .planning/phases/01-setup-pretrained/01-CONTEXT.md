# Phase 1: Setup & Pretrained Model Integration - Context

**Gathered:** 2026-05-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Thiết lập môi trường phát triển Python, dọn dẹp code cũ, tải pretrained YOLOv12s từ HuggingFace, export ONNX, build detector module với ONNX Runtime + DirectML, test inference trên ảnh mẫu, setup logging framework, tuyển chọn ảnh demo.

</domain>

<decisions>
## Implementation Decisions

### Code Cleanup (INF-04)
- **D-01:** Dọn dẹp triệt để — xóa `notebooks/01_prepare_dataset.ipynb` (Colab crash, không dùng cho strategy pretrained)
- **D-02:** Xóa toàn bộ `src/` stubs hiện tại (engine/, ui/, utils/ — chỉ chứa __init__.py trống)
- **D-03:** Tạo cấu trúc src/ mới theo module chức năng: `src/engine/` (detector.py, pci.py), `src/utils/` (config.py, logging_setup.py, io.py), `src/ui/` (main_window.py, widgets/)
- **D-04:** Dọn dẹp TRƯỚC khi implement — task đầu tiên của Phase 1, đảm bảo môi trường sạch
- **D-05:** Update requirements.txt: bỏ `torch` (không cần cho ONNX Runtime inference), pin versions cụ thể

### Model Download (DET-08)
- **D-06:** Claude's discretion — chọn cơ chế tải model tối ưu (ultralytics built-in vs huggingface_hub script)

### ONNX Export Strategy (DET-02)
- **D-07:** Claude's discretion — export .pt→ONNX tại setup time hay ship pre-exported

### DirectML Fallback (DET-03)
- **D-08:** Claude's discretion — fallback behavior khi DirectML không khả dụng

### Demo Images (INF-03)
- **D-09:** Claude's discretion — tuyển chọn ảnh demo phù hợp cho testing

### Logging Framework (INF-01)
- **D-10:** Claude's discretion — thiết kế logging framework phù hợp

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Planning
- `.planning/PROJECT.md` — Project overview, 3-tier architecture, PCI error history, constraints
- `.planning/REQUIREMENTS.md` — 61 requirements including DET-01~08, INF-01~06
- `.planning/ROADMAP.md` — Phase 1 details with requirements mapping and success criteria
- `.planning/STATE.md` — Tech stack, hardware profile, model sources, timeline

### PCI Data
- `data/pci_astm_d6433.json` — Deduct value curves, CDV correction, severity assignment, rating scale, survey_procedure, maintenance_recommendation

### Model Sources
- HuggingFace: `SreekarAditya/yolo-rdd2022-benchmark` (yolo12s_seed0_best.pt)
- HuggingFace: `rezzzq/yolo12s-road-damage-rdd2022` (alternative, with usage instructions)

### Supplementary Proposals
- `docs/DE_XUAT_BO_SUNG.md` — 36 đề xuất bổ sung, nguồn tham chiếu cho requirements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None — src/ chỉ chứa __init__.py trống (2 dòng comment). Không có code tái sử dụng.

### Established Patterns
- Package structure: `src/engine/`, `src/ui/`, `src/utils/` — giữ nguyên tên thư mục nhưng tạo module files mới
- `data/pci_astm_d6433.json` — JSON data file đã có, Phase 2 sẽ đọc từ đây

### Integration Points
- `data/samples/` — hiện trống (.gitkeep), cần tuyển chọn ảnh demo
- `requirements.txt` — cần update (bỏ torch, pin versions)
- `outputs/` — hiện trống, cần tạo cấu trúc con (INF-06, Phase 3)

</code_context>

<specifics>
## Specific Ideas

- Notebook cũ `01_prepare_dataset.ipynb` crash ở Japan (Cell 4, 43% progress) — không hoàn thành, không dùng được
- `requirements.txt` hiện có `torch>=2.0.0` — không cần cho ONNX Runtime inference, nên bỏ để giảm cài đặt từ ~2GB xuống ~200MB
- YOLOv12s model: 18.9MB, mAP50=0.632, confidence threshold optimal 0.15
- Hardware: Dell Latitude 3540, i5-4300U, Intel HD 4400 (DirectML), 12GB RAM

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 01-setup-pretrained*
*Context gathered: 2026-05-21*
