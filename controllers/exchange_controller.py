import json
import urllib.parse
from decimal import Decimal, ROUND_HALF_UP
from models.currency_dao import CurrencyDAO
from models.exchange_rates_dao import ExchangeRatesDAO

class ExchangeController:

    def __init__(self, currency_dao: CurrencyDAO, exchange_rates_dao: ExchangeRatesDAO):
        self._currency_dao = currency_dao
        self._exchange_rates_dao = exchange_rates_dao

    def _send_error_response(self, handler, status_code, message):
        """Отправка ошибки в формате JSON"""
        error_response = {"message": message}
        handler.send_response(status_code)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        handler.end_headers()
        handler.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))

    def handle_exchange(self, handler):
        """Calculation of the transfer of a certain amount of funds from one currency to another"""
        try:
            
            parsed_url = urllib.parse.urlparse(handler.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            
            required_params = ['from', 'to', 'amount']
            for param in required_params:
                if param not in query_params or not query_params[param][0].strip():
                    self._send_error_response(handler, 400, f"Required parameter '{param}' is missing")
                    return
            
            from_code = query_params['from'][0].strip().upper()
            to_code = query_params['to'][0].strip().upper()
            amount_str = query_params['amount'][0].strip()
            
            
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    raise ValueError("Amount must be positive")
            except (ValueError, TypeError):
                self._send_error_response(handler, 400, "Invalid amount value")
                return
            
            
            from_currency = self._currency_dao.get_currency_by_code(from_code)
            to_currency = self._currency_dao.get_currency_by_code(to_code)
            
            if not from_currency:
                self._send_error_response(handler, 404, f"Currency '{from_code}' not found")
                return
            if not to_currency:
                self._send_error_response(handler, 404, f"Currency '{to_code}' not found")
                return
            
            
            exchange_rate = self._get_exchange_rate(from_currency["id"], to_currency["id"])
            
            if exchange_rate is None:
                self._send_error_response(handler, 404, "Exchange rate not found")
                return
            
            
            converted_amount = amount * Decimal(str(exchange_rate))
            
            
            converted_amount = converted_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            
            response = {
                "baseCurrency": {
                    "id": from_currency["id"],
                    "name": from_currency["fullname"],
                    "code": from_currency["code"],
                    "sign": from_currency["sign"]
                },
                "targetCurrency": {
                    "id": to_currency["id"],
                    "name": to_currency["fullname"],
                    "code": to_currency["code"],
                    "sign": to_currency["sign"]
                },
                "rate": float(exchange_rate),
                "amount": float(amount),
                "convertedAmount": float(converted_amount)
            }
            
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json; charset=utf-8")
            handler.send_header("Access-Control-Allow-Origin", "*")
            handler.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS") 
            handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
            handler.end_headers()
            handler.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self._send_error_response(handler, 500, "Server error")

    def _get_exchange_rate(self, from_id: int, to_id: int):
        """
        Getting the exchange rate in one of three scenarios:
        1. Direct rate A -> B
        2. Reverse rate B -> A (take 1/rate)
        3. Cross rate via USD (USD -> A and USD -> B, calculate A -> B)
        """
        
        direct_rate = self._exchange_rates_dao.get_exchange_rate(from_id, to_id)
        if direct_rate:
            return direct_rate["rate"]
        
        reverse_rate = self._exchange_rates_dao.get_exchange_rate(to_id, from_id)
        if reverse_rate:
            return 1.0 / reverse_rate["rate"]
        
        usd_currency = self._currency_dao.get_currency_by_code("USD")
        if not usd_currency:
            return None
        
        usd_id = usd_currency["id"]
        
        if from_id == usd_id or to_id == usd_id:
            return None
        
        usd_to_from = self._exchange_rates_dao.get_exchange_rate(usd_id, from_id)
        usd_to_to = self._exchange_rates_dao.get_exchange_rate(usd_id, to_id)
        
        if usd_to_from and usd_to_to:
            return usd_to_to["rate"] / usd_to_from["rate"]
        
        from_to_usd = self._exchange_rates_dao.get_exchange_rate(from_id, usd_id)
        to_to_usd = self._exchange_rates_dao.get_exchange_rate(to_id, usd_id)
        
        if from_to_usd and to_to_usd:
            # from -> USD, to -> USD => from -> to = (from -> USD) / (to -> USD)
            return from_to_usd["rate"] / to_to_usd["rate"]
        
        if from_to_usd and usd_to_to:
            return from_to_usd["rate"] * usd_to_to["rate"]
        
        if usd_to_from and to_to_usd:
            return (1.0 / usd_to_from["rate"]) * (1.0 / to_to_usd["rate"])
        
        return None

    