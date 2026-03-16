from datetime import datetime


class FileObject:
    def __init__(file, name: str, creation_date: datetime, size: int, color: str):
        file.name = name
        file.creation_date = creation_date
        file.size = size
        file.color = color

    def __str__(file):
        return f'{file.name} {file.creation_date.strftime("%Y.%m.%d")} {file.size} {file.color}'


def parse_line(line: str):
    parts = line.strip().split()

    if len(parts) != 5:
        return None

    obj_type = parts[0]
    name = parts[1].strip('"')
    date_str = parts[2]
    size_str = parts[3]
    color_str = parts[4]

    if obj_type != "Файл":
        return None

    creation_date = datetime.strptime(date_str, "%Y.%m.%d")
    size = int(size_str)
    color = str(color_str)

    return FileObject(name, creation_date, size, color)

def menu():
    objects = []

    while True:
        print("\n1. Добавить объект")
        print("2. Показать список")
        print("0. Выход")

        choice = input("Выбор: ")

        if choice == "1":
            line = input("Введите описание (Файл \"имя\" гггг.мм.дд размер, цвет): ")
            obj = parse_line(line)
            if obj:
                objects.append(obj)
                print("Объект добавлен.")
            else:
                print("Некорректный ввод.")

        elif choice == "2":
            if not objects:
                print("Список пуст.")
            else:
                for obj in objects:
                    print(obj)

        elif choice == "0":
            break

        else:
            print("Неверный пункт меню.")

if __name__ == "__main__":
    menu()