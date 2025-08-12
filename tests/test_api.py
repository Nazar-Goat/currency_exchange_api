import requests
import json

BASE_URL = "http://localhost:8000"

def test_get_currencies():
    print("=== Тестируем GET /currencies ===")
    response = requests.get(f"{BASE_URL}/currencies")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_currency():
    print("=== Тестируем GET /currency/USD ===")
    response = requests.get(f"{BASE_URL}/currency/USD")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_post_currency():
    print("=== Тестируем POST /currencies ===")
    data = {
        "name": "Chinese Yuan",
        "code": "CNY", 
        "sign": "¥"
    }
    response = requests.post(f"{BASE_URL}/currencies", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_exchange_rates():
    print("=== Тестируем GET /exchangeRates ===")
    response = requests.get(f"{BASE_URL}/exchangeRates")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_get_exchange_rate():
    print("=== Тестируем GET /exchangeRate/USDEUR ===")
    response = requests.get(f"{BASE_URL}/exchangeRate/USDEUR")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_post_exchange_rate():
    print("=== Тестируем POST /exchangeRates ===")
    data = {
        "baseCurrencyCode": "CNY",
        "targetCurrencyCode": "RUB", 
        "rate": "13.2"
    }
    response = requests.post(f"{BASE_URL}/exchangeRates", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_patch_exchange_rate():
    print("=== Тестируем PATCH /exchangeRate/USDEUR ===")
    data = {
        "rate": "0.92"
    }
    response = requests.patch(f"{BASE_URL}/exchangeRate/USDEUR", data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_exchange():
    print("=== Тестируем GET /exchange ===")
    
    print("Тест 1: Прямой курс USD -> EUR")
    response = requests.get(f"{BASE_URL}/exchange?from=USD&to=EUR&amount=100")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    print("Тест 2: Обратный курс EUR -> USD")
    response = requests.get(f"{BASE_URL}/exchange?from=EUR&to=USD&amount=100")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    print("Тест 3: Кросс-курс AUD -> JPY (через USD)")
    response = requests.get(f"{BASE_URL}/exchange?from=AUD&to=JPY&amount=100")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

def test_error_cases():
    print("=== Тестируем обработку ошибок ===")
    
    print("Тест: Несуществующая валюта")
    response = requests.get(f"{BASE_URL}/currency/XXX")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()
    
    print("Тест: Несуществующий курс")
    response = requests.get(f"{BASE_URL}/exchange?from=USD&to=XXX&amount=100")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()

if __name__ == "__main__":
    try:
        print("Запустите сервер командой: python myServer.py")
        print("Затем запустите этот скрипт для тестирования API\n")
        
        test_get_currencies()
        test_get_currency()
        test_post_currency()
        test_get_exchange_rates()
        test_get_exchange_rate()
        test_post_exchange_rate()
        test_patch_exchange_rate()
        test_exchange()
        test_error_cases()
        
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удается подключиться к серверу.")
        print("Убедитесь, что сервер запущен на http://localhost:8000")