# Installation Guide

Полное руководство по установке и настройке TML Read API.

## Требования

### Системные требования

- **ОС**: Windows 10/11, Windows Server 2016+
- **Python**: 3.10+
- **SQL Server**: 2016+
- **RAM**: минимум 512 МБ, рекомендуется 2+ ГБ
- **Диск**: минимум 1 ГБ свободного места

### Сетевые требования

- Доступ к SQL Server (по умолчанию `127.0.0.1:1433`)
- Открытый порт для API (по умолчанию `8787`)
- Интернет для установки Python пакетов (опционально, можно использовать оффлайн-режим)

## Пошаговая установка

### 1. Установка Python

Если Python не установлен:

```powershell
# Загрузить Python 3.14+ с https://www.python.org/downloads/
# или использовать Windows Package Manager
winget install Python.Python.3.14
```

Проверить версию:
```powershell
python --version
```

### 2. Клонирование репозитория

```powershell
git clone https://github.com/NohchiyBors/API-scada-TML.git
cd API-scada-TML
```

### 3. Создание виртуального окружения (рекомендуется)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Для выхода из окружения:
```powershell
deactivate
```

### 4. Установка зависимостей

```powershell
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Содержимое `requirements.txt`:
- `flask>=2.3.0` - веб-фреймворк
- `python-dotenv>=1.0.0` - работа с переменными окружения
- `pyodbc>=4.0.35` - подключение к SQL Server

### 5. Конфигурирование

Скопировать файл конфигурации:

```powershell
Copy-Item .env.example .env
```

Отредактировать `.env` с вашими параметрами (см. [CONFIGURATION.md](CONFIGURATION.md)).

### 6. Проверка установки

```powershell
python app.py
```

Проверить доступность API:
```powershell
Invoke-WebRequest http://127.0.0.1:8787/health
```

Ожидаемый ответ:
```json
{
  "ok": true,
  "app": "tml-read-api",
  "time_utc": "2026-06-27T..."
}
```

## Установка на Firebird (опционально)

Если вы используете Firebird вместо SQL Server:

```powershell
# Установить Firebird (https://www.firebirdsql.org/en/downloads/)
# Обновить .env:
# TML_FIREBIRD_DATABASES=alias=D:\path\to\database.fdb
# TML_FIREBIRD_ISQL=C:\Program Files\Firebird\Firebird_3_0\isql.exe
```

## Запуск как служба (Windows)

Создать батник для автоматического запуска:

```batch
REM run-service.cmd
@echo off
cd /d D:\Data\Repos\API
.\venv\Scripts\python app.py
```

Использовать инструмент вроде NSSM для регистрации как Windows Service:

```powershell
nssm install TML-Read-API "D:\Data\Repos\API\run-service.cmd"
nssm start TML-Read-API
```

## Запуск с Docker

Для dev-режима в Docker используйте готовые файлы `Dockerfile` и `docker-compose.dev.yml`.

### 1. Подготовка

Убедитесь, что Docker Desktop запущен.

```powershell
docker --version
docker compose version
```

### 2. Важно для SQL Server

В контейнере `127.0.0.1` указывает на сам контейнер, а не на хост.
Для локального SQL Server используется `host.docker.internal,1433`
(это уже задано в `docker-compose.dev.yml`).

### 3. Запуск

```powershell
docker compose -f docker-compose.dev.yml up --build -d
```

### 4. Проверка

```powershell
Invoke-WebRequest http://127.0.0.1:8787/health
```

### 5. Остановка

```powershell
docker compose -f docker-compose.dev.yml down
```

### 6. Логи контейнера

```powershell
docker compose -f docker-compose.dev.yml logs -f api
```

## Трубешутинг

### Ошибка подключения к SQL Server

```
pyodbc.Error: ('08001', '[08001] [Microsoft][ODBC Driver 17 for SQL Server]...
```

**Решение:**
- Проверить параметры подключения в `.env`
- Убедиться, что SQL Server запущен
- Проверить сетевую доступность: `Test-NetConnection 127.0.0.1 -p 1433`

### Ошибка "Port already in use"

```
OSError: [Errno 48] Address already in use
```

**Решение:**
- Изменить порт в `.env`: `TML_API_PORT=8788`
- Или убить процесс, занимающий порт

### Ошибка "pyodbc is not installed"

```
ModuleNotFoundError: No module named 'pyodbc'
```

**Решение:**
```powershell
pip install pyodbc
# Если установка не удалась, установить ODBC драйвер:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

Подробная диагностика в [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Следующие шаги

1. Прочитать [CONFIGURATION.md](CONFIGURATION.md) для полной конфигурации
2. Посмотреть [API.md](API.md) для описания эндпоинтов
3. Ознакомиться с [SECURITY.md](SECURITY.md) для безопасности в production
