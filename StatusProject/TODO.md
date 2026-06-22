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
