# Configuration Guide

Полная документация по конфигурированию TML Read API через переменные окружения.

## Обзор

Все параметры API хранятся в файле `.env` и могут быть изменены через:
1. Редактирование файла `.env` вручную
2. Веб-интерфейс `/admin` (требует перезагрузки для некоторых параметров)
3. Переменные окружения ОС

## API Configuration

### TML_API_HOST

**Тип:** string
**По умолчанию:** `0.0.0.0`
**Описание:** Адрес для привязки API сервера.

- `0.0.0.0` - слушать на всех интерфейсах
- `127.0.0.1` - только локальный доступ
- `192.168.1.100` - привязать к конкретному интерфейсу

**Пример:**
```env
TML_API_HOST=0.0.0.0
```

**Требует перезагрузку:** Да

---

### TML_API_PORT

**Тип:** integer
**По умолчанию:** `8787`
**Диапазон:** 1-65535
**Описание:** Порт, на котором слушает API.

**Пример:**
```env
TML_API_PORT=8787
```

**Требует перезагрузку:** Да

---

### TML_API_CORS_ORIGIN

**Тип:** string
**По умолчанию:** `*`
**Описание:** CORS Origin для кроссдоменных запросов.

- `*` - разрешить все источники
- `http://localhost:3000` - конкретный источник
- `http://localhost:3000, http://example.com` - несколько источников

**Пример:**
```env
TML_API_CORS_ORIGIN=http://localhost:3000
```

**Требует перезагрузку:** Да

---

## SQL Server Configuration

### TML_SQL_DRIVER

**Тип:** string
**По умолчанию:** `ODBC Driver 17 for SQL Server`
**Описание:** ODBC драйвер для подключения к SQL Server.

**Доступные опции:**
- `ODBC Driver 17 for SQL Server` (рекомендуется)
- `ODBC Driver 18 for SQL Server` (более новый)
- `SQL Server` (базовый, часто не работает)

**Установка драйвера:**
```powershell
# Скачать с https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
# или использовать Package Manager
choco install odbc-driver-17-for-sql-server
```

**Пример:**
```env
TML_SQL_DRIVER=ODBC Driver 17 for SQL Server
```

---

### TML_SQL_SERVER

**Тип:** string
**По умолчанию:** `127.0.0.1,1433`
**Описание:** Адрес и порт SQL Server.

**Форматы:**
- `127.0.0.1,1433` - IP адрес и порт
- `localhost,1433` - имя хоста
- `server.example.com,1433` - удалённый сервер
- `(local)` - локальный экземпляр (Windows)

**Пример:**
```env
TML_SQL_SERVER=192.168.1.50,1433
```

---

### TML_SQL_USER

**Тип:** string
**По умолчанию:** (пусто - использует Windows authentication)
**Описание:** Имя пользователя для подключения к SQL Server.

Если не задан, API использует Windows authentication (более безопасно).

**Пример:**
```env
TML_SQL_USER=tml_reader
```

---

### TML_SQL_PASSWORD

**Тип:** string (sensitive)
**По умолчанию:** (пусто)
**Описание:** Пароль для SQL Server пользователя.

⚠️ **Безопасность:** Никогда не коммитить пароль в Git!

**Пример:**
```env
TML_SQL_PASSWORD=your_secure_password_here
```

---

### TML_SQL_DATABASES

**Тип:** string (comma-separated)
**По умолчанию:** `ProjectOWEN`
**Описание:** Список разрешённых баз данных.

API будет отказывать в доступе к БД, которых нет в этом списке.

**Пример:**
```env
TML_SQL_DATABASES=ProjectOWEN,ProjectTest,ProjectArchive
```

---

### TML_SQL_TIMEOUT

**Тип:** integer (seconds)
**По умолчанию:** `10`
**Диапазон:** 1-300
**Описание:** Таймаут для SQL запросов.

**Пример:**
```env
TML_SQL_TIMEOUT=15
```

---

### TML_DATABASE_READ_ONLY

**Тип:** boolean
**По умолчанию:** `true`
**Описание:** Включить режим read-only для SQL Server.

