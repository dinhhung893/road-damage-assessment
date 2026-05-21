# Phase 3: Desktop App Core (GUI) — Plan

**Phase:** 03
**Status:** Planned
**Requirements:** VIS-01~03, GUI-01~06, GUI-11~14, INF-06
**Depends on:** Phase 2 (✅ pass 52/52 tests)
**Est. Time:** 2 tuần
**Mode:** mvp

---

## Task Overview

| Task | Type | Requirements | Priority | Est. |
|------|------|-------------|----------|------|
| T1: Install PySide6-Fluent-Widgets + verify | infra | GUI-01 | [BLOCKING] | 30min |
| T2: Vietnamese strings module | code | GUI-12 | [BLOCKING] | 30min |
| T3: Main window skeleton (QMainWindow + toolbar + panels) | code | GUI-01, GUI-04 | [BLOCKING] | 2h |
| T4: Image viewer widget (QGraphicsView) | code | GUI-02 | high | 2h |
| T5: Detection worker thread (QThread) | code | GUI-01 | high | 1h |
| T6: Wire detector + PCI → GUI | code | VIS-01, GUI-01 | high | 1h |
| T7: PCI gauge widget | code | VIS-03 | high | 2h |
| T8: Damage summary table | code | VIS-02, PCI-06 | high | 1h |
| T9: Settings dialog | code | GUI-06, GUI-14 | medium | 1h |
| T10: Dark/Light theme toggle | code | GUI-05 | medium | 30min |
| T11: File open + directory batch | code | GUI-03, GUI-11 | medium | 1h |
| T12: CSV export + output management | code | GUI-13, INF-06 | medium | 1h |
| T13: End-to-end GUI test | test | All | high | 1h |

---

## T1: Install PySide6-Fluent-Widgets + Verify [BLOCKING]

**Requirement:** GUI-01
**Context decision:** D-01 (use qfluentwidgets)

### Steps
1. Add `PySide6-Fluent-Widgets` to `requirements.txt`
2. Install in venv: `pip install PySide6-Fluent-Widgets`
3. Verify: run minimal test — `FluentWindow` + `setTheme` + `PushButton`
4. Check compatibility with existing `PySide6` version

### Exit Criteria
- [ ] `qfluentwidgets` imports without error
- [ ] Basic FluentWindow renders
- [ ] Theme toggle works programmatically

---

## T2: Vietnamese Strings Module [BLOCKING]

**Requirement:** GUI-12
**Context decision:** D-07 (Vietnamese primary, centralized strings)

### Steps
1. Create `src/ui/strings.py` with `STRINGS` dict for "vi" and "en"
2. Include all UI labels: app title, menu items, button text, table headers, PCI labels, maintenance text
3. `get_string(key, lang="vi")` helper function
4. Read `language` from config for default

### Exit Criteria
- [ ] All UI text centralized in strings module
- [ ] Vietnamese and English versions available
- [ ] No hardcoded UI strings in widget code

---

## T3: Main Window Skeleton [BLOCKING]

**Requirement:** GUI-01, GUI-04
**Context decision:** D-02 (single-window, no sidebar navigation)

### Steps
1. Create `src/ui/main_window.py` — `MainWindow(QMainWindow)`
2. Layout: Toolbar (top) | Splitter: Image Viewer (left) | PCI Panel (right) | Status Bar (bottom)
3. Toolbar actions: Open Image, Open Folder, Run Detection, Save Image, Export Report, Settings, Theme Toggle
4. Status bar: shows inference time, detection count, PCI score
5. Menu bar: File, Analysis, View, Help (minimal)
6. Window title from strings module
7. Minimum size: 1200×700

### Files Created
- `src/ui/main_window.py` — Main window class

### Exit Criteria
- [ ] Window renders with toolbar, splitter, status bar
- [ ] Toolbar buttons visible with icons
- [ ] Window title in Vietnamese

---

## T4: Image Viewer Widget

**Requirement:** GUI-02
**Context decision:** D-03 (QGraphicsView + QGraphicsScene)

