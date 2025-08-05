from models.db import DB 
from models.currency_dao import CurrencyDAO
from models.exchange_rates_dao import ExchangeRatesDAO

def main():
    db = DB("currency_exchange.db")
    currency_dao = CurrencyDAO(db)
    exchange_rates_dao = ExchangeRatesDAO(db)

    usd = currency_dao.get_currency_by_code("USD")
    eur = currency_dao.get_currency_by_code("EUR")

    print("USD:", usd)
    print("EUR:", eur)

    base_id = usd["id"]
    target_id = eur["id"]

    rate = 0.91
    exchange_rates_dao.set_exchange_rate(base_id, target_id, rate)

    retrieved_rate = exchange_rates_dao.get_exchange_rate(base_id, target_id)

    assert retrieved_rate["rate"] == rate, f"Expected rate {rate}, got {retrieved_rate['rate']}"
    print("Тест прошёл успешно!")
