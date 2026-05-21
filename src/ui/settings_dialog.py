"""Settings dialog for model path, confidence, sample unit area, etc."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
)

from qfluentwidgets import (
    LineEdit,
    SpinBox,
    DoubleSpinBox,
    ComboBox,
    PushButton as FluentPushButton,
)

from src.ui.strings import get_string
from src.utils.config import save_config


class SettingsDialog(QDialog):
    """Settings dialog for configuring model path, confidence, and other parameters.

    Reads from and saves to config/default.json via the config module.
    """

    def __init__(self, config: dict, parent=None) -> None:
        super().__init__(parent)

        self._config = config.copy()

        self.setWindowTitle(get_string("settings_title"))
        self.setMinimumWidth(450)
        self.setModal(True)

        # --- Layout ---
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Model path
        self._model_path_edit = LineEdit()
        self._model_path_edit.setText(config.get("model_path", ""))
        self._model_path_edit.setPlaceholderText("models/yolo-rdd2022-benchmark/yolo12s_seed0_best.pt")
        model_row = QHBoxLayout()
        model_row.addWidget(self._model_path_edit, stretch=1)
        model_browse = FluentPushButton("…")
        model_browse.setFixedWidth(40)
        model_browse.clicked.connect(self._browse_model)
        model_row.addWidget(model_browse)
        form.addRow(get_string("settings_model_path"), model_row)

        # Confidence threshold
        self._confidence_spin = DoubleSpinBox()
        self._confidence_spin.setRange(0.01, 1.00)
        self._confidence_spin.setSingleStep(0.05)
        self._confidence_spin.setDecimals(2)
        self._confidence_spin.setValue(config.get("confidence", 0.15))
        form.addRow(get_string("settings_confidence"), self._confidence_spin)

        # Sample unit area
        self._unit_area_spin = SpinBox()
        self._unit_area_spin.setRange(100, 100000)
        self._unit_area_spin.setSingleStep(500)
        self._unit_area_spin.setValue(config.get("sample_unit_area_sqft", 5000))
        form.addRow(get_string("settings_unit_area"), self._unit_area_spin)

        # PCI data path
        self._pci_data_edit = LineEdit()
        self._pci_data_edit.setText(config.get("pci_data_path", ""))
        self._pci_data_edit.setPlaceholderText("data/pci_astm_d6433.json")
        pci_row = QHBoxLayout()
        pci_row.addWidget(self._pci_data_edit, stretch=1)
        pci_browse = FluentPushButton("…")
        pci_browse.setFixedWidth(40)
        pci_browse.clicked.connect(self._browse_pci_data)
        pci_row.addWidget(pci_browse)
        form.addRow(get_string("settings_pci_data"), pci_row)

        # Language
        self._language_combo = ComboBox()
        self._language_combo.addItems(["Tiếng Việt (vi)", "English (en)"])
        lang = config.get("language", "vi")
        self._language_combo.setCurrentIndex(0 if lang == "vi" else 1)
        form.addRow(get_string("settings_language"), self._language_combo)

        # Output directory
        self._output_dir_edit = LineEdit()
        self._output_dir_edit.setText(config.get("output_dir", "outputs"))
        output_row = QHBoxLayout()
        output_row.addWidget(self._output_dir_edit, stretch=1)
        output_browse = FluentPushButton("…")
        output_browse.setFixedWidth(40)
        output_browse.clicked.connect(self._browse_output_dir)
        output_row.addWidget(output_browse)
        form.addRow(get_string("settings_output_dir"), output_row)

        layout.addLayout(form)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = FluentPushButton(get_string("settings_save"))
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = FluentPushButton(get_string("settings_cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _browse_model(self) -> None:
        """Browse for model file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Model", "", "PyTorch (*.pt);;ONNX (*.onnx)"
        )
        if path:
            self._model_path_edit.setText(path)

    def _browse_pci_data(self) -> None:
        """Browse for PCI data JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select PCI Data", "", "JSON (*.json)"
        )
        if path:
            self._pci_data_edit.setText(path)

    def _browse_output_dir(self) -> None:
        """Browse for output directory."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder:
            self._output_dir_edit.setText(folder)

    def _on_save(self) -> None:
        """Save settings to config file and accept dialog."""
        self._config["model_path"] = self._model_path_edit.text()
        self._config["confidence"] = self._confidence_spin.value()
        self._config["sample_unit_area_sqft"] = self._unit_area_spin.value()
        self._config["pci_data_path"] = self._pci_data_edit.text()
        lang_index = self._language_combo.currentIndex()
        self._config["language"] = "vi" if lang_index == 0 else "en"
        self._config["output_dir"] = self._output_dir_edit.text()

        save_config(self._config)
        self.accept()
