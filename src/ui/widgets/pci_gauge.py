"""PCI gauge widget — semicircular gauge with color bands and needle."""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QConicalGradient, QPainterPath
from PySide6.QtWidgets import QWidget, QSizePolicy

from src.ui.strings import get_string, get_rating_name

# ASTM D6433 rating colors and ranges
RATING_BANDS = [
    ("Good",          QColor(46, 204, 113)),   # green
    ("Satisfactory",  QColor(39, 174, 96)),    # dark green
    ("Fair",          QColor(241, 196, 15)),    # yellow
    ("Poor",          QColor(230, 126, 34)),    # orange
    ("Very Poor",     QColor(231, 76, 60)),     # red
    ("Failed",        QColor(142, 68, 173)),    # dark red/purple
]

# PCI ranges for each rating (used for arc segments)
RATING_RANGES = [
    ("Good",          85, 100),
    ("Satisfactory",  70, 85),
    ("Fair",          55, 70),
    ("Poor",          40, 55),
    ("Very Poor",     25, 40),
    ("Failed",         0, 25),
]

# Arc geometry
ARC_START_DEG = 180   # left side (0° = 3 o'clock, 180° = 9 o'clock)
ARC_SPAN_DEG = 180    # semicircle
NEEDLE_LENGTH_RATIO = 0.75  # needle length as ratio of radius


class PCIGauge(QWidget):
    """Semicircular PCI gauge with color bands, needle, and digital readout.

    Visual design:
    - 180° arc with 6 color bands matching ASTM D6433 rating categories
    - Needle pointing to current PCI value
    - Digital PCI value displayed below needle
    - Rating text + color indicator below digital readout
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._pci_value: float = 0.0
        self._rating: str = ""
        self._rating_color: QColor = QColor(149, 165, 166)

        self.setMinimumSize(200, 140)
        self.setMaximumHeight(180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_pci_value(self, value: float, rating: str = "") -> None:
        """Update the PCI value and rating, then repaint.

        Args:
            value: PCI value (0-100).
            rating: PCI rating string (e.g. "Good", "Fair").
        """
        self._pci_value = max(0.0, min(100.0, value))
        self._rating = rating

        # Find rating color
        self._rating_color = QColor(149, 165, 166)  # default gray
        for name, color in RATING_BANDS:
            if rating == name:
                self._rating_color = color
                break

        self.update()

    def reset(self) -> None:
        """Reset gauge to empty state."""
        self._pci_value = 0.0
        self._rating = ""
        self._rating_color = QColor(149, 165, 166)
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the semicircular gauge."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Gauge geometry — arc centered at bottom-center
        margin = 20
        radius = min(w // 2 - margin, h - 40)
        if radius < 40:
            radius = 40

        cx = w // 2
        cy = h - 30  # leave space for text below

        # --- Draw color bands ---
        pen_width = 16
        for name, low, high in RATING_RANGES:
            color = dict(RATING_BANDS)[name]

            # Convert PCI range to degree range
            # PCI 100 = left (180°), PCI 0 = right (0°)
            start_deg = ARC_START_DEG - (high / 100.0) * ARC_SPAN_DEG
            span_deg = ((high - low) / 100.0) * ARC_SPAN_DEG

            pen = QPen(color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)
            # Qt angles: 1/16th degree, start from 3 o'clock, CCW positive
            painter.drawArc(rect, int(start_deg * 16), int(-span_deg * 16))

        # --- Draw tick marks ---
        pen = QPen(QColor(180, 180, 180), 1)
        painter.setPen(pen)
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for val in [0, 25, 40, 55, 70, 85, 100]:
            # Angle: PCI 100 = 180°, PCI 0 = 0°
            angle_deg = (val / 100.0) * 180.0
            angle_rad = math.radians(angle_deg)

            # Tick line
            inner_r = radius - pen_width // 2 - 2
            outer_r = radius + pen_width // 2 + 2
            x1 = cx - inner_r * math.cos(angle_rad)
            y1 = cy - inner_r * math.sin(angle_rad)
            x2 = cx - outer_r * math.cos(angle_rad)
            y2 = cy - outer_r * math.sin(angle_rad)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Tick label
            label_r = radius + pen_width // 2 + 14
            lx = cx - label_r * math.cos(angle_rad)
            ly = cy - label_r * math.sin(angle_rad)
            painter.drawText(QPointF(lx - 8, ly + 4), str(val))

        # --- Draw needle ---
        if self._rating:  # Only draw needle if we have a result
            needle_angle_deg = (self._pci_value / 100.0) * 180.0
            needle_angle_rad = math.radians(needle_angle_deg)

            needle_len = radius * NEEDLE_LENGTH_RATIO
            nx = cx - needle_len * math.cos(needle_angle_rad)
            ny = cy - needle_len * math.sin(needle_angle_rad)

            # Needle body
            needle_pen = QPen(QColor(44, 62, 80), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(needle_pen)
            painter.drawLine(QPointF(cx, cy), QPointF(nx, ny))

            # Center dot
            painter.setBrush(QBrush(QColor(44, 62, 80)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)

        # --- Digital readout ---
        if self._rating:
            # PCI value (large)
            font_large = QFont("Segoe UI", 22, QFont.Weight.Bold)
            painter.setFont(font_large)
            painter.setPen(QPen(self._rating_color))
            pci_text = f"{self._pci_value:.1f}"
            text_rect = QRectF(cx - 50, cy + 4, 100, 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, pci_text)

            # Rating label
            font_small = QFont("Segoe UI", 11)
            painter.setFont(font_small)
            rating_name = get_rating_name(self._rating)
            painter.setPen(QPen(QColor(100, 100, 100)))
            rating_rect = QRectF(cx - 60, cy + 32, 120, 20)
            painter.drawText(rating_rect, Qt.AlignmentFlag.AlignCenter, rating_name)
        else:
            # No result yet — show placeholder
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.setPen(QPen(QColor(180, 180, 180)))
            no_result = get_string("pci_no_result")
            text_rect = QRectF(cx - 60, cy + 10, 120, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, no_result)

        painter.end()
