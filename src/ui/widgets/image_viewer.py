"""Image viewer widget with zoom, pan, and annotation overlay."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QWheelEvent, QPen, QBrush, QColor, QFont, QPainter
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
)

from src.ui.strings import get_string, get_damage_type_name

# Damage class colors (consistent with supervision annotation)
DAMAGE_COLORS = {
    "D00": QColor(231, 76, 60),    # red
    "D10": QColor(230, 126, 34),   # orange
    "D20": QColor(241, 196, 15),   # yellow
    "D40": QColor(155, 89, 182),   # purple
}
DEFAULT_COLOR = QColor(149, 165, 166)  # gray for unknown

BOX_PEN_WIDTH = 3
LABEL_FONT_SIZE = 11
LABEL_PADDING = 4


class ImageViewer(QGraphicsView):
    """Image viewer with zoom, pan, and bounding box annotation overlay.

    Features:
    - Mouse wheel zoom (centered on cursor)
    - Click-drag pan when zoomed
    - Fit-to-window on double-click or initial load
    - Annotation overlay with class-colored bounding boxes + labels
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._annotation_items: list = []
        self._zoom_level = 1.0

        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)

        # Scroll bar policy
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setMinimumWidth(400)

    # --- Image loading ---

    def load_image(self, path: str | Path) -> bool:
        """Load an image from file path.

        Args:
            path: Path to image file.

        Returns:
            True if image loaded successfully.
        """
        path = Path(path)
        if not path.exists():
            return False

        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            return False

        self.clear_scene()

        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._pixmap_item.setTransformationMode(
            Qt.TransformationMode.SmoothTransformation
        )
        self._scene.addItem(self._pixmap_item)

        # Set scene rect to image bounds
        self._scene.setSceneRect(QRectF(pixmap.rect()))

        # Fit to window
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self._zoom_level = 1.0

        return True

    def clear_scene(self) -> None:
        """Clear all items from the scene."""
        self._scene.clear()
        self._pixmap_item = None
        self._annotation_items.clear()

    # --- Annotation overlay ---

    def add_detections(
        self,
        detections: list[dict],
    ) -> None:
        """Draw bounding box annotations on the image.

        Args:
            detections: List of dicts with keys: code, bbox (x1,y1,x2,y2), confidence.
        """
        self.clear_annotations()

        for det in detections:
            code = det.get("code", "UNKNOWN")
            bbox = det.get("bbox", (0, 0, 0, 0))
            confidence = det.get("confidence", 0.0)

            x1, y1, x2, y2 = bbox
            color = DAMAGE_COLORS.get(code, DEFAULT_COLOR)

            # Bounding box rectangle
            rect = QRectF(x1, y1, x2 - x1, y2 - y1)
            pen = QPen(color, BOX_PEN_WIDTH)
            rect_item = QGraphicsRectItem(rect)
            rect_item.setPen(pen)
            rect_item.setBrush(QBrush(Qt.GlobalColor.transparent))
            self._scene.addItem(rect_item)
            self._annotation_items.append(rect_item)

            # Label text
            type_name = get_damage_type_name(code)
            label_text = f"{code} {type_name} {confidence:.0%}"
            text_item = QGraphicsSimpleTextItem(label_text)
            text_item.setFont(QFont("Segoe UI", LABEL_FONT_SIZE))
            text_item.setBrush(QBrush(color))

            # Position label above the box (or inside if at top edge)
            text_y = y1 - 18 if y1 > 20 else y1 + 2
            text_item.setPos(x1 + LABEL_PADDING, text_y)
            self._scene.addItem(text_item)
            self._annotation_items.append(text_item)

    def clear_annotations(self) -> None:
        """Remove annotation items from the scene, keep the image."""
        for item in self._annotation_items:
            self._scene.removeItem(item)
        self._annotation_items.clear()

    # --- Zoom / Pan ---

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom in/out with mouse wheel, centered on cursor position."""
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15

        # Clamp zoom level
        new_zoom = self._zoom_level * factor
        if new_zoom < 0.1 or new_zoom > 20.0:
            event.accept()
            return

        self.scale(factor, factor)
        self._zoom_level = new_zoom
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        """Double-click to fit image to window."""
        if self._scene.sceneRect().isValid():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_level = 1.0
        event.accept()

    def fit_to_window(self) -> None:
        """Fit the image to the current viewport size."""
        if self._scene.sceneRect().isValid():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self._zoom_level = 1.0
