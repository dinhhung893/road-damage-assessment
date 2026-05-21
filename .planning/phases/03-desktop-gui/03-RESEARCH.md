# Phase 3: Desktop App Core (GUI) — Research

**Phase:** 03
**Date:** 2026-05-21

---

## R-01: PySide6-Fluent-Widgets Library

**Package:** `PySide6-Fluent-Widgets` (pip install, provides `qfluentwidgets`)
**Key classes:**
- `FluentWindow` — Main window with built-in navigation sidebar
- `setTheme(Theme.DARK/LIGHT)` — Global theme toggle
- `FluentIcon` — Icon set for toolbar/navigation
- `PushButton`, `CardWidget`, `InfoBar` — Modern widget set
- `ThemeListener` — Auto-detect system theme changes

**Verdict:** Use for theme management and modern widget styling. BUT — avoid `FluentWindow` navigation sidebar (D-02: single-window layout). Use `QMainWindow` directly + `qfluentwidgets` for individual widgets and theme.

---

## R-02: QGraphicsView for Image Display

`QGraphicsView` + `QGraphicsScene` is the standard Qt pattern for image display with zoom/pan.

**Key methods:**
- `QGraphicsView.scale(zoom, zoom)` — Zoom in/out
- `QGraphicsView.setDragMode(ScrollHandDrag)` — Pan with mouse
- `QGraphicsView.fitInView()` — Fit image to window
- `QGraphicsPixmapItem` — Display image
- `QGraphicsRectItem` / `QGraphicsSimpleTextItem` — Overlay annotations

**Zoom implementation:**
- Override `wheelEvent()` → `self.scale(1.1, 1.1)` or `self.scale(0.9, 0.9)`
- Track zoom level to prevent over-zoom

**Annotation approach:**
- After detection, add rect items + text items to scene
- Store annotation items in list for removal when new image loaded
- Color-code by damage class: D00=red, D10=orange, D20=yellow, D40=purple

---

## R-03: QThread for Non-Blocking Inference

Detection takes ~900ms on CPU. Must run in background thread.

**Pattern:**
```python
class DetectionWorker(QThread):
    finished = Signal(PCIResult, DetectionResult, QImage)

    def __init__(self, detector, pci_engine, image_path):
        super().__init__()
        self.detector = detector
        self.pci_engine = pci_engine
        self.image_path = image_path

    def run(self):
        det_result = self.detector.detect(self.image_path)
        pci_input = [...]
        pci_result = self.pci_engine.calculate_pci(pci_input, ...)
        self.finished.emit(pci_result, det_result, image)
```

**Key:** Worker owns detector/PCI engine instances (thread safety). Main thread receives results via signal.

---

## R-04: PCI Gauge Widget Design

Custom `QWidget` subclass using `QPainter`:

**Visual design:**
- Semicircular gauge (180° arc)
- Color bands matching ASTM rating: Good(green), Satisfactory(dark green), Fair(yellow), Poor(orange), Very Poor(red), Failed(dark red)
- Needle pointing to PCI value
- Digital readout below needle
- Rating text + maintenance recommendation below gauge

**Implementation:**
- Override `paintEvent()` with `QPainter`
- Draw arc segments with `QPainter.drawArc()` or `QPainterPath`
- Draw needle with `QPainter.drawLine()` + rotation transform
- Size: ~200×120 px, scalable

---

## R-05: Damage Summary Table

Use `QTableWidget` or `qfluentwidgets.TableWidget`:

**Columns:**
| Mã | Loại hư hỏng | Mức độ | Mật độ (%) | Giá trị khấu trừ | Độ tin cậy |

**Rows:** One per `DamageRecord` in `PCIResult.damages`
**Footer row:** PCI = XX (Rating), CDV = XX, q = X

**Vietnamese labels** from `strings.py` module.

---

## R-06: CSV Export Format

**Filename:** `PCI_report_YYYYMMDD_HHMMSS.csv`
**Location:** `outputs/reports/`

**Format:**
```
Image, path/to/image.jpg
Date, 2026-05-21 10:30:00
PCI, 92.2
Rating, Good
CDV, 7.8
Maintenance, Routine maintenance

Code,Type,Severity,Density%,DeductValue,Confidence
D40,Pothole,Low,0.32,7.8,0.65
```

**Implementation:** Python `csv` module. UTF-8-BOM encoding for Excel Vietnamese compatibility.

---

## R-07: Vietnamese UI Strings

All UI text in Vietnamese with English fallback. Centralized in `strings.py`:

```python
STRINGS = {
    "vi": {
        "app_title": "Hệ thống Đánh giá Hư hỏng Mặt đường",
        "run_detection": "Phát hiện hư hỏng",
        "pci_score": "Điểm PCI",
        "rating": "Phân loại",
        ...
    },
    "en": {
        "app_title": "Road Damage Assessment System",
        ...
    }
}
```

Language selected from `config/default.json` → `language` key.

---

## R-08: Output Directory Management

**Structure:**
```
outputs/
├── images/     # Annotated images saved here
├── reports/    # CSV/Excel reports
└── videos/     # Video output (Phase 5)
```

**GUI features:**
- "Save Annotated Image" → `outputs/images/`
- "Export Report" → `outputs/reports/`
- "Open Output Folder" → `os.startfile()` / `subprocess.Popen()`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PySide6-Fluent-Widgets incompatible with PySide6 version | GUI won't render | Pin compatible versions; test early |
| QGraphicsView annotation performance with many detections | Slow rendering | Limit to <50 annotations; batch add to scene |
| Thread safety with detector model | Crash/hang | Worker owns its own detector instance |
| Vietnamese font rendering | Garbled text | Use UTF-8 throughout; test with Vietnamese strings early |
| PCI gauge widget complexity | Time overrun | Start with simple QProgressBar; upgrade to gauge if time permits |
