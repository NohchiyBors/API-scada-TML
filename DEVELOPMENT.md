# Development Guide

Руководство для разработчиков, работающих над проектом TML Read API.

## Структура проекта

```
API-scada-TML/
├── app.py                    # Главный файл приложения
├── requirements.txt          # Python зависимости
├── pyproject.toml            # Конфигурация пакета
├── .env                      # Переменные окружения (не коммитить)
├── .env.example              # Пример конфигурации
├── .gitignore               # Git исключения
├── run.cmd                  # Батник для запуска
│
├── Documentation/
├── README.md                # Основное описание
├── INSTALLATION.md          # Инструкция по установке
├── CONFIGURATION.md         # Документация по конфигурации
├── API.md                   # Полная документация по эндпоинтам
├── DEPLOYMENT.md            # Развёртывание в production
├── SECURITY.md              # Политика безопасности
├── CHANGELOG.md             # История версий
├── LICENSE                  # Лицензия MIT
│
├── logs/                    # Директория логов (создаётся при запуске)
│
├── StatusProject/           # Состояние проекта
├── .github/                 # GitHub конфигурация
│   ├── CONTRIBUTING.md      # Правила контрибьютинга
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/           # GitHub Actions (планируется)
│
└── .venv/                   # Виртуальное окружение Python
```

## Настройка окружения разработки

### 1. Клонирование репозитория

```bash
git clone https://github.com/NohchiyBors/API-scada-TML.git
cd API-scada-TML
```

### 2. Создание виртуального окружения

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
pip install -e .  # Установить пакет в режиме разработки
```

### 4. Копирование .env

```powershell
Copy-Item .env.example .env
```

Отредактировать `.env` под вашу локальную среду.

### 5. Проверка установки

```bash
python app.py
```

Должно вывести:
```
2026-06-27 12:00:00 INFO tml-read-api listening on http://0.0.0.0:8787
```

## Структура кода

### app.py

Главный файл приложения (около 1000 строк):

```python
# Импорты и константы
APP_NAME = "tml-read-api"
SETTING_KEYS = [...]  # Список конфигурационных параметров

# Функции загрузки конфигурации
def load_env_file(path=ENV_PATH):
    """Загрузить переменные из .env файла"""

def read_env_map(path=ENV_PATH):
    """Прочитать текущую конфигурацию"""

# Логирование
def setup_logging():
    """Инициализировать логирование"""

# Функции базы данных
def query(database, sql, params=None):
    """Выполнить SELECT запрос к SQL Server"""

def firebird_query(database, sql):
    """Выполнить запрос к Firebird"""

# Вспомогательные функции
def csv_env(key, default=""):
    """Получить CSV переменную окружения"""

def env_bool(key, default=False):
    """Получить булев переменную окружения"""

