# PROJECT RESUME

Date: `2026-06-22 00:00:00 +05`
Project: `TML Read API / D:\Data\Repos\API`
Owner: `operator + Codex`

## State
- Life cycle stage: `development`
- Phase: `admin/security/runtime controls implemented`
- Status: `in-progress`
- Last result: `Admin UI now has dropdowns, checkboxes, textareas, online log viewer, IP/CIDR allow-list, Bearer-token API protection, Firebird read endpoints, and database read-only mode.`
- Focus: `Move from generic infrastructure/API controls to domain endpoints for events, alarms, objects, and measurements.`
- Blockers: `No git/gh binary in PATH; publication to GitHub must use connector or install git.`

## Systems Engineering Checkpoint
- Active process: `implementation, integration, verification, operation`
- Requirement / need being served: `External application must read TML data safely while operator can configure DB, tokens, users, IP access, logs, and runtime controls from web UI.`
- Evidence produced: `app.py, README.md, PROJECT_STATUS.md, StatusProject/*.md, live checks for /admin, /admin/logs, /StatusProject, Firebird endpoints, and API token behavior.`
- Residual risk: `Generic sample endpoints still need table-level access policy; HTTP admin/API still need deployment-grade auth/network controls before broad exposure.`

## Next
- Action: `Add domain endpoints: /api/events/latest, /api/alarms/latest, /api/objects, /api/measurements/latest.`
- Recheck: `SQL schema, Firebird aliases, TML WDT/DASrvAPI health, Windows Service requirement, and remote IP allow-list before external use.`
- Read: `PLAN -> TODO -> MEMORY -> PROJECT-RESUME -> ARCHITECTURE -> INFRASTRUCTURE -> SOFTWARE -> TESTING -> STATUS-LOG`
- Last StatusProject update check: `2026-06-22`
