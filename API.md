# API Reference

Полная документация по всем эндпоинтам TML Read API.

## Общая информация

### Базовый URL

```
http://localhost:8787
```

### Аутентификация

API поддерживает несколько типов аутентификации:

#### Bearer Token (рекомендуется)

Когда `TML_REQUIRE_API_TOKEN=true` (по умолчанию):

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8787/api/databases
```

#### HTTP Basic Auth (только для /admin)

Для веб-интерфейса настроек:

```bash
curl -u admin:password http://localhost:8787/admin
```

### Коды ответов

| Код | Значение |
|-----|----------|
| 200 | OK - Успешный запрос |
| 401 | Unauthorized - Требуется токен или неверная аутентификация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 500 | Server Error - Ошибка сервера |

## Эндпоинты

### Health Check

#### `GET /health`

Проверка живого состояния API.

**Не требует аутентификации.**

**Пример запроса:**
```bash
curl http://localhost:8787/health
```

**Ответ (200):**
```json
{
  "ok": true,
  "app": "tml-read-api",
  "time_utc": "2026-06-27T12:00:00Z"
}
```

---

### Status Project

#### `GET /StatusProject`
#### `GET /api/status`

Получить статус проекта, логов и конфигурации.

**Требует аутентификацию.**

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/StatusProject
```

**Ответ (200):**
```json
{
  "app": "tml-read-api",
  "version": "0.2.0",
  "environment": {
    "api_host": "0.0.0.0",
    "api_port": 8787,
    "project_root": "D:\\TML-Project\\BiService",
    "log_level": "INFO"
  },
  "databases": {
    "sql_server": {
      "server": "127.0.0.1,1433",
      "databases": ["ProjectOWEN"],
      "readonly": true
    },
    "firebird": {
      "databases": []
    }
  },
  "security": {
    "api_token_required": true,
    "allowed_ips": ["127.0.0.1", "::1"],
    "client_ip": "127.0.0.1"
  },
  "timestamps": {
    "api_started": "2026-06-27T11:54:59Z",
    "current_time": "2026-06-27T12:00:00Z"
  }
}
```

---

### Mobile / ScadaMobile Endpoints

All `/mobile/*` endpoints require Bearer token authentication when `TML_REQUIRE_API_TOKEN=true`.
They are read-only except the guarded status endpoint, which validates input and returns `501 integration_not_ready`.

#### `GET /mobile/me`

Returns the current mobile user/session stub.

#### `GET /mobile/objects`

Returns controller/object records from `dbo.scada_controllers`.

#### `GET /mobile/objects/{id}`

Returns one controller/object record.

#### `GET /mobile/objects/{id}/points`

Returns point catalog rows from `dbo.scada_points`, joined to `dbo.scada_point_current` for latest value fields when available.

#### `GET /mobile/objects/{id}/events`

Returns object-scoped mobile incidents.

#### `GET /mobile/incidents`

Returns mobile incidents. The API prefers indexed `dbo.mobile_incidents` when present, otherwise falls back to `dbo.scada_events`.

#### `GET /mobile/incidents/source-status`

Reports readiness for catalog fallback, raw `events.LIST_EVENTS`, and the materialized `dbo.mobile_incidents` adapter.

#### `GET /mobile/objects/{id}/scheme`

Returns a `not_available` scheme placeholder until scheme indexing is integrated.

#### `POST /mobile/incidents/{id}/status`

Validates requested status transitions (`accepted`, `en_route`, `resolved`) and returns `501 integration_not_ready`.

---

### Database Operations

#### `GET /api/databases`

Проверить подключение ко всем настроенным базам данных.

**Требует аутентификацию.**

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/api/databases
```

**Ответ (200):**
```json
{
  "databases": [
    {
      "database": "ProjectOWEN",
      "ok": true,
      "result": {
        "database_name": "ProjectOWEN"
      }
    }
  ]
}
```

---

#### `GET /api/{db}/tables`

Получить список таблиц в базе данных.

**Параметры:**
- `db` (path) - Имя базы данных из `TML_SQL_DATABASES`

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/api/ProjectOWEN/tables
```

**Ответ (200):**
```json
{
  "database": "ProjectOWEN",
  "tables": [
    {
      "schema": "dbo",
      "table": "Events",
      "column_count": 15
    },
    {
      "schema": "dbo",
      "table": "Alarms",
      "column_count": 12
    }
  ]
}
```

---

#### `GET /api/{db}/table-stats`

Получить список таблиц с количеством строк.

**Параметры:**
- `db` (path) - Имя базы данных

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/api/ProjectOWEN/table-stats
```

**Ответ (200):**
```json
{
  "database": "ProjectOWEN",
  "tables": [
    {
      "schema": "dbo",
      "table": "Events",
      "row_count": 154230
    },
    {
      "schema": "dbo",
      "table": "Alarms",
      "row_count": 42100
    }
  ]
}
```

---

#### `GET /api/{db}/tables/{schema.table}/sample`

Получить примеры строк из таблицы.

**Параметры:**
- `db` (path) - Имя базы данных
- `schema.table` (path) - Полное имя таблицы (например, `dbo.Events`)
- `limit` (query) - Количество строк (по умолчанию 20, максимум 1000)

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=10"
```

**Ответ (200):**
```json
{
  "database": "ProjectOWEN",
  "table": "dbo.Events",
  "total_rows": 154230,
  "returned": 10,
  "columns": [
    {
      "name": "EventID",
      "type": "int"
    },
    {
      "name": "EventTime",
      "type": "datetime"
    },
    {
      "name": "Description",
      "type": "nvarchar"
    }
  ],
  "rows": [
    ["1", "2026-06-27 12:00:00", "System started"],
    ["2", "2026-06-27 12:05:00", "Value changed"],
    ...
  ]
}
```

