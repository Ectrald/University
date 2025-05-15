from sqlite3 import *
from xml_handler import save_to_xml, load_from_xml

class Model:
    def __init__(self):
        self.connection = connect('database.db')
        self.cursor = self.connection.cursor()
        self._create_database()

    def _create_database(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS BankAccountTable(
                surname TEXT NOT NULL,
                name TEXT NOT NULL,
                patronymic TEXT NOT NULL,
                account_number INTEGER NOT NULL,
                registration_address TEXT NOT NULL,
                mobile_phone TEXT,
                landline_phone TEXT,
                CHECK(mobile_phone IS NOT NULL OR landline_phone IS NOT NULL)
            )
        """)
        self.connection.commit()

    def add_data(self, surname: str, name: str, patronymic: str, account_number: int, registration_address: str, mobile_phone: str = "", landline_phone: str = ""):
        self.cursor.execute('INSERT INTO BankAccountTable (surname, name, patronymic, account_number, registration_address, mobile_phone, landline_phone) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (surname, name, patronymic, account_number, registration_address, mobile_phone, landline_phone))
        self.connection.commit()

    def delete_data_with_count(self, surname: str = None, name: str = None, patronymic: str = None,
                              account_number: int = None, registration_address: str = None,
                              mobile_phone: str = None, landline_phone: str = None, number_contains: str = None) -> int:
        conditions = []
        values = []

        if surname:
            conditions.append("surname = ?")
            values.append(surname)
        if name:
            conditions.append("name = ?")
            values.append(name)
        if patronymic:
            conditions.append("patronymic = ?")
            values.append(patronymic)
        if account_number is not None:
            conditions.append("account_number = ?")
            values.append(account_number)
        if registration_address:
            conditions.append("registration_address = ?")
            values.append(registration_address)
        if mobile_phone:
            conditions.append("mobile_phone = ?")
            values.append(mobile_phone)
        if landline_phone:
            conditions.append("landline_phone = ?")
            values.append(landline_phone)
        if number_contains:
            conditions.append("(mobile_phone LIKE ? OR landline_phone LIKE ?)")
            values.extend([f"%{number_contains}%", f"%{number_contains}%"])

        if not conditions:
            return 0

        sql = f"DELETE FROM BankAccountTable WHERE {' AND '.join(conditions)}"
        self.cursor.execute(sql, values)
        count = self.cursor.rowcount
        self.connection.commit()
        return count

    def search_data(self, surname: str = None, name: str = None, patronymic: str = None,
                    account_number: int = None, registration_address: str = None,
                    mobile_phone: str = None, landline_phone: str = None, number_contains: str = None) -> list:
        conditions = []
        values = []

        if surname:
            conditions.append("surname = ?")
            values.append(surname)
        if name:
            conditions.append("name = ?")
            values.append(name)
        if patronymic:
            conditions.append("patronymic = ?")
            values.append(patronymic)
        if account_number is not None:
            conditions.append("account_number = ?")
            values.append(account_number)
        if registration_address:
            conditions.append("registration_address = ?")
            values.append(registration_address)
        if mobile_phone:
            conditions.append("mobile_phone = ?")
            values.append(mobile_phone)
        if landline_phone:
            conditions.append("landline_phone = ?")
            values.append(landline_phone)
        if number_contains:
            conditions.append("(mobile_phone LIKE ? OR landline_phone LIKE ?)")
            values.extend([f"%{number_contains}%", f"%{number_contains}%"])

        sql = "SELECT rowid, * FROM BankAccountTable"
        if conditions:
            sql += f" WHERE {' AND '.join(conditions)}"

        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def get_items(self, page=1, per_page=10):
        offset = (page - 1) * per_page
        self.cursor.execute('SELECT rowid, * FROM BankAccountTable LIMIT ? OFFSET ?', (per_page, offset))
        return self.cursor.fetchall()

    def get_total_pages(self, per_page=10):
        self.cursor.execute('SELECT COUNT(*) FROM BankAccountTable')
        total_items = self.cursor.fetchone()[0]
        return (total_items + per_page - 1) // per_page

    def get_total_items(self):
        self.cursor.execute('SELECT COUNT(*) FROM BankAccountTable')
        return self.cursor.fetchone()[0]

    def save_to_xml(self, filename):
        data = self.cursor.execute('SELECT * FROM BankAccountTable').fetchall()
        save_to_xml(data, filename)

    def load_from_xml(self, filename):
        records = load_from_xml(filename)
        self.cursor.execute('DELETE FROM BankAccountTable')
        for record in records:
            # Проверяем наличие всех обязательных полей
            if (not record[0] or not record[1] or not record[2] or
                    record[3] is None or not record[4]):
                continue  # Пропускаем записи без обязательных данных

            # Проверяем наличие хотя бы одного номера телефона
            if not record[5] and not record[6]:
                continue

            self.add_data(
                surname=record[0],
                name=record[1],
                patronymic=record[2],
                account_number=record[3],
                registration_address=record[4],
                mobile_phone=record[5],
                landline_phone=record[6]
            )
        self.connection.commit()

    def add_from_xml(self, filename):
        records = load_from_xml(filename)
        for record in records:
            # Проверяем наличие всех обязательных полей
            if (not record[0] or not record[1] or not record[2] or
                    record[3] is None or not record[4]):
                continue  # Пропускаем записи без обязательных данных

            # Проверяем наличие хотя бы одного номера телефона
            if not record[5] and not record[6]:
                continue

            # Проверяем, существует ли уже такая запись в базе (по номеру счета)
            self.cursor.execute('''
                SELECT COUNT(*) FROM BankAccountTable 
                WHERE account_number = ?
            ''', (record[3],))

            count = self.cursor.fetchone()[0]

            # Если записи нет, добавляем её
            if count == 0:
                self.add_data(
                    surname=record[0],
                    name=record[1],
                    patronymic=record[2],
                    account_number=record[3],
                    registration_address=record[4],
                    mobile_phone=record[5],
                    landline_phone=record[6]
                )
        self.connection.commit()

    def add_test_data(self):
        test_records = [
            ("Иванов", "Иван", "Иванович", 100001, "ул. Ленина, 10", "+79161234567", "+74951234567"),
            ("Петров", "Пётр", "Петрович", 100002, "ул. Пушкина, 5", "+79167654321", ""),
            ("Сидорова", "Анна", "Сергеевна", 100003, "пр. Мира, 15", "", "+74957654321"),
            ("Кузнецов", "Алексей", "", 100004, "ул. Гагарина, 3", "+79165554433", "+74959876543"),
            ("Смирнова", "Ольга", "Владимировна", 100005, "ул. Садовая, 20", "+79162223344", ""),
            ("Васильев", "Дмитрий", "Николаевич", 100006, "пр. Ленинградский, 30", "", "+74951231231"),
            ("Николаева", "Елена", "", 100007, "ул. Центральная, 1", "+79163334455", "+74954564567"),
            ("Фёдоров", "Михаил", "Фёдорович", 100008, "ул. Лесная, 7", "+79164445566", ""),
            ("Алексеева", "Татьяна", "Алексеевна", 100009, "ул. Школьная, 12", "", "+74955675678"),
            ("Дмитриев", "Сергей", "Дмитриевич", 100010, "пр. Победы, 9", "+79167778899", "+74956786789"),
            ("Морозова", "Екатерина", "Александровна", 100011, "ул. Южная, 25", "+79168889900", ""),
            ("Ковалёв", "Андрей", "Викторович", 100012, "ул. Северная, 8", "", "+74957891234"),
            ("Зайцева", "Мария", "Игоревна", 100013, "пр. Солнечный, 14", "+79169990011", ""),
            ("Григорьев", "Владимир", "Сергеевич", 100014, "ул. Звёздная, 6", "+79160001122", "+74958912345"),
            ("Соколова", "Наталья", "Павловна", 100015, "ул. Речная, 17", "", "+74959023456"),
            ("Лебедев", "Роман", "Олегович", 100016, "ул. Луговая, 4", "+79161112233", ""),
            ("Козлова", "Юлия", "Михайловна", 100017, "пр. Весенний, 22", "", "+74959134567"),
            ("Новиков", "Артём", "Дмитриевич", 100018, "ул. Осенняя, 9", "+79162223344", ""),
            ("Филиппова", "Алина", "Евгеньевна", 100019, "ул. Парковая, 11", "", "+74959245678"),
            ("Макаров", "Игорь", "Валерьевич", 100020, "пр. Центральный, 16", "+79163334455", "+74959356789"),
            ("Андреева", "Светлана", "Николаевна", 100021, "ул. Солнечная, 18", "+79164445566", ""),
            ("Крылов", "Егор", "Алексеевич", 100022, "ул. Лесная, 13", "", "+74959467890"),
            ("Медведева", "Виктория", "Сергеевна", 100023, "пр. Южный, 7", "+79165556677", ""),
            ("Белов", "Максим", "Иванович", 100024, "ул. Полевая, 5", "", "+74959578901"),
            ("Семёнова", "Ксения", "Владимировна", 100025, "ул. Горная, 20", "+79166667788", "+74959689012"),
            ("Виноградов", "Даниил", "Петрович", 100026, "пр. Западный, 3", "+79167778899", ""),
            ("Кудрявцева", "Полина", "Олеговна", 100027, "ул. Сиреневая, 12", "", "+74959790123"),
            ("Савельев", "Никита", "Михайлович", 100028, "ул. Рябиновая, 15", "+79168889900", ""),
            ("Рябова", "Анастасия", "Дмитриевна", 100029, "пр. Восточный, 9", "", "+74959801234"),
            ("Егоров", "Илья", "Викторович", 100030, "ул. Цветочная, 6", "+79169990011", "+74959912345"),
            ("Шарова", "Дарья", "Александровна", 100031, "ул. Берёзовая, 14", "+79160001122", ""),
            ("Титов", "Глеб", "Сергеевич", 100032, "пр. Северный, 11", "", "+74950023456"),
            ("Захарова", "Варвара", "Игоревна", 100033, "ул. Вишнёвая, 8", "+79161112233", ""),
            ("Громов", "Лев", "Павлович", 100034, "ул. Кленовая, 17", "", "+74950134567"),
            ("Фомина", "София", "Михайловна", 100035, "пр. Летний, 22", "+79162223344", "+74950245678"),
            ("Орлов", "Тимофей", "Дмитриевич", 100036, "ул. Тенистая, 9", "+79163334455", ""),
            ("Миронова", "Вероника", "Евгеньевна", 100037, "ул. Радужная, 11", "", "+74950356789"),
            ("Воробьёв", "Арсений", "Валерьевич", 100038, "пр. Осенний, 16", "+79164445566", ""),
            ("Котова", "Милана", "Николаевна", 100039, "ул. Жемчужная, 18", "", "+74950467890"),
            ("Богданов", "Марк", "Алексеевич", 100040, "ул. Изумрудная, 13", "+79165556677", "+74950578901"),
            ("Степанова", "Ева", "Сергеевна", 100041, "пр. Зимний, 7", "+79166667788", ""),
            ("Горбунов", "Ярослав", "Иванович", 100042, "ул. Янтарная, 5", "", "+74950689012"),
            ("Куликова", "Арина", "Владимировна", 100043, "ул. Сапфировая, 20", "+79167778899", ""),
            ("Пономарёв", "Вадим", "Петрович", 100044, "пр. Южный, 3", "", "+74950790123"),
            ("Гаврилова", "Лидия", "Олеговна", 100045, "ул. Рубиновая, 12", "+79168889900", "+74950801234"),
            ("Лазарев", "Матвей", "Михайлович", 100046, "ул. Алмазная, 15", "+79169990011", ""),
            ("Ефимова", "Злата", "Дмитриевна", 100047, "пр. Весенний, 9", "", "+74950912345"),
            ("Чернов", "Кирилл", "Викторович", 100048, "ул. Жасминовая, 6", "+79160001122", ""),
            ("Романова", "Элина", "Александровна", 100049, "ул. Лавандовая, 14", "", "+74951023456"),
            ("Суханов", "Виктор", "Сергеевич", 100050, "пр. Солнечный, 11", "+79161112233", "+74951134567")
        ]

        for record in test_records:
            self.add_data(*record)

        print(f"Добавлено {len(test_records)} тестовых записей")