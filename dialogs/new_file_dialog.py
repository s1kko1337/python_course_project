
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class NewFileDialog(QDialog):
    def __init__(self, parent=None, title="Новый файл"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.file_name = None
        self.file_type = None
        self.custom_type = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поле для ввода имени файла
        name_layout = QHBoxLayout()
        name_label = QLabel("Имя файла:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Выпадающий список типов файлов
        type_layout = QHBoxLayout()
        type_label = QLabel("Тип файла:")
        self.type_combo = QComboBox()
        self.type_combo.addItems([".txt", ".py", ".md", ".csv", ".json"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Кнопка для ввода собственного типа файла
        self.custom_type_button = QPushButton("Не нашли свой тип?")
        self.custom_type_button.clicked.connect(self.show_custom_type_input)
        layout.addWidget(self.custom_type_button)

        # Поле для ввода собственного типа файла (скрыто по умолчанию)
        self.custom_type_edit = QLineEdit()
        self.custom_type_edit.setPlaceholderText("Введите свой тип файла (с точкой, например, .log)")
        self.custom_type_edit.hide()
        layout.addWidget(self.custom_type_edit)

        # Кнопки ОК и Отмена
        buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("ОК")
        self.cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.ok_button.clicked.connect(self.on_ok)
        self.cancel_button.clicked.connect(self.reject)

    def show_custom_type_input(self):
        self.custom_type_edit.show()
        self.type_combo.setEnabled(False)
        self.custom_type_button.setEnabled(False)

    def on_ok(self):
        self.file_name = self.name_edit.text()
        if self.custom_type_edit.isVisible():
            self.custom_type = self.custom_type_edit.text()
            self.file_type = self.custom_type
        else:
            self.file_type = self.type_combo.currentText()

        if not self.file_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите имя файла.")
            return
        if not self.file_type.startswith('.'):
            self.file_type = '.' + self.file_type
        self.accept()
        