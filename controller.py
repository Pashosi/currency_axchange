from DTO import DTOCurrencyGet, DTOCurrencyPOST
from models import Currencies


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

