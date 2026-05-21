# Phase 3: Desktop App Core (GUI) — Context

**Phase:** 03
**Status:** Planning
**Date:** 2026-05-21

---

## Phase Boundary

**In scope:**
- PySide6 main window with Fluent Design navigation
- Image viewer widget (zoom, pan, fit-to-window)
- File open dialog (single image + directory batch)
- "Run Detection" action → inference → annotated display
- PCI panel: gauge chart + damage summary table + maintenance recommendation
- Settings dialog (model path, confidence, sample unit area) — JSON persistence
- Dark/Light theme toggle
- CSV/Excel export of detection + PCI results
- Vietnamese UI (primary language)
- Output directory management + "Open Output Folder" button

**Out of scope:**
- Video processing (Phase 5)
- Segmentation mask display (Phase 4)
- PDF report generation (Phase 7b)
- PyInstaller packaging (Phase 7a)
- Model training UI (Phase 6)

---

## Implementation Decisions

### D-01: Fluent Widget Library
- **Decision:** Use `PySide6-Fluent-Widgets` (`qfluentwidgets`) for Fluent Design UI
- **Rationale:** Provides NavigationInterface, FluentWindow, theme toggle, modern widgets out-of-box. Much faster than hand-crafting QSS. Active maintenance, PySide6 support.
- **Package:** `pip install PySide6-Fluent-Widgets`
- **Alternative rejected:** Hand-written QSS — too much effort for thesis timeline

### D-02: Single-Window Layout (No Navigation Sidebar)
- **Decision:** Use a single-window layout with toolbar + central image viewer + right-side PCI panel
- **Rationale:** The app is a single-purpose tool (detect → PCI). Navigation sidebar adds complexity without value. Users want: open image → run detection → see results in one view.
- **Layout:** Toolbar (top) | Image Viewer (left/center) | PCI Panel (right) | Status Bar (bottom)

### D-03: Image Viewer with QGraphicsView
- **Decision:** Use `QGraphicsView` + `QGraphicsPixmapItem` for image display
- **Rationale:** Built-in zoom/pan support via `QGraphicsView.scale()` and drag mode. No need for custom scroll handling.
- **Annotation overlay:** Draw bounding boxes and labels as `QGraphicsRectItem` / `QGraphicsTextItem` on top of pixmap

### D-04: PCI Gauge as Custom Widget
- **Decision:** Custom `PCIGaugeWidget` painted with `QPainter` — semicircular gauge with color bands
- **Rationale:** No ready-made gauge in qfluentwidgets. Custom painting gives full control over ASTM rating colors and Vietnamese labels.
- **Alternative rejected:** QDial/QProgressBar — not visually representative of PCI scale

### D-05: Threading for Inference
- **Decision:** Use `QThread` + signals/slots for detection and PCI calculation
- **Rationale:** Inference takes ~900ms on CPU. Must not freeze GUI. Worker thread emits `detection_finished(PCIResult)` signal.
- **Pattern:** `DetectionWorker(QThread)` → runs `detector.detect()` + `pci_engine.calculate_pci()` → emits result

### D-06: CSV Export (Not Excel)
- **Decision:** Use Python `csv` module for export. No `openpyxl` dependency.
- **Rationale:** CSV opens in Excel anyway. Keeps dependencies minimal. Add optional Excel later if needed.
- **Format:** One row per detection + PCI summary row

### D-07: Vietnamese as Primary UI Language
- **Decision:** All UI labels in Vietnamese. English as optional config setting.
- **Rationale:** Thesis defense in Vietnamese. Enterprise internship deliverable targets Vietnamese road management.
- **Implementation:** String constants in a `strings.py` module, switchable via config `language` key

---

## Canonical References

1. PySide6-Fluent-Widgets: https://github.com/zhiyiYo/PyQt-Fluent-Widgets (PySide6 branch)
2. PySide6 QGraphicsView: https://doc.qt.io/qt-6/qgraphicsview.html
3. ASTM D6433 PCI data: `data/pci_astm_d6433.json`
4. Config: `config/default.json`

---

## Existing Code Insights

- `src/engine/detector.py` — `RoadDamageDetector.detect()` returns `DetectionResult` with `pci_detections`, `image_shape`, `inference_time_ms`
- `src/engine/pci.py` — `PCIEngine.calculate_pci()` returns `PCIResult` with `pci_value`, `rating`, `cdv`, `damages`, `pci_color`, `maintenance_action`
- `src/utils/config.py` — `load_config()` / `save_config()` for JSON persistence
- `src/utils/logging_setup.py` — `get_logger()` with rotating file handler
- `config/default.json` — Has `model_path`, `confidence`, `device`, `sample_unit_area_sqft`, `pci_data_path`, `output_dir`, `language`
- Integration pattern: `DetectionResult.pci_detections` → list of dicts with `code`, `bbox`, `confidence` → `PCIEngine.calculate_pci()`

---

## Deferred Ideas

1. **Batch processing progress bar** — Show per-image progress in batch mode (Phase 3 stretch goal)
2. **Side-by-side original vs annotated** — GUI-08 requirement (Phase 4+)
3. **Damage heatmap overlay** — GUI-09 requirement (Phase 4+)
4. **PDF report export** — GUI-10 requirement (Phase 7b)
5. **Drag-and-drop image loading** — Nice-to-have, not in requirements
