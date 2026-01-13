
# 💱 Currency Exchange API

**REST API** for managing currencies and exchange rates, implemented in **Python** using the **MVC pattern**.

---

## 📁 Project Structure

```
CURRENCY_EXCHANGE_API/
├── models/
│   ├── __init__.py
│   ├── db.py                    # Database connection and helper class
│   ├── currency_dao.py          # DAO for the Currencies table
│   └── exchange_rates_dao.py    # DAO for the ExchangeRates table
├── controllers/
│   ├── __init__.py
│   ├── currency_controller.py   # Controller for currency endpoints
│   ├── exchange_rate_controller.py  # Controller for exchange rates
│   └── exchange_controller.py   # Controller for currency exchange logic
├── tests/
│   └── test_dao.py              # Tests for the DAO layer
│   └── test_api.py              # API integration tests
├── database_setup.py            # Database creation and initialization
├── myServer.py                  # Main server file
├── currency_exchange.db         # SQLite database
├── start_with_frontend.py       # Launch server with basic frontend
└── README.md
```

---

## ⚙️ Quick Start

### Initialize the database:

```bash
python database_setup.py
```

### Start the server:

```bash
python myServer.py
```

Server will run at:

```
http://localhost:8000
```

### Run the app with frontend:

```bash
python start_with_frontend.py
```

### Test the API:

```bash
python test_api.py
```

---

## 🌐 API Endpoints

### **Currencies**

* `GET /currencies` — Get all currencies
* `GET /currency/{code}` — Get currency by code (e.g. `/currency/USD`)
* `POST /currencies` — Add a new currency
  **Form fields:** `name`, `code`, `sign`

### **Exchange Rates**

* `GET /exchangeRates` — Get all exchange rates
* `GET /exchangeRate/{basecode}{targetcode}` — Get rate for a currency pair (e.g. `/exchangeRate/USDEUR`)
* `POST /exchangeRates` — Add a new exchange rate
  **Form fields:** `baseCurrencyCode`, `targetCurrencyCode`, `rate`
* `PATCH /exchangeRate/{basecode}{targetcode}` — Update an existing exchange rate
  **Form field:** `rate`

### **Currency Exchange**

* `GET /exchange?from={code}&to={code}&amount={amount}` — Convert an amount from one currency to another
  Example: `/exchange?from=USD&to=EUR&amount=100`

---

## 🔁 Exchange Rate Scenarios

The API supports three exchange rate scenarios:

1. **Direct rate:** The pair A → B exists in the database.
2. **Reverse rate:** The pair B → A exists; use `1 / rate`.
3. **Cross rate via USD:** If USD → A and USD → B exist, compute A → B through USD.

---

## 📋 Example Requests

**Get all currencies**

```bash
curl http://localhost:8000/currencies
```

**Add a new currency**

```bash
curl -X POST http://localhost:8000/currencies \
  -d "name=Chinese Yuan&code=CNY&sign=¥"
```

**Add a new exchange rate**

```bash
curl -X POST http://localhost:8000/exchangeRates \
  -d "baseCurrencyCode=USD&targetCurrencyCode=CNY&rate=7.2"
```

**Convert currency**

```bash
curl "http://localhost:8000/exchange?from=USD&to=EUR&amount=100"
```

**Update an exchange rate**

```bash
curl -X PATCH http://localhost:8000/exchangeRate/USDEUR \
  -d "rate=0.92"
```

---

## ⚠️ Error Handling

Errors are returned in JSON format:

```json
{
  "message": "Error description"
}
```

**HTTP Status Codes:**

* `200` — Success (GET, PATCH)
* `201` — Created (POST)
* `400` — Bad Request (missing or invalid parameters)
* `404` — Not Found (currency or rate doesn’t exist)
* `409` — Conflict (currency/rate already exists)
* `500` — Server Error

---

## 🧪 Testing

The project includes:

* `test_dao.py` — Unit tests for database operations
* `test_api.py` — Integration tests for API endpoints

---

## 🗄 Database Structure

SQLite database with two main tables:

### **Currencies**

| Field      | Type                        | Description            |
| ---------- | --------------------------- | ---------------------- |
| `id`       | INTEGER (PK, AUTOINCREMENT) | Unique identifier      |
| `code`     | VARCHAR (UNIQUE)            | 3-letter currency code |
| `fullname` | VARCHAR                     | Full currency name     |
| `sign`     | VARCHAR                     | Currency symbol        |

### **ExchangeRates**

| Field              | Type                        | Description       |
| ------------------ | --------------------------- | ----------------- |
| `id`               | INTEGER (PK, AUTOINCREMENT) | Unique identifier |
| `baseCurrencyId`   | INTEGER (FK)                | Base currency     |
| `targetCurrencyId` | INTEGER (FK)                | Target currency   |
| `rate`             | DECIMAL(20,6)               | Exchange rate     |

Unique index on `(baseCurrencyId, targetCurrencyId)`.

By default, the database includes test data for the following currencies:
**USD, EUR, RUB, AUD, JPY, GBP, CAD**
