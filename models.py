import sqlite3

from DTO import DTOCurrencyPOST, DTOExchangeRatesPOST, DTOExchangeRatesPUTCH
from exceptons import DatabaseUnavailableError, CurrencyNotFoundError, CurrencyDuplicationError, CurrencyNotExistError


class Currencies:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_one_data(self, code: str):
        try:
            with sqlite3.connect(self.db_name) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute(f'SELECT * FROM Currencies WHERE Code = "{code}"')
                if results := cursor.fetchone():
                    return dict(results)
                else:
                    raise CurrencyNotFoundError()
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()

    def get_all_data(self):
        try:
            with sqlite3.connect(self.db_name) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                cursor.execute(f'SELECT * FROM Currencies')
                results = cursor.fetchall()
                results = list(map(lambda x: dict(x), results))
                return results
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()

    def add_one_data(self, dto: DTOCurrencyPOST):
        try:
            with sqlite3.connect(self.db_name) as connection:
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                if cursor.execute(f'SELECT * FROM Currencies WHERE Code = "{dto.code[0]}"').fetchone():
                    raise CurrencyDuplicationError()
                cursor.execute(f'INSERT INTO Currencies (FullName, Code, Sign) VALUES (?, ?, ?)',
                               (dto.name[0], dto.code[0], dto.sign[0]))
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()


class ExchangeRates:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_all_data(self) -> list:
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                cursor.execute("""SELECT ex.ID,
                                        ex.Rate,
                                        crs.ID,
                                        crs.Code,
                                        crs.FullName,
                                        crs.Sign,
                                        cr.ID,
                                        cr.Code,
                                        cr.FullName,
                                        cr.Sign
                                    FROM ExchangeRates ex
                                    JOIN Currencies crs
                                      ON crs.id = ex.BaseCurrencyId
                                    JOIN Currencies cr
                                      ON cr.id = ex.TargetCurrencyId""")
                results = cursor.fetchall()
                return results
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()

    def get_one_data(self, base_currency, target_currency):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            sql = """SELECT ex.ID,
                            ex.Rate,
                            crs.ID,
                            crs.Code,
                            crs.FullName,
                            crs.Sign,
                            cr.ID,
                            cr.Code,
                            cr.FullName,
                            cr.Sign
                        FROM ExchangeRates ex
                        JOIN Currencies crs
                          ON crs.id = ex.BaseCurrencyId
                        JOIN Currencies cr
                          ON cr.id = ex.TargetCurrencyId
                       WHERE crs.Code =:base_curr 
                         AND cr.Code =:targ_curr"""
            cursor.execute(sql, {'base_curr': base_currency, 'targ_curr': target_currency})
            results = cursor.fetchone()
            return results

    def add_one_data(self, dto: DTOExchangeRatesPOST):
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                # Запрос на поиск id каждой валюты
                sql = """SELECT id FROM Currencies WHERE Code = (?)
                          UNION ALL
                         SELECT id FROM Currencies WHERE Code = (?)"""
                cursor.execute(sql, (dto.baseCurrency, dto.targetCurrency))
                numbers_currencies = cursor.fetchall()
                if len(numbers_currencies) < 2:
                    raise CurrencyNotExistError(message='Одна (или обе) валюта из валютной пары не существует в БД')
                num_base, num_target = numbers_currencies
                # Проверка на наличие повторяющихся валют
                sql = '''SELECT * 
                           FROM ExchangeRates 
                          WHERE BaseCurrencyId=(?) 
                            AND TargetCurrencyId=(?)'''
                if cursor.execute(sql, (num_base[0], num_target[0])).fetchone():
                    raise CurrencyDuplicationError(message='Валютная пара с таким кодом уже существует')
                # вставка валютной пары и курса
                sql = """INSERT INTO ExchangeRates (BaseCurrencyId, TargetCurrencyId, Rate)
                            VALUES (?, ?, ?)"""
                cursor.execute(sql, (num_base[0], num_target[0], dto.rate))
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()

    def update_one_data(self, dto: DTOExchangeRatesPUTCH):
        try:
            with sqlite3.connect(self.db_name) as connection:
                cursor = connection.cursor()
                sql = """SELECT id FROM Currencies WHERE Code = (?)
                          UNION ALL
                         SELECT id FROM Currencies WHERE Code = (?)"""
                cursor.execute(sql, (dto.baseCurrency, dto.targetCurrency))
                numbers_currencies = cursor.fetchall()
                if len(numbers_currencies) < 2:
                    raise CurrencyNotExistError(message='Валютная пара отсутствует в базе данных')
                num_base, num_target = numbers_currencies
                sql = """UPDATE ExchangeRates 
                            SET Rate = (?)
                          WHERE BaseCurrencyId = (?)
                            AND TargetCurrencyId = (?)"""
                cursor.execute(sql, (dto.rate, num_base[0], num_target[0]))
        except sqlite3.DatabaseError:
            raise DatabaseUnavailableError()

    def get_exchange_rate(self, base_currency: str, target_currency: str):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            num_base, num_target = self.get_id_currencies(cursor, base_currency, target_currency)
            sql = """SELECT Rate FROM ExchangeRates
                      WHERE BaseCurrencyId = (?)
                        AND TargetCurrencyId = (?)"""
            cursor.execute(sql, (num_base[0], num_target[0]))
            rate = cursor.fetchone()
            return rate

    def get_id_currencies(self, cursor, base_currency, target_currency):
        """Получение id-шников по заданным содам валют"""
        sql = """SELECT id FROM Currencies WHERE Code = (?)
                  UNION ALL
                 SELECT id FROM Currencies WHERE Code = (?)"""
        cursor.execute(sql, (base_currency, target_currency))
        return cursor.fetchall()
