# PROJECT-TREE: TML Read API

## Summary
- Scope: `local API repository and connected TML/SQL services`
- Owner: `operator + Codex`
- Last updated: `2026-06-20`

## Repository Tree
```text
D:\Data\Repos\API/
├── app.py
├── README.md
├── PROJECT_STATUS.md
├── requirements.txt
├── run.cmd
├── .env              # local only, ignored
├── .env.example      # safe template
├── .gitignore
├── logs/             # runtime logs, ignored
└── StatusProject/
    ├── PLAN.md
    ├── TODO.md
    ├── MEMORY.md
    ├── PROJECT-RESUME.md
    ├── ARCHITECTURE.md
    ├── PROJECT-TREE.md
    ├── INFRASTRUCTURE.md
    ├── SOFTWARE.md
    ├── DEVELOPMENT-STATUS.md
    ├── TESTING.md
    ├── LINKS.md
    └── SOURCE.md
```

## Services Tree
```text
TML Read API
├── Python HTTP API :8787
│   ├── depends on pyodbc
│   ├── depends on ODBC Driver 17
│   └── reads SQL Server ProjectOWEN
├── SQL Server 127.0.0.1:1433
│   └── database ProjectOWEN
└── OWEN TML runtime
    ├── OwenTMlite.exe
    ├── DAServer.exe
    ├── KVision.exe
    └── KEvents.exe
```

## Nodes
| Node | Type | Responsibility | Owner | Interfaces/dependencies |
| --- | --- | --- | --- | --- |
| `app.py` | `app` | HTTP API and SQL reads | operator | Python, pyodbc |
| `ProjectOWEN` | `db` | TML data source | operator | SQL Server |
| `D:\TML-Project\BiService` | `external project` | TML config/log source | operator | filesystem |
| `StatusProject/` | `docs/state` | durable project state | operator + agents | Markdown |

## Important Paths
- `app.py` — API implementation.
- `.env` — local credentials/config; never commit.
- `.env.example` — safe environment template.
- `StatusProject/PROJECT-RESUME.md` — restart context.
- `StatusProject/TODO.md` — current work.
- `StatusProject/MEMORY.md` — durable facts and rules.

## External Systems
| System | Purpose | Interface | Environment note |
| --- | --- | --- | --- |
| `SQL Server` | database source | ODBC/TCP 1433 | local host |
| `OWEN TML / Telemechanika Lite` | upstream SCADA/runtime | SQL, filesystem logs | local host |
| `GitHub NohchiyBors/StatusProject` | target/source repo reference | GitHub connector/web | git binary not installed locally |
