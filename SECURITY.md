# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not open public issues for security vulnerabilities.**

Send security concerns to: [security contact email]

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if available)

We will acknowledge receipt within 48 hours and work on a fix.

## Security Features

### Database Access Control
- Read-only access only (no modification operations)
- SQL injection prevention
- Database whitelist (`TML_SQL_DATABASES`)
- Table-level access restrictions

### Authentication
- SQL Server authentication support
- Windows authentication support
- Environment variable-based credentials

### API Security
- No arbitrary SQL execution
- Limited endpoint set
- Input validation on all queries

## Best Practices

### Deployment
1. Use strong passwords for SQL accounts
2. Run API in a restricted network segment
3. Use Windows authentication when possible
4. Enable SSL/TLS for remote connections
5. Run as non-administrator user
6. Regular security updates for Python and dependencies

### Access Control
1. Create dedicated read-only SQL user
2. Grant only `db_datareader` permissions
3. Restrict API network access via firewall
4. Use API key/authentication layer in production
5. Monitor access logs

## Compliance

- GDPR compliant (read-only data access)
- No data modification capabilities
- Audit trail support (via SQL Server)
