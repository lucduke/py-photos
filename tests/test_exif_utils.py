import unittest
from src.exif_utils import get_exif_data

class TestExifUtils(unittest.TestCase):
    def test_get_exif_data(self):
        exif_data = get_exif_data('non_existent_file.jpg')
        self.assertIsNotNone(exif_data)

if __name__ == '__main__':
    unittest.main()
