from decimal import Decimal, ROUND_DOWN

from DTO import DTOExchangeCurrencyCalculationGET, DTOCurrencyGet
from models import ExchangeRates, Currencies


class ExchangeCurrencyCalculation:
    def __init__(self):
        self.model_exchange = ExchangeRates('database.db')
        self.model_currency = Currencies('database.db')

    def get_currency_calculation(self, dto: DTOExchangeCurrencyCalculationGET):
        get_base_data = self.get_currency_for_dto(dto.baseCurrency.code)
        get_target_data = self.get_currency_for_dto(dto.targetCurrency.code)

        self.add_data_on_dto(dto.baseCurrency, get_base_data)
        self.add_data_on_dto(dto.targetCurrency, get_target_data)

        rate = self.model_exchange.get_exchange_rate(dto)
        dto.rate = rate
        dto.converted = (Decimal(dto.rate) * Decimal(dto.amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        return dto

    def get_currency_for_dto(self, code: str):
        """Запрос кода валюты для получения данных для составления dto"""
        return self.model_currency.get_one_data(code)

    def add_data_on_dto(self, dto: DTOCurrencyGet, data: dict):
        """Вставка данных в существующий dto, кроме code"""
        dto.id = data['id']
        dto.name = data['FullName']
        dto.sign = data['Sign']
