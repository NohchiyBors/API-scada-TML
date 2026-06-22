# ARCHITECTURE: TML Read API

## Summary
- Scope: `External read-only API around OWEN TML SQL data`
- Owner: `operator + Codex`
- Primary goal: `Enable external applications to read TML data safely over HTTP JSON.`
- Life cycle stage: `development`
- Architecture baseline: `implemented draft`

## Stakeholder Needs And Drivers
| Stakeholder | Need / driver | Architecture implication |
| --- | --- | --- |
| Operator | Read data outside TML UI | HTTP API over SQL Server |
| API consumer | Stable JSON | Domain endpoints should hide raw DB complexity |
| TML runtime | No interference | Read-only SQL access; no TML process control |

## System Requirements Trace
| Requirement | Source | Architecture element | Verification method |
| --- | --- | --- | --- |
| Read TML data externally | operator request | `app.py` + pyodbc + ProjectOWEN | HTTP smoke test |
| Provide StatusProject-style status | operator request | `/StatusProject` route | HTTP smoke test |
| Avoid writes | safety rule | no write routes, no arbitrary SQL | code review |
| Avoid secret leakage | StatusProject rules | `.gitignore`, `.env.example`, masking | file review + sample response |

## System Context
| Actor/System | Role | Interface | Notes |
| --- | --- | --- | --- |
| External client | consumes TML data | HTTP JSON on port 8787 | local/network access |
| TML Read API | adapter service | Python `http.server` | single process |
| SQL Server | source database | ODBC / TCP 1433 | database `ProjectOWEN` |
| OWEN TML | upstream SCADA runtime | writes/uses SQL, logs | `OwenTMlite`, `DAServer`, `KVision`, `KEvents` |

## Components
| Component | Responsibility | Inputs | Outputs | Important files/services |
| --- | --- | --- | --- | --- |
| HTTP handler | route GET requests | URL path/query | JSON responses | `app.py` |
| SQL access | connect/query ProjectOWEN | `.env`, pyodbc | row dictionaries | `sql_connection_string`, `query` |
| Status collector | process/log state | tasklist, log files | `/StatusProject` JSON | `project_status()` |
| Config loader | load local env | `.env` | process env | `load_env_file()` |

## Interfaces And Contracts
| Interface | Producer | Consumer | Contract | Compatibility rule |
| --- | --- | --- | --- | --- |
| `/health` | API | monitor/client | `{ ok, app, time_utc }` | keep 200 when process healthy |
| `/StatusProject` | API | operator/client | status JSON | keep process/log/sql summary fields |
| `/api/databases` | API | client | allow-listed DB connectivity | no secrets in response |
| `/api/{db}/tables` | API | client | table list | db must be allow-listed |
| `/api/{db}/table-stats` | API | client | table row counts | read-only metadata query |
| `/api/{db}/tables/{table}/sample` | API | internal client | limited rows | mask sensitive columns |

## Data Flows
- `External client -> HTTP GET -> TML Read API -> SQL Server ProjectOWEN -> JSON response`.
- `External client -> /StatusProject -> TML Read API -> tasklist/log files -> JSON response`.

## Dependencies
| Dependency | Type | Used by | Failure impact | Notes |
| --- | --- | --- | --- | --- |
| Python 3.14 | runtime | API | service cannot start | installed |
| pyodbc | library | SQL access | database endpoints fail | installed |
| ODBC Driver 17 | driver | SQL access | database endpoints fail | installed |
| SQL Server | internal service | data source | no TML SQL data | local `127.0.0.1,1433` |
| ProjectOWEN | database | data source | no domain data | contains `events`, `dispatcher`, `ascue`, `kdb`, `users` |

## Deployment Mapping
- `prod`: `not defined; likely same operator machine until service deployment is designed`.
- `staging`: `not defined`.
- `dev/local`: `D:\Data\Repos\API`, Python process on `0.0.0.0:8787`.

## Verification And Validation
| Concern | Method | Evidence | Status |
| --- | --- | --- | --- |
| API process | HTTP test | `/health` 200 | pass |
| SQL connectivity | HTTP/SQL test | `/api/databases` ProjectOWEN ok | pass |
| Table metadata | HTTP test | `/api/ProjectOWEN/table-stats` | pass |
| Sensitive masking | HTTP test | `users.USERLIST` sample masks password fields | pass |

## Decisions And Constraints
- Decisions: `2026-06-20: SQL Server ProjectOWEN is the primary data source because TML already connects to it.`
- Constraints: `read-only`, `no arbitrary SQL`, `do not commit secrets`.
- Do not: `do not expose .env`, `do not add control/write commands without explicit redesign`.
