from decimal import Decimal, ROUND_DOWN

from DTO import DTOExchangeCurrencyCalculationGET, DTOCurrencyGet
from config import Addresses
from models import ExchangeRates, Currencies


class ExchangeCurrencyCalculation:
    def __init__(self):
        self.model_exchange = ExchangeRates(Addresses.db_name)
        self.model_currency = Currencies(Addresses.db_name)

    def get_currency_calculation(self, dto: DTOExchangeCurrencyCalculationGET):
        """
        Варианты обработки курсов:
        -прямой
        -обратный
        -кросс-курс
        """
        # Прямой курс
        if rate := self.model_exchange.get_exchange_rate(dto.baseCurrency.code, dto.targetCurrency.code):
            dto.rate = rate[0]
            dto.converted = (Decimal(dto.rate) * Decimal(dto.amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        # Обратный
        elif rate := self.model_exchange.get_exchange_rate(dto.targetCurrency.code, dto.baseCurrency.code):
            dto.rate = (Decimal('1') / Decimal(rate[0])).quantize(Decimal('.01'), rounding=ROUND_DOWN)
            dto.converted = (Decimal(dto.rate) * Decimal(dto.amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)
        # Кросс-курс
        elif self.model_exchange.get_exchange_rate('USD',
                                                   dto.baseCurrency.code) or self.model_exchange.get_exchange_rate(
                'USD', dto.targetCurrency.code):
            base_rate_usd = self.model_exchange.get_exchange_rate('USD', dto.baseCurrency.code)
            target_rat_usd = self.model_exchange.get_exchange_rate('USD', dto.targetCurrency.code)
            dto.rate = (Decimal(base_rate_usd[0]) * Decimal(target_rat_usd[0])).quantize(Decimal('.01'),
                                                                                         rounding=ROUND_DOWN)
            dto.converted = (Decimal(dto.rate) * Decimal(dto.amount)).quantize(Decimal('.01'), rounding=ROUND_DOWN)

        # Запрос данных для формирования DTO
        get_base_data = self.get_currency_for_dto(dto.baseCurrency.code)
        get_target_data = self.get_currency_for_dto(dto.targetCurrency.code)

        # Добавление данных в DTO
        self.add_data_on_dto(dto.baseCurrency, get_base_data)
        self.add_data_on_dto(dto.targetCurrency, get_target_data)
        return dto

    def get_currency_for_dto(self, code: str):
        """Запрос кода валюты для получения данных для составления dto"""
        return self.model_currency.get_one_data(code)

    def add_data_on_dto(self, dto: DTOCurrencyGet, data: dict):
        """Вставка данных в существующий dto, кроме code"""
        dto.id = data['id']
        dto.name = data['FullName']
        dto.sign = data['Sign']
