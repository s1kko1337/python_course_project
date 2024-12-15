try:
    from internal_os import os, path # type: ignore
except ImportError:
    from os import path

from PySide6.QtCore import *
from PySide6.QtGui import *

import os
from PySide6.QtWidgets import *

class AboutDeveloperDialog(QDialog):
    def __init__(self, parent=None, title="О разработчике"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)  
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.content_display = QTextBrowser()
        self.content_display.setOpenExternalLinks(True)

        resources_path = os.path.join(os.path.dirname(__file__), 'resources', 'images')
        image_path = os.path.join(resources_path, 'developer_photo.png') 

        html_content = f"""
        <h2>О разработчике</h2>
        <p><strong>ФИО:</strong> Ивахненко Михаил Романович</p>
        <p><strong>Курс:</strong> 3</p>
        <p><strong>Группа:</strong> бПО-221</p>
        """

        self.content_display.setHtml(html_content)
        layout.addWidget(self.content_display)

        # Кнопка закрытия
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.accept)
        layout.addWidget(self.close_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)