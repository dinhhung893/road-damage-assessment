"""PySide6 main window — Fluent Design theme with detection + PCI integration."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QLabel,
)

from qfluentwidgets import (
    FluentIcon,
    setTheme,
    Theme,
    InfoBar,
    InfoBarPosition,
)

from src.ui.strings import get_string, set_default_language, get_damage_type_name, get_severity_name
from src.ui.widgets.image_viewer import ImageViewer
from src.ui.widgets.pci_gauge import PCIGauge
from src.ui.widgets.damage_table import DamageTable
from src.ui.workers import DetectionWorker, BatchDetectionWorker
from src.utils.config import load_config, save_config
from src.utils.logging_setup import get_logger

logger = get_logger("main_window")


class MainWindow(QMainWindow):
    """Main application window with image viewer, PCI panel, and toolbar.

    Layout: Toolbar (top) | QSplitter: Image Viewer (65%, left) | PCI Panel (35%, right) | Status Bar (bottom)
    """

    def __init__(self) -> None:
        super().__init__()

        # Load config
        self._config = load_config()
        lang = self._config.get("language", "vi")
        set_default_language(lang)

        # State
        self._current_image_path: str = ""
        self._current_pci_result = None
        self._current_det_result = None
        self._worker: DetectionWorker | BatchDetectionWorker | None = None
        self._is_dark_theme = self._config.get("theme", "dark") == "dark"

        # Batch results state
        self._batch_results: list[tuple] = []  # [(path, pci_result, det_result), ...]
        self._batch_index: int = -1

        # --- Window setup ---
        self.setWindowTitle(get_string("app_title"))
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)

        # --- Build UI ---
        self._create_actions()
        self._build_central()
        self._build_menu_bar()

        # --- Apply theme ---
        self._apply_theme()

        # --- Ensure output directories ---
        self._ensure_output_dirs()

    # =====================================================================
    # UI Construction
    # =====================================================================

    def _create_actions(self) -> None:
        """Create all QActions (used by menu bar, no toolbar)."""
        # Open Image
        self._action_open = QAction(FluentIcon.PHOTO.icon(), get_string("action_open_image"), self)
        self._action_open.triggered.connect(self._on_open_image)

        # Open Folder
        self._action_folder = QAction(FluentIcon.FOLDER.icon(), get_string("action_open_folder"), self)
        self._action_folder.triggered.connect(self._on_open_folder)

        # Run Detection
        self._action_run = QAction(FluentIcon.PLAY.icon(), get_string("action_run_detection"), self)
        self._action_run.triggered.connect(self._on_run_detection)
        self._action_run.setEnabled(False)  # disabled until image loaded

        # Save Annotated Image
        self._action_save = QAction(FluentIcon.SAVE.icon(), get_string("action_save_image"), self)
        self._action_save.triggered.connect(self._on_save_image)
        self._action_save.setEnabled(False)

        # Export CSV
        self._action_export = QAction(FluentIcon.DOCUMENT.icon(), get_string("action_export_report"), self)
        self._action_export.triggered.connect(self._on_export_csv)
        self._action_export.setEnabled(False)

        # Theme Toggle
        self._action_theme = QAction(FluentIcon.BRIGHTNESS.icon(), get_string("action_theme_toggle"), self)
        self._action_theme.triggered.connect(self._on_toggle_theme)

        # Settings
        self._action_settings = QAction(FluentIcon.SETTING.icon(), get_string("action_settings"), self)
        self._action_settings.triggered.connect(self._on_settings)

        # Open Output Folder
        self._action_output = QAction(FluentIcon.FOLDER_ADD.icon(), get_string("action_open_output"), self)
        self._action_output.triggered.connect(self._on_open_output_folder)

        # Batch navigation
        self._action_prev = QAction(FluentIcon.LEFT_ARROW.icon(), get_string("action_prev_image"), self)
        self._action_prev.triggered.connect(self._on_prev_batch_image)
        self._action_prev.setEnabled(False)

        self._action_next = QAction(FluentIcon.RIGHT_ARROW.icon(), get_string("action_next_image"), self)
        self._action_next.triggered.connect(self._on_next_batch_image)
        self._action_next.setEnabled(False)

    def _build_central(self) -> None:
        """Build the central widget with splitter layout."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        # Splitter: Image Viewer Area (left) | PCI Panel (right)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # --- Image Viewer Area (viewer + nav + log) ---
        viewer_area = QWidget()
        viewer_layout = QVBoxLayout(viewer_area)
        viewer_layout.setContentsMargins(0, 0, 0, 0)
        viewer_layout.setSpacing(2)

        # Batch navigation bar (hidden by default, above image)
        self._batch_nav = QToolBar()
        self._batch_nav.setMovable(False)
        self._batch_nav.setVisible(False)
        self._batch_nav.addAction(self._action_prev)
        self._batch_nav.addAction(self._action_next)
        self._batch_nav.addSeparator()
        self._batch_counter = QLabel("")
        self._batch_nav.addWidget(self._batch_counter)
        viewer_layout.addWidget(self._batch_nav)

        # Image Viewer
        self._image_viewer = ImageViewer()
        viewer_layout.addWidget(self._image_viewer, stretch=1)

        # Batch progress bar (hidden by default)
        self._batch_progress = QProgressBar()
        self._batch_progress.setVisible(False)
        viewer_layout.addWidget(self._batch_progress)

        # Log panel (below image)
        self._build_log_panel()
        viewer_layout.addWidget(self._log_panel)

        splitter.addWidget(viewer_area)

        # --- PCI Panel ---
        pci_panel = QWidget()
        pci_layout = QVBoxLayout(pci_panel)
        pci_layout.setContentsMargins(8, 8, 8, 8)
        pci_layout.setSpacing(8)

        # PCI Gauge
        self._pci_gauge = PCIGauge()
        pci_layout.addWidget(self._pci_gauge)

        # Damage Table
        self._damage_table = DamageTable()
        pci_layout.addWidget(self._damage_table, stretch=1)

        pci_panel.setMinimumWidth(250)
        splitter.addWidget(pci_panel)

        # Splitter ratios: 65% image, 35% PCI panel
        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)

        layout.addWidget(splitter)

    def _build_log_panel(self) -> None:
        """Build the log panel — replaces thin status bar with larger colored log."""
        from src.ui.widgets.log_panel import LogPanel
        self._log_panel = LogPanel(is_dark=self._is_dark_theme)
        self._log_panel.log(get_string("status_ready"), "info")

    def _build_menu_bar(self) -> None:
        """Build the menu bar with all actions."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu(get_string("menu_file"))
        file_menu.addAction(self._action_open)
        file_menu.addAction(self._action_folder)
        file_menu.addSeparator()
        file_menu.addAction(self._action_save)
        file_menu.addAction(self._action_export)
        file_menu.addAction(self._action_output)
        file_menu.addSeparator()

        exit_action = QAction(get_string("action_exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Analysis menu
        analysis_menu = menubar.addMenu(get_string("menu_analysis"))
        analysis_menu.addAction(self._action_run)

        # View menu
        view_menu = menubar.addMenu(get_string("menu_view"))
        view_menu.addAction(self._action_theme)
        view_menu.addAction(self._action_settings)

        # Help menu
        help_menu = menubar.addMenu(get_string("menu_help"))
        about_action = QAction(get_string("action_about"), self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    # =====================================================================
    # Theme
    # =====================================================================

    def _apply_theme(self) -> None:
        """Apply dark or light theme based on config."""
        if self._is_dark_theme:
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)
        if hasattr(self, "_log_panel"):
            self._log_panel.set_dark_theme(self._is_dark_theme)

    def _on_toggle_theme(self) -> None:
        """Toggle between dark and light theme."""
        self._is_dark_theme = not self._is_dark_theme
        self._config["theme"] = "dark" if self._is_dark_theme else "light"
        save_config(self._config)
        self._apply_theme()

    # =====================================================================
    # File Operations
    # =====================================================================

    def _on_open_image(self) -> None:
        """Open a single image file."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            get_string("dialog_open_image"),
            "",
            get_string("filter_images"),
        )
        if path:
            self._load_image(path)

    def _on_open_folder(self) -> None:
        """Open a folder of images for batch processing."""
        folder = QFileDialog.getExistingDirectory(
            self,
            get_string("dialog_open_folder"),
        )
        if folder:
            self._start_batch_processing(folder)

    def _load_image(self, path: str) -> None:
        """Load an image into the viewer and enable detection."""
        if self._image_viewer.load_image(path):
            self._current_image_path = path
            self._action_run.setEnabled(True)
            self._log_panel.log(
                get_string("msg_image_loaded", name=Path(path).name), "info"
            )
            # Reset PCI panel
            self._pci_gauge.reset()
            self._damage_table.reset()
            self._current_pci_result = None
            self._current_det_result = None
            self._action_save.setEnabled(False)
            self._action_export.setEnabled(False)
        else:
            self._show_error(f"Cannot load image: {path}")

    # =====================================================================
    # Detection
    # =====================================================================

    def _on_run_detection(self) -> None:
        """Run detection on the current image."""
        if not self._current_image_path:
            return
        self._start_detection(self._current_image_path)

    def _start_detection(self, image_path: str) -> None:
        """Start detection in a background thread."""
        self._action_run.setEnabled(False)
        self._action_open.setEnabled(False)
        self._action_folder.setEnabled(False)
        self._log_panel.log(get_string("status_detecting"), "info")

        self._worker = DetectionWorker(image_path)
        self._worker.finished.connect(self._on_detection_finished)
        self._worker.error.connect(self._on_detection_error)
        self._worker.status.connect(lambda msg: self._log_panel.log(msg, "info"))
        self._worker.start()

    def _on_detection_finished(self, pci_result, det_result) -> None:
        """Handle detection completion — update all UI panels."""
        self._current_pci_result = pci_result
        self._current_det_result = det_result

        # Update image viewer with annotations
        if det_result and det_result.detections:
            detections = []
            masks = []
            for det in det_result.detections:
                detections.append({
                    "code": det.code,
                    "bbox": det.bbox,
                    "confidence": det.confidence,
                })
                # Add mask contours if available
                if det.has_mask and det.mask_contours:
                    for contour in det.mask_contours:
                        masks.append({
                            "code": det.code,
                            "contour": contour,
                        })
            self._image_viewer.add_detections(detections)
            if masks:
                logger.info(f"Adding {len(masks)} mask overlays to image viewer")
                self._image_viewer.add_masks(masks)
            else:
                n_with_mask = sum(1 for d in det_result.detections if d.has_mask)
                logger.info(f"No mask overlays — {n_with_mask}/{len(det_result.detections)} detections have masks")

        # Update PCI gauge
        if pci_result:
            self._pci_gauge.set_pci_value(pci_result.pci_value, pci_result.rating)
            self._damage_table.update_from_pci_result(pci_result)
        else:
            self._pci_gauge.reset()
            self._damage_table.reset()

        # Update log panel
        n_det = len(det_result.detections) if det_result else 0
        if pci_result:
            pci_val = pci_result.pci_value
            self._log_panel.log(
                get_string("status_done", n=n_det, pci=f"{pci_val:.1f}"), "success"
            )
        else:
            self._log_panel.log(
                get_string("status_done", n=n_det, pci="100.0"), "success"
            )

        # Enable actions
        self._action_run.setEnabled(True)
        self._action_open.setEnabled(True)
        self._action_folder.setEnabled(True)
        self._action_save.setEnabled(n_det > 0)
        self._action_export.setEnabled(pci_result is not None)

        # Show info bar if no detections
        if n_det == 0:
            InfoBar.info(
                title="",
                content=get_string("msg_no_detections"),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=3000,
                parent=self,
            )

    def _on_detection_error(self, msg: str) -> None:
        """Handle detection error."""
        self._show_error(msg)
        self._action_run.setEnabled(True)
        self._action_open.setEnabled(True)
        self._action_folder.setEnabled(True)
        self._log_panel.log(get_string("status_error", msg=msg), "error")

    # =====================================================================
    # Batch Processing
    # =====================================================================

    def _start_batch_processing(self, folder: str) -> None:
        """Start batch processing of all images in a folder."""
        folder_path = Path(folder)
        extensions = {".jpg", ".jpeg", ".png", ".bmp"}
        image_paths = sorted([
            str(p) for p in folder_path.iterdir()
            if p.suffix.lower() in extensions
        ])

        if not image_paths:
            self._show_error("No images found in folder")
            return

        # Disable actions during batch
        self._action_run.setEnabled(False)
        self._action_open.setEnabled(False)
        self._action_folder.setEnabled(False)

        # Show progress bar
        self._batch_progress.setVisible(True)
        self._batch_progress.setRange(0, len(image_paths))
        self._batch_progress.setValue(0)

        self._log_panel.log(
            get_string("msg_batch_start", n=len(image_paths)), "info"
        )

        self._worker = BatchDetectionWorker(image_paths)
        self._worker.progress.connect(self._on_batch_progress)
        self._worker.image_finished.connect(self._on_batch_image_finished)
        self._worker.batch_finished.connect(self._on_batch_finished)
        self._worker.error.connect(self._on_detection_error)
        self._worker.start()

    def _on_batch_progress(self, current: int, total: int, name: str) -> None:
        """Update progress bar during batch processing."""
        self._batch_progress.setValue(current)
        self._log_panel.log(
            get_string("msg_batch_progress", i=current, n=total, name=name), "info"
        )

    def _on_batch_image_finished(self, path: str, pci_result, det_result) -> None:
        """Handle single image completion during batch — log result."""
        if pci_result:
            self._log_panel.log(
                f"  → PCI = {pci_result.pci_value:.1f} ({pci_result.rating})", "success"
            )
        else:
            n_det = len(det_result.detections) if det_result else 0
            if n_det == 0:
                self._log_panel.log("  → Không phát hiện hư hỏng — PCI = 100.0 (Tốt)", "info")
            else:
                self._log_panel.log(f"  → {n_det} phát hiện (không tính PCI)", "warning")

    def _on_batch_finished(self, results: list) -> None:
        """Handle batch processing completion — store results, show first image, enable navigation."""
        self._batch_progress.setVisible(False)
        self._batch_results = results
        self._batch_index = -1

        # Calculate section PCI using PCIEngine
        pci_results = [r[1] for r in results if r[1] is not None]
        if pci_results:
            from src.engine.pci import PCIEngine
            pci_engine = PCIEngine(pci_data_path=self._config.get("pci_data_path", "data/pci_astm_d6433.json"))
            section = pci_engine.calculate_section_pci(pci_results)
            section_pci = section["section_pci"]
            section_rating = section["rating"]
            self._log_panel.log(
                f"{get_string('msg_batch_done', n=len(results))} "
                f"— {get_string('batch_section_pci')}: {section_pci:.1f} ({section_rating})",
                "success",
            )
        else:
            self._log_panel.log(
                get_string("msg_batch_done", n=len(results)), "warning"
            )

        # Show navigation bar
        if len(results) > 1:
            self._batch_nav.setVisible(True)

        # Show first image with detections (or first image overall)
        first_det_idx = next((i for i, r in enumerate(results) if r[1] is not None), 0)
        self._show_batch_image(first_det_idx)

        # Enable actions
        self._action_run.setEnabled(True)
        self._action_open.setEnabled(True)
        self._action_folder.setEnabled(True)
        self._action_export.setEnabled(any(r[1] is not None for r in results))

    def _show_batch_image(self, index: int) -> None:
        """Display a specific batch result by index."""
        if not self._batch_results or index < 0 or index >= len(self._batch_results):
            return

        self._batch_index = index
        path, pci_result, det_result = self._batch_results[index]

        # Load image
        self._image_viewer.load_image(path)
        self._current_image_path = path

        # Show annotations
        if det_result and det_result.detections:
            detections = []
            masks = []
            for d in det_result.detections:
                detections.append({"code": d.code, "bbox": d.bbox, "confidence": d.confidence})
                if d.has_mask and d.mask_contours:
                    for contour in d.mask_contours:
                        masks.append({"code": d.code, "contour": contour})
            self._image_viewer.add_detections(detections)
            if masks:
                self._image_viewer.add_masks(masks)

        # Update PCI panel
        if pci_result:
            self._pci_gauge.set_pci_value(pci_result.pci_value, pci_result.rating)
            self._damage_table.update_from_pci_result(pci_result)
            self._current_pci_result = pci_result
            self._current_det_result = det_result
        else:
            self._pci_gauge.set_pci_value(100.0, "Good")
            self._damage_table.reset()
            self._current_pci_result = None
            self._current_det_result = det_result

        # Update navigation state
        total = len(self._batch_results)
        self._action_prev.setEnabled(index > 0)
        self._action_next.setEnabled(index < total - 1)
        self._batch_counter.setText(f" {index + 1}/{total} ")

    def _on_prev_batch_image(self) -> None:
        """Navigate to previous batch result."""
        if self._batch_index > 0:
            self._show_batch_image(self._batch_index - 1)

    def _on_next_batch_image(self) -> None:
        """Navigate to next batch result."""
        if self._batch_index < len(self._batch_results) - 1:
            self._show_batch_image(self._batch_index + 1)

    # =====================================================================
    # Save / Export
    # =====================================================================

    def _on_save_image(self) -> None:
        """Save annotated image to outputs/images/."""
        if not self._current_image_path:
            return

        output_dir = Path(self._config.get("output_dir", "outputs")) / "images"
        output_dir.mkdir(parents=True, exist_ok=True)

        name = Path(self._current_image_path).stem + "_annotated.png"
        default_path = str(output_dir / name)

        path, _ = QFileDialog.getSaveFileName(
            self,
            get_string("dialog_save_image"),
            default_path,
            "PNG (*.png);;JPEG (*.jpg)",
        )
        if path:
            pixmap = self._image_viewer.grab()
            if pixmap.save(path):
                self._log_panel.log(get_string("msg_save_success", path=path), "success")
            else:
                self._show_error("Failed to save image")

    def _on_export_csv(self) -> None:
        """Export detection + PCI results to CSV."""
        if self._current_pci_result is None:
            return

        output_dir = Path(self._config.get("output_dir", "outputs")) / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_path = str(output_dir / f"PCI_report_{timestamp}.csv")

        path, _ = QFileDialog.getSaveFileName(
            self,
            get_string("dialog_save_report"),
            default_path,
            "CSV (*.csv)",
        )
        if path:
            self._export_csv_to_path(path)

    def _export_csv_to_path(self, path: str) -> None:
        """Write CSV report to file."""
        import csv

        pci_result = self._current_pci_result

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)

                # Header
                writer.writerow(["Image", self._current_image_path])
                writer.writerow(["Date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                if pci_result:
                    writer.writerow(["PCI", f"{pci_result.pci_value:.1f}"])
                    writer.writerow(["Rating", pci_result.rating])
                    writer.writerow(["CDV", f"{pci_result.cdv:.1f}"])
                    if pci_result.maintenance_action:
                        writer.writerow(["Maintenance", pci_result.maintenance_action])
                writer.writerow([])

                # Damage rows
                writer.writerow([
                    get_string("table_code"),
                    get_string("table_type"),
                    get_string("table_severity"),
                    get_string("table_density"),
                    get_string("table_deduct"),
                    get_string("table_confidence"),
                ])

                if pci_result and pci_result.damages:
                    for dmg in pci_result.damages:
                        writer.writerow([
                            getattr(dmg, "code", ""),
                            get_damage_type_name(getattr(dmg, "code", "")),
                            get_severity_name(getattr(dmg, "severity", "")),
                            f"{getattr(dmg, 'density_pct', 0):.2f}",
                            f"{getattr(dmg, 'deduct_value', 0):.1f}",
                            f"{getattr(dmg, 'confidence', 0):.0%}",
                        ])

            self._log_panel.log(get_string("msg_export_success", path=path), "success")

        except Exception as e:
            self._show_error(f"Export failed: {e}")

    # =====================================================================
    # Settings
    # =====================================================================

    def _on_settings(self) -> None:
        """Open settings dialog."""
        from src.ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(self._config, self)
        if dialog.exec():
            # Config was saved by dialog
            self._config = load_config()
            set_default_language(self._config.get("language", "vi"))
            self._damage_table.update_strings()

    # =====================================================================
    # Output Folder
    # =====================================================================

    def _on_open_output_folder(self) -> None:
        """Open the output directory in file explorer."""
        output_dir = Path(self._config.get("output_dir", "outputs"))
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            os.startfile(str(output_dir))
        except AttributeError:
            import subprocess
            subprocess.Popen(["xdg-open", str(output_dir)])

    # =====================================================================
    # About
    # =====================================================================

    def _on_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            get_string("action_about"),
            f"{get_string('app_title')}\n{get_string('app_subtitle')}\n\n"
            f"YOLOv12s + ASTM D6433 PCI\n"
            f"Version 1.0 — Phase 3 MVP",
        )

    # =====================================================================
    # Helpers
    # =====================================================================

    def _show_error(self, msg: str) -> None:
        """Show error info bar."""
        InfoBar.error(
            title="Error",
            content=msg,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=5000,
            parent=self,
        )

    def _ensure_output_dirs(self) -> None:
        """Create output directories if they don't exist."""
        output_dir = Path(self._config.get("output_dir", "outputs"))
        (output_dir / "images").mkdir(parents=True, exist_ok=True)
        (output_dir / "reports").mkdir(parents=True, exist_ok=True)

    # =====================================================================
    # Cleanup
    # =====================================================================

    def closeEvent(self, event) -> None:
        """Clean up worker threads on close."""
        if self._worker and self._worker.isRunning():
            self._worker.quit()
            self._worker.wait(3000)
        event.accept()

    def keyPressEvent(self, event) -> None:
        """Handle keyboard shortcuts."""
        key = event.key()
        if key == Qt.Key.Key_Left and self._batch_index > 0:
            self._on_prev_batch_image()
        elif key == Qt.Key.Key_Right and self._batch_index < len(self._batch_results) - 1:
            self._on_next_batch_image()
        else:
            super().keyPressEvent(event)
