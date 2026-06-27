# Troubleshooting Guide

Решение типичных проблем при работе с TML Read API.

## Connection Issues

### SQL Server Connection Failed

**Ошибка:**
```
pyodbc.DatabaseError: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]
[SQL Server]Unable to complete login process before timeout expired.')
```

**Причины и решения:**

1. **SQL Server не запущен**
   ```powershell
   # Проверить статус службы
   Get-Service | Where-Object { $_.Name -like "*SQL*" } | Format-Table

   # Запустить SQL Server
   Start-Service MSSQLServer
   ```

2. **Неверный адрес/порт**
   ```powershell
   # Проверить доступность
   Test-NetConnection -ComputerName 127.0.0.1 -Port 1433

   # Узнать реальный порт SQL Server
   # Открыть SQL Server Configuration Manager
   # Зайти в SQL Server Network Configuration -> Protocols for MSSQLSERVER
   ```

3. **Неверные credentials**
   ```powershell
   # Проверить пользователя SQL Server
   # Открыть SQL Server Management Studio (SSMS)
   # Проверить существование пользователя и его права
   ```

4. **ODBC драйвер не установлен**
   ```powershell
   # Проверить установленные драйверы
   Get-OdbcDriver

   # Установить ODBC Driver 17
   # https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   ```

---

### Port Already in Use

**Ошибка:**
```
OSError: [WinError 10048] Only one usage of each socket address (protocol/IP/port) is normally permitted
```

**Решения:**

1. **Изменить порт в .env**
   ```env
   TML_API_PORT=8788
   ```

2. **Найти и остановить процесс, занимающий порт**
   ```powershell
   # Найти процесс на порту 8787
   netstat -ano | Select-String 8787

   # Kill процесс (замените PID)
   Stop-Process -Id <PID> -Force
   ```

3. **Проверить, не запущен ли уже API**
   ```powershell
   Get-Process python | Where-Object { $_.CommandLine -like "*app.py*" }
   ```

---

### Permission Denied

**Ошибка:**
```
PermissionError: [Errno 13] Permission denied: 'logs/app.log'
```

**Решения:**

1. **Проверить права на директорию логов**
   ```powershell
   # Создать директорию если её нет
   New-Item -ItemType Directory -Path logs -Force

   # Дать полные права текущему пользователю
   icacls "D:\Data\Repos\API\logs" /grant:r "$($env:USERNAME):(F)" /t
   ```

2. **Запустить с правами администратора**
   ```powershell
   # Если текущий пользователь не имеет прав
   Start-Process python -ArgumentList "app.py" -Verb RunAs
   ```

---

## Authentication Issues

### 401 Unauthorized

**Ошибка:**
```json
{"error": "api_token_required"}
```

**Решения:**

1. **Добавить Bearer токен**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8787/api/databases
   ```

2. **Проверить токен в .env**
   ```env
   TML_REQUIRE_API_TOKEN=true
   TML_API_TOKENS=change-me-token
   ```

3. **Отключить требование токена для разработки**
   ```env
   TML_REQUIRE_API_TOKEN=false
   ```
   ⚠️ **Только для развития!**

4. **Сгенерировать новый токен**
   ```powershell
   $token = -join ((0..31) | ForEach-Object { [char][0x0..0xF | Get-Random] })
   Write-Host $token
   ```

---

### 403 Forbidden (IP not allowed)

**Ошибка:**
```json
{"error": "ip_not_allowed"}
```

**Решения:**

1. **Добавить ваш IP в белый список**
   ```env
   # Получить текущий IP
   (Invoke-WebRequest -Uri "http://127.0.0.1:8787/StatusProject" -Headers @{ Authorization = "Bearer TOKEN" }
   ).Content | ConvertFrom-Json | Select-Object -ExpandProperty security | Select-Object client_ip

   # Добавить в .env
   TML_ALLOWED_IPS=127.0.0.1,::1,YOUR_IP
   ```

2. **Использовать CIDR диапазон**
   ```env
   TML_ALLOWED_IPS=127.0.0.1,::1,10.100.100.0/24
   ```

3. **Проверить через веб-интерфейс /admin**
   - Открыть http://localhost:8787/admin
   - Ввести admin/password
   - Скопировать свой IP из информации по TML_ALLOWED_IPS

---

### Admin UI Login Failed

**Ошибка:**
```
HTTP 401 Unauthorized
```

**Решения:**

1. **Проверить credentials**
   ```env
   TML_ADMIN_USER=admin
   TML_ADMIN_PASSWORD=change-me
   ```

2. **Проверить в браузере правильно ввести пароль**
   - Часто пароль скопирован с пробелами
   - Убедиться, что CapsLock выключен

3. **Сбросить пароль**
   ```env
   TML_ADMIN_PASSWORD=NewPassword123
   ```

---

## API Errors

### 404 Not Found (Database)

**Ошибка:**
```json
{"error": "database_not_found"}
```

**Решение:**
```env
# Добавить БД в список разрешённых
TML_SQL_DATABASES=ProjectOWEN,ProjectTest
```

Затем перезагрузить API.

---

### 404 Not Found (Table)

**Ошибка:**
```
GET /api/ProjectOWEN/tables/invalid.table/sample
{"error": "table_not_found"}
```

**Решение:**

1. **Проверить существование таблицы**
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8787/api/ProjectOWEN/tables
   ```

2. **Используйте полное имя schema.table**
   ```bash
   # Правильно
   /api/ProjectOWEN/tables/dbo.Events/sample

   # Неправильно (забыли schema)
   /api/ProjectOWEN/tables/Events/sample
   ```

---

### 500 Server Error

**Ошибка:**
```json
{"error": "internal_error"}
```

**Решения:**

