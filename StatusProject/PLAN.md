# PLAN: TML Read API

## Purpose
- Strategic plan and major workstreams. Current execution lives in `TODO`; archived detail lives in `STATE-HISTORY`.
- Systems engineering basis: ISO/IEC 15288-style life cycle thinking; record practical process coverage, not certification claims.

## Life Cycle Scope
- Current stage: `development`
- System of interest: `External read-only API for OWEN TML / Telemechanika Lite SQL data`
- Boundary: `In scope: API status, table discovery, table stats, safe read endpoints. Out of scope: TML control/write operations, database migration, DAServer repair.`
- Success criteria: `External client can query status and domain data from ProjectOWEN over HTTP without database writes or secret exposure.`

## Stakeholders And Needs
| Stakeholder | Need / Concern | Success measure | Priority |
| --- | --- | --- | --- |
| Operator | Get TML data from an external app | API returns JSON from ProjectOWEN | high |
| API consumer | Stable endpoints | Domain endpoints documented and verified | high |
| Operations | Avoid harming TML runtime | No write SQL, no TML process control | high |

## Workstreams
| # | Workstream | ISO/IEC 15288 area | Goal | Principle | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | Read API foundation | `technical` | Running local HTTP API | minimal dependencies | `done` |
| 2 | Domain endpoints | `technical` | Events/alarms/objects/measurements | stable contracts | `open` |
| 3 | Operations | `project` | Service startup, logs, health | observable and reversible | `open` |
| 4 | Publication | `transition` | GitHub repo without secrets | safe release | `blocked` |

## Process Coverage
| Process area | Applies? | Project evidence | Gap / next action |
| --- | --- | --- | --- |
| Stakeholder needs and requirements | `yes` | `MEMORY.md`, `TODO.md` | refine domain data needs |
| System requirements | `yes` | `PLAN.md`, `SOFTWARE.md` | define endpoint schemas |
| Architecture definition | `yes` | `ARCHITECTURE.md` | review table-level data policy |
| Implementation / realization | `yes` | `app.py` | add domain endpoints |
| Integration | `yes` | `pyodbc` to `ProjectOWEN` | add service install path |
| Verification | `yes` | manual HTTP smoke checks | add automated tests |
| Transition / deployment | `yes` | `run.cmd`, `.env.example` | Windows Service decision |
| Validation | `yes` | operator feedback | validate data fields with real client |
| Operation and maintenance | `yes` | `INFRASTRUCTURE.md` | logging/rotation/service owner |
| Disposal / retirement | `no` | none | define only if needed |

## Priorities
- Now: `domain endpoints and access policy`
- Next: `Windows Service or scheduled startup`
- Later: `GitHub publication and release process`

## Risks And Tradeoffs
| Risk / tradeoff | Impact | Mitigation | Owner |
| --- | --- | --- | --- |
| Using `sa` in local `.env` | high credential blast radius | create read-only SQL login | operator |
| Generic sample endpoint | accidental data exposure | mask sensitive fields and restrict tables | API owner |
| DAServer instability | upstream data freshness risk | expose WDT status and handle SQL availability separately | operator |

## Verification Strategy
- Evidence to collect: `HTTP endpoint responses, SQL smoke checks, logs, later automated tests`.
- Acceptance rule: `API returns expected JSON from ProjectOWEN and never performs database writes.`

## Do Not
- Do not commit `.env`.
- Do not add write endpoints or arbitrary SQL execution.
