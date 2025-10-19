# Guia de Deploy

Este documento descreve como fazer o deploy da API Books to Scrape em diferentes plataformas.

## Índice

1. [Deploy Local](#deploy-local)
2. [Deploy com Docker](#deploy-com-docker)
3. [Deploy no Render](#deploy-no-render)
4. [Deploy no Heroku](#deploy-no-heroku)
5. [Deploy no Fly.io](#deploy-no-flyio)
6. [Deploy no Railway](#deploy-no-railway)

---

## Deploy Local

### Requisitos

- Python 3.10+
- pip

### Passos

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/books-scraper-api.git
cd books-scraper-api

# 2. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. (Opcional) Executar scraper para obter dados
python scripts/scraper.py

# 5. Iniciar API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse: `http://localhost:8000/docs`

---

## Deploy com Docker

### Requisitos

- Docker 20+
- Docker Compose (opcional)

### Opção 1: Docker simples

```bash
# Build
docker build -t books-api .

# Run
docker run -d -p 8000:8000 --name books-api books-api

# Logs
docker logs -f books-api

# Stop
docker stop books-api
docker rm books-api
```

### Opção 2: Docker Compose

```bash
# Iniciar todos os serviços (API + Redis)
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Rebuild
docker-compose up -d --build
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - REDIS_HOST=redis
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

---

## Deploy no Render

### Passos

1. **Criar conta em [render.com](https://render.com)**

2. **Conectar repositório GitHub**

3. **Criar novo Web Service**
   - Name: `books-api`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

4. **Configurar variáveis de ambiente** (opcional)
   ```
   ENVIRONMENT=production
   ```

5. **Deploy automático**
   - Render fará deploy automaticamente a cada push

### Arquivo render.yaml

```yaml
services:
  - type: web
    name: books-api
    env: python
    plan: free
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

### Executar Scraper no Render

```bash
# Adicionar Cron Job no Render
# Schedule: 0 2 * * *
# Command: python scripts/scraper.py
```

**URL Final:** `https://books-api-xxxx.onrender.com`

---

## Deploy no Heroku

### Requisitos

- Conta no [Heroku](https://heroku.com)
- Heroku CLI instalado

### Passos

```bash
# 1. Login
heroku login

# 2. Criar app
heroku create books-api-production

# 3. Adicionar buildpack
heroku buildpacks:set heroku/python

# 4. Configurar variáveis
heroku config:set ENVIRONMENT=production

# 5. Deploy
git push heroku main

# 6. Abrir app
heroku open

# 7. Ver logs
heroku logs --tail

# 8. Escalar
heroku ps:scale web=1
```

### Procfile

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### runtime.txt

```
python-3.11.0
```

### Adicionar Scheduler para Scraper

```bash
# Instalar addon
heroku addons:create scheduler:standard

# Abrir dashboard
heroku addons:open scheduler

# Adicionar job:
# Command: python scripts/scraper.py
# Frequency: Daily at 2:00 AM UTC
```

**URL Final:** `https://books-api-production.herokuapp.com`

---

## Deploy no Fly.io

### Requisitos

- Conta no [Fly.io](https://fly.io)
- Flyctl CLI instalado

### Passos

```bash
# 1. Login
flyctl auth login

# 2. Lançar app
flyctl launch

# Configuração interativa:
# - App name: books-api
# - Region: escolher mais próxima
# - Database: No
# - Deploy now: Yes

# 3. Ver status
flyctl status

# 4. Ver logs
flyctl logs

# 5. Abrir app
flyctl open

# 6. Escalar (se necessário)
flyctl scale count 2
```

### fly.toml (gerado automaticamente)

```toml
app = "books-api"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.http_checks]]
    interval = 10000
    grace_period = "5s"
    method = "get"
    path = "/health"
    protocol = "http"
    timeout = 2000
```

**URL Final:** `https://books-api.fly.dev`

---

## Deploy no Railway

### Passos

1. **Criar conta em [railway.app](https://railway.app)**

2. **Criar novo projeto**
   - New Project → Deploy from GitHub repo

3. **Configurar**
   - Root Directory: `/`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

4. **Configurar domínio**
   - Settings → Generate Domain

5. **Deploy automático**
   - A cada push no GitHub

**URL Final:** `https://books-api-production-xxxx.up.railway.app`

---

## Configurações Recomendadas de Produção

### Variáveis de Ambiente

```bash
ENVIRONMENT=production
API_HOST=0.0.0.0
REDIS_HOST=seu-redis-host
SENTRY_DSN=seu-sentry-dsn  # Para error tracking
```

### Gunicorn (alternativa ao Uvicorn)

```bash
# Instalar
pip install gunicorn

# Procfile
web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT
```

### Configuração de Workers

```python
# Para 1GB RAM: 2-4 workers
# Para 2GB RAM: 4-8 workers
# Fórmula: (2 x CPU cores) + 1

workers = multiprocessing.cpu_count() * 2 + 1
```

---

## Monitoramento

### Sentry (Error Tracking)

```bash
pip install sentry-sdk[fastapi]
```

```python
# api/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=1.0,
)
```

### New Relic (APM)

```bash
pip install newrelic

# Procfile
web: newrelic-admin run-program uvicorn api.main:app
```

### Prometheus Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

---

## SSL/HTTPS

Todas as plataformas mencionadas fornecem SSL/HTTPS automaticamente:

- ✅ Render: SSL automático
- ✅ Heroku: SSL automático
- ✅ Fly.io: SSL automático
- ✅ Railway: SSL automático

---

## Backup e Disaster Recovery

### Backup dos Dados

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp data/books.csv backups/books_$DATE.csv

# Enviar para S3
aws s3 cp data/books.csv s3://seu-bucket/backups/books_$DATE.csv
```

### Cron Job (servidor Unix)

```bash
crontab -e

# Backup diário às 3:00 AM
0 3 * * * /path/to/backup.sh
```

---

## Troubleshooting

### Erro: Port already in use

```bash
# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Erro: Module not found

```bash
pip install -r requirements.txt --upgrade
```

### API não responde

```bash
# Verificar logs
docker logs books-api
heroku logs --tail
flyctl logs
```

### Out of Memory

```bash
# Reduzir workers
# Aumentar plano de hosting
# Implementar cache Redis
```

---

## Checklist de Deploy

- [ ] Testes passando (`pytest`)
- [ ] Lint ok (`flake8`)
- [ ] `requirements.txt` atualizado
- [ ] Variáveis de ambiente configuradas
- [ ] Health check endpoint funcionando
- [ ] Dados do scraper disponíveis
- [ ] SSL/HTTPS ativo
- [ ] Domínio configurado
- [ ] Monitoramento ativo
- [ ] Backup configurado
- [ ] Documentação atualizada

---

## Suporte

Para problemas ou dúvidas:
- Abrir issue no GitHub
- Consultar documentação da plataforma
- Verificar logs de erro

