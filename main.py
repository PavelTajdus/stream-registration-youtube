import os
import secrets
import string
import asyncpg
import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Config
DATABASE_URL = os.getenv("DATABASE_URL")
POSTMARK_TOKEN = os.getenv("POSTMARK_API_TOKEN")
FROM_EMAIL = os.getenv("POSTMARK_FROM_EMAIL", "info@hotend.cz")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")


class Registration(BaseModel):
    name: str
    email: EmailStr
    newsletter: bool = False


def generate_code(length: int = 6) -> str:
    """Generuje unikátní kód pro ověření"""
    chars = string.ascii_uppercase + string.digits
    # Vynecháme podobné znaky O/0, I/1/L
    chars = chars.replace("O", "").replace("0", "").replace("I", "").replace("1", "").replace("L", "")
    return "".join(secrets.choice(chars) for _ in range(length))


async def get_db():
    return await asyncpg.connect(DATABASE_URL)


async def send_confirmation_email(email: str, name: str, code: str):
    """Pošle potvrzovací email přes Postmark"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.postmarkapp.com/email",
            headers={
                "X-Postmark-Server-Token": POSTMARK_TOKEN,
                "Content-Type": "application/json",
            },
            json={
                "From": FROM_EMAIL,
                "To": email,
                "Subject": "Registrace do soutěže - Poslední Stream Roku 2025",
                "HtmlBody": f"""
                <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;">
                    <h2>Ahoj {name}!</h2>
                    <p>Tvoje registrace do soutěže proběhla úspěšně.</p>
                    
                    <div style="background: #161616; color: #fff; padding: 24px; border-radius: 8px; margin: 24px 0; text-align: center;">
                        <p style="margin: 0 0 8px 0; font-size: 14px; opacity: 0.7;">Tvůj ověřovací kód</p>
                        <p style="margin: 0; font-size: 32px; font-weight: bold; letter-spacing: 4px;">{code}</p>
                    </div>
                    
                    <p><strong>Jak to funguje:</strong></p>
                    <ol>
                        <li>Přijď na stream <strong>29. 12. 2025 v 19:00</strong></li>
                        <li>Pokud budeš vylosován/a, ozvu se v chatu</li>
                        <li>Napiš do chatu svůj ověřovací kód</li>
                        <li>Výhra je tvoje!</li>
                    </ol>
                    
                    <p style="margin-top: 24px;">
                        <a href="https://youtube.com/live/A5nt3ERlLVk" style="background: #000; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                            Odkaz na stream
                        </a>
                    </p>
                    
                    <p style="margin-top: 32px; font-size: 14px; opacity: 0.6;">
                        Hodně štěstí!<br>
                        Pavel Tajduš / Hotend.cz
                    </p>
                </div>
                """,
                "TextBody": f"""
Ahoj {name}!

Tvoje registrace do soutěže proběhla úspěšně.

Tvůj ověřovací kód: {code}

Jak to funguje:
1. Přijď na stream 29. 12. 2025 v 19:00
2. Pokud budeš vylosován/a, ozvu se v chatu
3. Napiš do chatu svůj ověřovací kód
4. Výhra je tvoje!

Odkaz na stream: https://youtube.com/live/A5nt3ERlLVk

Hodně štěstí!
Pavel Tajduš / Hotend.cz
                """,
            },
        )
        
        if response.status_code != 200:
            print(f"Postmark error: {response.text}")


@app.post("/api/register")
async def register(data: Registration):
    code = generate_code()
    
    conn = await get_db()
    try:
        # Zkus vložit, pokud email existuje, vrať existující kód
        existing = await conn.fetchrow(
            "SELECT code FROM registrations WHERE email = $1", 
            data.email
        )
        
        if existing:
            return {
                "success": True,
                "message": "Už jsi registrován/a",
                "code": existing["code"]
            }
        
        await conn.execute(
            """
            INSERT INTO registrations (email, name, code, newsletter)
            VALUES ($1, $2, $3, $4)
            """,
            data.email,
            data.name,
            code,
            data.newsletter,
        )
        
        # Pošli email
        await send_confirmation_email(data.email, data.name, code)
        
        return {
            "success": True,
            "message": "Registrace úspěšná",
            "code": code
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Chyba při registraci")
    finally:
        await conn.close()


@app.get("/api/stats")
async def stats(secret: str = None, x_admin_secret: str = Header(default=None)):
    """Pro tebe - kolik lidí se registrovalo"""
    token = secret or x_admin_secret
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = await get_db()
    try:
        count = await conn.fetchval("SELECT COUNT(*) FROM registrations")
        return {"registrations": count}
    finally:
        await conn.close()


@app.get("/api/export", response_class=PlainTextResponse)
async def export(secret: str = None, x_admin_secret: str = Header(default=None)):
    """Pro losování - export emailů (jeden email na řádek)"""
    token = secret or x_admin_secret
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = await get_db()
    try:
        rows = await conn.fetch("SELECT email FROM registrations ORDER BY created_at")
        emails = [row["email"] for row in rows]
        return "\n".join(emails)
    finally:
        await conn.close()


@app.get("/api/participants")
async def participants(secret: str = None, x_admin_secret: str = Header(default=None)):
    """Pro losovací kolo - export s kódy"""
    token = secret or x_admin_secret
    if token != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = await get_db()
    try:
        rows = await conn.fetch("SELECT email, name, code FROM registrations ORDER BY created_at")
        return [dict(r) for r in rows]
    finally:
        await conn.close()


# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/wheel")
async def wheel():
    return FileResponse("static/wheel.html")
