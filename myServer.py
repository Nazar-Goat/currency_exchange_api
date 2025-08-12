from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from models.currency_dao import CurrencyDAO
from models.exchange_rates_dao import ExchangeRatesDAO
from models.db import DB
from controllers.currency_controller import CurrencyController
from controllers.exchange_rate_controller import ExchangeRateController
from controllers.exchange_controller import ExchangeController

db = DB("currency_exchange.db")
currency_dao = CurrencyDAO(db)
exchange_rates_dao = ExchangeRatesDAO(db)


currency_controller = CurrencyController(currency_dao)
exchange_rate_controller = ExchangeRateController(exchange_rates_dao, currency_dao)
exchange_controller = ExchangeController(currency_dao, exchange_rates_dao)


class MyServer(BaseHTTPRequestHandler):

    def _set_cors_headers(self):
        """Устанавливает CORS заголовки для всех ответов"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Max-Age", "86400")

    def do_GET(self):
        try:
            
            if self.path == "/currencies":
                currency_controller.handle_get_currencies(self)
            elif self.path.startswith("/currency/"):
                currency_controller.handle_get_currency_by_code(self)
            
            
            elif self.path == "/exchangeRates":
                exchange_rate_controller.handle_get_exchange_rates(self)
            elif self.path.startswith("/exchangeRate/"):
                exchange_rate_controller.handle_get_exchange_rate_by_codes(self)
            
            
            elif self.path.startswith("/exchange"):
                exchange_controller.handle_exchange(self)
            
            else:
                self._send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Unexpected error in GET: {e}")
            self._send_error_response(500, "Internal server error")

    def do_POST(self):
        try:
            if self.path == "/currencies":
                currency_controller.handle_post_currencies(self)
            
            elif self.path == "/exchangeRates":
                exchange_rate_controller.handle_post_exchange_rates(self)
            
            else:
                self._send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Unexpected error in POST: {e}")
            self._send_error_response(500, "Internal server error")

    def do_PATCH(self):
        try:
            if self.path.startswith("/exchangeRate/"):
                exchange_rate_controller.handle_patch_exchange_rate(self)
            
            else:
                self._send_error_response(404, "Endpoint not found")
                
        except Exception as e:
            print(f"Unexpected error in PATCH: {e}")
            self._send_error_response(500, "Internal server error")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_error_response(self, status_code, message):
        error_response = {"message": message}
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self._set_cors_headers()  
        self.end_headers()
        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))


def run():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, MyServer)
    print("Server started on http://localhost:8000")
    print("Available endpoints:")
    print("  GET    /currencies")
    print("  GET    /currency/{code}")
    print("  POST   /currencies")
    print("  GET    /exchangeRates")
    print("  GET    /exchangeRate/{basecode}{targetcode}")
    print("  POST   /exchangeRates")
    print("  PATCH  /exchangeRate/{basecode}{targetcode}")
    print("  GET    /exchange?from={code}&to={code}&amount={amount}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()