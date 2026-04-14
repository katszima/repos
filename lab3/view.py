from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
import modelc


class FileManagerWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.filename = "files.txt"
        self.objects = modelc.load_from_file(self.filename)

        self.window = tk.Toplevel()
        self.window.title("Менеджер файлов")
        self.window.geometry("600x400")

        self.tree = ttk.Treeview(
            self.window,
            columns=("name", "date", "size"),
            show="headings"
        )
        self.tree.heading("name", text="Имя файла")
        self.tree.heading("date", text="Дата создания")
        self.tree.heading("size", text="Размер (байт)")

        self.tree.column("name", width=200)
        self.tree.column("date", width=100)
        self.tree.column("size", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        tk.Button(frame, text="Добавить", command=self.add_object).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Удалить", command=self.delete_object).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)

        tk.Button(self.window, text="В главное меню", command=self.back).pack(pady=10)

        self.refresh_table()
        self.window.protocol("WM_DELETE_WINDOW", self.back)

    # --- LOGIC (теперь тестируемая) ---
    def create_object(self, name, date_str, size_str):
        try:
            date = datetime.strptime(date_str, "%Y.%m.%d")
            size = int(size_str)

            obj = modelc.FileObject(name, date, size)
            self.objects.append(obj)
            self.refresh_table()

            return True, None
        except ValueError as e:
            return False, str(e)

    # --- UI ---
    def add_object(self):
        window = tk.Toplevel(self.window)
        window.title("Добавить файл")
        window.geometry("300x200")

        tk.Label(window, text="Имя файла:").pack(pady=5)
        name_entry = tk.Entry(window)
        name_entry.pack()

        tk.Label(window, text="Дата (ГГГГ.ММ.ДД):").pack(pady=5)
        date_entry = tk.Entry(window)
        date_entry.pack()

        tk.Label(window, text="Размер (байт):").pack(pady=5)
        size_entry = tk.Entry(window)
        size_entry.pack()

        def on_submit():
            success, error = self.create_object(
                name_entry.get(),
                date_entry.get(),
                size_entry.get()
            )

            if success:
                window.destroy()
                messagebox.showinfo("Успех", "Файл добавлен!")
            else:
                messagebox.showerror("Ошибка", error)

        tk.Button(window, text="Добавить", command=on_submit).pack(pady=10)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for obj in self.objects:
            self.tree.insert(
                "",
                tk.END,
                values=(obj.name, obj.creation_date.strftime("%Y.%m.%d"), obj.size),
            )

    def delete_object(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите файл для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить файл?"):
            index = self.tree.index(selected[0])
            del self.objects[index]
            self.refresh_table()

    def save(self):
        modelc.save_to_file(self.filename, self.objects)
        messagebox.showinfo("Успех", "Сохранено!")

    def back(self):
        self.window.destroy()
        self.main_app.show_main()


class HelpWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel()

        try:
            response = requests.get("https://img.freepik.com/free-photo/cute-kitten.jpg")
            img = Image.open(BytesIO(response.content))
            self.photo = ImageTk.PhotoImage(img)

            tk.Label(self.window, image=self.photo).pack()
        except:
            tk.Label(self.window, text="Нет картинки").pack()

        tk.Button(self.window, text="Назад", command=self.back).pack()

    def back(self):
        self.window.destroy()
        self.main_app.show_main()


class MainApp:
    def __init__(self, root):
        self.root = root

        tk.Button(root, text="Справка", command=self.open_help).pack()
        tk.Button(root, text="Работа", command=self.open_input).pack()
        tk.Button(root, text="Выход", command=self.exit_app).pack()

    def hide_main(self):
        self.root.withdraw()

    def show_main(self):
        self.root.deiconify()

    def open_help(self):
        self.hide_main()
        HelpWindow(self)

    def open_input(self):
        self.hide_main()
        FileManagerWindow(self)

    def exit_app(self):
        if messagebox.askyesno("Выход", "Выйти?"):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()