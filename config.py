from dataclasses import dataclass


@dataclass
class Addresses:
    # GET Получение списка валют или в случае c
    # POST добавление новой валюты в базу
    currencies: str = '/currencies'

    # Получение конкретной валюты
    currency: str = '/currency/'

    # GET Получение списка всех обменных курсов или в случае с
    # POST добавление нового обменного курса в базу
    exchangeRates: str = '/exchangeRates'

    # GET Получение конкретного обменного курса или в случае с
    # POST обновление существующего в базе обменного курса
    # PATCH Обновление существующего в базе обменного курса
    exchangeRate: str = '/exchangeRate/'

    # GET Расчёт перевода определённого количества средств из одной валюты в другую.
    currency_calculation: str = '/exchange?'

    db_name = 'database.db'
