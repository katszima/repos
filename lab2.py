from datetime import datetime
import tkinter as tk
from tkinter import ttk


class FileObject:
    def __init__(self, name: str, creation_date: datetime, size: int):
        self.name = name
        self.creation_date = creation_date
        self.size = size

    def __str__(self):
        return f'Файл "{self.name}" {self.creation_date.strftime("%Y.%m.%d")} {self.size}'


def parse_line(line: str):
    parts = line.strip().split()
    name = parts[1].strip('"')
    date_obj = datetime.strptime(parts[2], "%Y.%m.%d")
    size = int(parts[3])
    return FileObject(name, date_obj, size)


def load_from_file(filename: str):
    objects = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            objects.append(parse_line(line))
    return objects


def save_to_file(filename: str, objects: list):
    with open(filename, "w", encoding="utf-8") as f:
        for obj in objects:
            f.write(str(obj) + "\n")


class App:
    def __init__(self, root):
        self.filename = "files.txt"
        self.objects = load_from_file(self.filename)

        self.root = root
        self.root.title("Файлы")

        self.tree = ttk.Treeview(root, columns=("name", "date", "size"), show="headings")
        self.tree.heading("name", text="Имя")
        self.tree.heading("date", text="Дата")
        self.tree.heading("size", text="Размер")

        self.tree.pack(fill=tk.BOTH, expand=True)

        frame = tk.Frame(root)
        frame.pack()

        tk.Button(frame, text="Добавить", command=self.add_object).pack(side=tk.LEFT)
        tk.Button(frame, text="Удалить", command=self.delete_object).pack(side=tk.LEFT)
        tk.Button(frame, text="Сохранить", command=self.save).pack(side=tk.LEFT)

        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for obj in self.objects:
            self.tree.insert(
                "",
                tk.END,
                values=(obj.name, obj.creation_date.strftime("%Y.%m.%d"), obj.size),
            )

    def add_object(self):
        window = tk.Toplevel(self.root)

        tk.Label(window, text="Имя").pack()
        name_entry = tk.Entry(window)
        name_entry.pack()

        tk.Label(window, text="Дата YYYY.MM.DD").pack()
        date_entry = tk.Entry(window)
        date_entry.pack()

        tk.Label(window, text="Размер").pack()
        size_entry = tk.Entry(window)
        size_entry.pack()

        def save_new():
            name = name_entry.get()
            date = datetime.strptime(date_entry.get(), "%Y.%m.%d")
            size = int(size_entry.get())

            self.objects.append(FileObject(name, date, size))
            self.refresh_table()
            window.destroy()

        tk.Button(window, text="Добавить", command=save_new).pack()

    def delete_object(self):
        selected = self.tree.selection()

        if not selected:
            return

        index = self.tree.index(selected[0])
        del self.objects[index]

        self.refresh_table()

    def save(self):
        save_to_file(self.filename, self.objects)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()