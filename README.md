# Проект "Обмен валют"

REST API для работы с валютами и обменными курсами, реализованный на Python с использованием паттерна MVC.

## Структура проекта

```
CURRENCY_EXCHANGE_API/
├── models/
│   ├── __init__.py
│   ├── db.py                    # Класс для работы с БД
│   ├── currency_dao.py          # DAO для таблицы Currencies
│   └── exchange_rates_dao.py    # DAO для таблицы ExchangeRates
├── controllers/
│   ├── __init__.py
│   ├── currency_controller.py   # Контроллер для валют
│   ├── exchange_rate_controller.py  # Контроллер для курсов
│   └── exchange_controller.py   # Контроллер для обмена
├── tests/
│   └── test_dao.py             # Тесты DAO слоя
|   |__    test_api.py          # Скрипт для тестирования API
├── database_setup.py           # Создание и инициализация БД
├── myServer.py                 # Основной сервер                
├── currency_exchange.db        # База данных SQLite
└── README.md
```

## Быстрый старт

1. **Инициализация базы данных**:
   ```bash
   python database_setup.py
   ```

2. **Запуск сервера**:
   ```bash
   python myServer.py
   ```
   Сервер запустится на `http://localhost:8000`

3. **Запуск приложения с фронтендом**:
   ```bash
   python start_with_frontend.py

4. **Тестирование API**:
   ```bash
   python test_api.py
   ```

## API Endpoints

### Валюты

- **GET /currencies** - Получить список всех валют
- **GET /currency/{code}** - Получить валюту по коду (например, `/currency/USD`)
- **POST /currencies** - Добавить новую валюту
  - Поля формы: `name`, `code`, `sign`

### Обменные курсы

- **GET /exchangeRates** - Получить список всех обменных курсов
- **GET /exchangeRate/{basecode}{targetcode}** - Получить курс для пары валют (например, `/exchangeRate/USDEUR`)
- **POST /exchangeRates** - Добавить новый обменный курс
  - Поля формы: `baseCurrencyCode`, `targetCurrencyCode`, `rate`
- **PATCH /exchangeRate/{basecode}{targetcode}** - Обновить существующий курс
  - Поле формы: `rate`

### Обмен валюты

- **GET /exchange?from={code}&to={code}&amount={amount}** - Конвертировать сумму из одной валюты в другую
  - Пример: `/exchange?from=USD&to=EUR&amount=100`

## Сценарии обмена валют

API поддерживает 3 сценария получения курса обмена:

1. **Прямой курс**: Есть курс A → B в таблице
2. **Обратный курс**: Есть курс B → A, берем 1/rate
3. **Кросс-курс через USD**: Есть курсы USD → A и USD → B, вычисляем A → B

## Примеры запросов

### Получить все валюты
```bash
curl http://localhost:8000/currencies
```

### Добавить новую валюту
```bash
curl -X POST http://localhost:8000/currencies \
  -d "name=Chinese Yuan&code=CNY&sign=¥"
```

### Добавить обменный курс
```bash
curl -X POST http://localhost:8000/exchangeRates \
  -d "baseCurrencyCode=USD&targetCurrencyCode=CNY&rate=7.2"
```

### Конвертировать валюту
```bash
curl "http://localhost:8000/exchange?from=USD&to=EUR&amount=100"
```

### Обновить курс
```bash
curl -X PATCH http://localhost:8000/exchangeRate/USDEUR \
  -d "rate=0.92"
```

## Обработка ошибок

API возвращает ошибки в формате JSON:

```json
{
  "message": "Описание ошибки"
}
```

### HTTP коды ответов:
- **200** - Успех (GET, PATCH)
- **201** - Создано (POST)
- **400** - Неверный запрос (отсутствуют параметры, неверный формат)
- **404** - Не найдено (валюта или курс не существует)
- **409** - Конфликт (валюта/курс уже существует)
- **500** - Ошибка сервера

## Особенности реализации

- **Паттерн MVC**: Четкое разделение на Model (DAO), View (JSON responses), Controller
- **Защита от SQL Injection**: Использование параметризированных запросов
- **CORS поддержка**: Для работы с фронтенд приложениями
- **Точность вычислений**: Использование `Decimal` для работы с денежными суммами
- **Округление**: Все суммы округляются до 2 знаков после запятой
- **Валидация данных**: Проверка всех входящих параметров
- **Обработка ошибок**: Централизованная обработка исключений

## Тестирование

Проект включает:
- **test_dao.py** - Тесты для проверки работы с базой данных
- **test_api.py** - Интеграционные тесты API endpoints

Для тестирования с фронтендом используйте: https://github.com/zhukovsd/currency-exchange-frontend

## База данных

Используется SQLite с двумя таблицами:

### Currencies
- `id` - PRIMARY KEY, AUTOINCREMENT
- `code` - VARCHAR, UNIQUE (трехбуквенный код валюты)
- `fullname` - VARCHAR (полное название)
- `sign` - VARCHAR (символ валюты)

### ExchangeRates
- `id` - PRIMARY KEY, AUTOINCREMENT  
- `baseCurrencyId` - INTEGER, FOREIGN KEY
- `targetCurrencyId` - INTEGER, FOREIGN KEY
- `rate` - DECIMAL(20,6)
- UNIQUE INDEX на пару (baseCurrencyId, targetCurrencyId)

По умолчанию БД создается с тестовыми данными для валют: USD, EUR, RUB, AUD, JPY, GBP, CAD.