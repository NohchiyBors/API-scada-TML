# PROJECT RESUME

Date: `2026-06-27 15:20:00 +05`
Project: `TML Read API / D:\Data\Repos\API`
Owner: `operator + Codex`

## State
- Life cycle stage: `development`
- Phase: `mobile read adapter implemented`
- Status: `in-progress`
- Last result: `dbo.mobile_incidents now exists with indexes and 100 bounded backfilled rows; API /mobile/incidents returns materialized events.LIST_EVENTS rows and sourceWarning reflects the adapter.`
- Focus: `Define recurring incremental load for dbo.mobile_incidents and improve point/object mapping for live journal rows.`
- Blockers: `No git/gh binary in PATH; publication to GitHub must use connector or install git.`

## Systems Engineering Checkpoint
- Active process: `implementation, integration, verification, operation`
- Requirement / need being served: `External application must read TML data safely while operator can configure DB, tokens, users, IP access, logs, and runtime controls from web UI.`
- Evidence produced: `app.py, README.md, PROJECT_STATUS.md, StatusProject/*.md, live checks for /mobile/objects, /mobile/incidents, /mobile/me, /mobile/incidents/{id}/status, and existing auth behavior.`
- Residual risk: `Current materialized incidents are a small historical sample only; recurring loader, CRM assignment/status source, and latest telemetry population remain open.`

## Next
- Action: `Design and implement bounded incremental loader for dbo.mobile_incidents; keep dbo.scada_point_current/latest telemetry work separate.`
- Recheck: `SQL schema, Firebird aliases, TML WDT/DASrvAPI health, Windows Service requirement, and remote IP allow-list before external use.`
- Read: `PLAN -> TODO -> MEMORY -> PROJECT-RESUME -> ARCHITECTURE -> INFRASTRUCTURE -> SOFTWARE -> TESTING -> STATUS-LOG`
- Last StatusProject update check: `2026-06-22`
