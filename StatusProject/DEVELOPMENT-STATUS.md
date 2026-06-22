# DEVELOPMENT-STATUS: TML Read API

## Summary
- Overall progress: `65%`
- Status: `in progress`
- Owner: `operator + Codex`
- Last updated: `2026-06-22`

## Workstream Progress
| Workstream | Progress | Status | Next step |
| --- | --- | --- | --- |
| `requirements` | `70%` | `in progress` | define exact event/alarm/measurement fields |
| `architecture` | `75%` | `in progress` | review table-level data exposure policy |
| `implementation` | `70%` | `in progress` | add domain endpoints |
| `testing/release` | `40%` | `in progress` | add automated smoke tests and service deploy plan |
| `operations/admin` | `80%` | `in progress` | token rotation and Windows Service decision |

## Development Tree
```text
TML Read API
├── API foundation [done] 90%
├── Admin/security controls [done] 85%
│   ├── /admin settings [done] 90%
│   ├── token auth [done] 80%
│   ├── IP/CIDR allow-list [done] 80%
│   └── read-only toggle [done] 85%
├── Data endpoints [in progress] 45%
│   ├── SQL metadata/table-stats [done] 100%
│   ├── Firebird metadata/sample [done] 80%
│   └── domain endpoints [not started] 0%
├── Operations [in progress] 55%
│   ├── run.cmd [done] 100%
│   ├── access/app logs [done] 80%
│   ├── web log viewer [done] 85%
│   └── Windows Service [not started] 0%
└── Documentation [in progress] 80%
```

## Node Status
| Node | Progress | Status | Blocker | Next step |
| --- | --- | --- | --- | --- |
| `app.py` | `70%` | `in progress` | none | add domain endpoints |
| `SQL ProjectOWEN integration` | `75%` | `in progress` | read-only user not created | replace sa credentials |
| `Firebird integration` | `70%` | `in progress` | old ODS DBs need compatible tooling | add aliases only for supported DBs |
| `Admin UI` | `85%` | `in progress` | no TLS/auth hardening beyond Basic/Auth token | decide deployment boundary |
| `GitHub publication` | `10%` | `blocked` | git/gh not in PATH | publish via connector or install git |

## Risks
- `sa credential in .env` — replace with dedicated read-only login.
- `generic sample endpoints` — restrict or keep internal.
- `DASrvAPI frozen upstream` — status endpoint reports it, root cause is outside API.
- `HTTP admin/API` — keep on trusted network or secure behind proxy before broad exposure.

## Release Readiness
- Requirements: `70%`
- Implementation: `70%`
- Testing: `40%`
- Ops/docs: `70%`
- Confidence: `medium`
