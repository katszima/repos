import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

import modelc_lab4
from view_lab4 import FileManagerWindow, MainApp

@pytest.fixture
def mock_main():
    return MagicMock()

@pytest.fixture
def file_manager(root, mock_main):
    with patch("modelc_lab4.load_from_file", return_value=[]):
        fm = FileManagerWindow(mock_main)
        yield fm
        try:
            fm.window.destroy()
        except:
            pass

def test_create_object_success(file_manager):
    # Вызываем метод
    file_manager.create_object("file.txt", "2024.01.01", "100")
    
    # Проверяем результат
    assert len(file_manager.objects) == 1
    assert file_manager.objects[0].name == "file.txt"

def test_create_object_invalid(file_manager):
    # Просто проверяем что объект не создался и не упало с ошибкой
    file_manager.create_object("file.txt", "bad-date", "abc")
    
    # Объект не должен добавиться
    assert len(file_manager.objects) == 0

def test_refresh_table(file_manager):
    obj = modelc_lab4.FileObject("test.txt", datetime(2024, 1, 1), 100)
    file_manager.objects = [obj]
    file_manager.refresh_table()
    
    items = file_manager.tree.get_children()
    assert len(items) == 1

def test_delete_no_selection(file_manager):
    # Просто проверяем что не падает с ошибкой
    file_manager.delete_object()

def test_delete_selected(file_manager):
    obj = modelc_lab4.FileObject("test.txt", datetime(2024, 1, 1), 100)
    file_manager.objects = [obj]
    file_manager.refresh_table()
    
    item = file_manager.tree.get_children()[0]
    file_manager.tree.selection_set(item)
    file_manager.delete_object()
    
    assert len(file_manager.objects) == 0

def test_save(file_manager):
    with patch("modelc_lab4.save_to_file") as mock_save:
        file_manager.save()
        mock_save.assert_called_once()

def test_back(file_manager, mock_main):
    file_manager.back()
    mock_main.show_main.assert_called_once()

def test_main_navigation(root):
    app = MainApp(root)
    
    with patch.object(app, "hide_main") as hide:
        with patch("view_lab4.HelpWindow") as mock_help:
            app.open_help()
            hide.assert_called_once()
            mock_help.assert_called_once_with(app)
    
    with patch.object(app, "hide_main") as hide:
        with patch("view_lab4.FileManagerWindow") as mock_fm:
            app.open_input()
            hide.assert_called_once()
            mock_fm.assert_called_once_with(app)

def test_exit(root):
    # Не используем @patch, askyesno уже замокан в conftest
    app = MainApp(root)
    with patch.object(root, "quit") as quit_mock:
        app.exit_app()
        quit_mock.assert_called_once()