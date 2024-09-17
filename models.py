import sqlite3

from DTO import DTOCurrencyPOST


class Currencies:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_one_data(self, code: str):
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM Currencies WHERE Code = "{code}"')
            results = cursor.fetchone()
            return dict(results)

    def get_all_data(self):
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM Currencies')
            results = cursor.fetchall()
            results = list(map(lambda x: dict(x), results))
            return results

    def add_one_data(self, dto: DTOCurrencyPOST):
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO Currencies (FullName, Code, Sign) VALUES (?, ?, ?)', (dto.name, dto.code, dto.sign))

