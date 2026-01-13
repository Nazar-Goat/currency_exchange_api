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
        """Отправляет приветственную страницу с документацией API"""
        welcome_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Currency Exchange API</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                    color: #333;
                }
                .container { 
                    max-width: 900px; 
                    margin: 0 auto; 
                    background: white; 
                    border-radius: 20px; 
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                h1 { 
                    color: #667eea; 
                    margin-bottom: 10px;
                    font-size: 2.5em;
                }
                .subtitle { 
                    color: #666; 
                    margin-bottom: 30px;
                    font-size: 1.1em;
                }
                h2 { 
                    color: #764ba2; 
                    margin-top: 30px; 
                    margin-bottom: 15px;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                }
                .endpoint { 
                    background: #f8f9fa; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }
                .method { 
                    display: inline-block;
                    padding: 4px 12px; 
                    border-radius: 4px; 
                    font-weight: bold; 
                    margin-right: 10px;
                    font-size: 0.9em;
                }
                .get { background: #28a745; color: white; }
                .post { background: #007bff; color: white; }
                .patch { background: #ffc107; color: #333; }
                code { 
                    background: #e9ecef; 
                    padding: 2px 6px; 
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    color: #d63384;
                }
                .example { 
                    background: #e7f3ff; 
                    padding: 10px; 
                    margin: 10px 0; 
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 0.9em;
                }
                .status { 
                    display: inline-block;
                    padding: 4px 8px; 
                    background: #28a745; 
                    color: white; 
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin-bottom: 20px;
                }
                a { 
                    color: #667eea; 
                    text-decoration: none;
                    font-weight: 500;
                }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>💱 Currency Exchange API</h1>
                <p class="subtitle">RESTful API for currency exchange operations</p>
                <div class="status">✅ API is running</div>
                
                <h2>📚 Available Endpoints</h2>
                
                <h3 style="margin-top: 20px; color: #555;">Currencies</h3>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/currencies</code>
                    <p style="margin-top: 8px;">Get all currencies</p>
                    <div class="example">
                        <a href="/currencies" target="_blank">Try it: /currencies</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/currency/{code}</code>
                    <p style="margin-top: 8px;">Get currency by code (e.g., USD, EUR)</p>
                    <div class="example">
                        <a href="/currency/USD" target="_blank">Try it: /currency/USD</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/currencies</code>
                    <p style="margin-top: 8px;">Add a new currency</p>
                    <p style="margin-top: 8px; font-size: 0.9em;">Body: <code>{"code": "CNY", "name": "Chinese Yuan", "sign": "¥"}</code></p>
                </div>
                
                <h3 style="margin-top: 20px; color: #555;">Exchange Rates</h3>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/exchangeRates</code>
                    <p style="margin-top: 8px;">Get all exchange rates</p>
                    <div class="example">
                        <a href="/exchangeRates" target="_blank">Try it: /exchangeRates</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/exchangeRate/{basecode}{targetcode}</code>
                    <p style="margin-top: 8px;">Get exchange rate for currency pair</p>
                    <div class="example">
                        <a href="/exchangeRate/USDEUR" target="_blank">Try it: /exchangeRate/USDEUR</a>
                    </div>
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <code>/exchangeRates</code>
                    <p style="margin-top: 8px;">Add a new exchange rate</p>
                    <p style="margin-top: 8px; font-size: 0.9em;">Body: <code>{"baseCurrencyCode": "USD", "targetCurrencyCode": "EUR", "rate": 0.91}</code></p>
                </div>
                
                <div class="endpoint">
                    <span class="method patch">PATCH</span>
                    <code>/exchangeRate/{basecode}{targetcode}</code>
                    <p style="margin-top: 8px;">Update exchange rate</p>
                    <p style="margin-top: 8px; font-size: 0.9em;">Body: <code>{"rate": 0.92}</code></p>
                </div>
                
                <h3 style="margin-top: 20px; color: #555;">Currency Exchange</h3>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <code>/exchange?from={code}&to={code}&amount={amount}</code>
                    <p style="margin-top: 8px;">Convert currency</p>
                    <div class="example">
                        <a href="/exchange?from=USD&to=EUR&amount=100" target="_blank">Try it: /exchange?from=USD&to=EUR&amount=100</a>
                    </div>
                </div>
                
                <h2>🔗 Frontend Interface</h2>
                <p>Update your <code>frontend.html</code> with this API URL:</p>
                <div class="example" style="background: #fff3cd; padding: 15px;">
                    const API_BASE_URL = 'https://currency-exchange-api-m146.onrender.com';
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(welcome_html.encode('utf-8'))


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