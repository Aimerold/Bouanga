import httpx
from app.config import settings


async def send_telegram_message(message: str):
    url = (
        f"https://api.telegram.org/bot"
        f"{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)