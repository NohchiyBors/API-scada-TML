# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-06-27

### Added
- Project attribution in README and web interface
- .gitignore for StatusProject folder
- License compliance information in documentation

### Changed
- Updated license from generic MIT to MIT with explicit attribution requirement
- Added copyright holder information (HSPhub.com)
- Updated project metadata in pyproject.toml with author information
- Web interface now displays developer and customer information

### Security
- Ensured license and attribution requirements are clearly documented

## [0.1.0] - 2026-06-22

### Added
- Initial release of TML Read API
- Health check endpoint (`GET /health`)
- Status endpoint (`GET /StatusProject`, `GET /api/status`)
- Database connection check (`GET /api/databases`)
- Table listing endpoints (`GET /api/{db}/tables`, `GET /api/{db}/table-stats`)
- Sample data endpoint (`GET /api/{db}/tables/{schema.table}/sample`)
- Admin settings web interface
- Read-only access to OWEN TML / Telemechanika Lite database
- SQL Server connection via pyodbc
- Environment variable configuration

### Security
- Read-only database access (no INSERT/UPDATE/DELETE)
- SQL injection prevention
- Database whitelist support
- Windows and SQL authentication support

## [Unreleased]

### Planned
- Domain-specific endpoints for events, alarms, objects, and measurements
- WebSocket support for real-time data
- Advanced filtering and pagination
- Caching layer
- GraphQL API
- Docker containerization
- Kubernetes deployment support
