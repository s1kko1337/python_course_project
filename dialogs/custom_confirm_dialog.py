from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class CustomConfirmDialog(QDialog):
    def __init__(self, parent=None, title="Подтверждение", message="Вы уверены?"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.result = False
        self.setFixedSize(400, 150)
        self.init_ui(message)

    def init_ui(self, message):
        layout = QVBoxLayout()

        self.label = QLabel(message)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        buttons_layout = QHBoxLayout()
        self.yes_button = QPushButton("Да")
        self.no_button = QPushButton("Нет")
        buttons_layout.addWidget(self.yes_button)
        buttons_layout.addWidget(self.no_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.yes_button.clicked.connect(self.on_yes)
        self.no_button.clicked.connect(self.on_no)

    def on_yes(self):
        self.result = True
        self.accept()

    def on_no(self):
        self.result = False
        self.reject()