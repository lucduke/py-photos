import unittest
import sqlite3
from src.database import init_db, close_db, get_db_connection

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()

    def tearDown(self):
        close_db()

    def test_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)

if __name__ == '__main__':
    unittest.main()
