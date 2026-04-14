from datetime import datetime
import logging

logging.basicConfig(
    filename="errors.log",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s"
)

class ParseError(Exception):
    pass

class FileObject:
    def __init__(self, name: str, creation_date: datetime, size: int):
        if not name:
            logging.warning(f"Имя файла не может быть пустым")
            raise ValueError("Имя файла не может быть пустым")            
        if size < 0:
            logging.warning(f"Размер файла не может быть отрицательным")
            raise ValueError(f"Размер файла не может быть отрицательным")
            
        self.name = name
        self.creation_date = creation_date
        self.size = size

    def __str__(self):
        return f'Файл "{self.name}" {self.creation_date.strftime("%Y.%m.%d")} {self.size}'

def parse_line(line: str):
    try:
        parts = line.strip().split()
        if len(parts) < 4:
            raise ParseError("Недостаточно данных")
        
        name = parts[1].strip('"')
        date_obj = datetime.strptime(parts[2], "%Y.%m.%d")
        size = int(parts[3])
        return FileObject(name, date_obj, size)
    except Exception as e:
        logging.warning(f"Ошибка парсинга строки: {line.strip()} ({e})")
        raise ParseError(f"Ошибка парсинга строки: {line.strip()} ({e})")


def load_from_file(filename: str):
    objects = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = parse_line(line)   
                    objects.append(obj)
                except ParseError as e:
                    logging.warning(str(e))
    except FileNotFoundError:
        logging.warning(f"Файл не найден: {filename}")
    return objects

def save_to_file(filename: str, objects: list):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for obj in objects:
                f.write(str(obj) + "\n")
    except Exception:
        logging.warning(f"Ошибка при сохранении в файл: {filename}")