Когда включено, соединение использует ApplicationIntent=ReadOnly и API отказывает в любых write операциях.

**Значения:** `true`, `false`

**Пример:**
```env
TML_DATABASE_READ_ONLY=true
```

---

## Firebird Configuration

### TML_FIREBIRD_ISQL

**Тип:** string (path)
**По умолчанию:** `C:\Program Files\Firebird\Firebird_3_0\isql.exe`
**Описание:** Путь к исполняемому файлу isql.exe (Firebird command-line tool).

**Установка Firebird:**
```powershell
# Загрузить с https://www.firebirdsql.org/en/downloads/
# или через Package Manager
choco install firebird
```

**Пример:**
```env
TML_FIREBIRD_ISQL=C:\Program Files\Firebird\Firebird_4_0\isql.exe
```

---

### TML_FIREBIRD_DATABASES

**Тип:** string (semicolon-separated aliases)
**По умолчанию:** (пусто)
**Описание:** Список Firebird баз данных в формате `alias=path`.

**Формат:**
```env
TML_FIREBIRD_DATABASES=users=D:\TML-Project\BiService\Base\USERS.FDB;projects=D:\TML-Project\BiService\Base\PROJECTS.FDB
```

**Пример:**
```env
TML_FIREBIRD_DATABASES=users=D:\TML-Project\BiService\Base\USERS.FDB
```

---

### TML_FIREBIRD_USER

**Тип:** string
**По умолчанию:** `sysdba`
**Описание:** Пользователь для подключения к Firebird.

**Пример:**
```env
TML_FIREBIRD_USER=sysdba
```

---

### TML_FIREBIRD_PASSWORD

**Тип:** string (sensitive)
**По умолчанию:** `masterkey`
**Описание:** Пароль для Firebird пользователя.

⚠️ **Безопасность:** Использовать сложные пароли в production!

**Пример:**
```env
TML_FIREBIRD_PASSWORD=secure_password_123
```

---

## Security Configuration

### TML_REQUIRE_API_TOKEN

**Тип:** boolean
**По умолчанию:** `true`
**Описание:** Требовать Bearer токен для API запросов.

Когда включено, все запросы к `/api/*` требуют заголовок `Authorization: Bearer TOKEN`.

**Значения:** `true`, `false`

**Пример:**
```env
TML_REQUIRE_API_TOKEN=true
```

---

### TML_API_TOKENS

**Тип:** string (comma-separated)
**По умолчанию:** (пусто - используется из .env)
**Описание:** Допустимые Bearer токены для API.

Можно вводить несколько токенов через запятую.

⚠️ **Безопасность:** Использовать длинные случайные токены!

**Генерирование токена:**
```powershell
$token = -join ((0..31) | ForEach-Object { [char][byte](Get-Random -InputObject (0..9 + 'a'..'f') | ForEach-Object { [byte]$_ }) })
```

**Пример:**
```env
TML_API_TOKENS=change-me-token,another-change-me-token
```

---

### TML_ALLOWED_IPS

**Тип:** string (comma/CIDR-separated)
**По умолчанию:** `127.0.0.1,::1,10.100.100.10`
**Описание:** IP адреса, которым разрешен доступ к API.

**Форматы:**
- `127.0.0.1` - конкретный IP
- `10.100.100.0/24` - CIDR диапазон
- `::1` - IPv6 localhost
- `2001:db8::/32` - IPv6 диапазон

**Пример:**
```env
TML_ALLOWED_IPS=127.0.0.1,::1,10.100.100.0/24,192.168.1.50
```

---

### TML_ADMIN_USER

**Тип:** string
**По умолчанию:** `admin`
**Описание:** Имя пользователя для HTTP Basic Auth веб-интерфейса.

**Пример:**
```env
TML_ADMIN_USER=admin
```

---

### TML_ADMIN_PASSWORD

**Тип:** string (sensitive)
**По умолчанию:** (пусто)
**Описание:** Пароль для веб-интерфейса.

⚠️ **Безопасность:** Использовать сильный пароль!

**Пример:**
```env
TML_ADMIN_PASSWORD=SecurePassword123!@#
```

---

## Logging Configuration

