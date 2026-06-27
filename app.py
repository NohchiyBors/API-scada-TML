import base64
import html
import ipaddress
import json
import logging
import os
import re
import secrets
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

try:
    import pyodbc
except ImportError:  # pragma: no cover
    pyodbc = None

APP_DIR = Path(__file__).resolve().parent
ENV_PATH = APP_DIR / ".env"
APP_NAME = "tml-read-api"
APP_ATTRIBUTION = "Разработчик HSPhub.com по заказу astana.company."
DEFAULT_DATABASES = ["ProjectOWEN"]
DB_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]+$")
TABLE_NAME_RE = re.compile(r"^[A-Za-z0-9_\.\-]+$")
SENSITIVE_COLUMN_RE = re.compile(r"pass|pwd|token|secret|hash|key", re.IGNORECASE)
SETTING_KEYS = [
    "TML_API_HOST",
    "TML_API_PORT",
    "TML_PROJECT_ROOT",
    "TML_SQL_DRIVER",
    "TML_SQL_SERVER",
    "TML_SQL_USER",
    "TML_SQL_PASSWORD",
    "TML_SQL_DATABASES",
    "TML_SQL_TIMEOUT",
    "TML_API_CORS_ORIGIN",
    "TML_ALLOWED_IPS",
    "TML_ADMIN_USER",
    "TML_ADMIN_PASSWORD",
    "TML_REQUIRE_API_TOKEN",
    "TML_API_TOKENS",
    "TML_LOG_DIR",
    "TML_ACCESS_LOG",
    "TML_APP_LOG",
    "TML_LOG_LEVEL",
    "TML_DATABASE_READ_ONLY",
    "TML_FIREBIRD_ISQL",
    "TML_FIREBIRD_DATABASES",
    "TML_FIREBIRD_USER",
    "TML_FIREBIRD_PASSWORD",
]
SECRET_KEYS = {"TML_SQL_PASSWORD", "TML_ADMIN_PASSWORD", "TML_API_TOKENS", "TML_FIREBIRD_PASSWORD"}


def load_env_file(path=ENV_PATH, override=False):
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if override or key not in os.environ:
            os.environ[key] = value


def read_env_map(path=ENV_PATH):
    result = {}
    env_path = Path(path)
    if not env_path.exists():
        return result
    for raw_line in env_path.read_text(encoding="utf-8-sig").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#") or "=" not in raw_line:
            continue
        key, value = raw_line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def write_env_map(updates, path=ENV_PATH):
    env_path = Path(path)
    current = read_env_map(env_path)
    current.update({k: v for k, v in updates.items() if k in SETTING_KEYS})
    lines = [f"{key}={current.get(key, '')}" for key in SETTING_KEYS if key in current]
    for key in sorted(k for k in current if k not in SETTING_KEYS):
        lines.append(f"{key}={current[key]}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    load_env_file(env_path, override=True)
    setup_logging()


load_env_file()
PROJECT_ROOT = Path(os.getenv("TML_PROJECT_ROOT", r"D:\TML-Project\BiService"))


def rel_path(raw, default):
    value = os.getenv(raw, default)
    p = Path(value)
    return p if p.is_absolute() else APP_DIR / p


def setup_logging():
    log_dir = rel_path("TML_LOG_DIR", "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    app_log = rel_path("TML_APP_LOG", "logs/app.log")
    access_log = rel_path("TML_ACCESS_LOG", "logs/access.log")
    level = getattr(logging, os.getenv("TML_LOG_LEVEL", "INFO").upper(), logging.INFO)

    logging.getLogger().handlers.clear()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(app_log, encoding="utf-8"), logging.StreamHandler()],
    )
    access_logger = logging.getLogger("access")
    access_logger.handlers.clear()
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(logging.FileHandler(access_log, encoding="utf-8"))
    access_logger.propagate = False


