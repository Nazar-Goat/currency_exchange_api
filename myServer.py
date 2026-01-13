from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
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

    def do_OPTIONS(self):
        """Обработка preflight запросов"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        try:
            # Главная страница с документацией
            if self.path == "/" or self.path == "":
                self._send_welcome_page()
            
            # Валюты
            elif self.path == "/currencies":
                currency_controller.handle_get_currencies(self)
            elif self.path.startswith("/currency/"):
                currency_controller.handle_get_currency_by_code(self)
            
            # Обменные курсы
            elif self.path == "/exchangeRates":
                exchange_rate_controller.handle_get_exchange_rates(self)
            elif self.path.startswith("/exchangeRate/"):
                exchange_rate_controller.handle_get_exchange_rate_by_codes(self)
            
            # Конвертация
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

    def _send_error_response(self, status_code, message):
        error_response = {"message": message}
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def _send_welcome_page(self):
        """Отдаёт ваш frontend.html на главной странице"""
        try:
            with open('frontend.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Автоматически подставляем URL API (текущий домен)
            content = content.replace(
                "const API_BASE_URL = 'your url';",
                "const API_BASE_URL = window.location.origin;"
            )
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except FileNotFoundError:
            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Error - Frontend Not Found</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
                    h1 { color: #dc3545; }
                    .info { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px auto; max-width: 600px; }
                    a { color: #667eea; text-decoration: none; font-weight: bold; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <h1>⚠️ Error: frontend.html not found</h1>
                <div class="info">
                    <p>Please make sure <code>frontend.html</code> is in the same directory as myServer.py</p>
                    <p>Meanwhile, you can test the API directly:</p>
                    <p><a href="/currencies">📋 View all currencies</a></p>
                    <p><a href="/exchangeRates">💱 View exchange rates</a></p>
                </div>
            </body>
            </html>
            """
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(error_html.encode('utf-8'))


def run():
    port = int(os.environ.get("PORT", 8000))
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, MyServer)
    print(f"Server started on port {port}")
    print("Available endpoints:")
    print("  GET    /")
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