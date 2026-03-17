from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO

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
    try:
        with open(filename, "r", encoding="utf-8") as f:
            objects = []
            for line in f:
                objects.append(parse_line(line))
            return objects
    except FileNotFoundError:
        return []


def save_to_file(filename: str, objects: list):
    with open(filename, "w", encoding="utf-8") as f:
        for obj in objects:
            f.write(str(obj) + "\n")


class FileManagerWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.filename = "files.txt"
        self.objects = load_from_file(self.filename)

        self.window = tk.Toplevel()
        self.window.title("Менеджер файлов")
        self.window.geometry("600x400")


        self.tree = ttk.Treeview(self.window, columns=("name", "date", "size"), show="headings")
        self.tree.heading("name", text="Имя файла")
        self.tree.heading("date", text="Дата создания")
        self.tree.heading("size", text="Размер (байт)")
        
        self.tree.column("name", width=200)
        self.tree.column("date", width=100)
        self.tree.column("size", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        tk.Button(frame, text="Добавить", command=self.add_object, 
                 bg="lightgray", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Удалить", command=self.delete_object, 
                 bg="lightgray", width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(frame, text="Сохранить", command=self.save, 
                 bg="lightgray", width=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(self.window, text="в главное меню", command=self.back,
                 bg="lightgray", width=20).pack(pady=10)

        self.refresh_table()
        self.window.protocol("WM_DELETE_WINDOW", self.back)

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
        window = tk.Toplevel(self.window)
        window.title("Добавить файл")
        window.geometry("300x200")

        tk.Label(window, text="Имя файла:").pack(pady=5)
        name_entry = tk.Entry(window, width=30)
        name_entry.pack()

        tk.Label(window, text="Дата (ГГГГ.ММ.ДД):").pack(pady=5)
        date_entry = tk.Entry(window, width=30)
        date_entry.pack()

        tk.Label(window, text="Размер (байт):").pack(pady=5)
        size_entry = tk.Entry(window, width=30)
        size_entry.pack()

        def save_new():
            try:
                name = name_entry.get()
                date = datetime.strptime(date_entry.get(), "%Y.%m.%d")
                size = int(size_entry.get())

                self.objects.append(FileObject(name, date, size))
                self.refresh_table()
                window.destroy()
                messagebox.showinfo("Успех", "Файл добавлен!")
            except ValueError as e:
                messagebox.showerror("Ошибка", f"Неверный формат данных: {e}")

        tk.Button(window, text="Добавить", command=save_new, bg="lightgray").pack(pady=10)

    def delete_object(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите файл для удаления!")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранный файл?"):
            index = self.tree.index(selected[0])
            del self.objects[index]
            self.refresh_table()

    def save(self):
        save_to_file(self.filename, self.objects)
        messagebox.showinfo("Успех", "Данные сохранены в файл!")

    def back(self):
        self.window.destroy()
        self.main_app.show_main()


class HelpWindow:
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = tk.Toplevel()
        self.window.title("Справка")
        self.window.geometry("850x650")
        
        tk.Label(self.window, text="СПРАВКА", font=("Arial", 16, "bold")).pack(pady=10)
        
        try:
            response = requests.get("https://img.freepik.com/free-photo/cute-kitten-sitting-staring-playful-fluffy-looking-camera-generated-by-artificial-intelligence_188544-113029.jpg?semt=ais_hybrid&w=740")
            img = Image.open(BytesIO(response.content))
            self.photo = ImageTk.PhotoImage(img)
            
            label_img = tk.Label(self.window, image=self.photo)
            label_img.pack(pady=20)
        except:
            tk.Label(self.window, text="(картинка не загрузилась)", fg="red").pack(pady=20)
        
        tk.Label(self.window, text=" Это котик ", 
                font=("Arial", 10), justify="left").pack(pady=10)
        
        tk.Button(self.window, text="в главное меню", command=self.back,
                 bg="lightgray", width=20, height=2).pack(pady=20)
        
        self.window.protocol("WM_DELETE_WINDOW", self.back)
    
    def back(self):
        self.window.destroy()
        self.main_app.show_main()


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Главное меню")
        self.root.geometry("300x250")
        
        tk.Label(root, text="ГЛАВНОЕ МЕНЮ", font=("Arial", 16, "bold")).pack(pady=20)
        
        tk.Button(root, text="Справка", command=self.open_help, 
                 width=15, height=1, bg="lightgray").pack(pady=5)
        tk.Button(root, text="Работа", command=self.open_input, 
                 width=15, height=1, bg="lightgray").pack(pady=5)
        tk.Button(root, text="Нажми меня", command=self.open_help, 
                 width=15, height=1, bg="red").pack(pady=5)
        tk.Button(root, text="Выход", command=self.exit_app, 
                 width=15, height=1, bg="lightgray").pack(pady=5)
        
    
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
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()