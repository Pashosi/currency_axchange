from DTO import DTOCurrencyGet, DTOCurrencyPOST, DTOExchangeRatesGET
from models import Currencies, ExchangeRates


class ControllerCurrency:
    def __init__(self, *args, **kwargs):
        self.model = Currencies('database.db')
        super().__init__(*args, **kwargs)

    def get_one_data(self, currency):
        result = self.model.get_one_data(currency)
        return DTOCurrencyGet(id=result['id'],
                              name=result['FullName'],
                              code=result['Code'],
                              sign=result['Sign'])

    def get_all_data(self):
        all_data = self.model.get_all_data()
        return [DTOCurrencyGet(id=currency['id'],
                               name=currency['FullName'],
                               code=currency['Code'],
                               sign=currency['Sign']).to_dict() for currency in all_data]

    def add_one_data(self, data: dict):
        dto = DTOCurrencyPOST(name=data['name'],
                              code=data['code'],
                              sign=data['sign'])
        self.model.add_one_data(dto)


class ControllerExchangeRates:
    def __init__(self, *args, **kwargs):
        self.model = ExchangeRates('database.db')
        super().__init__(*args, **kwargs)

    def get_all_data(self):
        result = []
        for data in self.model.get_all_data():
            result.append(DTOExchangeRatesGET(
                id=data[0],
                baseCurrency=DTOCurrencyGet(data[2], data[3], data[4], data[5]),
                targetCurrency=DTOCurrencyGet(data[6], data[7], data[8], data[9]),
                rate=data[1]
            ).to_dict())
        return result

    def get_one_data(self, base_currency, target_currency):
        data = self.model.get_one_data(base_currency, target_currency)
        return DTOExchangeRatesGET(
            id=data[0],
            baseCurrency=DTOCurrencyGet(data[2], data[3], data[4], data[5]),
            targetCurrency=DTOCurrencyGet(data[6], data[7], data[8], data[9]),
            rate=data[1]
        ).to_dict()