### Steps
1. Create `src/ui/widgets/image_viewer.py` — `ImageViewer(QGraphicsView)`
2. Load image as `QGraphicsPixmapItem`
3. Zoom: override `wheelEvent()` with scale factor
4. Pan: `setDragMode(ScrollHandDrag)` when zoomed
5. Fit-to-window: `fitInView()` method
6. Annotation overlay: `add_detections(detections)` method
   - Create `QGraphicsRectItem` for each bbox with class-specific color
   - Create `QGraphicsSimpleTextItem` for label (class + confidence)
   - Store items in `_annotation_items` list for cleanup
7. Clear: `clear_annotations()` before adding new ones
8. Color scheme: D00=#e74c3c, D10=#e67e22, D20=#f1c40f, D40=#9b59b6

### Files Created
- `src/ui/widgets/__init__.py`
- `src/ui/widgets/image_viewer.py`

### Exit Criteria
- [ ] Image loads and displays
- [ ] Zoom in/out with mouse wheel
- [ ] Pan with click-drag when zoomed
- [ ] Bounding boxes drawn with class colors and labels
- [ ] Annotations clear when new image loaded

---

## T5: Detection Worker Thread

**Requirement:** GUI-01
**Context decision:** D-05 (QThread + signals)

### Steps
1. Create `src/ui/workers.py` — `DetectionWorker(QThread)`
2. Constructor: takes `image_path`, reads config for model path, confidence, PCI data path
3. `run()` method:
   a. Create `RoadDamageDetector` instance
   b. Call `detector.detect(image_path)`
   c. Convert `DetectionResult.pci_detections` to PCI input format
   d. Create `PCIEngine` instance
   e. Call `pci_engine.calculate_pci(pci_input, image_area_px)`
   f. Emit `finished(pci_result, det_result)` signal
4. Error handling: emit `error(str)` signal on exception
5. Progress: emit `status_update(str)` for status bar updates

### Files Created
- `src/ui/workers.py`

### Exit Criteria
- [ ] Detection runs in background thread
- [ ] GUI remains responsive during inference
- [ ] Results emitted via signal
- [ ] Errors handled gracefully

---

## T6: Wire Detector + PCI → GUI

**Requirement:** VIS-01, GUI-01

### Steps
1. In `MainWindow`, connect "Run Detection" button to `_run_detection()` slot
2. `_run_detection()`: create `DetectionWorker`, connect signals, start thread
3. `_on_detection_finished(pci_result, det_result)`:
   a. Update image viewer with annotations from `det_result`
   b. Update PCI gauge with `pci_result.pci_value`
   c. Update damage table from `pci_result.damages`
   d. Update status bar with inference time + PCI score
   e. Store results for export
4. Disable "Run Detection" while worker is active
5. Handle error signal: show `InfoBar` error message

### Exit Criteria
- [ ] Click "Run Detection" → image annotated + PCI displayed
- [ ] GUI responsive during inference
- [ ] Error shown if detection fails

---

## T7: PCI Gauge Widget

**Requirement:** VIS-03
**Context decision:** D-04 (custom QPainter gauge)

### Steps
1. Create `src/ui/widgets/pci_gauge.py` — `PCIGauge(QWidget)`
2. Override `paintEvent()`:
   a. Draw semicircular arc with 6 color bands (Good→Failed)
   b. Draw needle pointing to PCI value
   c. Draw digital PCI value below needle
   d. Draw rating text + color indicator
3. `set_pci_value(value)` — Updates needle position and triggers repaint
4. Smooth animation: `QPropertyAnimation` on needle angle (optional, time permitting)
5. Size: fixed height ~150px, width stretches with panel

### Files Created
- `src/ui/widgets/pci_gauge.py`

### Exit Criteria
- [ ] Gauge renders with color bands matching ASTM rating
- [ ] Needle points to correct PCI value
- [ ] Digital readout shows PCI number
- [ ] Rating text displayed below gauge

---

## T8: Damage Summary Table

**Requirement:** VIS-02, PCI-06

### Steps
1. Create `src/ui/widgets/damage_table.py` — `DamageTable(QWidget)`
2. Use `QTableWidget` with Vietnamese headers from strings module
3. Columns: Mã | Loại hư hỏng | Mức độ | Mật độ (%) | GT khấu trừ | Độ tin cậy
4. `update_from_pci_result(pci_result)` — Populate from `PCIResult.damages`
5. Footer: PCI score, rating, CDV, maintenance recommendation
6. Color-code rows by severity: Low=green, Medium=yellow, High=red
7. Alternating row colors for readability

