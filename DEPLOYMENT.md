# Deployment Guide

## Prerequisites

- Python 3.10+
- SQL Server with ODBC Driver 17
- Windows or Linux with Python support

## Development Deployment

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/API-SCADA-TML.git
cd API-SCADA-TML
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file:
```env
TML_API_HOST=0.0.0.0
TML_API_PORT=8787
TML_SQL_SERVER=127.0.0.1,1433
TML_SQL_USER=tml_reader
TML_SQL_PASSWORD=your_password
TML_SQL_DATABASES=ProjectOWEN
TML_PROJECT_ROOT=D:\TML-Project\BiService
```

### 5. Run API
```bash
python app.py
```

API available at `http://localhost:8787`

## Production Deployment

### Windows Service

Create `install_service.bat`:
```batch
@echo off
cd D:\Data\Repos\API
"C:\Program Files\Python310\python.exe" -m pip install pywin32
"C:\Program Files\Python310\Scripts\pyinstaller.exe" --onefile app.py
sc create TML_API binPath="D:\Data\Repos\API\dist\app.exe"
sc start TML_API
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-windowsservercore
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8787
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t api-scada-tml:0.2.0 .
docker run -d -p 8787:8787 --env-file .env api-scada-tml:0.2.0
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name api.scada.local;

    location / {
        proxy_pass http://127.0.0.1:8787;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Monitoring

### Health Check
```bash
curl http://localhost:8787/health
```

### Logs
- Check application console output
- Review SQL Server error logs
- Monitor system event log

### Metrics
- Response time
- Database connection pool status
- Error rate
- Request throughput

## Backup & Recovery

1. **Database backups** - Configure SQL Server maintenance plans
2. **Configuration backups** - Backup `.env` file
3. **Code backups** - Use Git version control

## Troubleshooting

### Connection Issues
- Verify SQL Server is running
- Check firewall rules
- Validate connection string
- Check ODBC driver installation

### Performance Issues
- Monitor database query times
- Check SQL Server performance
- Review API logs
- Increase thread pool if needed

### API Won't Start
- Check Python version compatibility
- Verify all dependencies installed
- Review environment variables
- Check port availability
