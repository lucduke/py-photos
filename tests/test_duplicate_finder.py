import unittest
from src.duplicate_finder import find_duplicates

class TestDuplicateFinder(unittest.TestCase):
    def test_find_duplicates(self):
        # This test assumes that the database is already populated
        find_duplicates()

if __name__ == '__main__':
    unittest.main()
