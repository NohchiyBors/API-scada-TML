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
