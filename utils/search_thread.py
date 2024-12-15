try:
    from internal_os import os, path # type: ignore
except ImportError:
    import os
    from os import path

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class SearchThread(QThread):
    results_ready = Signal(list)

    def __init__(self, query, current_path):
        super().__init__()
        self.query = query.lower()
        self.current_path = current_path

    def run(self):
        matches = []
        try:
            for root, dirs, files in os.walk(self.current_path):
                if self.isInterruptionRequested():
                    return
                for name in files + dirs:
                    if self.isInterruptionRequested():
                        return
                    if self.query in name.lower():
                        full_path = os.path.join(root, name)
                        matches.append(full_path)
            self.results_ready.emit(matches)
        except Exception as e:
            pass