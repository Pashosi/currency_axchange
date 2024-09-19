import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from controller import ControllerCurrency, ControllerExchangeRates
from config import Addresses


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.controller_currency = ControllerCurrency()
        self.controller_exchange = ControllerExchangeRates()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith(Addresses.currency):  # Получение конкретной валюты
            curr = self.path.split('/')[-1]
            print(json.dumps(self.controller_currency.get_one_data(curr).to_dict(), ensure_ascii=False, indent=4))
        elif self.path == Addresses.currencies:  # Получение списка валют
            print(json.dumps(self.controller_currency.get_all_data(), ensure_ascii=False, indent=4))
        elif self.path == Addresses.exchangeRates:  # Получение списка всех обменных курсов
            print(json.dumps(self.controller_exchange.get_all_data(), ensure_ascii=False, indent=4))
        elif self.path.startswith(Addresses.exchangeRate):  # Получение конкретного обменного курса
            base_currency, target_currency = self.path[-6:-3], self.path[-3:]
            print(json.dumps(self.controller_exchange.get_one_data(base_currency, target_currency), ensure_ascii=False,
                             indent=4))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Request, {self.path}!".encode())

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


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()
