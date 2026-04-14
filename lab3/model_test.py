import unittest
from datetime import datetime
from modelc import parse_line, FileObject, ParseError

class TestModel(unittest.TestCase):

    def test_parse_correct_line(self):
        line = 'Файл "test.txt" 2023.10.01 123'
        obj = parse_line(line)

        self.assertEqual(obj.name, "test.txt")
        self.assertEqual(obj.size, 123)
        self.assertEqual(obj.creation_date, datetime(2023, 10, 1))

    def test_parse_invalid_line(self):
        line = 'неправильная строка'

        with self.assertRaises(ParseError):
            parse_line(line)

    def test_parse_invalid_date(self):
        line = 'Файл "test.txt" 2023-10-01 123'

        with self.assertRaises(ParseError):
            parse_line(line)


if __name__ == "__main__":
    unittest.main()