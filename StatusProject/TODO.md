# TODO: TML Read API

## Open
- [ ] Add `GET /api/events/latest` endpoint — process: `implementation`
- [ ] Add `GET /api/alarms/latest` endpoint — process: `implementation`
- [ ] Add `GET /api/objects` endpoint — process: `implementation`
- [ ] Add `GET /api/measurements/latest` endpoint — process: `implementation`
- [ ] Define table allow/deny policy for SQL and Firebird sample endpoints — process: `system requirements`
- [ ] Replace local `sa` SQL login with dedicated read-only login — process: `operation`
- [ ] Decide whether to install API as Windows Service — process: `transition`
- [ ] Publish repository without `.env` and without logs — process: `transition`
- [ ] Verify read-only toggle behavior after changing it through `/admin` — process: `verification`
- [ ] Add token rotation procedure for `TML_API_TOKENS` and admin password — process: `operation`

## Done
- [x] Add first ScadaMobile `GET /mobile/me` endpoint — process: `implementation`
- [x] Add first ScadaMobile `GET /mobile/objects` and `GET /mobile/objects/{id}` endpoints — process: `implementation`
- [x] Add first ScadaMobile `GET /mobile/objects/{id}/points` endpoint — process: `implementation`
- [x] Join ScadaMobile point responses to `dbo.scada_point_current` latest-value table — process: `implementation`
- [x] Add first ScadaMobile `GET /mobile/incidents` endpoint over `dbo.scada_events` — process: `implementation`
- [x] Map ScadaMobile incidents to object ids through `point_id -> scada_points.controller_id` fallback — process: `implementation`
- [x] Add `pointName` to ScadaMobile incident responses — process: `implementation`
- [x] Add ScadaMobile `GET /mobile/incidents/source-status` endpoint — process: `implementation`
- [x] Auto-prefer `dbo.mobile_incidents` materialized adapter for `/mobile/incidents` when table/index are present — process: `implementation`
- [x] Add guarded `POST /mobile/incidents/{id}/status` returning `501 integration_not_ready` — process: `safety`
- [x] Create initial Python HTTP API — process: `implementation`
- [x] Connect API to SQL Server `ProjectOWEN` through pyodbc — process: `integration`
- [x] Add `/StatusProject` runtime status endpoint — process: `implementation`
- [x] Add web settings UI `/admin` backed by `.env` — process: `operation`
- [x] Add Basic Auth for admin UI — process: `operation`
- [x] Add Bearer token protection for data API endpoints — process: `operation`
- [x] Add IP allow-list with exact IP and CIDR support — process: `operation`
- [x] Add logging to `logs/access.log` and `logs/app.log` — process: `operation`
- [x] Add online log viewer `/admin/logs` with level/text/count/refresh/live controls — process: `operation`
- [x] Add SQL database read-only checkbox in `/admin` — process: `operation`
- [x] Add Firebird read-only endpoints through `isql.exe` — process: `integration`
- [x] Render admin settings with dropdowns, checkboxes, and textareas — process: `implementation`

## Acceptance
- [x] Stakeholder need or requirement is identified.
- [x] Expected evidence is named.
- [x] Verification or validation result is recorded.

## Blockers
- [ ] `git` and `gh` are not available in PATH for normal local commit/push.

## Risks
- [ ] API currently uses SQL login `sa` locally; replace with dedicated read-only login before broader deployment.
- [ ] DAServer WDT has shown repeated `DASrvAPI frozen`; API can still read SQL but TML runtime health may be degraded.
- [ ] Generic sample endpoints may reveal operational data; keep internal or restrict before public exposure.
- [ ] Admin/API is HTTP without TLS; keep on trusted network or place behind a secure reverse proxy before broad access.

## Rules
- [x] Do not commit `.env`, secrets, logs, or private exports.
- [x] API must remain read-only by default: no arbitrary SQL and no write endpoints.
- [x] Prefer domain endpoints over exposing raw table samples to consumers.

## Files
- `app.py`
- `.env.example`
- `README.md`
- `PROJECT_STATUS.md`
- `StatusProject/*.md`

## Latest Update 2026-06-27
- [x] Added read-only mobile domain adapter functions in `app.py`.
- [x] Verified syntax by compiling `app.py` text in memory with `utf-8-sig`.
- [x] Verified direct API `POST /mobile/incidents/{id}/status` returns `501 integration_not_ready` for valid transition request.
- [x] Verified `dbo.scada_point_current` exists but currently has 0 rows.
- [x] Verified `dbo.scada_points` currently groups rows under `controller_id=tml-alarms`.
- [x] Verified `/mobile/incidents?objectId=tml-alarms&limit=3` returns mapped alarm catalog incidents.
- [x] Verified `events.LIST_EVENTS` is a heap/no usable latest-event index.
- [x] Verified `/mobile/incidents/source-status` reports catalog ready and live journal not ready.
- [x] Verified `/mobile/incidents/source-status` reports `dbo.mobile_incidents` adapter missing before DDL execution.
- [x] Ran reviewed ScadaMobile DDL/backfill scripts; `dbo.mobile_incidents` exists with indexes and 100 bounded rows.
- [x] Updated `/mobile/incidents` source warning to report `events.LIST_EVENTS` through indexed `dbo.mobile_incidents` projection when the adapter exists.
- [x] Verified `/mobile/incidents?limit=3` returns `adapterStatus=materialized_mobile_incidents`.
- [ ] Next: design bounded incremental loader for `dbo.mobile_incidents` and improve point mapping for live journal rows with null `pointName`.
