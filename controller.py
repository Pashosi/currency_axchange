from DTO import DTOCurrencyGet, DTOCurrencyPOST, DTOExchangeRatesGET, DTOExchangeRatesPOST, DTOExchangeRatesPUTCH, \
    DTOExchangeCurrencyCalculationGET
from exceptons import CurrenciesCodesMissingInPathError, CurrencyCodeMissingInPathError, CurrencyNotExistError
from models import Currencies, ExchangeRates
from urllib.parse import urlparse, parse_qs
from decimal import Decimal, ROUND_DOWN

from service import ExchangeCurrencyCalculation


class ControllerCurrency:
    def __init__(self, *args, **kwargs):
        self.model = Currencies('database.db')
        super().__init__(*args, **kwargs)

    def get_one_data(self, currency: str):
        if len(currency) < 3:
            raise CurrencyCodeMissingInPathError()
        result = self.model.get_one_data(currency)
        return DTOCurrencyGet(id=result['id'],
                              name=result['FullName'],
                              code=result['Code'],
                              sign=result['Sign']).to_dict()

    def get_all_data(self):
        all_data = self.model.get_all_data()
        return [DTOCurrencyGet(id=currency['id'],
                               name=currency['FullName'],
                               code=currency['Code'],
                               sign=currency['Sign']).to_dict() for currency in all_data]

    def add_one_data(self, data: dict):
        if not data['name'] or not data['code'] or not data['sign']:
            raise CurrencyCodeMissingInPathError(message='Отсутствует нужное поле формы')
        dto = DTOCurrencyPOST(name=data['name'],
                              code=data['code'],
                              sign=data['sign'])
        self.model.add_one_data(dto)


class ControllerExchangeRates:
    def __init__(self, *args, **kwargs):
        self.model = ExchangeRates('database.db')
        self.service = ExchangeCurrencyCalculation()
        super().__init__(*args, **kwargs)

    def get_all_data(self):
        result = []
        for data in self.model.get_all_data():
            result.append(DTOExchangeRatesGET(
                id=data[0],
                baseCurrency=DTOCurrencyGet(id=data[2], code=data[3], name=data[4], sign=data[5]),
                targetCurrency=DTOCurrencyGet(id=data[6], code=data[7], name=data[8], sign=data[9]),
                rate=data[1]
            ).to_dict())
        return result

    def get_one_data(self, path: str):
        currency_pair = path.split('/')[-1]
        if len(currency_pair) < 6:
            raise CurrenciesCodesMissingInPathError()
        base_currency, target_currency = currency_pair[-6:-3], currency_pair[-3:]
        data = self.model.get_one_data(base_currency, target_currency)
        return DTOExchangeRatesGET(
            id=data[0],
            baseCurrency=DTOCurrencyGet(id=data[2], code=data[3], name=data[4], sign=data[5]),
            targetCurrency=DTOCurrencyGet(id=data[6], code=data[7], name=data[8], sign=data[9]),
            rate=data[1]
        ).to_dict()

    def add_one_data(self, data: dict):
        if len(data['baseCurrencyCode'][0]) < 3 or len(data['targetCurrencyCode'][0]) < 3:
            raise CurrenciesCodesMissingInPathError()
        self.model.add_one_data(
            DTOExchangeRatesPOST(
                baseCurrency=data['baseCurrencyCode'][0],
                targetCurrency=data['targetCurrencyCode'][0],
                rate=data['rate'][0]
            )
        )

    def update_one_data(self, path: str, data: dict):
        currency_pair = path.split('/')[-1]
        if len(currency_pair) < 6:
            raise CurrenciesCodesMissingInPathError()
        base_currency, target_currency = path[-6:-3], path[-3:]
        self.model.update_one_data(DTOExchangeRatesPUTCH(
            baseCurrency=base_currency,
            targetCurrency=target_currency,
            rate=data['rate'][0]
        ))
        data = self.model.get_one_data(base_currency, target_currency)
        return DTOExchangeRatesGET(
            id=data[0],
            baseCurrency=DTOCurrencyGet(id=data[2], code=data[3], name=data[4], sign=data[5]),
            targetCurrency=DTOCurrencyGet(id=data[6], code=data[7], name=data[8], sign=data[9]),
            rate=data[1]
        ).to_dict()

    def get_currency_calculation(self, path: str):
        parse = urlparse(path)
        pars_dict = parse_qs(parse.query)
        calculated_currency = self.service.get_currency_calculation(DTOExchangeCurrencyCalculationGET(
            baseCurrency=DTOCurrencyGet(code=pars_dict['from'][0]),
            targetCurrency=DTOCurrencyGet(code=pars_dict['to'][0]),
            amount=Decimal(pars_dict['amount'][0]).quantize(Decimal('.01'), rounding=ROUND_DOWN),
        ))
        return calculated_currency.to_dict()
