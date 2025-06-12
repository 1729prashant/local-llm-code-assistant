# tests.py

#import unittest
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file


"""
class TestGetFilesInfo(unittest.TestCase):
    def setUp(self):
        self.get_files_info = get_files_info()

    def test_dot(self):
        result = self.get_files_info.evaluate("calculator", ".")
        self.assertEqual(result, 8)

    def test_pkg(self):
        result = self.get_files_info.evaluate("calculator", "pkg")
        self.assertEqual(result, 6)

    def test_multiplication(self):
        result = self.get_files_info.evaluate("calculator", ".")
        self.assertEqual(result, 12)

    def test_division(self):
        result = self.get_files_info.evaluate("calculator", ".")
        self.assertEqual(result, 5)

    def test_nested_expression(self):
        result = self.get_files_info.evaluate("calculator", ".")
        self.assertEqual(result, 17)

    def test_complex_expression(self):
        result = self.get_files_info.evaluate("2 * 3 - 8 / 2 + 5")
        self.assertEqual(result, 7)

    def test_empty_expression(self):
        result = self.get_files_info.evaluate("")
        self.assertIsNone(result)

    def test_invalid_operator(self):
        with self.assertRaises(ValueError):
            self.get_files_info.evaluate("$ 3 5")

    def test_not_enough_operands(self):
        with self.assertRaises(ValueError):
            self.get_files_info.evaluate("+ 3")


if __name__ == "__main__":
    unittest.main()
"""

"""
print(get_files_info("calculator", "."))
print(get_files_info("calculator", "pkg"))
print(get_files_info("calculator", "/bin"))
print(get_files_info("calculator", "../"))
"""
# print(get_file_content("calculator", "lorem.txt"))

# print(get_file_content("calculator", "main.py"))
# print(get_file_content("calculator", "pkg/calculator.py"))
# print(get_file_content("calculator", "/bin/cat"))



# print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
# print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
# print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))


print(run_python_file("calculator", "main.py"))
print(run_python_file("calculator", "tests.py"))
print(run_python_file("calculator", "../main.py"))
print(run_python_file("calculator", "nonexistent.py"))