import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from controller import ControllerCurrency, ControllerExchangeRates
from config import Addresses
from exceptons import DatabaseUnavailableError, CurrencyCodeMissingInPathError, CurrencyNotFoundError, \
    CurrenciesCodesMissingInPathError, CurrencyDuplicationError, CurrencyNotExistError


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            result = self.get_controller(self.path, self.command)
            result = json.dumps(result, ensure_ascii=False)
            self.send_json_response(200, result)
        except DatabaseUnavailableError as ex:
            self.send_json_response(500, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrencyCodeMissingInPathError as ex:
            self.send_json_response(400, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrencyNotFoundError as ex:
            self.send_json_response(404, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrenciesCodesMissingInPathError as ex:
            self.send_json_response(404, json.dumps({'message': ex.message}, ensure_ascii=False))

    def __init__(self, *args, **kwargs):
        self.controller_currency = ControllerCurrency()
        self.controller_exchange = ControllerExchangeRates()
        super().__init__(*args, **kwargs)

    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)  # Тело запроса
            data = json.loads(post_data)
            result = self.get_controller(self.path, self.command, data)
            result = json.dumps(result, ensure_ascii=False)
            self.send_json_response(201, result)
        except CurrencyCodeMissingInPathError as ex:
            self.send_json_response(400, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrenciesCodesMissingInPathError as ex:
            self.send_json_response(400, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrencyDuplicationError as ex:
            self.send_json_response(409, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrencyNotExistError as ex:
            self.send_json_response(404, json.dumps({'message': ex.message}, ensure_ascii=False))
        except DatabaseUnavailableError as ex:
            self.send_json_response(500, json.dumps({'message': ex.message}, ensure_ascii=False))

    def do_PATCH(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)  # Тело запроса
            data = json.loads(post_data)

            result = self.get_controller(self.path, self.command, data)
            result = json.dumps(result, ensure_ascii=False)
            self.send_json_response(200, result)
        except CurrenciesCodesMissingInPathError as ex:
            self.send_json_response(400, json.dumps({'message': ex.message}, ensure_ascii=False))
        except CurrencyNotExistError as ex:
            self.send_json_response(404, json.dumps({'message': ex.message}, ensure_ascii=False))
        except DatabaseUnavailableError as ex:
            self.send_json_response(500, json.dumps({'message': ex.message}, ensure_ascii=False))

    def get_controller(self, path, command: str, data=None):
        if command == 'GET':
            if path.startswith(Addresses.currency):  # Получение конкретной валюты
                return self.controller_currency.get_one_data(path)
            elif path == Addresses.currencies:  # Получение списка валют
                return self.controller_currency.get_all_data()
            elif path == Addresses.exchangeRates:  # Получение списка всех обменных курсов
                return self.controller_exchange.get_all_data()
            elif path.startswith(Addresses.exchangeRate):  # Получение конкретного обменного курса
                return self.controller_exchange.get_one_data(path)
            elif path.startswith(Addresses.currency_calculation):  # Расчёт кол-ва средств из одной валюты в другую.
                return self.controller_exchange.get_currency_calculation(self.path)
        elif command == 'POST':
            if self.path == Addresses.currencies:  # добавление новой валюты в базу
                self.controller_currency.add_one_data(data)
                return self.controller_currency.get_one_data('/' + data['code'])
            elif self.path == Addresses.exchangeRates:  # добавление нового обменного курса в базу
                self.controller_exchange.add_one_data(data)
                return self.controller_exchange.get_one_data(
                    '/' + data['baseCurrencyCode'] + data['targetCurrencyCode'])
        elif command == 'PATCH':
            if self.path.startswith(Addresses.exchangeRate):
                return self.controller_exchange.update_one_data(self.path, data)

    def send_json_response(self, code: int, message: json):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        print(message)
        self.wfile.write(message.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()
