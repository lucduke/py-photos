import unittest
import os
from src.file_utils import calculate_file_hash

class TestFileUtils(unittest.TestCase):
    def test_calculate_file_hash(self):
        test_file = 'test_file.txt'
        with open(test_file, 'w') as f:
            f.write('test content')

        file_hash = calculate_file_hash(test_file)
        self.assertIsNotNone(file_hash)

        os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