### TML_LOG_LEVEL

**Тип:** string
**По умолчанию:** `INFO`
**Описание:** Уровень логирования.

**Уровни (от наименьшего к наибольшему):**
- `DEBUG` - подробная диагностическая информация
- `INFO` - информационные сообщения
- `WARNING` - предупреждения (рекомендуется для production)
- `ERROR` - ошибки и исключения

**Пример:**
```env
TML_LOG_LEVEL=INFO
```

---

### TML_LOG_DIR

**Тип:** string (path)
**По умолчанию:** `logs`
**Описание:** Директория для log-файлов.

Путь может быть относительным (от папки приложения) или абсолютным.

**Пример:**
```env
TML_LOG_DIR=logs
# или
TML_LOG_DIR=D:\Logs\TML-API
```

---

### TML_APP_LOG

**Тип:** string (path)
**По умолчанию:** `logs/app.log`
**Описание:** Файл логов приложения.

**Пример:**
```env
TML_APP_LOG=logs/app.log
```

---

### TML_ACCESS_LOG

**Тип:** string (path)
**По умолчанию:** `logs/access.log`
**Описание:** Файл логов доступа (все HTTP запросы).

**Пример:**
```env
TML_ACCESS_LOG=logs/access.log
```

---

## Project Configuration

### TML_PROJECT_ROOT

**Тип:** string (path)
**По умолчанию:** `D:\TML-Project\BiService`
**Описание:** Корневая директория проекта TML.

Используется для контекста и может быть показана в статус-странице.

**Пример:**
```env
TML_PROJECT_ROOT=D:\TML-Project\BiService
```

---

## Пример полного .env файла

```env
# API Configuration
TML_API_HOST=0.0.0.0
TML_API_PORT=8787
TML_API_CORS_ORIGIN=*

# SQL Server
TML_SQL_DRIVER=ODBC Driver 17 for SQL Server
TML_SQL_SERVER=127.0.0.1,1433
TML_SQL_USER=tml_reader
TML_SQL_PASSWORD=YourSecurePassword
TML_SQL_DATABASES=ProjectOWEN,ProjectTest
TML_SQL_TIMEOUT=10
TML_DATABASE_READ_ONLY=true

# Firebird (опционально)
TML_FIREBIRD_ISQL=C:\Program Files\Firebird\Firebird_3_0\isql.exe
TML_FIREBIRD_DATABASES=users=D:\TML-Project\BiService\Base\USERS.FDB
TML_FIREBIRD_USER=sysdba
TML_FIREBIRD_PASSWORD=masterkey

# Security
TML_REQUIRE_API_TOKEN=true
TML_API_TOKENS=token_1,token_2,token_3
TML_ALLOWED_IPS=127.0.0.1,::1,10.100.100.0/24
TML_ADMIN_USER=admin
TML_ADMIN_PASSWORD=AdminPassword123

# Logging
TML_LOG_LEVEL=INFO
TML_LOG_DIR=logs
TML_APP_LOG=logs/app.log
TML_ACCESS_LOG=logs/access.log

# Project
TML_PROJECT_ROOT=D:\TML-Project\BiService
```

---

## Лучшие практики конфигурации

### Development

```env
TML_LOG_LEVEL=DEBUG
TML_REQUIRE_API_TOKEN=false
TML_ALLOWED_IPS=127.0.0.1,::1
TML_SQL_DATABASES=ProjectOWEN
```

### Staging

```env
TML_LOG_LEVEL=INFO
TML_REQUIRE_API_TOKEN=true
TML_ALLOWED_IPS=10.100.100.0/24,192.168.1.0/24
TML_DATABASE_READ_ONLY=true
```

### Production

```env
TML_LOG_LEVEL=WARNING
TML_REQUIRE_API_TOKEN=true
TML_ALLOWED_IPS=10.100.100.10,10.100.100.11
TML_DATABASE_READ_ONLY=true
TML_API_TOKENS=<strong_random_token_1>,<strong_random_token_2>
TML_ADMIN_PASSWORD=<complex_password>
```

---

Подробная информация о безопасности в [SECURITY.md](SECURITY.md).
