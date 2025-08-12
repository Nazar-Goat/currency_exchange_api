import json
import urllib.parse
from models.currency_dao import CurrencyDAO

class CurrencyController:
    """
    Controller class for Currency table
    """

    def __init__(self, curr_dao: CurrencyDAO):
        self._currency_dao = curr_dao

    def handle_get_currencies(self, handler):
        try:
            currencies = self._currency_dao.get_all_currencies()
            formatted_currencies = []
            for currency in currencies:
                formatted_currencies.append({
                    "id": currency["id"],
                    "name": currency["fullname"],  
                    "code": currency["code"],
                    "sign": currency["sign"]
                })
            
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(formatted_currencies, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self._send_error_response(handler, 500, "Database error")

    def handle_get_currency_by_code(self, handler):
        try:
            path_parts = handler.path.split("/")
            if len(path_parts) < 3 or not path_parts[-1]:
                self._send_error_response(handler, 400, "Currency code is missing")
                return
            
            curr_code = path_parts[-1].upper()
            
            currency = self._currency_dao.get_currency_by_code(curr_code)
            if currency:
                formatted_currency = {
                    "id": currency["id"],
                    "name": currency["fullname"],  
                    "code": currency["code"],
                    "sign": currency["sign"]
                }
                
                handler.send_response(200)
                handler.send_header("Content-Type", "application/json; charset=utf-8")
                handler.send_header("Access-Control-Allow-Origin", "*")
                handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
                handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                handler.end_headers()
                handler.wfile.write(json.dumps(formatted_currency, ensure_ascii=False).encode('utf-8'))
            else:
                self._send_error_response(handler, 404, "Currency not found")
        except Exception as e:
            self._send_error_response(handler, 500, "Database error")

    def handle_post_currencies(self, handler):
        try:
            content_length = int(handler.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_error_response(handler, 400, "Request body is required")
                return
            
            post_data = handler.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)
            
            required_fields = ['name', 'code', 'sign']
            for field in required_fields:
                if field not in form_data or not form_data[field][0].strip():
                    self._send_error_response(handler, 400, f"Required field '{field}' is missing")
                    return
            
            name = form_data['name'][0].strip()
            code = form_data['code'][0].strip().upper()
            sign = form_data['sign'][0].strip()
            
            # Валидация
            if len(code) != 3:
                self._send_error_response(handler, 400, "Currency code must be 3 characters")
                return
            
            currency_id = self._currency_dao.insert(code, name, sign)
            
            new_currency = {
                "id": currency_id,
                "name": name,
                "code": code,
                "sign": sign
            }
            
            handler.send_response(201)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(new_currency, ensure_ascii=False).encode('utf-8'))
            
        except ValueError as e:
            if "already exists" in str(e):
                self._send_error_response(handler, 409, "Currency with this code already exists")
            else:
                self._send_error_response(handler, 400, str(e))
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
        