import sqlite3


class Currencies:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_one_data(self, code: str):
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM Currencies WHERE Code = "{code}"')
            results = cursor.fetchone()
            print(dict(results))

    def get_all_data(self):
        with sqlite3.connect(self.db_name) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM Currencies')
            results = cursor.fetchall()
            results = list(map(lambda x: dict(x), results))
            print(results)

