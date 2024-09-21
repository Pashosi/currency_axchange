import json
import sqlite3

from DTO import DTOCurrencyPOST, DTOExchangeRatesPOST, DTOExchangeRatesPUTCH, DTOExchangeCurrencyCalculationGET


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
            cursor.execute(f'INSERT INTO Currencies (FullName, Code, Sign) VALUES (?, ?, ?)',
                           (dto.name, dto.code, dto.sign))


class ExchangeRates:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def get_all_data(self) -> list:
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
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            sql = """SELECT id FROM Currencies WHERE Code = (?)
                      UNION 
                     SELECT id FROM Currencies WHERE Code = (?)"""
            cursor.execute(sql, (dto.baseCurrency, dto.targetCurrency))
            num_base, num_target = cursor.fetchall()
            sql = """INSERT INTO ExchangeRates (BaseCurrencyId, TargetCurrencyId, Rate)
                        VALUES (?, ?, ?)"""
            cursor.execute(sql, (num_base[0], num_target[0], dto.rate))

    def update_one_data(self, dto: DTOExchangeRatesPUTCH):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            sql = """SELECT id FROM Currencies WHERE Code = (?)
                      UNION 
                     SELECT id FROM Currencies WHERE Code = (?)"""
            cursor.execute(sql, (dto.baseCurrency, dto.targetCurrency))
            num_base, num_target = cursor.fetchall()
            sql = """UPDATE ExchangeRates 
                        SET Rate = (?)
                      WHERE BaseCurrencyId = (?)
                        AND TargetCurrencyId = (?)"""
            cursor.execute(sql, (dto.rate, num_base[0], num_target[0]))

    def get_exchange_rate(self, dto: DTOExchangeCurrencyCalculationGET):
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            sql = """SELECT id FROM Currencies WHERE Code = (?)
                      UNION 
                     SELECT id FROM Currencies WHERE Code = (?)"""
            cursor.execute(sql, (dto.baseCurrency.code, dto.targetCurrency.code))
            num_base, num_target = cursor.fetchall()
            sql = """SELECT Rate FROM ExchangeRates
                      WHERE BaseCurrencyId = (?)
                        AND TargetCurrencyId = (?)"""
            cursor.execute(sql, (num_base[0], num_target[0]))
            rate = cursor.fetchone()
            return rate[0]