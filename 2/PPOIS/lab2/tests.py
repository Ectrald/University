import unittest
import sqlite3
from model import Model

class TestBankApp(unittest.TestCase):
    def setUp(self):
        # Initialize in-memory database for testing
        self.model = Model()
        self.model.connection = sqlite3.connect(':memory:')
        self.model.cursor = self.model.connection.cursor()
        # Explicitly create the database schema
        self.model.cursor.execute("""
            CREATE TABLE BankAccountTable(
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                account_number INTEGER,
                registration_address TEXT NOT NULL,
                mobile_phone TEXT,
                landline_phone TEXT,
                CHECK(mobile_phone IS NOT NULL OR landline_phone IS NOT NULL)
            )
        """)
        self.model.connection.commit()

    def tearDown(self):
        # Ensure database connection is closed
        try:
            self.model.cursor.close()
            self.model.connection.close()
        except:
            pass

    def test_add_data(self):
        # Test adding a valid record
        self.model.add_data(
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            account_number=100001,
            registration_address="ул. Ленина, 10",
            mobile_phone="+79161234567",
            landline_phone=""
        )
        self.model.cursor.execute("SELECT * FROM BankAccountTable")
        result = self.model.cursor.fetchall()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], ("Иванов", "Иван", "Иванович", 100001, "ул. Ленина, 10", "+79161234567", ""))

    def test_delete_data(self):
        # Add test data
        self.model.add_test_data()
        # Delete records with specific surname
        count = self.model.delete_data_with_count(surname="Иванов")
        self.assertEqual(count, 1)
        self.model.cursor.execute("SELECT COUNT(*) FROM BankAccountTable WHERE surname = ?", ("Иванов",))
        self.assertEqual(self.model.cursor.fetchone()[0], 0)

    def test_search_data(self):
        # Add test data
        self.model.add_test_data()
        # Search by surname
        results = self.model.search_data(surname="Петров")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1], "Петров")
        # Search by phone number contains
        results = self.model.search_data(number_contains="7916")
        self.assertTrue(len(results) > 0)
        for result in results:
            self.assertTrue("7916" in (result[6] or "") or "7916" in (result[7] or ""))

    def test_pagination(self):
        # Add test data
        self.model.add_test_data()
        # Test pagination
        items = self.model.get_items(page=1, per_page=10)
        self.assertEqual(len(items), 10)
        total_pages = self.model.get_total_pages(per_page=10)
        self.assertEqual(total_pages, 5)  # 50 records / 10 per page = 5 pages
        total_items = self.model.get_total_items()
        self.assertEqual(total_items, 50)




if __name__ == '__main__':
    unittest.main()