setup_logging()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def csv_env(name):
    raw = os.getenv(name, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


def configured_databases():
    return csv_env("TML_SQL_DATABASES") or DEFAULT_DATABASES


def allowed_ips():
    return set(csv_env("TML_ALLOWED_IPS"))


def api_tokens():
    return set(csv_env("TML_API_TOKENS"))


def database_read_only():
    return env_bool("TML_DATABASE_READ_ONLY", True)

def sql_connection_string(database=None):
    driver = os.getenv("TML_SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("TML_SQL_SERVER", "127.0.0.1,1433")
    user = os.getenv("TML_SQL_USER")
    password = os.getenv("TML_SQL_PASSWORD")
    timeout = os.getenv("TML_SQL_TIMEOUT", "5")
    parts = [
        f"Driver={{{driver}}}",
        f"Server={server}",
        "Encrypt=no",
        "TrustServerCertificate=yes",
        f"Connection Timeout={timeout}",
        "ApplicationIntent=ReadOnly" if database_read_only() else "ApplicationIntent=ReadWrite",
    ]
    if database:
        parts.append(f"Database={database}")
    if user:
        parts.append(f"Uid={user}")
        parts.append(f"Pwd={password or ''}")
    else:
        parts.append("Trusted_Connection=yes")
    return ";".join(parts) + ";"


def connect(database=None):
    if pyodbc is None:
        raise RuntimeError("pyodbc is not installed")
    return pyodbc.connect(sql_connection_string(database), autocommit=True)


def rows_to_dicts(cursor, rows, redact_sensitive=True):
    columns = [col[0] for col in cursor.description or []]
    result = []
    for row in rows:
        item = {}
        for idx, col in enumerate(columns):
            value = row[idx]
            if redact_sensitive and SENSITIVE_COLUMN_RE.search(col):
                value = None if value is None else "***"
            elif isinstance(value, datetime):
                value = value.isoformat()
            item[col] = value
        result.append(item)
    return result




def ensure_select_only(sql):
    cleaned = re.sub(r"--.*?$|/\*.*?\*/", "", sql, flags=re.MULTILINE | re.DOTALL).strip().lower()
    allowed_prefixes = ("select", "set list on;\nselect", "set list on;\r\nselect")
    if not cleaned.startswith(allowed_prefixes):
        raise ValueError("Only SELECT statements are allowed")
    forbidden = re.search(r"\b(insert|update|delete|merge|drop|alter|create|truncate|exec|execute|grant|revoke|backup|restore)\b", cleaned)
    if forbidden:
        raise ValueError("Write or administrative SQL is not allowed")

def query(database, sql, params=None):
    if database_read_only():
        ensure_select_only(sql)
    with connect(database) as cn:
        cur = cn.cursor()
        cur.execute(sql, params or [])
        return rows_to_dicts(cur, cur.fetchall())


def bracket_identifier(identifier):
    if not TABLE_NAME_RE.match(identifier):
        raise ValueError("Invalid identifier")
    return ".".join("[" + part.replace("]", "]]") + "]" for part in identifier.split("."))


def list_processes():
    names = {"OwenTMlite.exe", "DAServer.exe", "KVision.exe", "KEvents.exe", "firebird.exe", "sqlservr.exe"}
    found = {name: False for name in names}
    try:
        output = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, encoding="cp866", errors="ignore")
        for line in output.splitlines():
            parts = [part.strip('"') for part in line.split('","')]
            if parts and parts[0] in found:
                found[parts[0]] = True
    except Exception as exc:
        return {"error": str(exc), "processes": found}
    return found


def file_info(path):
    p = Path(path)
    if not p.exists():
        return {"exists": False}
    stat = p.stat()
    return {"exists": True, "path": str(p), "bytes": stat.st_size, "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()}


def tail_lines(path, limit=40):
    p = Path(path)
    if not p.exists():
        return []
    data = p.read_bytes()[-65536:]
    text = data.decode("utf-8", errors="replace")
    return text.splitlines()[-limit:]


def project_status():
    project_root = Path(os.getenv("TML_PROJECT_ROOT", str(PROJECT_ROOT)))
    das_log = project_root / "DAServer" / "Station_1" / "DAServer.log"
    wdt_log = project_root / "DAServer" / "Station_1" / "WDT.log"
    wdt_tail = tail_lines(wdt_log, 30)
    return {
        "app": APP_NAME,
        "time_utc": utc_now(),
        "project_root": str(project_root),
        "processes": list_processes(),
        "logs": {
            "daserver": file_info(das_log),
            "wdt": file_info(wdt_log),
            "wdt_tail": wdt_tail,
            "dasrvapi_frozen_recent": any("DASrvAPI frozen" in line for line in wdt_tail),
        },
        "sql": {
            "server": os.getenv("TML_SQL_SERVER", "127.0.0.1,1433"),
            "databases": configured_databases(),
            "auth": "sql" if os.getenv("TML_SQL_USER") else "trusted",
            "driver": os.getenv("TML_SQL_DRIVER", "ODBC Driver 17 for SQL Server"),
        },
        "security": {
            "allowed_ips": csv_env("TML_ALLOWED_IPS"),
            "api_token_required": env_bool("TML_REQUIRE_API_TOKEN", True),
            "database_read_only": database_read_only(),
            "token_count": len(api_tokens()),
        },
    }




def firebird_databases():
    raw = os.getenv("TML_FIREBIRD_DATABASES", "")
    result = {}
    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        if "=" in item:
            alias, path = item.split("=", 1)
        else:
            path_obj = Path(item)
            alias, path = path_obj.stem, item
        alias = alias.strip()
        path = path.strip()
        if DB_NAME_RE.match(alias) and path:
            result[alias] = path
    return result


def run_firebird_isql(alias, sql):
    if database_read_only():
        ensure_select_only(sql)
    databases = firebird_databases()
    if alias not in databases:
        raise ValueError("Firebird database is not in TML_FIREBIRD_DATABASES allow-list")
    isql = os.getenv("TML_FIREBIRD_ISQL", r"C:\Program Files\Firebird\Firebird_3_0\isql.exe")
    user = os.getenv("TML_FIREBIRD_USER", "sysdba")
    password = os.getenv("TML_FIREBIRD_PASSWORD", "")
    cmd = [isql, "-user", user, "-password", password, "-q", databases[alias]]
    proc = subprocess.run(cmd, input=sql, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8", errors="replace", timeout=30)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.strip())
    return proc.stdout


def parse_firebird_list_output(output):
    rows = []
    current = {}
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        if not line or line.startswith("Database:") or line.startswith("SQL>") or line.startswith("CON>"):
            if current:
                rows.append(current)
                current = {}
            continue
        match = re.match(r"^([A-Z0-9_]+)\s+(.*)$", line.strip(), re.IGNORECASE)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            if SENSITIVE_COLUMN_RE.search(key):
                value = "***" if value else value
            current[key] = value
    if current:
        rows.append(current)
    return rows


def firebird_tables(alias):
    sql = """
set list on;
select trim(rdb$relation_name) as table_name
from rdb$relations
where coalesce(rdb$system_flag, 0) = 0
  and rdb$view_blr is null
order by rdb$relation_name;
"""
    rows = parse_firebird_list_output(run_firebird_isql(alias, sql))
    return [row.get("TABLE_NAME") for row in rows if row.get("TABLE_NAME")]



def firebird_identifier(identifier):
    if not TABLE_NAME_RE.match(identifier):
        raise ValueError("Invalid Firebird identifier")
    return ".".join('"' + part.replace('"', '""').upper() + '"' for part in identifier.split("."))
def firebird_sample(alias, table, limit):
    if not TABLE_NAME_RE.match(table):
        raise ValueError("Invalid Firebird table name")
    limit = min(max(int(limit), 1), 200)
    sql = f"set list on;\nselect first {limit} * from {firebird_identifier(table)};\n"
    return parse_firebird_list_output(run_firebird_isql(alias, sql))

def log_file_map():
    return {
        "app": rel_path("TML_APP_LOG", "logs/app.log"),
        "access": rel_path("TML_ACCESS_LOG", "logs/access.log"),
        "stdout": APP_DIR / "logs" / "api.out.log",
        "stderr": APP_DIR / "logs" / "api.err.log",
    }


def read_log_events(name="app", level="ALL", limit=200, contains=""):
    files = log_file_map()
    path = files.get(name, files["app"])
    limit = min(max(int(limit), 1), 2000)
    level = (level or "ALL").upper()
    contains_lower = (contains or "").lower()
    if not path.exists():
        return {"file": name, "path": str(path), "exists": False, "events": []}
    data = path.read_bytes()[-1048576:]
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    filtered = []
    for line in lines:
        upper = line.upper()
        if level != "ALL" and level not in upper:
            continue
        if contains_lower and contains_lower not in line.lower():
            continue
        filtered.append(line)
    return {
        "file": name,
        "path": str(path),
        "exists": True,
        "level": level,
        "contains": contains,
        "limit": limit,
        "total_matched": len(filtered),
        "events": filtered[-limit:],
        "time_utc": utc_now(),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "TmlReadApi/0.2"

    def log_message(self, fmt, *args):
        msg = fmt % args
        logging.getLogger("access").info('%s "%s"', self.client_address[0], msg)

    def client_ip(self):
        return self.client_address[0]

    def ip_allowed(self):
        rules = allowed_ips()
        if not rules:
            return True
        client = self.client_ip()
        if client in rules:
            return True
        try:
            client_ip = ipaddress.ip_address(client)
        except ValueError:
            return False
        for rule in rules:
            try:
                if "/" in rule and client_ip in ipaddress.ip_network(rule, strict=False):
                    return True
            except ValueError:
                continue
        return False

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", os.getenv("TML_API_CORS_ORIGIN", "*"))
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, status, content):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_OPTIONS(self):
        if not self.ip_allowed():
            self.send_json(403, {"error": "ip_not_allowed"})
            return
        self.send_json(204, {})

    def do_GET(self):
        if not self.ip_allowed():
            self.send_json(403, {"error": "ip_not_allowed", "ip": self.client_ip()})
            return
        try:
            self.route_get()
        except Exception as exc:
            logging.exception("GET failed")
            self.send_json(500, {"error": type(exc).__name__, "message": str(exc)})

    def do_POST(self):
        if not self.ip_allowed():
            self.send_json(403, {"error": "ip_not_allowed", "ip": self.client_ip()})
            return
        try:
            self.route_post()
        except Exception as exc:
            logging.exception("POST failed")
            self.send_json(500, {"error": type(exc).__name__, "message": str(exc)})

    def route_get(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/":
            self.redirect("/admin")
            return
        if path == "/health":
            self.send_json(200, {"ok": True, "app": APP_NAME, "time_utc": utc_now()})
            return
        if path == "/admin":
            if not self.require_admin():
                return
            self.send_html(200, self.admin_page(saved=qs.get("saved", [""])[0] == "1"))
            return
        if path == "/admin/logs":
            if not self.require_admin():
                return
            self.send_html(200, self.logs_page())
            return
        if path == "/admin/logs/data":
            if not self.require_admin():
                return
            payload = read_log_events(
                name=qs.get("file", ["app"])[0],
                level=qs.get("level", ["ALL"])[0],
                limit=qs.get("limit", ["200"])[0],
                contains=qs.get("contains", [""])[0],
            )
            self.send_json(200, payload)
            return
        if path == "/api/config/public":
            if not self.require_api_token():
                return
            self.send_json(200, self.public_config())
            return
        if path in {"/StatusProject", "/api/status"}:
            if not self.require_api_token():
                return
            payload = project_status()
            payload["client_ip"] = self.client_ip()
            self.send_json(200, payload)
            return
        if path == "/api/databases":
            if not self.require_api_token():
                return
            self.send_json(200, self.databases_payload())
            return


        if path == "/api/firebird/databases":
            if not self.require_api_token():
                return
            payload = []
            for alias, db_path in firebird_databases().items():
                try:
                    tables = firebird_tables(alias)
                    payload.append({"alias": alias, "path": db_path, "ok": True, "table_count": len(tables)})
                except Exception as exc:
                    payload.append({"alias": alias, "path": db_path, "ok": False, "error": str(exc)})
            self.send_json(200, {"databases": payload})
            return

        match = re.fullmatch(r"/api/firebird/([^/]+)/tables", path)
        if match:
            if not self.require_api_token():
                return
            alias = unquote(match.group(1))
            if not DB_NAME_RE.match(alias):
                self.send_json(400, {"error": "invalid firebird alias"})
                return
            self.send_json(200, {"database": alias, "tables": firebird_tables(alias)})
            return

        match = re.fullmatch(r"/api/firebird/([^/]+)/tables/([^/]+)/sample", path)
        if match:
            if not self.require_api_token():
                return
            alias = unquote(match.group(1))
            table = unquote(match.group(2))
            if not DB_NAME_RE.match(alias):
                self.send_json(400, {"error": "invalid firebird alias"})
                return
            limit = min(max(int(qs.get("limit", [20])[0]), 1), 200)
            self.send_json(200, {"database": alias, "table": table, "limit": limit, "rows": firebird_sample(alias, table, limit)})
            return
        match = re.fullmatch(r"/api/([^/]+)/tables", path)
        if match:
            if not self.require_api_token():
                return
            db = unquote(match.group(1))
            self.validate_db(db)
            rows = query(db, """
                SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                FROM INFORMATION_SCHEMA.TABLES
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            self.send_json(200, {"database": db, "tables": rows})
            return

        match = re.fullmatch(r"/api/([^/]+)/table-stats", path)
        if match:
            if not self.require_api_token():
                return
            db = unquote(match.group(1))
            self.validate_db(db)
            rows = query(db, """
                SELECT s.name AS schema_name, t.name AS table_name, SUM(p.rows) AS rows
                FROM sys.tables t
                JOIN sys.schemas s ON s.schema_id = t.schema_id
                JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
                GROUP BY s.name, t.name
                ORDER BY SUM(p.rows) DESC, s.name, t.name
            """)
            self.send_json(200, {"database": db, "tables": rows})
            return

        match = re.fullmatch(r"/api/([^/]+)/tables/([^/]+)/sample", path)
        if match:
            if not self.require_api_token():
                return
            db = unquote(match.group(1))
            table = unquote(match.group(2))
            self.validate_db(db)
            if not TABLE_NAME_RE.match(table):
                self.send_json(400, {"error": "invalid table name"})
                return
            limit = min(max(int(qs.get("limit", [20])[0]), 1), 200)
            rows = query(db, f"SELECT TOP ({limit}) * FROM {bracket_identifier(table)}")
            self.send_json(200, {"database": db, "table": table, "limit": limit, "rows": rows})
            return

        self.send_json(404, {"error": "not_found", "path": path})

    def route_post(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if path == "/admin/settings":
            if not self.require_admin():
                return
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8", errors="replace")
            form = {k: v[-1] for k, v in parse_qs(raw, keep_blank_values=True).items()}
            updates = {}
            current = read_env_map()
            for key in SETTING_KEYS:
                if key in SECRET_KEYS and not form.get(key):
                    updates[key] = current.get(key, os.getenv(key, ""))
                else:
                    updates[key] = form.get(key, current.get(key, os.getenv(key, "")))
            write_env_map(updates)
            logging.info("settings updated by %s", self.client_ip())
            self.redirect("/admin?saved=1")
            return
        self.send_json(404, {"error": "not_found", "path": path})

    def require_admin(self):
        expected_user = os.getenv("TML_ADMIN_USER", "admin")
        expected_password = os.getenv("TML_ADMIN_PASSWORD", "")
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:]).decode("utf-8")
                user, password = decoded.split(":", 1)
                if secrets.compare_digest(user, expected_user) and secrets.compare_digest(password, expected_password):
                    return True
            except Exception:
                pass
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="TML Admin"')
        self.end_headers()
        return False

    def require_api_token(self):
        if not env_bool("TML_REQUIRE_API_TOKEN", True):
            return True
        tokens = api_tokens()
        header = self.headers.get("Authorization", "")
        supplied = ""
        if header.startswith("Bearer "):
            supplied = header[7:].strip()
        if supplied and any(secrets.compare_digest(supplied, token) for token in tokens):
            return True
        self.send_json(401, {"error": "api_token_required"})
        return False

    def public_config(self):
        return {
            "app": APP_NAME,
            "client_ip": self.client_ip(),
            "host": os.getenv("TML_API_HOST", "0.0.0.0"),
            "port": os.getenv("TML_API_PORT", "8787"),
            "project_root": os.getenv("TML_PROJECT_ROOT", ""),
            "sql_server": os.getenv("TML_SQL_SERVER", ""),
            "databases": configured_databases(),
            "allowed_ips": csv_env("TML_ALLOWED_IPS"),
            "api_token_required": env_bool("TML_REQUIRE_API_TOKEN", True),
            "database_read_only": database_read_only(),
        }

    def databases_payload(self):
        payload = []
        for db in configured_databases():
            if not DB_NAME_RE.match(db):
                payload.append({"database": db, "ok": False, "error": "invalid configured database name"})
                continue
            try:
                result = query(db, "SELECT DB_NAME() AS database_name")
                payload.append({"database": db, "ok": True, "result": result[0] if result else None})
            except Exception as exc:
                payload.append({"database": db, "ok": False, "error": str(exc)})
        return {"databases": payload}

    def validate_db(self, db):
        if db not in configured_databases():
            raise ValueError("Database is not in TML_SQL_DATABASES allow-list")
        if not DB_NAME_RE.match(db):
            raise ValueError("Invalid database name")

    def logs_page(self):
        files_options = "".join(f'<option value="{html.escape(name)}">{html.escape(name)} - {html.escape(str(path))}</option>' for name, path in log_file_map().items())
        return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>TML Read API Logs</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f5f6f8; color: #1f2933; }}
header {{ background: #1f2933; color: white; padding: 16px 24px; }}
main {{ max-width: 1200px; margin: 24px auto; background: white; border: 1px solid #d9dee5; padding: 20px; }}
nav a {{ color: white; margin-right: 16px; }}
.controls {{ display: grid; grid-template-columns: repeat(6, minmax(120px, 1fr)); gap: 12px; align-items: end; margin-bottom: 16px; }}
label {{ display: grid; gap: 4px; font-weight: 600; }}
select, input, button {{ font: inherit; padding: 8px; border: 1px solid #b8c0cc; border-radius: 4px; }}
button {{ background: #2563eb; color: white; border: 0; cursor: pointer; }}
.logbox {{ background: #101828; color: #e4e7ec; padding: 14px; min-height: 520px; max-height: 70vh; overflow: auto; white-space: pre-wrap; font-family: Consolas, monospace; font-size: 13px; }}
.meta {{ color: #667085; margin: 8px 0 12px; }}
.badge {{ display: inline-block; padding: 3px 8px; border-radius: 12px; background: #e8f0fe; color: #1d4ed8; margin-left: 8px; }}
.attribution {{ margin-top: 14px; color: #667085; font-size: 13px; }}
</style>
</head>
<body>
<header><h1>TML Read API Logs</h1><nav><a href="/admin">settings</a><a href="/StatusProject">StatusProject</a><a href="/health">health</a></nav></header>
<main>
<div class="controls">
<label>Log file<select id="file">{files_options}</select></label>
<label>Level<select id="level"><option>ALL</option><option>DEBUG</option><option>INFO</option><option>WARNING</option><option>ERROR</option></select></label>
<label>Contains<input id="contains" type="text" placeholder="filter text"></label>
<label>Events<input id="limit" type="number" min="1" max="2000" value="200"></label>
<label>Refresh sec<input id="refresh" type="number" min="1" max="3600" value="5"></label>
<label><span>Live</span><input id="live" type="checkbox" checked></label>
<button id="load" type="button">Refresh</button>
</div>
<div class="meta" id="meta">not loaded</div>
<div class="logbox" id="logbox"></div>
<div class="attribution">{html.escape(APP_ATTRIBUTION)}</div>
</main>
<script>
let timer = null;
function esc(s) {{ return String(s).replace(/[&<>]/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c])); }}
async function loadLogs() {{
  const params = new URLSearchParams({{
    file: document.getElementById('file').value,
    level: document.getElementById('level').value,
    contains: document.getElementById('contains').value,
    limit: document.getElementById('limit').value
  }});
  const res = await fetch('/admin/logs/data?' + params.toString(), {{ cache: 'no-store' }});
  const data = await res.json();
  document.getElementById('meta').innerHTML = `${{esc(data.file)}} <span class="badge">matched: ${{data.total_matched ?? 0}}</span> <span class="badge">shown: ${{(data.events || []).length}}</span> <span class="badge">${{esc(data.time_utc || '')}}</span><br>${{esc(data.path || '')}}`;
  document.getElementById('logbox').innerHTML = esc((data.events || []).join('\n'));
  const box = document.getElementById('logbox'); box.scrollTop = box.scrollHeight;
}}
function resetTimer() {{
  if (timer) clearInterval(timer);
  if (document.getElementById('live').checked) {{
    const seconds = Math.max(parseInt(document.getElementById('refresh').value || '5'), 1);
    timer = setInterval(loadLogs, seconds * 1000);
  }}
}}
for (const id of ['file','level','contains','limit','refresh','live']) document.getElementById(id).addEventListener('change', () => {{ loadLogs(); resetTimer(); }});
document.getElementById('contains').addEventListener('keyup', () => {{ loadLogs(); resetTimer(); }});
document.getElementById('load').addEventListener('click', loadLogs);
loadLogs(); resetTimer();
</script>
</body>
</html>'''

    def admin_page(self, saved=False):
        env_map = read_env_map()
        fields = []
        bool_keys = {"TML_DATABASE_READ_ONLY", "TML_REQUIRE_API_TOKEN"}
        select_options = {
            "TML_LOG_LEVEL": ["DEBUG", "INFO", "WARNING", "ERROR"],
            "TML_SQL_DRIVER": ["ODBC Driver 17 for SQL Server", "ODBC Driver 18 for SQL Server", "SQL Server"],
            "TML_API_CORS_ORIGIN": ["*", "http://127.0.0.1:8787", "http://10.100.100.10:8787"],
        }
        textarea_keys = {"TML_ALLOWED_IPS", "TML_API_TOKENS", "TML_SQL_DATABASES", "TML_FIREBIRD_DATABASES"}
        hints = {
            "TML_ALLOWED_IPS": f"Comma-separated exact IPs or CIDR. Current client: {html.escape(self.client_ip())}",
            "TML_API_TOKENS": "Comma-separated Bearer tokens. Leave blank to keep current tokens.",
            "TML_SQL_DATABASES": "Comma-separated SQL database allow-list.",
            "TML_FIREBIRD_DATABASES": "Semicolon-separated aliases, for example users=D:\\path\\USERS.FDB",
        }
        for key in SETTING_KEYS:
            value = env_map.get(key, os.getenv(key, ""))
            label = html.escape(key)
            if key in SECRET_KEYS:
                if key in textarea_keys:
                    field = f'<textarea name="{label}" placeholder="leave blank to keep current value"></textarea>'
                else:
                    field = f'<input type="password" name="{label}" placeholder="leave blank to keep current value" autocomplete="off">'
                current = "set" if value else "empty"
            elif key in bool_keys:
                checked = "checked" if env_bool(key, True) else ""
                caption = "Enabled" if key == "TML_REQUIRE_API_TOKEN" else "Read-only database mode"
                field = f'<input type="hidden" name="{label}" value="false"><label class="switch"><input type="checkbox" name="{label}" value="true" {checked}><span>{caption}</span></label>'
                current = "true" if env_bool(key, True) else "false"
            elif key in select_options:
                options = []
                choices = select_options[key]
                if value and value not in choices:
                    choices = [value] + choices
                for option in choices:
                    selected = "selected" if option == value else ""
                    options.append(f'<option value="{html.escape(option)}" {selected}>{html.escape(option)}</option>')
                field = f'<select name="{label}">{"".join(options)}</select>'
                current = html.escape(value)
            elif key in textarea_keys:
                field = f'<textarea name="{label}">{html.escape(value)}</textarea>'
                current = html.escape(hints.get(key, value))
            elif key in {"TML_API_PORT", "TML_SQL_TIMEOUT"}:
                field = f'<input type="number" name="{label}" value="{html.escape(value)}" min="1">'
                current = html.escape(value)
            else:
                field = f'<input type="text" name="{label}" value="{html.escape(value)}">'
                current = html.escape(value)
            fields.append(f'<label><span>{label}</span>{field}<small>{current}</small></label>')
        saved_html = '<div class="ok">Settings saved. Restart may be required for host/port changes.</div>' if saved else ''
        return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>TML Read API Settings</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f5f6f8; color: #1f2933; }}
header {{ background: #1f2933; color: white; padding: 16px 24px; }}
main {{ max-width: 980px; margin: 24px auto; background: white; border: 1px solid #d9dee5; padding: 20px; }}
label {{ display: grid; grid-template-columns: 260px 1fr; gap: 8px 14px; padding: 10px 0; border-bottom: 1px solid #edf0f3; }}
label span {{ font-weight: 600; }}
input, textarea, select {{ font: inherit; padding: 8px; border: 1px solid #b8c0cc; border-radius: 4px; }}
textarea {{ min-height: 76px; resize: vertical; }}
small {{ grid-column: 2; color: #667085; overflow-wrap: anywhere; }}
button {{ margin-top: 18px; padding: 10px 16px; background: #2563eb; color: white; border: 0; border-radius: 4px; cursor: pointer; }}
.switch {{ display: flex; align-items: center; gap: 10px; padding: 0; border: 0; }}
.switch input {{ width: 20px; height: 20px; }}
.ok {{ background: #e8f7ee; border: 1px solid #97d4aa; padding: 10px; margin-bottom: 12px; }}
nav a {{ color: white; margin-right: 16px; }}
.attribution {{ margin-top: 14px; color: #667085; font-size: 13px; }}
</style>
</head>
<body>
<header><h1>TML Read API Settings</h1><nav><a href="/admin/logs">logs</a><a href="/health">health</a><a href="/StatusProject">StatusProject</a><a href="/api/databases">databases</a></nav></header>
<main>
{saved_html}
<form method="post" action="/admin/settings">
{''.join(fields)}
<button type="submit">Save settings</button>
</form>
<div class="attribution">{html.escape(APP_ATTRIBUTION)}</div>
</main>
</body>
</html>"""


def main():
    host = os.getenv("TML_API_HOST", "0.0.0.0")
    port = int(os.getenv("TML_API_PORT", "8787"))
    httpd = ThreadingHTTPServer((host, port), Handler)
    logging.info("%s listening on http://%s:%s", APP_NAME, host, port)
    print(f"{APP_NAME} listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()