1. **Проверить логи**
   ```powershell
   # Веб-интерфейс
   http://localhost:8787/admin/logs

   # Или файл
   Get-Content logs/app.log | Select-Object -Last 50
   ```

2. **Проверить подключение к БД**
   ```bash
   curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8787/api/databases
   ```

3. **Увеличить таймаут для больших запросов**
   ```env
   TML_SQL_TIMEOUT=30
   ```

4. **Проверить лимит на выборку**
   ```bash
   # Ошибка: лимит > 1000
   /api/ProjectOWEN/tables/dbo.Events/sample?limit=5000

   # Исправление
   /api/ProjectOWEN/tables/dbo.Events/sample?limit=1000
   ```

---

## Performance Issues

### Slow Queries

**Признак:** Запросы выполняются очень долго.

**Решения:**

1. **Уменьшить лимит данных**
   ```bash
   # Вместо
   curl "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=1000"

   # Использовать
   curl "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=100"
   ```

2. **Проверить индексы в SQL Server**
   ```sql
   -- Найти таблицы без индексов
   SELECT * FROM sys.tables t
   LEFT JOIN sys.indexes i ON t.object_id = i.object_id
   WHERE i.object_id IS NULL
   ```

3. **Проверить статистику**
   ```sql
   DBCC SHOWCONTIG (tableid) WITH TABLERESULTS
   ```

---

### High Memory Usage

**Признак:** API потребляет много памяти.

**Решения:**

1. **Ограничить размер выборки**
   ```env
   # В коде: максимум limit=1000
   ```

2. **Перезагружать API периодически**
   ```powershell
   # Создать задачу для перезагрузки каждый день
   Register-ScheduledTask -TaskName "Restart TML API" `
     -Trigger (New-ScheduledTaskTrigger -Daily -At 3AM) `
     -Action (New-ScheduledTaskAction -Execute "D:\restart-api.bat")
   ```

3. **Использовать потоковую обработку для больших данных**
   - Планируется в следующих версиях

---

## Firebird Issues

### Firebird Database Not Found

**Ошибка:**
```
Error: Firebird database not found: users
```

**Решения:**

1. **Проверить путь к файлу БД**
   ```env
   TML_FIREBIRD_DATABASES=users=D:\TML-Project\BiService\Base\USERS.FDB
   ```

2. **Проверить существование файла**
   ```powershell
   Test-Path "D:\TML-Project\BiService\Base\USERS.FDB"
   ```

3. **Проверить путь к isql.exe**
   ```env
   TML_FIREBIRD_ISQL=C:\Program Files\Firebird\Firebird_3_0\isql.exe
   ```

---

### Firebird Connection Failed

**Ошибка:**
```
Error connecting to Firebird database
```

**Решения:**

1. **Проверить доступность файла**
   ```powershell
   Get-Item "D:\TML-Project\BiService\Base\USERS.FDB"
   ```

2. **Проверить права доступа**
   ```powershell
   icacls "D:\TML-Project\BiService\Base\USERS.FDB"
   ```

3. **Проверить credentials**
   ```env
   TML_FIREBIRD_USER=sysdba
   TML_FIREBIRD_PASSWORD=masterkey
   ```

---

## Installation Issues

### pyodbc Installation Failed

**Ошибка:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Решение:**
1. Установить Visual C++ Build Tools
2. Или использовать wheel версию:
   ```bash
   pip install --only-binary :all: pyodbc
   ```

---

### Python Module Not Found

**Ошибка:**
```
ModuleNotFoundError: No module named 'flask'
```

**Решения:**

1. **Установить зависимости**
   ```bash
   pip install -r requirements.txt
   ```

2. **Проверить активацию venv**
   ```powershell
   # Должно показать путь к venv
   python -c "import sys; print(sys.prefix)"

   # Если нет, активировать
   .\.venv\Scripts\Activate.ps1
   ```

3. **Переустановить пакеты**
   ```bash
   pip install --force-reinstall -r requirements.txt
   ```

---

## Logging Issues

### Logs Not Written

**Причины:**

1. **Директория логов не существует**
   ```powershell
   New-Item -ItemType Directory -Path logs -Force
   ```

2. **Нет прав на запись**
   ```powershell
   icacls "D:\Data\Repos\API\logs" /grant:r "$($env:USERNAME):(F)" /t
   ```

3. **Путь в .env неправильный**
   ```env
   # Проверить
   TML_LOG_DIR=logs
   TML_APP_LOG=logs/app.log
   TML_ACCESS_LOG=logs/access.log
   ```

---

### Too Many Log Files

**Решение:** Архивировать старые логи

```powershell
# Архивировать логи старше 30 дней
Get-ChildItem logs/ -Filter "*.log" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
  ForEach-Object {
    Compress-Archive -Path $_.FullName -DestinationPath "$($_.FullName).zip"
    Remove-Item $_.FullName
  }
```

---

## Getting Help

### Сбор информации для отладки

Когда сообщаете об ошибке:

```powershell
# Получить всю информацию о системе
Write-Host "=== Python ==="
python --version
pip list | Select-String "flask|pyodbc|python-dotenv"

Write-Host "`n=== Environment ==="
Get-Content .env | Select-String -Pattern "^TML" | Select-String -NotMatch PASSWORD

Write-Host "`n=== Recent Logs ==="
Get-Content logs/app.log | Select-Object -Last 20

Write-Host "`n=== Health Check ==="
Invoke-WebRequest http://localhost:8787/health | Select-Object StatusCode
```

### Контактная информация

- **GitHub Issues:** https://github.com/NohchiyBors/API-scada-TML/issues
- **Security Issues:** см. SECURITY.md
- **Разработчик:** HSPhub.com
- **Заказчик:** astana.company

---

**Не нашли решение?** Создайте новый issue на GitHub с подробным описанием и информацией из раздела выше.
