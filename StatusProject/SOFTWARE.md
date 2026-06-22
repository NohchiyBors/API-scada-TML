# SOFTWARE: TML Read API

## Summary
- Users: `operator and future external application clients`
- Goal: `read OWEN TML / Telemechanika Lite data from SQL Server through safe HTTP JSON endpoints`
- Repo: `D:\Data\Repos\API; target GitHub repo https://github.com/NohchiyBors/StatusProject`
- System of interest: `Python API service`
- Life cycle stage: `development`

## Stack
- Language/framework: `Python 3.14 / standard library http.server`
- Runtime/package manager: `python / pip optional`
- DB/storage: `SQL Server ProjectOWEN through pyodbc and ODBC Driver 17`

## Entrypoints
- App/API/CLI/UI: `python app.py`
- Startup helper: `run.cmd`
- Status endpoint: `GET /StatusProject`

## Modules
| Module | Responsibility | Important files |
| --- | --- | --- |
| HTTP API | route GET requests and return JSON | `app.py` |
| Config | load .env/environment variables | `app.py`, `.env`, `.env.example` |
| SQL adapter | build ODBC connection and execute read queries | `app.py` |
| Status collector | inspect TML processes and logs | `app.py`, `D:\TML-Project\BiService` |
| Documentation | project state and runbook | `README.md`, `PROJECT_STATUS.md`, `StatusProject/*.md` |

## Data And Contracts
- Models: `raw SQL tables under schemas events, dispatcher, ascue, kdb, users`.
- External APIs: `none yet; API itself provides HTTP JSON`.
- Formats: `JSON responses, Markdown docs, .env config`.
- Compatibility: `keep existing endpoint paths and response top-level keys stable`.

## Config
- Env: `TML_API_HOST`, `TML_API_PORT`, `TML_PROJECT_ROOT`, `TML_SQL_DRIVER`, `TML_SQL_SERVER`, `TML_SQL_USER`, `TML_SQL_PASSWORD`, `TML_SQL_DATABASES`, `TML_SQL_TIMEOUT`, `TML_API_CORS_ORIGIN`.
- Files: `.env: local secrets/config`, `.env.example: safe template`, `.gitignore: excludes secrets/logs`.
- Rule: `local systems may use .env or .env.*; staging/prod should use platform environment variables or secret manager; commit only .env.example`

## Commands
- Install: `pyodbc already installed; otherwise python -m pip install -r requirements.txt`
- Dev/prod: `python app.py` / `not defined yet`
- Test/lint/build: `manual HTTP smoke tests` / `not configured` / `not applicable`

## Verification And Validation
| Concern | Method | Command / evidence | Status |
| --- | --- | --- | --- |
| API starts | manual test | `GET /health` | pass |
| SQL connects | manual test | `GET /api/databases` | pass |
| Metadata reads | manual test | `GET /api/ProjectOWEN/table-stats` | pass |
| Sensitive masking | manual test | `users.USERLIST sample` masks password-like fields | pass |
| Automated tests | test suite | none | unknown |

## Constraints / Do Not
- Constraints: `Windows host`, `local SQL Server`, `no git/gh in PATH`.
- Do not: `commit .env`, `commit logs`, `add database writes`, `expose raw SQL endpoint`.

## Added Interfaces 2026-06-21
- GET /admin — Basic Auth settings UI backed by .env.
- GET /api/firebird/databases — Firebird allow-list status.
- GET /api/firebird/{alias}/tables — Firebird table list.
- GET /api/firebird/{alias}/tables/{table}/sample?limit=20 — read-only Firebird sample rows.
- API data endpoints require Bearer token when TML_REQUIRE_API_TOKEN=true.


## Database Read-only Mode
- TML_DATABASE_READ_ONLY is rendered as a checkbox in /admin.
- Default is 	rue.
- SQL Server connection includes ApplicationIntent=ReadOnly while enabled.
- SQL and Firebird helper execution is guarded to SELECT-only statements.


## Web Log Viewer
- GET /admin/logs provides online log viewing for app/access/stdout/stderr logs.
- UI controls: log file, level filter, text filter, number of events, refresh period, live-view checkbox.
- GET /admin/logs/data returns filtered JSON log events for polling.


## Admin Form Controls
- Checkboxes: TML_REQUIRE_API_TOKEN, TML_DATABASE_READ_ONLY.
- Dropdowns: TML_LOG_LEVEL, TML_SQL_DRIVER, TML_API_CORS_ORIGIN.
- Textareas: allow-lists and multi-value settings.


## 2026-06-22 Current Interface Baseline
- Admin settings: `GET /admin`, `POST /admin/settings`.
- Admin log viewer: `GET /admin/logs`, `GET /admin/logs/data`.
- Boolean settings render as checkboxes: `TML_REQUIRE_API_TOKEN`, `TML_DATABASE_READ_ONLY`.
- Enumerated settings render as dropdowns: `TML_LOG_LEVEL`, `TML_SQL_DRIVER`, `TML_API_CORS_ORIGIN`.
- Multi-value settings render as textareas: `TML_ALLOWED_IPS`, `TML_API_TOKENS`, `TML_SQL_DATABASES`, `TML_FIREBIRD_DATABASES`.
- Data endpoints require Bearer token when `TML_REQUIRE_API_TOKEN=true`.
- Client access is restricted by `TML_ALLOWED_IPS`; exact IP and CIDR are supported.
- Database read-only mode is controlled by `TML_DATABASE_READ_ONLY`; default is `true`.
