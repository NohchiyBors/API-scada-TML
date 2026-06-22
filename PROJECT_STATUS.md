# StatusProject: TML Read API

```text
ProjectName:      TML Read API
ProjectType:      External read-only HTTP API
ProjectPath:      D:\Data\Repos\API
Runtime:          Python 3.14 + pyodbc
ListenAddress:    0.0.0.0:8787
LocalURL:         http://127.0.0.1:8787
NetworkURL:       http://10.100.100.10:8787
MainFile:         app.py
ConfigFile:       .env
Status:           RUNNING
Mode:             READ_ONLY
```

## Purpose

`TML Read API` - внешнее приложение для получения данных из проекта OWEN TML / Телемеханика Лайт через SQL Server.

Приложение не изменяет данные в базе и не принимает произвольный SQL от клиента. Доступ к таблицам ограничен списком баз из `TML_SQL_DATABASES`.

## DataSource

```text
SQLServer:        127.0.0.1,1433
Database:         ProjectOWEN
Driver:           ODBC Driver 17 for SQL Server
AuthMode:         SQL login
ProjectRoot:      D:\TML-Project\BiService
```

Основные схемы в `ProjectOWEN`:

```text
events       события и журналы
dispatcher   справочники и диспетчерские данные
ascue        данные АСКУЭ
kdb          исторические/технологические данные
users        пользователи и права
```

Крупная таблица, найденная при проверке:

```text
events.LIST_EVENTS  ~9,252,544 rows
```

## RuntimeStatus

```text
API process:       python.exe
API port:          8787 LISTENING
TML processes:     OwenTMlite.exe, DAServer.exe, KVision.exe, KEvents.exe
DB processes:      sqlservr.exe, firebird.exe
```

`/StatusProject` также показывает состояние логов DAServer и WDT. На момент первичной проверки в WDT фиксировалось:

```text
DASrvAPI frozen
WDTRestartServer
```

Это проблема TML/DAServer, не самого API. API продолжает читать SQL Server, если база доступна.

## Endpoints

```text
GET /health
GET /StatusProject
GET /api/status
GET /api/databases
GET /api/ProjectOWEN/tables
GET /api/ProjectOWEN/table-stats
GET /api/ProjectOWEN/tables/{schema.table}/sample?limit=20
```

Примеры:

```text
http://127.0.0.1:8787/health
http://127.0.0.1:8787/StatusProject
http://127.0.0.1:8787/api/ProjectOWEN/table-stats
http://127.0.0.1:8787/api/ProjectOWEN/tables/events.LIST_EVENTS/sample?limit=5
```

## Security

```text
WriteOperations:   DISABLED
ArbitrarySQL:      DISABLED
DatabaseAllowList: ENABLED
SensitiveMasking:  ENABLED
```

В sample-ответах маскируются колонки, похожие на чувствительные:

```text
pass, pwd, token, secret, hash, key
```

Такие значения возвращаются как:

```text
***
```

## Files

```text
app.py              HTTP API server
.env                local runtime config, not for git
.gitignore          excludes .env and generated files
README.md           quick start and endpoint list
requirements.txt    Python dependency note
run.cmd             simple local start command
logs/               runtime stdout/stderr logs
```

## StartCommand

```cmd
D:\Data\Repos\API\run.cmd
```

Или вручную:

```powershell
cd D:\Data\Repos\API
python app.py
```

## CurrentLimitations

```text
1. Нет отдельной бизнес-модели данных поверх таблиц TML.
2. Пока есть только generic чтение таблиц и статус проекта.
3. Для продуктивной эксплуатации лучше заменить sa на отдельного read-only пользователя.
4. API запущен как обычный процесс, не как Windows Service.
```

## NextStep

Рекомендуемый следующий этап - добавить доменные endpoints вместо прямого sample таблиц:

```text
GET /api/events/latest
GET /api/alarms/latest
GET /api/objects
GET /api/measurements/latest
GET /api/measurements/history?from=...&to=...
```
