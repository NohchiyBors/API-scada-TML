# TESTING: TML Read API

## Summary
- Owner: `operator + Codex`
- Quality target: `read-only API smoke-verified before local use; automated tests required before broader release`
- Last reviewed: `2026-06-20`

## Test Scope
- In scope: `HTTP routes`, `SQL connectivity`, `sensitive field masking`, `StatusProject runtime status`.
- Out of scope: `TML internal correctness`, `SQL Server backup/restore`, `DAServer repair`.

## Test Levels
| Level | Target | Tool/method | Gate |
| --- | --- | --- | --- |
| `unit` | `config parsing, masking, identifier validation` | `future Python tests` | `not configured yet` |
| `integration` | `pyodbc -> ProjectOWEN` | `manual HTTP and SQL smoke checks` | `must return 200 and expected JSON` |
| `e2e/manual` | `client -> API -> SQL -> JSON` | `Invoke-WebRequest` | `health/db/table-stats pass` |

## Critical Scenarios
| Scenario | Source requirement | Expected result | Evidence |
| --- | --- | --- | --- |
| API health | API availability | `/health` returns 200 | manual check passed 2026-06-20 |
| DB connectivity | read TML data | `/api/databases` shows ProjectOWEN ok | manual check passed 2026-06-20 |
| Table discovery | explore schema | `/api/ProjectOWEN/tables` returns schemas/tables | manual check passed 2026-06-20 |
| Table stats | inspect data volumes | `events.LIST_EVENTS` row count returned | manual check passed 2026-06-20 |
| Sensitive masking | avoid password leakage | password-like columns return `***` | manual check passed 2026-06-20 |

## Defect And Risk Focus
- High-risk areas: `generic sample endpoint`, `credential handling`, `SQL errors`, `network exposure`.
- Known gaps: `no automated tests`, `no auth on HTTP API`, `no Windows Service health supervision`.

## Release Check
- Required checks: `/health`, `/api/databases`, `/api/ProjectOWEN/table-stats`, sensitive masking sample, `.env` ignored.
- Blockers: `committed secret`, write-capable SQL endpoint, failed DB connection, public network exposure without controls`.
- Rollback confidence: `medium`

## Log Viewer Verification
- GET /admin/logs returned 200 with live/refresh/limit controls.
- GET /admin/logs/data?file=app&level=INFO&limit=5 returned app log events.


## 2026-06-22 Smoke Results
- `netstat` shows API listening on `0.0.0.0:8787`.
- `app.py` syntax checks passed after latest admin UI changes.
- `/admin` returned 200 and rendered dropdowns, checkboxes, and textareas in previous verification.
- `/admin/logs` returned 200 and rendered live/refresh/limit controls in previous verification.
- `/admin/logs/data?file=app&level=INFO&limit=5` returned app log events in previous verification.
- `/StatusProject` returned `client_ip=127.0.0.1` and `security.allowed_ips` in previous verification.
- Known manual gap: no automated regression test suite yet.

## 2026-06-27 Mobile Adapter Smoke Results
- `app.py` syntax compiled in memory with `utf-8-sig`.
- `GET /mobile/objects?limit=3` returned real `ProjectOWEN` controller rows.
- `GET /mobile/objects/{id}` returned object detail for id `tml-controller-112`.
- `GET /mobile/incidents?limit=3` returned `dbo.scada_events` rows.
- `POST /mobile/incidents/{id}/status` with `accepted` returned `501 integration_not_ready`.
- `GET /mobile/objects/tml-alarms/points?limit=3` returned point rows with `latestValue=null`, `quality=not_available`, and `currentSource=dbo.scada_point_current`.
- Schema probe verified `dbo.scada_point_current` exists but has 0 rows; all observed `dbo.scada_points` rows group under `controller_id=tml-alarms`.
- `GET /mobile/incidents?limit=3` returned `objectId=tml-alarms` and point names from the point catalog.
- `GET /mobile/incidents?objectId=tml-alarms&limit=3` returned filtered mapped alarm catalog rows.
- `events.LIST_EVENTS` index probe returned only `HEAP`; no usable latest-event index exists.
- `GET /mobile/incidents/source-status` returned `catalog.ready=true` and `liveJournal.ready=false`.
- `GET /mobile/incidents/source-status` returned `materializedAdapter.exists=false` before projection DDL execution, while `/mobile/incidents` continued serving `dbo.scada_events` fallback rows.
