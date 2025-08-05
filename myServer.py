from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from models.currency_dao import CurrencyDAO
from models.db import DB

db = DB("currency_exchange.db")
currency_dao = CurrencyDAO(db)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/currencies":
            currencies = currency_dao.get_all_currencies()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(currencies).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

def run():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, MyServer)
    print("Server started on port 8000...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
