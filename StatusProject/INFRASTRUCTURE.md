# INFRASTRUCTURE: TML Read API

## Summary
- Owner: `operator + Codex`
- Criticality: `medium`
- Primary env: `local`
- Env labels: `prod = production`, `staging = pre-production`, `dev = development`, `local = operator machine`
- Life cycle stage: `development`
- Service objective: `read-only local/network API available when SQL Server and TML host are running`

## Environment Status
| Env | Role | Status | Source of truth | Last verified | Notes |
| --- | --- | --- | --- | --- | --- |
| prod | `production` | `unknown` | none | `2026-06-20` | not separated from local yet |
| staging | `pre-production` | `unknown` | none | `2026-06-20` | not created |
| dev | `development` | `ready` | `D:\Data\Repos\API` | `2026-06-20` | local source tree |
| local | `operator machine` | `ready` | process/port 8787 | `2026-06-20` | API running as Python process |

## Environments
| Env | URL | Provider/region | Runtime | DB/storage | Notes |
| --- | --- | --- | --- | --- | --- |
| prod | `not defined` | `operator host` | `not defined` | `ProjectOWEN` | needs service decision |
| staging | `not defined` | `none` | `none` | `none` | not configured |
| dev | `http://127.0.0.1:8787` | `local Windows` | `Python 3.14` | `SQL Server ProjectOWEN` | current development mode |
| local | `http://10.100.100.10:8787` | `operator Windows host` | `Python 3.14 + pyodbc` | `127.0.0.1,1433` | network URL if firewall allows |

## Components
| Component | Role | Owner | Critical dependency |
| --- | --- | --- | --- |
| Python process | API server | operator | Python + app.py |
| SQL Server | data source | operator | ProjectOWEN database |
| TML runtime | upstream producer | operator | DAServer/KEvents/KVision |
| `.env` | local config | operator | protected filesystem |

## Secrets And Access
- Storage: `local .env only; not committed`
- Required: `TML_SQL_USER`, `TML_SQL_PASSWORD`
- Access rule: `operator machine only; replace sa with dedicated read-only SQL login before broader deployment`
- Env rule: `local systems may load secrets from .env or .env.*; staging/prod should inject secrets as environment variables or managed secrets, not from committed files`

## Transition, Deploy And Ops
- Deploy: `manual start via run.cmd or python app.py`
- Rollback: `stop python process and restore previous app.py from backup/repo`
- Migrations: `none; API reads existing database only`
- Healthcheck: `GET /health`
- Logs/metrics/alerts: `logs/api.out.log`, `logs/api.err.log`; no alerting yet
- Backups/restore: `not owned by API; SQL/TML backup process required separately`
- Transition criteria: `domain endpoints defined, read-only user created, service startup decided`

## Commands
- Start: `D:\Data\Repos\API\run.cmd`
- Stop: `Stop-Process -Id <python-pid>`
- Restart: `stop current python process, then run run.cmd`
- Status/logs: `GET /StatusProject`; `Get-Content D:\Data\Repos\API\logs\api.out.log -Tail 50`

## Risks / Do Not
- Risks: `sa credential in local .env`, `DASrvAPI frozen in upstream TML`, `no Windows Service install yet`.
- Do not: `commit .env`, `commit logs`, `expose port 8787 publicly without auth/network controls`.

## Security Controls Added 2026-06-21
- TML_ALLOWED_IPS restricts client IPs.
- TML_ADMIN_USER / TML_ADMIN_PASSWORD protect /admin with Basic Auth.
- TML_API_TOKENS protects data endpoints with Bearer token.
- TML_ACCESS_LOG and TML_APP_LOG write request and app logs under logs/ by default.


## Remote IP Allow-list
- TML_ALLOWED_IPS supports exact IPs and CIDR networks, comma-separated.
- Admin UI displays the current client IP for copying into the allow-list.
- /StatusProject includes client_ip and security.allowed_ips.


## 2026-06-22 Operational Baseline
- Runtime port: `0.0.0.0:8787`.
- Admin UI: `/admin`, protected by Basic Auth and IP allow-list.
- Log viewer: `/admin/logs`, protected by Basic Auth and IP allow-list.
- API data: Bearer token required by default.
- IP allow-list: `TML_ALLOWED_IPS`, exact IP and CIDR supported.
- Logs: `logs/access.log`, `logs/app.log`, plus stdout/stderr files from launcher.
- Read-only DB mode: `TML_DATABASE_READ_ONLY=true` by default.
- Deployment gap: not installed as Windows Service yet.
