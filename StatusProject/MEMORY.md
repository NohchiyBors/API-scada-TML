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

## 2026-06-27 Mobile Adapter Update
- `2026-06-27: Added /mobile/* endpoints for ScadaMobile` — endpoints expose current user stub, objects, object detail, points, incidents, scheme placeholder, and guarded incident status draft; impacted process: `implementation`.
- Source mapping: `/mobile/objects` reads `dbo.scada_controllers`; `/mobile/objects/{id}/points` reads `dbo.scada_points`; `/mobile/incidents` reads `dbo.scada_events`.
- Safety decision: `POST /mobile/incidents/{id}/status` validates requested status but returns `501 integration_not_ready`; no SCADA/CRM write is attempted.
- Constraint: do not query raw `events.LIST_EVENTS` unbounded from mobile endpoints; use indexed/materialized adapter first.
- Verified: direct API smoke checks returned real object/incidents and the expected `501` writeback guard.

## 2026-06-27 Telemetry Mapping Update
- `2026-06-27: /mobile point responses now LEFT JOIN dbo.scada_point_current` — rationale: keep latest-value fields stable while the current-value adapter is populated; impacted process: `implementation`.
- Verified: `dbo.scada_point_current` columns are `point_id`, `value_text`, `quality`, `source_timestamp_utc`, `received_at_utc`; current row count is 0.
- Verified: `dbo.scada_points` currently has 4918 rows under `controller_id=tml-alarms`; real `dbo.scada_controllers` object ids currently have no point rows.
- Constraint: `kdb.DATA_2026_04_27` uses compressed/binary parameter lists and must be decoded/normalized before mobile exposure.

## 2026-06-27 Incident Mapping Update
- `2026-06-27: /mobile incidents now resolve null object_id through point catalog` — mapping is `COALESCE(scada_events.object_id, scada_points.controller_id, 'tml-alarms')`; impacted process: `implementation`.
- Response addition: mobile incidents include `pointName` from `dbo.scada_points.name`.
- Verified: `/mobile/incidents?limit=3` and `/mobile/incidents?objectId=tml-alarms&limit=3` return mapped alarm catalog rows.
- Constraint: mapped rows are still `alarm_catalog` definitions, not live event journal incidents.

## 2026-06-27 Live Journal Readiness Update
- `2026-06-27: Added /mobile/incidents/source-status` — rationale: API clients need an explicit readiness signal for catalog vs live journal incident sources; impacted process: `implementation`.
- Verified: `events.LIST_EVENTS` has only `HEAP` shape in `sys.indexes`; no usable `EVENT_TIMESTAMP` or `NUMBER` index was found.
- Verified: direct `TOP` reads from `events.LIST_EVENTS` can return rows, but they are not latest/range safe and must not become the mobile feed.
- Source-status contract: `catalog.ready=true`, `liveJournal.ready=false`, `requiredAdapter=indexed_or_materialized_mobile_incidents`.

## 2026-06-27 Mobile Incidents Adapter Contract
- `2026-06-27: API auto-prefers dbo.mobile_incidents` — `/mobile/incidents` reads `dbo.mobile_incidents` when it exists; otherwise it falls back to `dbo.scada_events`; impacted process: `implementation`.
- Readiness rule: `/mobile/incidents/source-status` reports `liveJournal.ready=true` only when raw journal has a usable index or the `dbo.mobile_incidents` projection exists with `source_timestamp_utc` index coverage.
- Constraint: API still does not execute DDL/backfill; projection creation is an operator-controlled SQL action from the ScadaMobile repo script.
- Verified: ScadaMobile scripts created `dbo.mobile_incidents`, added timestamp/object indexes, and backfilled 100 rows for `events.LIST_EVENTS.NUMBER` window `4944061..4944477`.
- `2026-06-27: /mobile/incidents sourceWarning now reflects active adapter` — when `dbo.mobile_incidents` exists, warning says `events.LIST_EVENTS is exposed through indexed dbo.mobile_incidents projection`; impacted process: `implementation`.
- Known gap: current `dbo.mobile_incidents` data is a bounded historical sample; recurring latest/incremental load is not implemented.
