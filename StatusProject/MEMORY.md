# MEMORY: TML Read API

## Identity
- Owner: `operator + Codex`
- Workspace: `D:\Data\Repos\API`
- Systems: `Python HTTP API, SQL Server, OWEN TML / Telemechanika Lite, Firebird service`
- System of interest: `External read-only API for TML data`
- Life cycle stage: `development`
- Last StatusProject update check: `2026-06-20`

## Stakeholders
| Stakeholder | Role | Durable need / concern |
| --- | --- | --- |
| Operator | User / owner | External application can read TML data safely. |
| TML runtime | Upstream system | API must not interfere with DAServer, KVision, KEvents, or database writes. |
| Future API consumer | Client system | Stable JSON endpoints for status, events, alarms, objects, and measurements. |

## Rules
- Keep API read-only.
- Do not commit `.env`, passwords, runtime logs, database dumps, or sensitive exports.
- Mask sensitive columns in generic sample responses.
- Prefer a dedicated SQL read-only login over `sa` for operation.

## Decisions
- `2026-06-20: Use Python standard http.server + pyodbc` — rationale: Python and pyodbc are already installed; impacted process: `implementation`.
- `2026-06-20: Use SQL Server ProjectOWEN as primary source` — rationale: TML is already using SQL and Firebird old ODS files require older tooling; impacted process: `architecture`.
- `2026-06-20: Store local secrets in .env and commit only .env.example` — rationale: avoids secret leakage; impacted process: `infrastructure`.

## Requirements And Constraints
- Requirement: external app must retrieve data from TML database.
- Requirement: API must expose `/StatusProject` style status.
- Constraint: no write operations or arbitrary SQL from clients.
- Constraint: local machine currently lacks `git` and `gh` in PATH.

## Verification Memory
- Verified: `2026-06-20 / GET /health returned 200`.
- Verified: `2026-06-20 / GET /api/databases connected to ProjectOWEN`.
- Verified: `2026-06-20 / GET /api/ProjectOWEN/table-stats returned events.LIST_EVENTS with 9,252,544 rows`.
- Known gap: no automated tests yet; verification is manual HTTP and SQL smoke checks.

## Sources
- `README.md`
- `PROJECT_STATUS.md`
- `StatusProject/SOURCE.md`
- `https://github.com/NohchiyBors/StatusProject`

## Remember
- API listens on `0.0.0.0:8787` by default.
- Local network URL is `http://10.100.100.10:8787` when firewall/routing permits.
- TML project root is `D:\TML-Project\BiService`.
- `DASrvAPI frozen` is a TML runtime issue observed in WDT logs, not an API process failure.

- 2026-06-21: Firebird support uses isql.exe — rationale: Python Firebird drivers are not installed; impacted process: integration.
- 2026-06-21: Admin settings UI stores configuration in .env — rationale: operator requested web settings for DB, tokens, users, and security; impacted process: operation.


## 2026-06-22 Update
- `2026-06-22: Admin UI controls completed` — dropdowns for enumerated values, checkboxes for boolean flags, textareas for list settings; impacted process: `implementation`.
- `2026-06-22: Online log viewer completed` — `/admin/logs` supports file, level, text filter, event count, refresh period, and live mode; impacted process: `operation`.
- `2026-06-22: Remote IP allow-list extended` — exact IP and CIDR rules supported in `TML_ALLOWED_IPS`; impacted process: `operation`.
- `2026-06-22: Read-only mode is explicit` — `TML_DATABASE_READ_ONLY` controls SQL `ApplicationIntent=ReadOnly` and SELECT-only guards; impacted process: `safety`.
