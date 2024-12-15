
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class DelayedTooltipListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.timeout.connect(self._show_tooltip)
        self._current_item = None

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if item != self._current_item:
            self._tooltip_timer.stop()
            QToolTip.hideText()
            self._current_item = item
            if item:
                self._tooltip_timer.start(250)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._tooltip_timer.stop()
        QToolTip.hideText()
        super().leaveEvent(event)

    def _show_tooltip(self):
        if self._current_item:
            QToolTip.showText(QCursor.pos(), self._current_item.toolTip(), self)