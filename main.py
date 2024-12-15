import sys
import unittest
from os import path

from PySide6.QtWidgets import QApplication
from widgets.file_manager import FileManager

if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = FileManager()
        window.show()
        sys.exit(app.exec())
