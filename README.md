# TML Read API

Version: `0.2.0`.

Минимальный внешний HTTP API для чтения данных проекта OWEN TML / Телемеханика Лайт.

## Авторство

Разработчик HSPhub.com по заказу astana.company.

## Лицензия

Проект распространяется по свободной лицензии MIT.
При копировании, переработке и распространении обязательно сохранять
указание разработчика и текст лицензии из файла LICENSE.

## Запуск

```powershell
cd D:\Data\Repos\API
$env:TML_SQL_SERVER = '127.0.0.1,1433'
$env:TML_SQL_USER = 'tml_reader'
$env:TML_SQL_PASSWORD = 'password'
$env:TML_SQL_DATABASES = 'ProjectOWEN'
python app.py
```

По умолчанию API слушает `http://0.0.0.0:8787`.

## Dev в Docker

```powershell
cd D:\Data\Repos\API
docker compose -f docker-compose.dev.yml up --build -d
Invoke-WebRequest http://127.0.0.1:8787/health
```

Остановка:

```powershell
docker compose -f docker-compose.dev.yml down
```

## Endpoints

- `GET /health` - проверка, что API жив.
- `GET /StatusProject` - статус процессов TML, логов и конфигурации SQL.
- `GET /api/status` - то же, что `/StatusProject`.
- `GET /api/databases` - проверка подключения к разрешенным базам.
- `GET /api/{db}/tables` - список таблиц базы.
- `GET /api/{db}/table-stats` - список таблиц с количеством строк.
- `GET /api/{db}/tables/{schema.table}/sample?limit=20` - первые строки таблицы.
- `GET /mobile/me` - session/user stub for ScadaMobile clients.
- `GET /mobile/objects` - controller/object list for mobile UI.
- `GET /mobile/objects/{id}/points` - point catalog with latest-value fields when available.
- `GET /mobile/incidents` - incident feed from `dbo.mobile_incidents` adapter or catalog fallback.
- `GET /mobile/incidents/source-status` - readiness report for live journal/materialized adapter.
- `POST /mobile/incidents/{id}/status` - guarded status writeback stub returning `501 integration_not_ready`.

API не принимает произвольный SQL и не выполняет `INSERT/UPDATE/DELETE`.

## Настройки

- `TML_API_HOST`, default `0.0.0.0`
- `TML_API_PORT`, default `8787`
- `TML_PROJECT_ROOT`, default `D:\TML-Project\BiService`
- `TML_SQL_DRIVER`, default `ODBC Driver 17 for SQL Server`
- `TML_SQL_SERVER`, default `127.0.0.1,1433`
- `TML_SQL_USER`, optional. Если не задан, используется Windows authentication.
- `TML_SQL_PASSWORD`, optional.
- `TML_SQL_DATABASES`, default `ProjectOWEN`

## Рекомендуемый SQL пользователь

Создайте отдельный read-only логин и выдайте ему только `db_datareader` на нужные базы.

## Описание проекта

Сводное описание в стиле StatusProject: [PROJECT_STATUS.md](PROJECT_STATUS.md).

## StatusProject State

Project state follows https://github.com/NohchiyBors/StatusProject and lives in [StatusProject/PROJECT-RESUME.md](StatusProject/PROJECT-RESUME.md), [StatusProject/TODO.md](StatusProject/TODO.md), and [StatusProject/MEMORY.md](StatusProject/MEMORY.md).


## Admin UI And Security

- `GET /admin` - web interface for runtime settings stored in `.env`.
- Admin UI uses HTTP Basic Auth: `TML_ADMIN_USER` / `TML_ADMIN_PASSWORD`.
- Data API endpoints require `Authorization: Bearer <token>` when `TML_REQUIRE_API_TOKEN=true`.
- Allowed client IPs are controlled by `TML_ALLOWED_IPS` as comma-separated values.
- Access and app logs are written to `logs/access.log` and `logs/app.log` by default.

## Firebird Endpoints

Firebird is configured through `TML_FIREBIRD_*` variables and uses `isql.exe`.

- `GET /api/firebird/databases` - configured Firebird databases and status.
- `GET /api/firebird/{alias}/tables` - list user tables.
- `GET /api/firebird/{alias}/tables/{table}/sample?limit=20` - read-only sample rows.

Example:

```powershell
$headers = @{ Authorization = 'Bearer <token>' }
Invoke-RestMethod http://127.0.0.1:8787/api/firebird/users/tables -Headers $headers
```

## Database Read-only Mode

- TML_DATABASE_READ_ONLY=true is the default and is exposed as a checkbox in /admin.
- When enabled, SQL Server connections use ApplicationIntent=ReadOnly.
- SQL guards allow only SELECT-style statements and reject write/admin keywords for SQL Server and Firebird helper queries.


## Web Log Viewer

- `GET /admin/logs` - online log viewer protected by admin Basic Auth.
- Selectable log files: app, access, stdout, stderr.
- Controls: level filter, text filter, event count, refresh period in seconds, live update checkbox.
- JSON polling endpoint: `GET /admin/logs/data?file=app&level=INFO&limit=200&contains=`.

## Remote IP Allow-list

- TML_ALLOWED_IPS accepts exact IPs and CIDR networks separated by commas.
- Examples: 127.0.0.1,::1,10.100.100.10,10.100.100.0/24.
- /admin shows the current client IP near TML_ALLOWED_IPS so it can be added safely.
- /StatusProject returns client_ip and security.allowed_ips.


## Admin Form Controls

- Boolean settings are shown as checkboxes: TML_REQUIRE_API_TOKEN, TML_DATABASE_READ_ONLY.
- Enumerated settings are dropdowns: TML_LOG_LEVEL, TML_SQL_DRIVER, TML_API_CORS_ORIGIN.
- List settings use text areas: TML_ALLOWED_IPS, TML_API_TOKENS, TML_SQL_DATABASES, TML_FIREBIRD_DATABASES.

