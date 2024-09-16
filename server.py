import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from models import Currencies
from config import Addresses


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.model = Currencies('database.db')
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.startswith(Addresses.currency):
            curr = self.path.split('/')[-1]
            self.model.get_one_data(curr)
        elif self.path == Addresses.currencies:
            self.model.get_all_data()

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"Request, {self.path}!".encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        response = {"message": f"Hello, {data['name']}!"}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()
