import asyncio
from app.services.telegram import send_telegram_message

async def main():
    await send_telegram_message(
        """
✅ Telegram Bot Test

If you receive this message,
your bot is working correctly.
"""
    )

asyncio.run(main())