try:
    from internal_os import os, path # type: ignore
except ImportError:
    from os import path

from PySide6.QtCore import *
from PySide6.QtGui import *

from PySide6.QtWidgets import *

class AboutProgramDialog(QDialog):
    def __init__(self, parent=None, title="О программе"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(800, 600)  
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        # Левая сторона: список пунктов
        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(200)
        self.list_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        topics = [
            "Начало работы", "Поиск", "Работа с папками", "Работа с файлами",
            "Работа с фильтрами", "Работа с избранным/главным",
            "Режимы отображения", "Выход из приложения"
        ]
        self.list_widget.addItems(topics)
        self.list_widget.currentItemChanged.connect(self.on_topic_selected)
        layout.addWidget(self.list_widget)

        # Правая сторона: отображение содержимого
        self.content_display = QTextBrowser()
        self.content_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_display.setOpenExternalLinks(True)
        layout.addWidget(self.content_display)

        self.setLayout(layout)

    def on_topic_selected(self, current, previous):
        if current:
            topic = current.text()
            content = self.get_content_for_topic(topic)
            self.content_display.setHtml(content)

    def get_content_for_topic(self, topic):
        resources_path = path.join(path.dirname(__file__), 'resources', 'images')

        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 10px;
                }}
                h2 {{
                    color: #2F4F4F;
                }}
                p {{
                    text-align: justify;
                    font-size: 14px;
                }}
                img {{
                    float: right;
                    margin: 10px;
                    max-width: 100%;
                    height: auto;
                }}
                .content-section {{
                    overflow: auto;
                }}
            </style>
        </head>
        <body>
            <h2>{title}</h2>
            <div class="content-section">
                <p>{text}</p>
            </div>
            <img src="file:///{image_path}" alt="{image_alt}">
        </body>
        </html>
        """

        content_dict = {
            "Начало работы": {
                "title": "Начало работы",
                "text": "На главном окне представлены основные элементы интерфейса, такие как навигация по каталогам, боковая панель с историей посещений и избранным, а также верхнее меню для выполнения основных операций. Главный экран адаптируется к размеру окна для удобства работы.",
                "image": "start_screen.png",
                "image_alt": "Начало работы"
            },
            "Поиск": {
                "title": "Поиск",
                "text": "Для поиска файлов или папок введите ключевое слово в строку поиска. Выпадающее меню предложит подходящие результаты. Для открытия файла дважды щелкните ЛКМ или используйте ПКМ для перехода в директорию.",
                "image": "search_screen.png",
                "image_alt": "Поиск"
            },
            "Работа с папками": {
                "title": "Работа с папками",
                "text": "Приложение позволяет просматривать содержимое папок, создавать новые папки, переименовывать, копировать и удалять их. Все действия выполняются через контекстное меню или кнопки на панели инструментов.",
                "image": "folder_operations.png",
                "image_alt": "Работа с папками"
            },
            "Работа с файлами": {
                "title": "Работа с файлами",
                "text": "Пользователи могут выполнять основные операции с файлами: открытие, переименование, удаление, копирование, вставка и перемещение. Панель предпросмотра отображает содержимое поддерживаемых файлов.",
                "image": "file_operations.png",
                "image_alt": "Работа с файлами"
            },
            "Работа с фильтрами": {
                "title": "Работа с фильтрами",
                "text": "Поиск поддерживает фильтры по типу файлов, дате изменения и размеру. Результаты отображаются в списке с подробностями, что упрощает навигацию и выбор.",
                "image": "search_filters.png",
                "image_alt": "Работа с поиском"
            },
            "Работа с избранным/главным": {
                "title": "Работа с избранным/главным",
                "text": "Пользователи могут добавлять папки в избранное для быстрого доступа. Избранные элементы сохраняются при выходе из приложения и доступны на боковой панели.",
                "image": "favorites_screen.png",
                "image_alt": "Работа с избранным"
            },
            "Режимы отображения": {
                "title": "Режимы отображения",
                "text": "Для удобства работы приложение поддерживает несколько режимов отображения: список, крупные значки, мелкие значки и плитка. Выбранный режим сохраняется при повторном запуске приложения.",
                "image": "view_modes.png",
                "image_alt": "Режимы отображения"
            },
            "Выход из приложения": {
                "title": "Выход из приложения",
                "text": "Для выхода из приложения необходимо нажать на крестик в верхнем углу экрана. Список избранного будет сохранен.",
                "image": "exit_screen.png",
                "image_alt": "Выход из приложения"
            }
        }

        data = content_dict.get(topic)
        if data:
            image_path = path.join(resources_path, data.get("image"))
            html_content = html_template.format(
                title=data.get("title", ""),
                text=data.get("text", ""),
                image_path=image_path,
                image_alt=data.get("image_alt", "")
            )
            return html_content
        else:
            return "<p>Информация недоступна.</p>"
