class DatabaseUnavailableError(Exception):
    def __init__(self, message='База данных недоступна'):
        self.message = message
        super().__init__(self.message)


class CurrencyCodeMissingInPathError(Exception):
    def __init__(self, message='Код валюты отсутствует в адресе'):
        self.message = message
        super().__init__(self.message)


class CurrenciesCodesMissingInPathError(Exception):
    def __init__(self, message='Коды валют пары отсутствуют в адресе'):
        self.message = message
        super().__init__(self.message)


class CurrencyNotFoundError(Exception):
    def __init__(self, message='Валюта не найдена'):
        self.message = message
        super().__init__(self.message)
