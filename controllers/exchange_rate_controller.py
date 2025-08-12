import json
import urllib.parse
from models.exchange_rates_dao import ExchangeRatesDAO
from models.currency_dao import CurrencyDAO

class ExchangeRateController:
    """
    Controller for ExchangeRates table
    """
    def __init__(self, exchange_rates_dao: ExchangeRatesDAO, currency_dao: CurrencyDAO):
        self._exchange_rates_dao = exchange_rates_dao
        self._currency_dao = currency_dao

    def handle_get_exchange_rates(self, handler):
        try:
            exchange_rates = self._exchange_rates_dao.get_all()
            
            if not exchange_rates:
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json; charset=utf-8")
                handler.send_header("Access-Control-Allow-Origin", "*")
                handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
                handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                handler.end_headers()
                handler.wfile.write(json.dumps([], ensure_ascii=False).encode('utf-8'))
                return

            formatted_rates = []
            for rate in exchange_rates:
                base_currency = self._currency_dao.get_currency_by_id(rate['base_currency_id'])
                target_currency = self._currency_dao.get_currency_by_id(rate['target_currency_id'])
                
                if base_currency and target_currency:
                    formatted_rate = {
                        "id": rate["id"],
                        "baseCurrency": {
                            "id": base_currency["id"],
                            "name": base_currency["fullname"],
                            "code": base_currency["code"],
                            "sign": base_currency["sign"]
                        },
                        "targetCurrency": {
                            "id": target_currency["id"],
                            "name": target_currency["fullname"],
                            "code": target_currency["code"],
                            "sign": target_currency["sign"]
                        },
                        "rate": rate["rate"]
                    }
                    formatted_rates.append(formatted_rate)

            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(formatted_rates, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            print(f"Error in handle_get_exchange_rates: {e}")  # Добавили логирование
            self._send_error_response(handler, 500, "Database error")

    def handle_get_exchange_rate_by_codes(self, handler):
        try:
            path = handler.path
            path_parts = path.split("/")
            if len(path_parts) < 3 or not path_parts[-1]:
                self._send_error_response(handler, 400, "Currency pair codes are missing")
                return
            
            currency_pair = path_parts[-1].upper()
            if len(currency_pair) != 6:
                self._send_error_response(handler, 400, "Invalid currency pair format")
                return
                
            base_code = currency_pair[:3]
            target_code = currency_pair[3:]
            
            base_currency = self._currency_dao.get_currency_by_code(base_code)
            target_currency = self._currency_dao.get_currency_by_code(target_code)
            
            if not base_currency or not target_currency:
                self._send_error_response(handler, 404, "Currency not found")
                return
            
            exchange_rate = self._exchange_rates_dao.get_exchange_rate(
                base_currency["id"], target_currency["id"]
            )
            
            if not exchange_rate:
                self._send_error_response(handler, 404, "Exchange rate not found")
                return
            
            formatted_rate = {
                "id": exchange_rate["id"],
                "baseCurrency": {
                    "id": base_currency["id"],
                    "name": base_currency["fullname"],
                    "code": base_currency["code"],
                    "sign": base_currency["sign"]
                },
                "targetCurrency": {
                    "id": target_currency["id"],
                    "name": target_currency["fullname"],
                    "code": target_currency["code"],
                    "sign": target_currency["sign"]
                },
                "rate": exchange_rate["rate"]
            }
            
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(formatted_rate, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(handler, 500, "Database error")

    def handle_post_exchange_rates(self, handler):
        try:
            content_length = int(handler.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_response(handler, 400, "Request body is required")
                return
            
            post_data = handler.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            required_fields = ['baseCurrencyCode', 'targetCurrencyCode', 'rate']
            for field in required_fields:
                if field not in form_data or not form_data[field][0].strip():
                    self._send_error_response(handler, 400, f"Required field '{field}' is missing")
                    return
            
            base_code = form_data['baseCurrencyCode'][0].strip().upper()
            target_code = form_data['targetCurrencyCode'][0].strip().upper()
            rate_str = form_data['rate'][0].strip()
            
            try:
                rate = float(rate_str)
                if rate <= 0:
                    raise ValueError("Rate must be positive")
            except ValueError:
                self._send_error_response(handler, 400, "Invalid rate value")
                return
            
            base_currency = self._currency_dao.get_currency_by_code(base_code)
            target_currency = self._currency_dao.get_currency_by_code(target_code)
            
            if not base_currency:
                self._send_error_response(handler, 404, f"Base currency '{base_code}' not found")
                return
            if not target_currency:
                self._send_error_response(handler, 404, f"Target currency '{target_code}' not found")
                return
            
            rate_id = self._exchange_rates_dao.insert(
                base_currency["id"], target_currency["id"], rate
            )
            
            new_rate = {
                "id": rate_id,
                "baseCurrency": {
                    "id": base_currency["id"],
                    "name": base_currency["fullname"],
                    "code": base_currency["code"],
                    "sign": base_currency["sign"]
                },
                "targetCurrency": {
                    "id": target_currency["id"],
                    "name": target_currency["fullname"],
                    "code": target_currency["code"],
                    "sign": target_currency["sign"]
                },
                "rate": rate
            }
            
            handler.send_response(201)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(new_rate, ensure_ascii=False).encode('utf-8'))
            
        except ValueError as e:
            if "already exists" in str(e) or "invalid" in str(e).lower():
                self._send_error_response(handler, 409, "Exchange rate for this currency pair already exists")
            else:
                self._send_error_response(handler, 400, str(e))
        except Exception as e:
            self._send_error_response(handler, 500, "Database error")

    def handle_patch_exchange_rate(self, handler):
        try:
            path = handler.path
            path_parts = path.split("/")
            if len(path_parts) < 3 or not path_parts[-1]:
                self._send_error_response(handler, 400, "Currency pair codes are missing")
                return
            
            currency_pair = path_parts[-1].upper()
            if len(currency_pair) != 6:
                self._send_error_response(handler, 400, "Invalid currency pair format")
                return
                
            base_code = currency_pair[:3]
            target_code = currency_pair[3:]
            
            content_length = int(handler.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_response(handler, 400, "Request body is required")
                return
            
            patch_data = handler.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(patch_data)
            
            if 'rate' not in form_data or not form_data['rate'][0].strip():
                self._send_error_response(handler, 400, "Required field 'rate' is missing")
                return
            
            rate_str = form_data['rate'][0].strip()
            
            try:
                rate = float(rate_str)
                if rate <= 0:
                    raise ValueError("Rate must be positive")
            except ValueError:
                self._send_error_response(handler, 400, "Invalid rate value")
                return
            
            base_currency = self._currency_dao.get_currency_by_code(base_code)
            target_currency = self._currency_dao.get_currency_by_code(target_code)
            
            if not base_currency or not target_currency:
                self._send_error_response(handler, 404, "Currency not found")
                return
            
            success = self._exchange_rates_dao.set_exchange_rate(
                base_currency["id"], target_currency["id"], rate
            )
            
            if not success:
                self._send_error_response(handler, 404, "Exchange rate not found")
                return
            
            updated_rate = self._exchange_rates_dao.get_exchange_rate(
                base_currency["id"], target_currency["id"]
            )
            
            formatted_rate = {
                "id": updated_rate["id"],
                "baseCurrency": {
                    "id": base_currency["id"],
                    "name": base_currency["fullname"],
                    "code": base_currency["code"],
                    "sign": base_currency["sign"]
                },
                "targetCurrency": {
                    "id": target_currency["id"],
                    "name": target_currency["fullname"],
                    "code": target_currency["code"],
                    "sign": target_currency["sign"]
                },
                "rate": rate
            }
            
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(formatted_rate, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(handler, 500, "Database error")

    def _send_error_response(self, handler, status_code, message):
        error_response = {"message": message}
        handler.send_response(status_code)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        handler.end_headers()
        handler.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))