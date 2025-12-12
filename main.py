import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.api_check import check_endpoints
from app.bot import format_status_message
from config import config
from logger import log


async def check_and_send_status(bot: Bot, chat_id: int):
    """Check API endpoints and send status to Telegram"""
    try:
        log.info("Starting API check")
        endpoints_status = await check_endpoints()
        success = sum(1 for d in endpoints_status.values()
                      if d["status"] == "Success")
        log.info(f"Check done: {success}/{len(endpoints_status)} OK")
        messages = format_status_message(endpoints_status)
        for message in messages:
            await bot.send_message(chat_id=chat_id, text=message)
            await asyncio.sleep(0.1)
        
    except Exception as e:
        log.error(f"Check failed: {e}")
        await bot.send_message(chat_id=chat_id, text=f"❌ Error checking endpoints: {str(e)}")


async def main():
    log.info("")
    bot = Bot(config.tgbot.token,
              default=DefaultBotProperties(parse_mode="HTML"))

    # chat_id = -559707673 # Телега Бот
    chat_id = -1002076414278 # Тестовый
    await check_and_send_status(bot, chat_id)
    # bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
