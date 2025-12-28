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

## Live URL

https://stream.paveltajdus.cz/

## API Endpoints

- `POST /api/register` - Registrace (vrací kód)
- `GET /api/stats?secret=ADMIN_SECRET` - Počet registrací
- `GET /api/export?secret=ADMIN_SECRET` - Export emailů (jeden na řádek)
- `GET /api/participants?secret=ADMIN_SECRET` - Export s jmény a kódy (JSON)
- `GET /wheel` - Losovací kolo

### Admin URLs (vyžadují ADMIN_SECRET)

```
https://stream.paveltajdus.cz/api/stats?secret=YOUR_SECRET
https://stream.paveltajdus.cz/api/export?secret=YOUR_SECRET
https://stream.paveltajdus.cz/api/participants?secret=YOUR_SECRET
https://stream.paveltajdus.cz/wheel
```

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
