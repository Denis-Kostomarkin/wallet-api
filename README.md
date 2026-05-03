# Wallet API

REST API сервис для управления балансом электронных кошельков.

## Стек технологий

- **FastAPI** — асинхронный веб-фреймворк
- **SQLAlchemy 2.0 + aiosqlite** — асинхронная работа с SQLite
- **Pydantic** — валидация данных
- **pytest + pytest-asyncio + HTTPX** — асинхронное тестирование

## Архитектура

```
wallet-api/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── db.py                # Конфигурация БД (SQLite)
│   ├── core/
│   │   └── config.py        # Настройки приложения
│   ├── api/
│   │   └── wallet.py        # Роутеры API
│   ├── models/
│   │   └── wallet.py        # SQLAlchemy модели
│   ├── schemas/
│   │   └── wallet.py        # Pydantic схемы
│   └── services/
│       └── wallet_service.py # Бизнес-логика
├── tests/
│   ├── conftest.py          # Фикстуры pytest
│   └── test_wallet.py       # Тесты
├── Dockerfile
└── requirements.txt
```

## Запуск 

### 1. Создай виртуальное окружение

```bash
python -m venv venv
```

### 2. Активируй

**Windows (PowerShell):**
```powershell
.env\Scripts\Activate.ps1
```

Если ошибка политики выполнения:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.env\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scriptsctivate.bat
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Запусти приложение

```bash
python -m uvicorn app.main:app --reload
```

Приложение будет доступно по адресу: **http://127.0.0.1:8000**

### 5. Проверка

Открой в браузере: **http://127.0.0.1:8000/docs** — интерактивная документация Swagger UI.

## API

### Изменение баланса

```http
POST /api/v1/wallets/{WALLET_UUID}/operation
Content-Type: application/json
```

**Тело запроса:**
```json
{
  "operation_type": "DEPOSIT",
  "amount": "1000.00"
}
```

**Примеры:**

Пополнение:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation"   -H "Content-Type: application/json"   -d '{"operation_type": "DEPOSIT", "amount": "1500.50"}'
```

Списание:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/wallets/550e8400-e29b-41d4-a716-446655440000/operation"   -H "Content-Type: application/json"   -d '{"operation_type": "WITHDRAW", "amount": "500.00"}'
```

### Получение баланса

```http
GET /api/v1/wallets/{WALLET_UUID}
```

**Пример:**
```bash
curl "http://127.0.0.1:8000/api/v1/wallets/550e8400-e29b-41d4-a716-446655440000"
```

## Тестирование

```bash
pytest tests/ -v
```

Покрытие:
- Создание кошелька через депозит
- Пополнение существующего кошелька
- Успешное списание
- Недостаточно средств
- Несуществующий кошелёк
- Валидация невалидных данных
- Конкурентные депозиты и списания

## Запуск через VS Code

1. Открой папку `wallet-api` в VS Code
2. Выбери Python-интерпретатор из `venv` (`Ctrl+Shift+P` → `Python: Select Interpreter`)
3. Открой терминал (`Ctrl+\``)
4. Выполни шаги 2-4 из раздела "Запуск"

Или создай `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": ["app.main:app", "--reload"],
            "jinja": true
        }
    ]
}
```

И запускай через `F5`.
