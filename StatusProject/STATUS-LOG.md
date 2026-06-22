# STATUS-LOG: TML Read API

## 2026-06-22
- Status: `in-progress`
- Summary: `Captured latest admin/security/runtime controls in StatusProject.`
- Evidence:
  - API process is listening on `0.0.0.0:8787`.
  - `app.py` contains `/admin/logs`, Firebird routes, `TML_DATABASE_READ_ONLY`, `TML_ALLOWED_IPS`, token auth, dropdown/checkbox/textarea admin rendering.
  - `README.md` documents admin UI, Firebird endpoints, read-only mode, web log viewer, remote IP allow-list, and admin form controls.
- Completed since prior state:
  - Web settings UI backed by `.env`.
  - Basic Auth for `/admin`.
  - Bearer token requirement for data API endpoints.
  - IP allow-list with exact IP and CIDR support.
  - File logging to `logs/access.log` and `logs/app.log`.
  - Online log viewer at `/admin/logs` with file, level, text filter, event count, refresh period, and live checkbox.
  - SQL database read-only mode switch in `/admin` through `TML_DATABASE_READ_ONLY`.
  - SQL Server `ApplicationIntent=ReadOnly` while read-only mode is enabled.
  - Firebird read-only endpoints via `isql.exe`.
  - Admin form controls: dropdowns, checkboxes, and textareas for appropriate setting types.
- Open next:
  - Replace local `sa` SQL login with dedicated read-only login.
  - Add domain endpoints for events, alarms, objects, measurements.
  - Decide Windows Service deployment.
  - Define table-level allow/deny policy for generic sample endpoints.
- Risks:
  - `.env` contains local secrets and must remain uncommitted.
  - Broad network exposure requires stronger auth/TLS/reverse proxy or trusted network boundary.
  - TML WDT has previously shown `DASrvAPI frozen`; API status reports it but does not fix upstream runtime.