### Files Created
- `src/ui/widgets/damage_table.py`

### Exit Criteria
- [ ] Table shows all damage records with correct data
- [ ] Vietnamese column headers
- [ ] Severity color-coded
- [ ] Footer shows PCI summary

---

## T9: Settings Dialog

**Requirement:** GUI-06, GUI-14

### Steps
1. Create `src/ui/settings_dialog.py` — `SettingsDialog(QWidget)`
2. Fields:
   - Model path (file picker)
   - Confidence threshold (spin box, 0.0–1.0)
   - Sample unit area (spin box, sq ft)
   - PCI data path (file picker)
   - Language (combo: Vietnamese / English)
   - Output directory (folder picker)
3. Load from `config/default.json` on open
4. Save to `config/default.json` on accept
5. Use `qfluentwidgets` dialog style

### Files Created
- `src/ui/settings_dialog.py`

### Exit Criteria
- [ ] Dialog opens with current config values
- [ ] Changes persist to JSON file
- [ ] Model path and confidence editable

---

## T10: Dark/Light Theme Toggle

**Requirement:** GUI-05

### Steps
1. Add theme toggle button to toolbar (sun/moon icon)
2. Call `setTheme(Theme.DARK)` or `setTheme(Theme.LIGHT)` from qfluentwidgets
3. Save theme preference to config
4. Load saved theme on startup
5. Apply to all widgets (qfluentwidgets handles this automatically)

### Exit Criteria
- [ ] Toggle switches between dark and light theme
- [ ] Theme preference saved in config
- [ ] All widgets respect theme change

---

## T11: File Open + Directory Batch

**Requirement:** GUI-03, GUI-11

### Steps
1. "Open Image" → `QFileDialog.getOpenFileName()` with image filter
2. "Open Folder" → `QFileDialog.getExistingDirectory()` for batch processing
3. Batch mode: process all images in folder, show results in table
4. Save annotated images to `outputs/images/`
5. Supported formats: jpg, jpeg, png, bmp

### Exit Criteria
- [ ] Single image opens and displays
- [ ] Folder opens and processes all images
- [ ] Annotated images saved to output directory

---

## T12: CSV Export + Output Management

**Requirement:** GUI-13, INF-06

### Steps
1. "Export Report" → save CSV to `outputs/reports/`
2. CSV format: header (image path, date, PCI, rating, CDV) + damage rows
3. UTF-8-BOM encoding for Excel Vietnamese compatibility
4. "Save Annotated Image" → save to `outputs/images/`
5. "Open Output Folder" → `os.startfile()` on Windows
6. Create output directories on startup if missing

### Exit Criteria
- [ ] CSV export works with Vietnamese characters
- [ ] Annotated images save correctly
- [ ] Output folder opens in file explorer

---

## T13: End-to-End GUI Test

**Requirement:** All

### Steps
1. Launch app
2. Open sample image from `data/samples/`
3. Run detection → verify annotations appear
4. Verify PCI gauge shows correct value
5. Verify damage table populated
6. Toggle theme → verify switch
7. Open settings → change confidence → save → verify persisted
8. Export CSV → verify file contents
9. Save annotated image → verify file exists

### Exit Criteria
- [ ] Full workflow works without crash
- [ ] All GUI elements functional
- [ ] Results match CLI benchmark results

---

## Success Criteria Verification

| # | Criterion | How Verified |
|---|-----------|-------------|
| 1 | GUI hiển thị ảnh + annotated bounding boxes + labels | T4 + T6 visual test |
| 2 | PCI panel hiển thị điểm số + bảng tổng hợp | T7 + T8 visual test |
| 3 | Theme toggle hoạt động | T10 test |
| 4 | Settings lưu được model path + confidence threshold | T9 test |

---

## File Structure After Phase 3

```
src/ui/
├── __init__.py
├── main_window.py          # MainWindow(QMainWindow)
├── strings.py              # Vietnamese/English UI strings
├── settings_dialog.py      # Settings dialog
├── workers.py              # DetectionWorker(QThread)
├── widgets/
│   ├── __init__.py
│   ├── image_viewer.py     # ImageViewer(QGraphicsView)
│   ├── pci_gauge.py        # PCIGauge(QWidget) — custom painted
│   └── damage_table.py     # DamageTable(QWidget) — QTableWidget wrapper
```
