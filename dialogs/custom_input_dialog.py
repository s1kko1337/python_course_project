from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class CustomInputDialog(QDialog):
    def __init__(self, parent=None, title="Ввод", prompt="Введите значение"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.value = None
        self.setFixedSize(400, 150)
        self.init_ui(prompt)

    def init_ui(self, prompt):
        layout = QVBoxLayout()

        self.label = QLabel(prompt)
        layout.addWidget(self.label)

        self.text_edit = QLineEdit()
        layout.addWidget(self.text_edit)

        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("ОК")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.on_cancel)
        self.text_edit.returnPressed.connect(self.on_ok)

    def on_ok(self):
        self.value = self.text_edit.text()
        self.accept()

    def on_cancel(self):
        self.value = None
        self.reject()
