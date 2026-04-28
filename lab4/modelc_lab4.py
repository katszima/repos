#modelc_lab4.py
from datetime import datetime
import logging
import re

logging.basicConfig(
    filename="errors.log",
    level=logging.WARNING,
    format="%(asctime)s - %(message)s"
)

class ParseError(Exception):
    pass

class CommandError(Exception):
    pass

class FileObject:
    def __init__(self, name: str, creation_date: datetime, size: int, file_type: str = ""):
        if not name:
            logging.warning(f"Имя файла не может быть пустым")
            raise ValueError("Имя файла не может быть пустым")            
        if size < 0:
            logging.warning(f"Размер файла не может быть отрицательным")
            raise ValueError(f"Размер файла не может быть отрицательным")
            
        self.name = name
        self.creation_date = creation_date
        self.size = size
        self.file_type = file_type  # новое поле

    def __str__(self):
        return f'Файл "{self.name}" {self.creation_date.strftime("%Y.%m.%d")} {self.size} {self.file_type}'

    def get_field(self, field_name: str):
        if field_name == 'name':
            return self.name
        elif field_name == 'date' or field_name == 'creation_date':
            return self.creation_date
        elif field_name == 'size':
            return self.size
        elif field_name == 'type' or field_name == 'file_type':  # новое поле
            return self.file_type
        else: 
            raise ValueError(f"Неизвестное поле: {field_name}")

def parse_line(line: str):
    try:
        parts = line.strip().split()
        if len(parts) < 4:
            raise ParseError("Недостаточно данных")
        
        name = parts[1].strip('"')
        date_obj = datetime.strptime(parts[2], "%Y.%m.%d")
        size = int(parts[3])

        file_type = parts[4] if len(parts) >= 5 else ""
        return FileObject(name, date_obj, size, file_type)
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

def _parse_condition_value(field_name: str, value_str: str):
    value_str = value_str.strip()
    
    if field_name == 'size':
        return int(value_str)
    elif field_name == 'date' or field_name == 'creation_date':
        for fmt in ["%d.%m.%Y", "%Y.%m.%d"]:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Неверный формат даты: {value_str}")
    elif field_name == 'name':
        return value_str.strip('"').strip("'")
    else:
        return value_str
    
def evaluate_condition(obj: FileObject, condition: str) -> bool:
    condition = condition.strip()
    pattern = r'(\w+)\s*(<|>|<=|>=|==|!=)\s*(.+)'
    match = re.match(pattern, condition)
    
    if not match:
        raise ValueError(f"Неверный формат условия: '{condition}'")
    
    field, operator, value_str = match.groups()
    
    # Получаем значения для сравнения
    obj_value = obj.get_field(field)
    comp_value = _parse_condition_value(field, value_str)
    
    # Выполняем сравнение
    if operator == '<':
        return obj_value < comp_value
    elif operator == '>':
        return obj_value > comp_value
    elif operator == '<=':
        return obj_value <= comp_value
    elif operator == '>=':
        return obj_value >= comp_value
    elif operator == '==':
        return obj_value == comp_value
    elif operator == '!=':
        return obj_value != comp_value
    else:
        raise ValueError(f"Неподдерживаемый оператор: {operator}")
    
def execute_add_command(csv_data: str, objects: list) -> tuple[bool, str]:
    try:
        parts = [p.strip() for p in csv_data.split(';')]
        if len(parts) < 3:
            raise ValueError(f"Недостаточно данных в CSV (ожидается 3, получено {len(parts)})")
        
        name = parts[0]
        date = datetime.strptime(parts[1], "%d.%m.%Y")
        size = int(parts[2])
        file_type = parts[3] if len(parts) >= 4 else ""  # новое поле
        
        obj = FileObject(name, date, size, file_type)
        objects.append(obj)
        return True, f"Добавлен: {name}"
    except Exception as e:
        error_msg = f"Ошибка ADD: {str(e)}"
        logging.warning(error_msg)
        return False, error_msg

def execute_rem_command(condition: str, objects: list) -> tuple[bool, str]:
    try:
        original_count = len(objects)
        objects[:] = [obj for obj in objects if not evaluate_condition(obj, condition)]
        removed = original_count - len(objects)
        return True, f"Удалено объектов: {removed}"
    except Exception as e:
        error_msg = f"Ошибка REM: {str(e)}"
        logging.warning(error_msg)
        return False, error_msg
    
def execute_save_command(filename: str, objects: list) -> tuple[bool, str]:
    try:
        save_to_file(filename, objects)
        return True, f"Сохранено в {filename}"
    except Exception as e:
        error_msg = f"Ошибка SAVE: {str(e)}"
        logging.warning(error_msg)
        return False, error_msg
    
def execute_command_file(commands_filename: str, objects: list) -> list:
    results = []
    try:
        with open(commands_filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('ADD '):
                    csv_data = line[4:].strip()
                    success, msg = execute_add_command(csv_data, objects)
                    results.append((line_num, 'ADD', success, msg))
                    
                elif line.startswith('REM '):
                    condition = line[4:].strip()
                    success, msg = execute_rem_command(condition, objects)
                    results.append((line_num, 'REM', success, msg))
                    
                elif line.startswith('SAVE '):
                    save_filename = line[5:].strip()
                    success, msg = execute_save_command(save_filename, objects)
                    results.append((line_num, 'SAVE', success, msg))
                    
                else:
                    results.append((line_num, 'UNKNOWN', False, f"Неизвестная команда"))
    except FileNotFoundError:
        error = f"Файл команд не найден: {commands_filename}"
        logging.warning(error)
        results.append((0, 'FILE', False, error))
    except Exception as e:
        error = f"Ошибка чтения файла команд: {str(e)}"
        logging.warning(error)
        results.append((0, 'ERROR', False, error))
    return results