try:
    from internal_os import os, path # type: ignore
    from internal_shutil import shutil # type: ignore
    from internal_threading import threading # type: ignore
except ImportError:
    import os
    from os import path
    import shutil
    import psutil
    import logging

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widgets.favourites_list_widget import FavoritesListWidget
from widgets.delayed_tooltip_list_widget import DelayedTooltipListWidget
from widgets.delayed_tooltip_widget import DelayedTooltipListWidget
from dialogs.about_program_dialog import AboutProgramDialog
from dialogs.about_developer_dialog import AboutDeveloperDialog
from dialogs.custom_confirm_dialog import CustomConfirmDialog
from dialogs.custom_input_dialog import CustomInputDialog
from dialogs.custom_message_dialog import CustomMessageDialog
from dialogs.new_file_dialog import NewFileDialog

from utils.search_thread import SearchThread

class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_sort_column = 0  
        self.sort_order = Qt.AscendingOrder
        self.setWindowTitle("Файловый Менеджер")
        self.setGeometry(100, 100, 1000, 700)

        self.history = []
        self.back_history = []
        self.forward_history = []
        self.clipboard = None
        self.clip_action = None
        self.current_path = os.path.expanduser("~")

        self.in_search_mode = False 

        self.init_ui()
        self.show_files_in_directory(self.current_path)
        self.settings = QSettings("S1kko1337", "Course python app")
        theme = self.settings.value("theme", "system")
        self.apply_stylesheet(theme)
        self.set_system_theme()
        self.load_favorites()
        
        # Установка иконки приложения
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'folder-management.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print("Иконка приложения не найдена по пути:", icon_path)
        
        
        # Создаем QLabel для отображения анимации загрузки
        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("background-color: rgba(0, 0, 0, 128);")
        self.loading_label.setVisible(False)

        # Загружаем .gif файл с анимацией загрузки
        loading_gif_path = os.path.join(os.path.dirname(__file__), 'resources', 'loading.gif')
        self.loading_movie = QMovie(loading_gif_path)
        self.loading_label.setMovie(self.loading_movie)
        

    def init_ui(self):
        self.create_menu_bar()
        self.create_navigation_toolbar()
        self.create_main_layout()
        self.connect_signals()
        pass

    def create_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # "Файл" Menu
        file_menu = self.menu_bar.addMenu("Файл")
        home_action = QAction("Главная", self)
        view_files_action = QAction("Просмотр файлов", self)
        create_folder_action = QAction("Создать папку", self)
        create_file_action = QAction("Создать файл", self)
        exit_action = QAction("Выйти", self)
        file_menu.addAction(home_action)
        file_menu.addAction(view_files_action)
        file_menu.addSeparator()
        file_menu.addAction(create_folder_action)
        file_menu.addAction(create_file_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        home_action.triggered.connect(self.show_home)
        view_files_action.triggered.connect(self.show_file_view)
        create_folder_action.triggered.connect(self.create_folder)
        create_file_action.triggered.connect(self.create_file)
        exit_action.triggered.connect(self.close)

        view_menu = self.menu_bar.addMenu("Вид")
        view_list_action = QAction("Список", self)
        view_large_icons_action = QAction("Крупные значки", self)
        view_small_icons_action = QAction("Мелкие значки", self)
        view_tile_action = QAction("Плитка", self)
        view_menu.addAction(view_list_action)
        view_menu.addAction(view_large_icons_action)
        view_menu.addAction(view_small_icons_action)
        view_menu.addAction(view_tile_action)

        # "Сортировка" Menu
        sort_menu = self.menu_bar.addMenu("Сортировка")
        sort_name_action = QAction("По имени", self)
        sort_date_action = QAction("По дате", self)
        sort_size_action = QAction("По размеру", self)
        sort_menu.addAction(sort_name_action)
        sort_menu.addAction(sort_date_action)
        sort_menu.addAction(sort_size_action)
        sort_menu.addSeparator()
        sort_order_action = QAction("По убыванию", self)
        sort_order_action.setCheckable(True)
        sort_menu.addAction(sort_order_action)

        sort_name_action.triggered.connect(self.sort_by_name)
        sort_date_action.triggered.connect(self.sort_by_date)
        sort_size_action.triggered.connect(self.sort_by_size)
        sort_order_action.toggled.connect(self.toggle_sort_order)
        
        theme_menu = self.menu_bar.addMenu("Тема")
        theme_light_action = QAction("Светлая", self)
        theme_dark_action = QAction("Тёмная", self)
        theme_system_action = QAction("Системная", self)
        theme_menu.addAction(theme_light_action)
        theme_menu.addAction(theme_dark_action)
        theme_menu.addAction(theme_system_action)

        # Меню "О программе"
        about_menu = self.menu_bar.addMenu("О программе")
        about_program_action = QAction("О программе", self)
        about_developer_action = QAction("О разработчике", self)
        about_menu.addAction(about_program_action)
        about_menu.addAction(about_developer_action)

        about_program_action.triggered.connect(self.show_about_program)
        about_developer_action.triggered.connect(self.show_about_developer)
    
        view_list_action.triggered.connect(self.view_as_list)
        view_large_icons_action.triggered.connect(self.view_large_icons)
        view_small_icons_action.triggered.connect(self.view_small_icons)
        view_tile_action.triggered.connect(self.view_tile)
        theme_light_action.triggered.connect(self.set_light_theme)
        theme_dark_action.triggered.connect(self.set_dark_theme)
        theme_system_action.triggered.connect(self.set_system_theme)
        logging.debug('Вызов create_menu_bar')
        
    def show_file_view(self):
        self.main_layout.setCurrentWidget(self.splitter)
        
    def apply_stylesheet(self, theme):
        self.settings.setValue("theme", theme)
        if theme == "light":
            self.setStyleSheet("")
        elif theme == "dark":
            qss_file = os.path.join(os.path.dirname(__file__), 'themes', 'dark_theme.qss')
            with open(qss_file, "r") as f:
                dark_stylesheet = f.read()
            self.setStyleSheet(dark_stylesheet)
        elif theme == "system":
            self.setStyleSheet("")
    
    def set_light_theme(self):
        self.apply_stylesheet("light")

    def set_dark_theme(self):
        self.apply_stylesheet("dark")

    def set_system_theme(self):
        self.apply_stylesheet("system")
    
    def create_navigation_toolbar(self):
        self.nav_toolbar = QToolBar("Навигация")
        self.addToolBar(Qt.TopToolBarArea, self.nav_toolbar)

        home_action = QAction(QIcon.fromTheme("go-home"), "Главная", self)
        home_action.triggered.connect(self.show_home)
        self.nav_toolbar.addAction(home_action)

        file_view_icon = QIcon.fromTheme("document-open") 
        view_files_action = QAction(file_view_icon, "Просмотр файлов", self)
        view_files_action.triggered.connect(self.show_file_view)
        self.nav_toolbar.addAction(view_files_action)

        back_action = QAction("Назад", self)
        forward_action = QAction("Вперед", self)
        refresh_action = QAction("Обновить", self)

        back_action.triggered.connect(self.go_back)
        forward_action.triggered.connect(self.go_forward)
        refresh_action.triggered.connect(self.refresh)

        self.nav_toolbar.addAction(back_action)
        self.nav_toolbar.addAction(forward_action)
        self.nav_toolbar.addAction(refresh_action)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Введите путь")
        self.path_edit.returnPressed.connect(self.on_path_entered)

        spacer = QWidget()
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        spacer.setSizePolicy(size_policy)
        self.nav_toolbar.addWidget(spacer)
        self.nav_toolbar.addWidget(self.path_edit)

        # Поле поиска
        search_label = QLabel("Поиск:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите запрос")
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.on_search)

        self.nav_toolbar.addWidget(search_label)
        self.nav_toolbar.addWidget(self.search_edit)
        self.nav_toolbar.addWidget(self.search_button)
        
        toggle_preview_action = QAction("Предпросмотр", self)
        toggle_preview_action.setCheckable(True)
        toggle_preview_action.setChecked(False)
        toggle_preview_action.triggered.connect(self.toggle_preview_pane)
        self.nav_toolbar.addAction(toggle_preview_action)
        logging.debug('Вызов create_navigation_toolbar')
        
    def create_main_layout(self):
        self.main_layout = QStackedWidget() 

        self.splitter = QSplitter(Qt.Horizontal)
        self.create_sidebar()   

        # Создаем новый сплиттер для области просмотра файлов и панели предпросмотра
        self.file_view_splitter = QSplitter(Qt.Horizontal)
        self.create_file_view()
        self.create_preview_pane()  

        # Добавляем область просмотра файлов и панель предпросмотра в новый сплиттер
        self.file_view_splitter.addWidget(self.view_stack)
        self.file_view_splitter.addWidget(self.preview_widget)  

        # Изначально скрываем панель предпросмотра
        self.file_view_splitter.setSizes([1, 0])    

        # Добавляем боковую панель и новый сплиттер в основной сплиттер
        self.splitter.addWidget(self.sidebar_widget)
        self.splitter.addWidget(self.file_view_splitter)    

        self.adjust_sidebar_width()
        self.create_home_widget()   

        self.main_layout.addWidget(self.home_widget)
        self.main_layout.addWidget(self.splitter)   

        self.setCentralWidget(self.main_layout)
        logging.debug('Вызов create_main_layout')
        
    def adjust_sidebar_width(self):
        tab_bar = self.tab_widget.tabBar()
        total_tab_width = 0
        for i in range(tab_bar.count()):
            total_tab_width += tab_bar.tabRect(i).width()

        padding = 20 
        sidebar_width = total_tab_width + padding

        self.sidebar_widget.setFixedWidth(sidebar_width)

    def create_preview_pane(self):
        self.preview_widget = QWidget()
        self.preview_layout = QVBoxLayout()
        self.preview_widget.setLayout(self.preview_layout)

        # Добавляем тулбар с кнопкой скрытия
        self.preview_toolbar = QToolBar()
        hide_action = QAction("Скрыть", self)
        hide_action.triggered.connect(self.toggle_preview_pane)
        self.preview_toolbar.addAction(hide_action)
        self.preview_layout.addWidget(self.preview_toolbar)

        # Добавляем QTextBrowser для отображения информации о файле
        self.preview_text = QTextBrowser()
        self.preview_layout.addWidget(self.preview_text)
    
    def toggle_preview_pane(self):
        sizes = self.file_view_splitter.sizes()
        if sizes[1] == 0:
            # Показываем панель предпросмотра
            self.file_view_splitter.setSizes([int(sizes[0] * 0.7), int(sizes[0] * 0.3)])
            self.preview_visible = True
        else:
            # Скрываем панель предпросмотра
            self.file_view_splitter.setSizes([sizes[0] + sizes[1], 0])
            self.preview_visible = False

    def load_favorites(self):
        favorites = self.settings.value("favorites", [])
        if favorites:
            for path_str in favorites:
                if os.path.exists(path_str):
                    item = QListWidgetItem()
                    file_info = QFileInfo(path_str)
                    icon_provider = QFileIconProvider()
                    icon = icon_provider.icon(file_info)
                    item.setIcon(icon)
                    item.setText(os.path.basename(path_str))
                    item.setData(Qt.UserRole, path_str)
                    item.setToolTip(path_str)
                    self.favorites_list.addItem(item)
                
    def create_sidebar(self):
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_widget.setLayout(self.sidebar_layout)

        self.tab_widget = QTabWidget()
        self.sidebar_layout.addWidget(self.tab_widget)

        # Быстрый доступ
        self.quick_access_list = DelayedTooltipListWidget()
        self.quick_access_paths = {
            "Рабочий стол": os.path.join(os.path.expanduser("~"), "Desktop"),
            "Документы": os.path.join(os.path.expanduser("~"), "Documents"),
            "Загрузки": os.path.join(os.path.expanduser("~"), "Downloads"),
            "Изображения": os.path.join(os.path.expanduser("~"), "Pictures"),
            "Музыка": os.path.join(os.path.expanduser("~"), "Music"),
            "Видео": os.path.join(os.path.expanduser("~"), "Videos")
        }

        for name, path in self.quick_access_paths.items():
            item = QListWidgetItem()
            file_info = QFileInfo(path)
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(file_info)
            item.setIcon(icon)
            item.setText(name)
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.quick_access_list.addItem(item)

        self.favorites_list = FavoritesListWidget()
        self.favorites_list.favorite_removed.connect(self.save_favorites)
        self.history_list = DelayedTooltipListWidget()

        self.tab_widget.addTab(self.quick_access_list, "Быстрый доступ")
        self.tab_widget.addTab(self.favorites_list, "Избранное")
        self.tab_widget.addTab(self.history_list, "История")

        self.splitter.addWidget(self.sidebar_widget)
        self.adjust_sidebar_width()

    def on_search_finished(self):
        self.hide_loading_indicator()
        if not self.in_search_mode:
            self.tree_view.setModel(self.model)
            self.list_view.setModel(self.model)
            self.tree_view.setRootIndex(self.model.index(self.current_path))
            self.list_view.setRootIndex(self.model.index(self.current_path))
    def create_file_view(self):
        self.model = QFileSystemModel()
        self.model.setRootPath(self.current_path)

        # Tree view (Список)
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.current_path))
        self.tree_view.setSortingEnabled(True)
        self.tree_view.doubleClicked.connect(self.on_tree_double_click)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_file_select)
        self.tree_view.setExpandsOnDoubleClick(False)

        # List view (Иконки)
        self.list_view = QListView()
        self.list_view.setModel(self.model)
        self.list_view.setRootIndex(self.model.index(self.current_path))
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(96, 96)) 
        self.list_view.setGridSize(QSize(110, 110))
        self.list_view.setResizeMode(QListView.Adjust)
        self.list_view.doubleClicked.connect(self.on_list_double_click)
        self.list_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_view.customContextMenuRequested.connect(self.show_context_menu)

        # QStackedWidget для переключения между видами
        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.tree_view)
        self.view_stack.addWidget(self.list_view)

        self.splitter.addWidget(self.view_stack)
    def connect_signals(self):
        self.quick_access_list.itemDoubleClicked.connect(self.on_quick_access_select)
        self.history_list.itemDoubleClicked.connect(self.on_history_select)
        self.favorites_list.itemDoubleClicked.connect(self.on_favorite_select)
        self.tree_view.selectionModel().selectionChanged.connect(self.on_file_select)
        self.list_view.selectionModel().selectionChanged.connect(self.on_file_select)
        self.tree_view.doubleClicked.connect(self.on_tree_double_click)
        self.list_view.doubleClicked.connect(self.on_list_double_click)
        logging.debug('Вызов connect_signals')

    def on_list_double_click(self, index):
        self.open_item()
        
    def view_as_list(self):
        self.view_stack.setCurrentWidget(self.tree_view)

    def get_icon_for_path(self, path):
        file_info = QFileInfo(path)
        icon_provider = QFileIconProvider()
        icon = icon_provider.icon(file_info)
        return icon
    
    def toggle_sort_order(self, checked):
        if checked:
            self.sort_order = Qt.DescendingOrder
        else:
            self.sort_order = Qt.AscendingOrder
        self.sort_by_current()

    def sort_by_current(self):
        if self.current_sort_column is not None:
            self.model.sort(self.current_sort_column, self.sort_order)
        
    def view_large_icons(self):
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(96, 96))
        self.list_view.setGridSize(QSize(110, 110))
        self.view_stack.setCurrentWidget(self.list_view)

    def show_home(self):
        self.main_layout.setCurrentWidget(self.home_widget)
    
    def view_small_icons(self):
        self.list_view.setViewMode(QListView.IconMode)
        self.list_view.setIconSize(QSize(48, 48)) 
        self.list_view.setGridSize(QSize(60, 60))
        self.view_stack.setCurrentWidget(self.list_view)
    
    def sort_by_name(self):
        self.current_sort_column = 0
        self.model.sort(0, self.sort_order)
    
    def sort_by_date(self):
        self.current_sort_column = 3
        self.model.sort(3, self.sort_order)
    
    def sort_by_size(self):
        self.current_sort_column = 1
        self.model.sort(1, self.sort_order)
    
    def view_tile(self):
        self.list_view.setViewMode(QListView.ListMode)
        self.list_view.setIconSize(QSize(48, 48))
        self.list_view.setSpacing(5)
        self.view_stack.setCurrentWidget(self.list_view)
    
    def show_files_in_directory(self, path):
        try:
            if os.path.exists(path):
                self.current_path = path 
                self.model.setRootPath(path)
                index = self.model.index(path)

                if self.tree_view.model() != self.model:
                    self.tree_view.setModel(self.model)

                if self.list_view.model() != self.model:
                    self.list_view.setModel(self.model)

                self.tree_view.setRootIndex(index)
                self.list_view.setRootIndex(index)
                self.path_edit.setText(path)
                self.update_history(path)
                self.update_search_completer()
                self.sort_by_current()
                self.show_file_view()
            else:
                self.show_error("Путь не существует")
        except Exception as e:
            self.show_error(f"Ошибка при открытии директории: {str(e)}")

    def update_history(self, path):
        if path not in self.history:
            self.history.append(path)
            item = QListWidgetItem()
            file_info = QFileInfo(path)
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(file_info)
            item.setIcon(icon)
            if os.path.isdir(path):
                item.setText(file_info.fileName() or path)
            else:
                item.setText(file_info.fileName())
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.history_list.addItem(item)
        if self.back_history and self.back_history[-1] != path:
            self.back_history.append(path)
        elif not self.back_history:
            self.back_history.append(path)\

    def on_quick_access_select(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.show_files_in_directory(path)

    def on_history_select(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.show_files_in_directory(path)

    def show_about_program(self):
        dialog = AboutProgramDialog(self)
        dialog.exec()

    def show_about_developer(self):
        dialog = AboutDeveloperDialog(self)
        dialog.exec()
    def on_favorite_select(self, item):
       path_str = item.data(Qt.UserRole)
       if path_str and path.exists(path_str):
           if path.isfile(path_str):
               directory = path.dirname(path_str)
               self.show_files_in_directory(directory)
               index = self.model.index(path_str)
               if index.isValid():
                   current_view = self.view_stack.currentWidget()
                   current_view.setCurrentIndex(index)
           else:
               self.show_files_in_directory(path_str)
       else:
           self.show_error("Путь не существует")

    def show_context_menu(self, position):
        sender_view = self.sender()
        index = sender_view.indexAt(position)
        global_position = sender_view.viewport().mapToGlobal(position)

        if index.isValid():
            sender_view.setCurrentIndex(index)
            if self.in_search_mode and sender_view == self.tree_view:
                # Контекстное меню для результатов поиска
                menu = QMenu()
                open_action = QAction("Открыть", self)
                go_to_directory_action = QAction("Перейти в директорию", self)
                menu.addAction(open_action)
                menu.addAction(go_to_directory_action)

                action = menu.exec(global_position)

                if action == open_action:
                    self.open_search_result_item(index)
                elif action == go_to_directory_action:
                    self.go_to_directory_of_item(index)
            else:
                model = sender_view.model()

                if isinstance(model, QFileSystemModel):
                    file_info = model.fileInfo(index)
                else:
                    path = model.data(index, Qt.UserRole)
                    if not path:
                        return
                    file_info = QFileInfo(path)

                is_dir = file_info.isDir()
                menu = QMenu()

                open_action = QAction("Открыть", self)
                rename_action = QAction("Переименовать", self)
                delete_action = QAction("Удалить", self)
                cut_action = QAction("Вырезать", self)
                copy_action = QAction("Копировать", self)
                add_to_favorites_action = QAction("Добавить в избранное", self)

                menu.addAction(open_action)
                menu.addAction(rename_action)
                menu.addAction(delete_action)
                menu.addSeparator()
                menu.addAction(cut_action)
                menu.addAction(copy_action)

                if is_dir and self.clipboard:
                    paste_action = QAction("Вставить", self)
                    menu.addAction(paste_action)

                menu.addSeparator()
                menu.addAction(add_to_favorites_action)

                action = menu.exec(global_position)

                if action == open_action:
                    self.open_item()
                elif action == rename_action:
                    self.rename_item()
                elif action == delete_action:
                    self.delete_item()
                elif action == cut_action:
                    self.cut_item()
                elif action == copy_action:
                    self.copy_item()
                # elif action == go_to_directory_action:
                #     self.go_to_directory_of_item(index)
                elif 'paste_action' in locals() and action == paste_action:
                    self.paste_item(target_directory=file_info.absoluteFilePath())
                elif action == add_to_favorites_action:
                    path = file_info.absoluteFilePath()
                    self.add_to_favorites(path)
        else:
            menu = QMenu()
            create_menu = menu.addMenu("Создать")
            new_folder_action = QAction("Папку", self)
            new_file_action = QAction("Файл", self)
            create_menu.addAction(new_folder_action)
            create_menu.addAction(new_file_action)

            if self.clipboard:
                paste_action = QAction("Вставить", self)
                menu.addAction(paste_action)

            action = menu.exec(global_position)

            if action == new_folder_action:
                self.create_folder()
            elif action == new_file_action:
                self.create_file()
            elif 'paste_action' in locals() and action == paste_action:
                self.paste_item()

    def select_file_in_view(self, file_path):
        index = self.model.index(file_path)
        if index.isValid():
            current_view = self.view_stack.currentWidget()
            selection_model = current_view.selectionModel()
            selection_model.clearSelection()
            selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            current_view.scrollTo(index)
    
    def go_to_directory_of_item(self, index):
        file_path = index.sibling(index.row(), 0).data(Qt.UserRole)
        if file_path:
            directory = os.path.dirname(file_path)
            if os.path.exists(directory):
                self.in_search_mode = False
                self.tree_view.setModel(self.model)
                self.list_view.setModel(self.model)
                self.show_files_in_directory(directory)
                # Выделяем файл в представлении
                self.select_file_in_view(file_path)
            else:
                self.show_error("Директория не найдена")
            
    def get_selected_item_path(self):
        current_view = self.view_stack.currentWidget()
        if current_view == self.tree_view:
            indexes = current_view.selectedIndexes()
        elif current_view == self.list_view:
            indexes = current_view.selectedIndexes()
        else:
            indexes = []    

        if indexes:
            index = indexes[0]
            model = current_view.model()    

            if isinstance(model, QFileSystemModel):
                file_info = model.fileInfo(index)
                return file_info.absoluteFilePath()
            elif isinstance(model, QStandardItemModel):
                name_index = index.sibling(index.row(), 0)  
                path = model.data(name_index, Qt.UserRole)
                return path if path else None
        return None

    def copy_item(self):
        path = self.get_selected_item_path()
        if path:
            self.clipboard = path
            self.clip_action = 'copy'
            
    def open_item(self):
        path = self.get_selected_item_path()
        if path:
            if os.path.isdir(path):
                self.show_files_in_directory(path)
            else:
                try:
                    os.startfile(path)
                except Exception as e:
                    self.show_error(f"Не удалось открыть файл: {e}")
        else:
            #self.show_error("Путь не найден")
            pass
    
    def open_search_result_item(self, index):
        file_path = index.sibling(index.row(), 0).data(Qt.UserRole)
        if file_path:
            if os.path.isdir(file_path):
                self.show_files_in_directory(file_path)
            else:
                try:
                    os.startfile(file_path)
                except Exception as e:
                    self.show_error(f"Не удалось открыть файл: {e}")
        
    
    def rename_item(self):
        old_path = self.get_selected_item_path()
        if old_path:
            if path.isdir(old_path):
                old_name = path.basename(old_path)
                dialog = CustomInputDialog(self, title="Переименовать папку", prompt="Введите новое название папки:")
                dialog.text_edit.setText(old_name)  
                if dialog.exec():
                    new_name = dialog.value
                    if new_name:
                        new_name = path.splitext(new_name)[0]
                        new_path = path.join(path.dirname(old_path), new_name)
                        if path.exists(new_path):
                            self.show_error("Папка с таким именем уже существует")
                            return
                        try:
                            os.rename(old_path, new_path)
                            self.refresh()
                        except Exception as e:
                            self.show_error(f"Не удалось переименовать папку: {e}")
            elif path.isfile(old_path):
                old_dir = path.dirname(old_path)
                old_filename = path.basename(old_path)
                old_name, old_ext = path.splitext(old_filename)
                dialog = CustomInputDialog(self, title="Переименовать файл", prompt="Введите новое название файла:")
                dialog.text_edit.setText(old_name)  
                if dialog.exec():
                    new_name = dialog.value
                    if new_name:
                        new_filename = new_name + old_ext
                        new_path = path.join(old_dir, new_filename)
                        if path.exists(new_path):
                            self.show_error("Файл с таким именем уже существует")
                            return
                        try:
                            os.rename(old_path, new_path)
                            self.refresh()
                        except Exception as e:
                            self.show_error(f"Не удалось переименовать файл: {e}")
            else:
                self.show_error("Неизвестный тип объекта")

    def delete_item(self):
        path = self.get_selected_item_path()
        if path:
            confirm_dialog = CustomConfirmDialog(
                self, title="Удалить",
                message=f"Вы действительно хотите удалить '{os.path.basename(path)}'?"
            )
            if confirm_dialog.exec() and confirm_dialog.result:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                    self.refresh()
                except Exception as e:
                    self.show_error(f"Не удалось удалить: {e}")

    def cut_item(self):
        path = self.get_selected_item_path()
        if path:
            self.clipboard = path
            self.clip_action = 'cut'

    def paste_item(self, target_directory=None):
        if self.clipboard:
            if target_directory and os.path.isdir(target_directory):
                dest_dir = target_directory
            else:
                dest_dir = self.current_path
            dest = os.path.join(dest_dir, os.path.basename(self.clipboard))
            try:
                if os.path.isdir(self.clipboard):
                    if self.clip_action == 'cut':
                        shutil.move(self.clipboard, dest)
                    elif self.clip_action == 'copy':
                        shutil.copytree(self.clipboard, dest)
                else:
                    if self.clip_action == 'cut':
                        shutil.move(self.clipboard, dest)
                    elif self.clip_action == 'copy':
                        shutil.copy2(self.clipboard, dest)
                self.clipboard = None
                self.clip_action = None
                self.refresh()
            except Exception as e:
                self.show_error(f"Не удалось вставить: {e}")

    def create_folder(self):
        dialog = CustomInputDialog(self, title="Новая папка", prompt="Введите название папки:")
        if dialog.exec():
            folder_name = dialog.value
            if folder_name:
                path = os.path.join(self.current_path, folder_name)
                try:
                    os.makedirs(path, exist_ok=True)
                    self.refresh()
                except Exception as e:
                    self.show_error(f"Не удалось создать папку: {e}")

    def create_file(self):
        dialog = NewFileDialog(self, title="Новый файл")
        if dialog.exec():
            file_name = dialog.file_name
            file_type = dialog.file_type
            if file_name and file_type:
                full_file_name = file_name + file_type
                path = os.path.join(self.current_path, full_file_name)
                try:
                    with open(path, 'w') as f:
                        pass
                    self.refresh()
                except Exception as e:
                    self.show_error(f"Не удалось создать файл: {e}")
                    
    def add_to_favorites(self, path=None):
        if not path:
            path = self.get_selected_item_path()
        if path:
            for index in range(self.favorites_list.count()):
                if self.favorites_list.item(index).data(Qt.UserRole) == path:
                    self.show_error("Элемент уже в избранном")
                    return
            item = QListWidgetItem()
            file_info = QFileInfo(path)
            icon_provider = QFileIconProvider()
            icon = icon_provider.icon(file_info)
            item.setIcon(icon)
            item.setText(os.path.basename(path))
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.favorites_list.addItem(item)
            self.save_favorites()

    def save_favorites(self):
        favorites = []
        for index in range(self.favorites_list.count()):
            path_str = self.favorites_list.item(index).data(Qt.UserRole)
            favorites.append(path_str)
        self.settings.setValue("favorites", favorites)
    
    def create_home_widget(self):
        self.home_widget = QWidget()
        main_layout = QVBoxLayout(self.home_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        quick_fav_label = QLabel("Быстрый доступ и Избранное")
        quick_fav_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        scroll_layout.addWidget(quick_fav_label)

        quick_fav_grid = QGridLayout()
        items = []

        for name, path in self.quick_access_paths.items():
            items.append((name, path))

        for index in range(self.favorites_list.count()):
            item = self.favorites_list.item(index)
            items.append((item.text(), item.data(Qt.UserRole)))

        for idx, (name, path) in enumerate(items):
            icon = self.get_icon_for_path(path)
            self.create_icon_button(icon, name, path, quick_fav_grid, idx)

        scroll_layout.addLayout(quick_fav_grid)

        recent_label = QLabel("Недавнее")
        recent_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        scroll_layout.addWidget(recent_label)

        recent_grid = QGridLayout()
        for idx in range(self.history_list.count()):
            item = self.history_list.item(idx)
            name = item.text()
            path = item.data(Qt.UserRole)
            icon = self.get_icon_for_path(path)
            self.create_icon_button(icon, name, path, recent_grid, idx)

        scroll_layout.addLayout(recent_grid)

        disk_label = QLabel("Выбор диска")
        disk_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        scroll_layout.addWidget(disk_label)

        disk_grid = QGridLayout()
        partitions = psutil.disk_partitions()
        for idx, partition in enumerate(partitions):    
            path = partition.mountpoint  
            name = os.path.basename(path.rstrip('/\\'))
            icon = QIcon.fromTheme("drive-harddisk")
            self.create_icon_button(icon, name, path, disk_grid, idx, disk=True)
        scroll_layout.addLayout(disk_grid)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def create_icon_button(self, icon, name, path, layout, idx, disk=False):
        button = QPushButton()
        button.setIcon(icon)
        button.setIconSize(QSize(64, 64))
        button.setFixedSize(80, 80)
        button.setToolTip(path)
        button.setFlat(True)
        button.setStyleSheet("border: none;")
        if disk:
            button.clicked.connect(lambda checked, p=path: self.on_disk_selected(p))
        else:
            button.clicked.connect(lambda checked, p=path: self.show_files_in_directory(p))

        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setFixedWidth(80)
        label.setStyleSheet("font-size: 10px;")

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.addWidget(button)
        vbox.addWidget(label)

        container = QWidget()
        container.setLayout(vbox)

        row = idx // 4 
        col = idx % 4
        layout.addWidget(container, row, col)
    
    def on_disk_selected(self, path):
        if os.path.exists(path):
            self.show_files_in_directory(path)
        else:
            self.show_error(f"Диск недоступен: {path}")
    
    def on_home_quick_access_select(self, index):
        sender = self.sender()
        path = sender.itemData(index)
        if path:
            self.show_files_in_directory(path)

    def on_home_recent_select(self, index):
        sender = self.sender()
        path = sender.itemData(index)
        if path:
            self.show_files_in_directory(path)

    def on_disk_select(self, index):
        sender = self.sender()
        disk = sender.itemText(index)
        if disk:
            self.show_files_in_directory(disk)
    def go_back(self):
        if len(self.back_history) > 1:
            self.forward_history.append(self.back_history.pop())
            path = self.back_history[-1]

            if self.in_search_mode:
                self.in_search_mode = False
                self.tree_view.setModel(self.model)
                self.list_view.setModel(self.model)

            self.current_path = path 
            self.path_edit.setText(path)
            self.show_files_in_directory(path)

    def go_forward(self):
        if self.forward_history:
            path = self.forward_history.pop()
            self.back_history.append(path)

            if self.in_search_mode:
                self.in_search_mode = False
                self.tree_view.setModel(self.model)
                self.list_view.setModel(self.model)

            self.current_path = path
            self.path_edit.setText(path)
            self.show_files_in_directory(path)

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and os.path.exists(parent):
            self.show_files_in_directory(parent)

    def refresh(self):
        self.show_files_in_directory(self.current_path)

    def on_path_entered(self):
        path = self.path_edit.text()
        if os.path.exists(path):
            self.show_files_in_directory(path)
        else:
            self.show_error("Путь не найден")

    def on_search(self):
        query = self.search_edit.text().strip()
        if query:
            self.in_search_mode = True
            if self.main_layout.currentWidget() == self.home_widget:
                self.show_file_view()

            if hasattr(self, 'search_thread'):
                if self.search_thread.isRunning():
                    self.search_thread.requestInterruption()
                    self.search_thread.wait()
                self.search_thread.deleteLater()

            self.search_thread = SearchThread(query, self.current_path)
            self.search_thread.results_ready.connect(self.on_search_results)
            self.search_thread.finished.connect(self.on_search_finished)
            self.search_thread.start()
            self.show_loading_indicator()
        else:
            self.in_search_mode = False
            self.tree_view.setModel(self.model)
            self.list_view.setModel(self.model)
            self.tree_view.setRootIndex(self.model.index(self.current_path))
            self.list_view.setRootIndex(self.model.index(self.current_path))

    def show_loading_indicator(self):
        self.loading_label.setVisible(True)
        self.loading_movie.start()
        self.loading_label.setGeometry(0, 0, self.width(), self.height())
        self.loading_label.raise_()

    def hide_loading_indicator(self):
        self.loading_movie.stop()
        self.loading_label.setVisible(False)
        
    def update_search_completer(self):
        files_and_dirs = set()
        for root, dirs, files in os.walk(self.current_path):
            files_and_dirs.update(files)
            files_and_dirs.update(dirs)
        completer_list = list(files_and_dirs)
        self.completer = QCompleter(completer_list)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_edit.setCompleter(self.completer)
    
    def search_files(self, query):
        matches = []
        for root, dirs, files in os.walk(self.current_path):
            for name in dirs + files:
                if query in name.lower():
                    matches.append(os.path.join(root, name))
        self.model.setNameFilters([f'*{query}*'])
        self.model.setNameFilterDisables(False)

    
    def on_search_results(self, matches):
        self.hide_loading_indicator()
        if matches:
            self.search_model = QStandardItemModel()
            self.search_model.setHorizontalHeaderLabels(['Имя', 'Путь', 'Тип', 'Размер', 'Дата изменения'])

            for file_path in matches:
                file_info = QFileInfo(file_path)
                name_item = QStandardItem(file_info.fileName())
                icon_provider = QFileIconProvider()
                icon = icon_provider.icon(file_info)
                name_item.setIcon(icon)
                name_item.setData(file_path, Qt.UserRole)

                path_item = QStandardItem(file_info.absoluteFilePath())
                type_item = QStandardItem(file_info.suffix())
                size_item = QStandardItem(str(file_info.size()))
                date_item = QStandardItem(file_info.lastModified().toString())

                self.search_model.appendRow([name_item, path_item, type_item, size_item, date_item])

            self.tree_view.setModel(self.search_model)
            self.view_stack.setCurrentWidget(self.tree_view)
            self.in_search_mode = True
        else:
            self.show_error("Ничего не найдено")
            self.in_search_mode = False
            self.tree_view.setModel(self.model)
            self.list_view.setModel(self.model)
            self.tree_view.setRootIndex(self.model.index(self.current_path))
            self.list_view.setRootIndex(self.model.index(self.current_path))
            self.path_edit.setText(self.current_path)

    def on_tree_double_click(self, index):
        self.open_item()
        
    def on_file_select(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            model = index.model()
            if isinstance(model, QFileSystemModel):
                file_path = self.model.filePath(index)
            else:
                # Для режима поиска
                file_path = index.data(Qt.UserRole)
            self.update_preview(file_path)
        else:
            self.preview_text.clear()

    
    def update_preview(self, file_path):
        if path.exists(file_path):
            if path.isfile(file_path):
                file_info = QFileInfo(file_path)
                details = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 10px;
                        }}
                        .image-preview {{
                            max-width: 100%;
                            height: auto;
                            display: block;
                            margin: 10px auto;
                        }}
                        pre {{
                            white-space: pre-wrap;
                            word-wrap: break-word;
                        }}
                    </style>
                </head>
                <body>
                    <b>Имя файла:</b> {file_info.fileName()}<br>
                    <b>Путь:</b> {file_info.absoluteFilePath()}<br>
                    <b>Размер:</b> {file_info.size()} байт<br>
                    <b>Дата изменения:</b> {file_info.lastModified().toString('dd.MM.yyyy HH:mm:ss')}<br>
                """ 
                if file_info.suffix().lower() in ['txt', 'py', 'md', 'csv', 'json']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(1000)
                        content = content.replace('<', '&lt;').replace('>', '&gt;')
                        details += f"<hr><pre>{content}</pre>"
                    except Exception as e:
                        details += f"<hr><i>Не удалось прочитать файл: {e}</i>"
                elif file_info.suffix().lower() in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                    image_url = QUrl.fromLocalFile(file_path).toString()
                    details += f"""
                    <hr>
                    <img src="{image_url}" alt="{file_info.fileName()}" class="image-preview">
                    """
                details += "</body></html>"
                self.preview_text.setHtml(details)
            elif path.isdir(file_path):
                details = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            margin: 10px;
                        }}
                    </style>
                </head>
                <body>
                    <b>Папка:</b> {file_path}<br>
                </body>
                </html>
                """
                self.preview_text.setHtml(details)
        else:
            self.preview_text.clear()

    def closeEvent(self, event):
        if hasattr(self, 'search_thread') and self.search_thread.isRunning():
            self.search_thread.requestInterruption()
            self.search_thread.wait()
            self.search_thread.deleteLater()
        super().closeEvent(event)
        
    def show_error(self, message):
        error_dialog = CustomMessageDialog(self, title="Ошибка", message=message)
        error_dialog.exec()