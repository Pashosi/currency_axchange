import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from controller import ControllerCurrency, ControllerExchangeRates
from config import Addresses
from exceptons import DatabaseUnavailableError, CurrencyCodeMissingInPathError, CurrencyNotFoundError, \
    CurrenciesCodesMissingInPathError


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            result = self.get_controller(self.path)
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
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)  # Тело запроса
        data = json.loads(post_data)
        if self.path == Addresses.currencies:  # добавление новой валюты в базу
            self.controller_currency.add_one_data(data)
        elif self.path == Addresses.exchangeRates:  # добавление нового обменного курса в базу
            self.controller_exchange.add_one_data(data)

        response = {'data': data}
        self.send_response(201)  # Статус ответа: Created
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def do_PATCH(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)  # Тело запроса
        data = json.loads(post_data)
        if self.path.startswith(Addresses.exchangeRate):
            self.controller_exchange.update_one_data(self.path, data)
        response = {'data': data}
        self.send_response(200)  # Статус ответа: PATCH
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def get_controller(self, path):
        if path.startswith(Addresses.currency):  # Получение конкретной валюты
            curr = path.split('/')[-1]
            if len(curr) < 3:
                raise CurrencyCodeMissingInPathError()
            return self.controller_currency.get_one_data(curr).to_dict()
        elif path == Addresses.currencies:  # Получение списка валют
            return self.controller_currency.get_all_data()
        elif path == Addresses.exchangeRates:  # Получение списка всех обменных курсов
            return self.controller_exchange.get_all_data()
        elif path.startswith(Addresses.exchangeRate):  # Получение конкретного обменного курса
            curr = path.split('/')[-1]
            return self.controller_exchange.get_one_data(curr)
        elif path.startswith(Addresses.currency_calculation):  # Расчёт кол-ва средств из одной валюты в другую.
            return self.controller_exchange.get_currency_calculation(self.path)

    def send_json_response(self, code: int, message: json):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(message.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()
