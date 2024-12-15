
try:
    from internal_os import os, path # type: ignore
    from internal_shutil import shutil # type: ignore
    from internal_threading import threading # type: ignore
except ImportError:
    from os import path

from widgets.delayed_tooltip_list_widget import DelayedTooltipListWidget
from dialogs.custom_confirm_dialog import CustomConfirmDialog

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class FavoritesListWidget(DelayedTooltipListWidget):
    favorite_removed = Signal()  # Сигнал для уведомления о удалении

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        index = self.indexAt(position)
        if index.isValid():
            menu = QMenu()
            remove_action = QAction("Удалить из избранного", self)
            menu.addAction(remove_action)
            action = menu.exec(self.viewport().mapToGlobal(position))
            if action == remove_action:
                self.remove_favorite_item(index)

    def remove_favorite_item(self, index):
        item = self.item(index.row())
        if item:
            # Подтверждение удаления
            confirm_dialog = CustomConfirmDialog(
                self, title="Удалить из избранного",
                message=f"Вы действительно хотите удалить '{item.text()}' из избранного?"
            )
            if confirm_dialog.exec() and confirm_dialog.result:
                self.takeItem(index.row())
                self.favorite_removed.emit()  # Извещаем о том, что элемент удален