from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class CustomMessageDialog(QDialog):
    def __init__(self, parent=None, title="Сообщение", message=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 150)
        self.init_ui(message)

    def init_ui(self, message):
        layout = QVBoxLayout()

        self.label = QLabel(message)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.ok_button = QPushButton("ОК")
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.ok_button.clicked.connect(self.accept)