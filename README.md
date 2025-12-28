# Stream Soutěž 2025

Jednoduchá registrační stránka pro stream soutěž s ověřovacími kódy.

## Setup

1. Vytvoř `.env` soubor podle `.env.example`

2. Spusť SQL schema v Neon:
```sql
-- Spusť obsah schema.sql
```

3. Instalace a spuštění:
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## API Endpoints

- `POST /api/register` - Registrace (vrací kód)
- `GET /api/stats` - Počet registrací
- `GET /api/export` - Export všech registrací pro losování

## Deploy

Pro produkci doporučuji Railway, Fly.io nebo Render - všechny podporují Python a mají free tier.

### Railway (nejjednodušší)
```bash
railway login
railway init
railway up
```

### Docker
```bash
docker build -t stream-soutez .
docker run -p 8000:8000 --env-file .env stream-soutez
```
