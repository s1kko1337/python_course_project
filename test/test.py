import logging
import unittest
from unittest import mock
from utils.search_thread import SearchThread
from widgets.file_manager import FileManager
from PySide6.QtWidgets import QApplication, QStackedWidget, QMenu
from PySide6.QtCore import QTimer, Qt
import sys
import os
# Создаем обработчик с указанием кодировки
handler = logging.FileHandler('test_results.log', mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Настройка логирования с использованием созданного обработчика
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[handler],
    force=True
)

class TestSearchThread(unittest.TestCase):
    def test_search_finds_matching_files_and_dirs_with_callback(self):
        logging.debug('Настройка mock для os.walk')
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', ['test_dir'], ['test.txt']),
                ('/root/test_dir', [], ['other.txt'])
            ]
            with mock.patch('os.path.join', side_effect=lambda *args: '/'.join(args)):
                search = SearchThread('test', '/root')
                expected = ['/root/test.txt', '/root/test_dir']
                results = []

                def capture_results(emitted_results):
                    logging.debug(f'Получены результаты: {emitted_results}')
                    results.extend(emitted_results)

                search.results_ready.connect(capture_results)

                logging.debug('Запуск поиска')
                search.run()

                logging.debug(f'Ожидаемые результаты: {expected}, Полученные результаты: {results}')
                self.assertEqual(set(results), set(expected))
                logging.debug('Тест завершен успешно')

    def test_empty_query_emits_all_matches(self):
        logging.debug('Настройка mock для os.walk с пустым запросом')
        with mock.patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', ['dir1'], ['file1.txt']),
                ('/root/dir1', [], ['file2.txt'])
            ]
            with mock.patch('os.path.join', side_effect=lambda *args: '/'.join(args)):
                search = SearchThread('', '/root')
                expected = ['/root/file1.txt', '/root/dir1', '/root/dir1/file2.txt']
                results = []

                def capture_results(emitted_results):
                    logging.debug(f'Получены результаты: {emitted_results}')
                    results.extend(emitted_results)

                search.results_ready.connect(capture_results)

                logging.debug('Запуск поиска с пустым запросом')
                search.run()

                logging.debug(f'Ожидаемые результаты: {expected}, Полученные результаты: {results}')
                self.assertEqual(set(results), set(expected))
                logging.debug('Тест с пустым запросом завершен успешно')


def capture_call(method_name, calls):
    logging.debug(f'Вызван метод: {method_name}')
    calls.append(method_name)

class TestMainWindow(unittest.TestCase):
    def test_main_window(self):
        logging.debug('Начало тестирования главного окна')

        # Список для записи порядка вызовов методов создания UI
        calls = []

        # Создаем приложение и главное окно
        app = QApplication(sys.argv)
        file_manager = FileManager()

        # Устанавливаем таймер для автоматического закрытия приложения через 5 секунд
        QTimer.singleShot(5000, app.quit)

        # Подменяем методы создания UI и устанавливаем побочные эффекты
        with mock.patch.object(file_manager, 'create_menu_bar', side_effect=lambda: capture_call('create_menu_bar', calls)) as mock_create_menu_bar, \
             mock.patch.object(file_manager, 'create_navigation_toolbar', side_effect=lambda: capture_call('create_navigation_toolbar', calls)) as mock_create_navigation_toolbar, \
             mock.patch.object(file_manager, 'create_main_layout', side_effect=lambda: capture_call('create_main_layout', calls)) as mock_create_main_layout, \
             mock.patch.object(file_manager, 'connect_signals', side_effect=lambda: capture_call('connect_signals', calls)) as mock_connect_signals:

            # Вызываем метод инициализации UI
            file_manager.init_ui()

            # Проверяем, что каждый метод был вызван один раз
            mock_create_menu_bar.assert_called_once()
            mock_create_navigation_toolbar.assert_called_once()
            mock_create_main_layout.assert_called_once()
            mock_connect_signals.assert_called_once()

            # Проверяем порядок вызовов методов
            expected_call_order = [
                'create_menu_bar',
                'create_navigation_toolbar',
                'create_main_layout',
                'connect_signals'
            ]

            logging.debug(f'Ожидаемый порядок вызовов: {expected_call_order}')
            logging.debug(f'Фактический порядок вызовов: {calls}')

            self.assertEqual(calls, expected_call_order)
            logging.debug('Проверка порядка создания UI-компонентов успешно завершена')

        # Дополнительные проверки внутри запущенного приложения

        # Проверяем начальные настройки
        user_home_path = os.path.expanduser("~")
        logging.debug(user_home_path)
        self.assertEqual(file_manager.history, [user_home_path])
        self.assertEqual(file_manager.current_sort_column, 0)
        self.assertEqual(file_manager.sort_order, Qt.AscendingOrder)
        self.assertEqual(file_manager.back_history, [user_home_path])
        self.assertEqual(file_manager.forward_history, [])
        self.assertIsNone(file_manager.clipboard)
        self.assertIsNone(file_manager.clip_action)
        self.assertFalse(file_manager.in_search_mode)
        logging.debug('Проверка начальных настроек успешно завершена')

        # Проверяем наличие всех необходимых меню
        menu_bar = file_manager.menuBar()
        menus = [menu.title() for menu in menu_bar.findChildren(QMenu)]
        logging.debug(f'Найденные меню: {menus}')
        expected_menus = ["Файл", "Вид", "Сортировка", "Тема", "О программе"]
        self.assertEqual(set(menus), set(expected_menus))
        logging.debug('Проверка наличия всех необходимых меню успешно завершена')

        # Проверяем наличие действий на панели навигации
        actions = file_manager.nav_toolbar.actions()
        action_texts = [action.text() for action in actions]
        expected_actions = ["Главная", "Просмотр файлов", "Назад", "Вперед", "Обновить", "Предпросмотр"]
        for action_text in expected_actions:
            self.assertIn(action_text, action_texts)
        logging.debug('Проверка действий на панели навигации успешно завершена')

        # Проверяем, что основное расположение создано с QStackedWidget
        self.assertIsInstance(file_manager.main_layout, QStackedWidget)
        self.assertEqual(file_manager.centralWidget(), file_manager.main_layout)
        logging.debug('Проверка основного расположения успешно завершена')

        # Проверяем соединения сигналов
        signals_connected = True
        try:
            file_manager.quick_access_list.itemDoubleClicked.connect(file_manager.on_quick_access_select)
            file_manager.history_list.itemDoubleClicked.connect(file_manager.on_history_select)
            file_manager.favorites_list.itemDoubleClicked.connect(file_manager.on_favorite_select)
            file_manager.tree_view.selectionModel().selectionChanged.connect(file_manager.on_file_select)
            file_manager.list_view.selectionModel().selectionChanged.connect(file_manager.on_file_select)
            file_manager.tree_view.doubleClicked.connect(file_manager.on_tree_double_click)
            file_manager.list_view.doubleClicked.connect(file_manager.on_list_double_click)
        except Exception as e:
            signals_connected = False
            logging.error(f'Ошибка при подключении сигналов: {e}')

        self.assertTrue(signals_connected)
        logging.debug('Проверка соединения сигналов успешно завершена')

        # Отображаем главное окно
        file_manager.show()
        logging.debug('Главное окно отображено')

        # Запускаем приложение
        app.exec()
        logging.debug('Завершение тестирования главного окна')

# Если файл запускается как самостоятельный скрипт, запускаются тесты
def run_all_tests():
    unittest.main()

if __name__ == '__main__':
    run_all_tests()
