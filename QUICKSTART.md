# Quick Start Guide

Быстрый старт за 5 минут.

## Установка и запуск

### 1. Скачать и установить

```powershell
git clone https://github.com/NohchiyBors/API-scada-TML.git
cd API-scada-TML
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Конфигурировать

```powershell
Copy-Item .env.example .env
# Отредактировать .env под вашу среду
notepad .env
```

**Минимальные параметры:**
```env
TML_SQL_SERVER=127.0.0.1,1433
TML_SQL_USER=your_user
TML_SQL_PASSWORD=your_password
TML_SQL_DATABASES=ProjectOWEN
```

### 3. Запустить

```powershell
python app.py
```

Вы должны увидеть:
```
2026-06-27 12:00:00 INFO tml-read-api listening on http://0.0.0.0:8787
```

### 4. Проверить

```bash
curl http://localhost:8787/health
```

Ответ:
```json
{"ok": true, "app": "tml-read-api", "time_utc": "..."}
```

## Первые запросы

### Health Check (без аутентификации)

```bash
curl http://localhost:8787/health
```

### Список баз данных (требует токен)

```bash
$token = "change-me-token"
$headers = @{ Authorization = "Bearer $token" }

Invoke-WebRequest -Headers $headers http://localhost:8787/api/databases | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### Список таблиц

```bash
Invoke-WebRequest -Headers $headers http://localhost:8787/api/ProjectOWEN/tables | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

### Примеры данных

```bash
Invoke-WebRequest -Headers $headers "http://localhost:8787/api/ProjectOWEN/tables/dbo.Events/sample?limit=10" | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

## Веб-интерфейс

**Настройки:** http://localhost:8787/admin
**Логи:** http://localhost:8787/admin/logs
**Статус:** http://localhost:8787/StatusProject

**Логин:** admin
**Пароль:** change-me

## Документация

| Документ | Для кого | Содержание |
|----------|----------|-----------|
| [README.md](README.md) | Все | Обзор проекта |
| [INSTALLATION.md](INSTALLATION.md) | DevOps | Подробная установка |
| [CONFIGURATION.md](CONFIGURATION.md) | DevOps | Все параметры конфигурации |
| [API.md](API.md) | Разработчики | Полная документация API |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Разработчики | Руководство разработчика |
| [DEPLOYMENT.md](DEPLOYMENT.md) | DevOps | Развёртывание в production |
| [SECURITY.md](SECURITY.md) | Все | Политика безопасности |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Все | Решение проблем |
| [CHANGELOG.md](CHANGELOG.md) | Все | История версий |

## Часто используемые команды

```powershell
# Активировать окружение
.\.venv\Scripts\Activate.ps1

# Деактивировать
deactivate

# Запустить API
python app.py

# Установить зависимости
pip install -r requirements.txt

# Просмотреть логи
Get-Content logs/app.log -Wait

# Посмотреть логи через браузер
Start-Process "http://localhost:8787/admin/logs"

# Остановить API (Ctrl+C в терминале где запущен API)
```

## Типичные проблемы

### Ошибка подключения к SQL Server

```powershell
# Проверить доступность
Test-NetConnection -ComputerName 127.0.0.1 -Port 1433

# Проверить параметры в .env
Get-Content .env | Select-String SQL
```

Подробнее в [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Ошибка аутентификации (401)

Добавить Bearer токен:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8787/api/databases
```

### Ошибка "Port already in use"

Изменить в `.env`:
```env
TML_API_PORT=8788
```

## Следующие шаги

1. Прочитать [INSTALLATION.md](INSTALLATION.md) для полной установки
2. Изучить [API.md](API.md) для описания всех эндпоинтов
3. Настроить [CONFIGURATION.md](CONFIGURATION.md) под вашу среду
4. Прочитать [SECURITY.md](SECURITY.md) перед production развёртыванием

## Контакты

- **Разработчик:** HSPhub.com
- **Заказчик:** astana.company
- **GitHub:** https://github.com/NohchiyBors/API-scada-TML
- **Лицензия:** MIT

---

**Нужна помощь?** Откройте issue на GitHub или посмотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