---

### Firebird Endpoints

#### `GET /api/firebird/databases`

Получить список настроенных Firebird баз данных.

**Требует аутентификацию.**

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/api/firebird/databases
```

**Ответ (200):**
```json
{
  "firebird": [
    {
      "alias": "users",
      "path": "D:\\TML-Project\\BiService\\Base\\USERS.FDB",
      "ok": true
    }
  ]
}
```

---

#### `GET /api/firebird/{alias}/tables`

Получить список таблиц в Firebird базе.

**Параметры:**
- `alias` (path) - Алиас базы из конфигурации

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" http://localhost:8787/api/firebird/users/tables
```

**Ответ (200):**
```json
{
  "database": "users",
  "tables": ["EMPLOYEES", "DEPARTMENTS", "PROJECTS"]
}
```

---

#### `GET /api/firebird/{alias}/tables/{table}/sample`

Получить примеры строк из Firebird таблицы.

**Параметры:**
- `alias` (path) - Алиас базы
- `table` (path) - Имя таблицы
- `limit` (query) - Количество строк (по умолчанию 20)

**Пример запроса:**
```bash
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:8787/api/firebird/users/tables/EMPLOYEES/sample?limit=5"
```

---

### Admin Interface

#### `GET /admin`

Веб-интерфейс для управления настройками API.

**Требует HTTP Basic Auth.**

**Использование:**
1. Открыть в браузере: `http://localhost:8787/admin`
2. Ввести `TML_ADMIN_USER` / `TML_ADMIN_PASSWORD`
3. Изменить любые переменные окружения
4. Нажать "Save settings"

---

#### `GET /admin/logs`

Просмотр логов в браузере.

**Требует HTTP Basic Auth.**

**Функции:**
- Выбор log-файла (app, access, stdout, stderr)
- Фильтрация по уровню (DEBUG, INFO, WARNING, ERROR)
- Текстовый поиск
- Автоматическое обновление (live mode)
- Контроль количества событий и интервала обновления

---

#### `GET /admin/logs/data`

JSON API для логов (используется веб-интерфейсом).

**Параметры:**
- `file` (query) - Имя файла (app, access, stdout, stderr)
- `level` (query) - Уровень фильтра (ALL, DEBUG, INFO, WARNING, ERROR)
- `contains` (query) - Текст для поиска
- `limit` (query) - Максимум событий (по умолчанию 200)

**Пример запроса:**
```bash
curl -u admin:password \
  "http://localhost:8787/admin/logs/data?file=app&level=ERROR&limit=50"
```

**Ответ (200):**
```json
{
  "file": "app",
  "path": "D:\\Data\\Repos\\API\\logs\\app.log",
  "total_matched": 3,
  "time_utc": "2026-06-27T12:00:00Z",
  "events": [
    "2026-06-27 11:54:59 ERROR Connection failed",
    ...
  ]
}
```

---

## Примеры использования

### Python

```python
import requests

# Инициализация
BASE_URL = "http://localhost:8787"
TOKEN = "your_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Health check
resp = requests.get(f"{BASE_URL}/health")
print(resp.json())

# Получить список таблиц
resp = requests.get(
    f"{BASE_URL}/api/ProjectOWEN/tables",
    headers=headers
)
tables = resp.json()["tables"]

# Получить примеры данных
resp = requests.get(
    f"{BASE_URL}/api/ProjectOWEN/tables/dbo.Events/sample?limit=10",
    headers=headers
)
data = resp.json()
```

### PowerShell

```powershell
$token = "your_token_here"
$headers = @{ Authorization = "Bearer $token" }

# Health check
Invoke-WebRequest -Uri "http://localhost:8787/health"

# Получить данные
$response = Invoke-WebRequest `
    -Uri "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=10" `
    -Headers $headers
$data = $response.Content | ConvertFrom-Json
$data.rows | Format-Table
```

### cURL

```bash
TOKEN="your_token_here"

# Health check
curl http://localhost:8787/health

# Получить данные с авторизацией
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=10"
```

---

## Ограничения и особенности

- **Только чтение**: API не позволяет выполнять INSERT/UPDATE/DELETE операции
- **Максимум данных**: Ограничение на размер выборки - не более 1000 строк за раз
- **Защита от SQL Injection**: Все входные параметры валидируются
- **Read-only режим**: По умолчанию соединение к SQL Server использует ApplicationIntent=ReadOnly
- **Таймаут**: По умолчанию TML_SQL_TIMEOUT=10 секунд
- **IP Allow-list**: Доступ ограничен только авторизованными IP-адресами

---

## Ошибки и их решение

### 401 Unauthorized

```json
{"error": "api_token_required"}
```

**Причина:** Отсутствует или неверный Bearer токен.
**Решение:** Добавить заголовок `Authorization: Bearer YOUR_TOKEN`

### 403 Forbidden

```json
{"error": "ip_not_allowed"}
```

**Причина:** IP адрес не в списке разрешённых.
**Решение:** Добавить IP в `TML_ALLOWED_IPS` через веб-интерфейс `/admin`

### 404 Not Found

```json
{"error": "database_not_found"}
```

**Причина:** База данных не в списке `TML_SQL_DATABASES`.
**Решение:** Добавить БД в конфигурацию и перезагрузить API.

### 500 Server Error

```json
{"error": "connection_failed", "details": "..."}
```

**Причина:** Ошибка подключения к БД.
**Решение:** Проверить параметры подключения и доступность SQL Server.

---

Дополнительная информация в [CONFIGURATION.md](CONFIGURATION.md) и [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
