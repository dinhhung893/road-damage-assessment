"""Log panel widget — colored status messages visible from distance."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QTextCursor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel


# Theme-aware colors
_COLORS_DARK = {
    "success": QColor(46, 204, 113),    # green
    "error":   QColor(231, 76, 60),     # red
    "info":    QColor(52, 152, 219),     # blue
    "warning": QColor(241, 196, 15),    # yellow
    "normal":  QColor(189, 195, 199),   # light gray
}

_COLORS_LIGHT = {
    "success": QColor(39, 174, 96),     # darker green
    "error":   QColor(192, 57, 43),     # darker red
    "info":    QColor(41, 128, 185),     # darker blue
    "warning": QColor(243, 156, 18),    # darker yellow
    "normal":  QColor(52, 73, 94),      # dark gray
}


class LogPanel(QWidget):
    """Scrollable log panel with colored messages.

    Replaces the thin status bar with a larger, more visible area.
    Messages are appended as colored text entries.
    """

    def __init__(self, parent=None, is_dark: bool = True) -> None:
        super().__init__(parent)
        self._is_dark = is_dark
        self._colors = _COLORS_DARK if is_dark else _COLORS_LIGHT

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title label
        self._title = QLabel("Nhật ký hoạt động")
        self._title.setObjectName("logPanelTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Segoe UI", 9)
        font.setBold(True)
        self._title.setFont(font)
        layout.addWidget(self._title)

        # Log text area
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        self._text_edit.setFont(QFont("Segoe UI", 11))
        self._text_edit.setMaximumHeight(120)
        self._text_edit.setMinimumHeight(60)
        self._text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self._text_edit)

        self._apply_theme()

    def _apply_theme(self) -> None:
        self._colors = _COLORS_DARK if self._is_dark else _COLORS_LIGHT
        if self._is_dark:
            bg = "#1e1e1e"
            title_bg = "#2d2d2d"
            title_fg = "#cccccc"
        else:
            bg = "#f8f9fa"
            title_bg = "#e9ecef"
            title_fg = "#495057"

        self._text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg};
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)
        self._title.setStyleSheet(f"""
            background-color: {title_bg};
            color: {title_fg};
            padding: 2px 4px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        """)

    def set_dark_theme(self, dark: bool) -> None:
        self._is_dark = dark
        self._apply_theme()

    def log(self, message: str, level: str = "normal") -> None:
        """Append a colored log message.

        Args:
            message: Text to display.
            level: One of 'success', 'error', 'info', 'warning', 'normal'.
        """
        color = self._colors.get(level, self._colors["normal"])

        fmt = QTextCharFormat()
        fmt.setForeground(color)

        cursor = self._text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        # Add newline if not empty
        if not self._text_edit.document().isEmpty():
            cursor.insertText("\n", fmt)

        cursor.insertText(message, fmt)
        self._text_edit.setTextCursor(cursor)
        self._text_edit.ensureCursorVisible()

    def clear_log(self) -> None:
        self._text_edit.clear()

    def set_title(self, title: str) -> None:
        self._title.setText(title)
