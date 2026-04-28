# conftest.py
import pytest
from unittest.mock import patch
import sys
import os

# Фикс для Windows Tkinter
if sys.platform == "win32":
    # Указываем пути явно (замените на ваши реальные пути!)
    os.environ['TCL_LIBRARY'] = r'C:\Users\семён\AppData\Local\Python\pythoncore-3.14-64\tcl\tcl8.6'
    os.environ['TK_LIBRARY'] = r'C:\Users\семён\AppData\Local\Python\pythoncore-3.14-64\tcl\tk8.6'

@pytest.fixture(scope="session")
def root():
    """Пытаемся создать root для тестов"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        yield root
        try:
            root.destroy()
        except:
            pass
    except Exception as e:
        # Если Tkinter не работает - пропускаем тесты с root
        pytest.skip(f"Tkinter не доступен: {e}")

@pytest.fixture(autouse=True)
def auto_mock_messagebox():
    """Мокаем все messagebox глобально"""
    with patch("tkinter.messagebox.showinfo") as mock_info:
        with patch("tkinter.messagebox.showwarning") as mock_warning:
            with patch("tkinter.messagebox.showerror") as mock_error:
                with patch("tkinter.messagebox.askyesno", return_value=True) as mock_ask:
                    yield