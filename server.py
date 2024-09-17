import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from controller import ControllerCurrency
from models import Currencies
from config import Addresses


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.controller = ControllerCurrency()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith(Addresses.currency):
            curr = self.path.split('/')[-1]
            print(self.controller.get_one_data(curr).to_dict())
        elif self.path == Addresses.currencies:
            print(self.controller.get_all_data())

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Request, {self.path}!".encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length) # Тело запроса
        data = json.loads(post_data)
        if self.path == Addresses.currencies:
            self.controller.add_one_data(data)
            response = {'data': data}

            self.send_response(201) # Статус ответа: Created
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()