# HTTP обработчик запросов
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Обработать GET запросы"""

    # Методы для эндпоинтов
    def health_check(self):
    def status_project(self):
    def databases_list(self):
    def tables_list(self, db):
    def table_sample(self, db, table):

    # Методы аутентификации
    def require_basic_auth(self):
    def require_api_token(self):

    # Веб-интерфейсы
    def admin_page(self, saved=False):
    def logs_page(self):

# Главная функция
def main():
    httpd = ThreadingHTTPServer((host, port), Handler)
    httpd.serve_forever()
```

## Работа с эндпоинтами

### Добавление нового эндпоинта

1. **Определить маршрут** в методе `do_GET()`:

```python
if path == "/api/new-endpoint":
    if not self.require_api_token():
        return
    self.send_json(200, {"result": "data"})
```

2. **Добавить вспомогательный метод** (если нужен):

```python
def new_endpoint_data(self):
    return {"status": "success"}
```

3. **Протестировать**:

```bash
curl -H "Authorization: Bearer token" http://localhost:8787/api/new-endpoint
```

### Тестирование эндпоинтов

Простые тесты в Python:

```python
import requests

BASE_URL = "http://localhost:8787"
TOKEN = "your_token"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Тест health
resp = requests.get(f"{BASE_URL}/health")
assert resp.status_code == 200
assert resp.json()["ok"] == True

# Тест защищённого эндпоинта
resp = requests.get(f"{BASE_URL}/api/databases", headers=headers)
assert resp.status_code == 200
```

## Логирование

### Использование логера

```python
import logging

logger = logging.getLogger(__name__)

# Логирование событий
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Просмотр логов

**В браузере:**
```
http://localhost:8787/admin/logs
```

**В терминале:**
```powershell
Get-Content logs/app.log -Wait  # следить за изменениями
```

## Работа с базами данных

### SQL Server

```python
# Выполнить запрос
result = query("ProjectOWEN", "SELECT TOP 10 * FROM dbo.Events")

# Результат - список словарей
for row in result:
    print(row["EventID"], row["EventTime"])
```

### Firebird

```python
# Выполнить запрос
result = firebird_query("users", "SELECT * FROM EMPLOYEES")
```

## Версионирование

Версии следуют [Semantic Versioning](https://semver.org/):

- **MAJOR** - критические изменения API
- **MINOR** - новые функции (обратно совместимы)
- **PATCH** - исправления ошибок

Текущая версия: `0.1.1`

**Изменение версии:**

1. Обновить в `pyproject.toml`:
```toml
[project]
version = "0.2.0"
```

2. Добавить запись в `CHANGELOG.md`

3. Создать git тег:
```bash
git tag v0.2.0
git push origin v0.2.0
```

## Code Style

### Conventions

- **Язык кода:** English (переменные, функции, комментарии)
- **Язык документации:** Русский (README, docs)
- **Line length:** 100 символов максимум
- **Indentation:** 4 пробела (не tabs)

### Docstrings

```python
def my_function(param1: str, param2: int) -> dict:
    """Краткое описание функции.

    Более подробное описание если нужно.

    Args:
        param1: Описание первого параметра
        param2: Описание второго параметра

    Returns:
        dict: Описание возвращаемого значения

    Raises:
        ValueError: При неверных параметрах
    """
```

### Error Handling

```python
try:
    result = query(db, sql)
except Exception as e:
    logger.error(f"Query failed: {e}", exc_info=True)
    self.send_json(500, {"error": "query_failed", "details": str(e)})
    return
```

## Работа с Git

### Коммиты

Следовать конвенции [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add new endpoint /api/events"
git commit -m "fix: handle connection timeout"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for database queries"
```

### Branches

- `main` - production код
- `develop` - разработка (если используется)
- `feature/something` - новые функции
- `fix/something` - исправления
- `docs/something` - документация

### Pull Requests

1. Создать branch: `git checkout -b feature/my-feature`
2. Сделать изменения
3. Коммитить: `git commit -m "feature: description"`
4. Пушить: `git push origin feature/my-feature`
5. Создать PR на GitHub

PR должен:
- ✅ Иметь понятное описание
- ✅ Обновить документацию
- ✅ Включать тесты (если применимо)
- ✅ Пройти код-ревью

## Тестирование

### Ручное тестирование

```powershell
# Запустить API
python app.py

# В отдельном терминале
$token = "change-me-token"
$headers = @{ Authorization = "Bearer $token" }

# Тест здоровья
Invoke-WebRequest http://localhost:8787/health

# Тест БД
Invoke-WebRequest -Headers $headers http://localhost:8787/api/databases

# Тест таблиц
Invoke-WebRequest -Headers $headers http://localhost:8787/api/ProjectOWEN/tables
```

### Автоматизированные тесты

**План:** Добавить pytest тесты (см. StatusProject/DEVELOPMENT-STATUS.md)

```bash
# Будущая команда
pytest tests/ -v
```

## Отладка

### Debug режим

Добавить в код:

```python
import pdb; pdb.set_trace()  # Точка остановки
```

Или использовать IDE debugger (VS Code, PyCharm).

### Просмотр переменных

```python
import sys
import json

print(f"DEBUG: {json.dumps(my_dict, indent=2)}", file=sys.stderr)
```

## Performance

### Профилирование

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Код для профилирования
result = query("ProjectOWEN", "SELECT * FROM LargeTable")

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumtime').print_stats(10)
```

### Optimizations

- Кэширование результатов частых запросов
- Пакетная обработка больших наборов данных
- Индексирование в SQL Server

## Документирование изменений

При добавлении новой функции/эндпоинта:

1. **Обновить README.md**
2. **Обновить API.md** с новым эндпоинтом
3. **Добавить запись в CHANGELOG.md**
4. **Обновить CONFIGURATION.md** если нужны новые параметры
5. **Добавить docstring** в код

## Развёртывание

### Локальное тестирование

```bash
python app.py
```

### Подготовка к production

1. Обновить версию в `pyproject.toml`
2. Добавить запись в `CHANGELOG.md`
3. Создать git тег: `git tag v0.1.1`
4. Пушить в GitHub

### Production развёртывание

Подробности в [DEPLOYMENT.md](DEPLOYMENT.md).

## Полезные ссылки

- [Flask документация](https://flask.palletsprojects.com/)
- [Python documentation](https://docs.python.org/)
- [SQL Server документация](https://learn.microsoft.com/en-us/sql/)
- [GitHub REST API](https://docs.github.com/en/rest)

## Поддержка

- Вопросы в GitHub Issues
- Обсуждение в GitHub Discussions
- Security issues - см. SECURITY.md

---

**Разработчик:** HSPhub.com
**Заказчик:** astana.company
**Лицензия:** MIT
