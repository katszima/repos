import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock
from datetime import datetime

import modelc
from view import FileManagerWindow, MainApp

@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()

@pytest.fixture
def mock_main():
    return MagicMock()

@pytest.fixture
def file_manager(root, mock_main):
    with patch("modelc.load_from_file", return_value=[]):
        fm = FileManagerWindow(mock_main)
        yield fm
        fm.window.destroy()

def test_create_object_success(file_manager):
    success, error = file_manager.create_object(
        "file.txt", "2024.01.01", "100"
    )

    assert success
    assert error is None
    assert len(file_manager.objects) == 1


def test_create_object_invalid(file_manager):
    success, error = file_manager.create_object(
        "file.txt", "bad-date", "abc"
    )

    assert not success
    assert error is not None

def test_refresh_table(file_manager):
    obj = modelc.FileObject("test.txt", datetime(2024, 1, 1), 100)
    file_manager.objects = [obj]

    file_manager.refresh_table()

    items = file_manager.tree.get_children()
    assert len(items) == 1


@patch("tkinter.messagebox.showwarning")
def test_delete_no_selection(mock_warn, file_manager):
    file_manager.delete_object()
    mock_warn.assert_called()


@patch("tkinter.messagebox.askyesno", return_value=True)
def test_delete_selected(mock_confirm, file_manager):
    obj = modelc.FileObject("test.txt", datetime(2024, 1, 1), 100)
    file_manager.objects = [obj]
    file_manager.refresh_table()

    item = file_manager.tree.get_children()[0]
    file_manager.tree.selection_set(item)

    file_manager.delete_object()

    assert len(file_manager.objects) == 0


@patch("modelc.save_to_file")
def test_save(mock_save, file_manager):
    file_manager.save()
    mock_save.assert_called()


def test_back(file_manager, mock_main):
    file_manager.back()
    mock_main.show_main.assert_called()


def test_main_navigation(root):
    app = MainApp(root)

    with patch.object(app, "hide_main") as hide:
        with patch("view.HelpWindow"):
            app.open_help()
            hide.assert_called()

    with patch.object(app, "hide_main") as hide:
        with patch("view.FileManagerWindow"):
            app.open_input()
            hide.assert_called()


@patch("tkinter.messagebox.askyesno", return_value=True)
def test_exit(root, mock_confirm):
    app = MainApp(root)

    with patch.object(root, "quit") as quit_mock:
        app.exit_app()
        quit_mock.assert_called()