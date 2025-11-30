import asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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


async def on_startup(bot: Bot, admin_ids: list[int]):
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id,
                                   "Hello, if you this, then you're admin!\n<b>/admin</b> - to see admin menu")
            await asyncio.sleep(0.05)
        except Exception:
            pass


async def on_scheduler(bot: Bot, chat_id: int):
    scheduler = AsyncIOScheduler()

    # Run immediately on startup
    await check_and_send_status(bot, chat_id)

    # Then schedule every 1 hour
    scheduler.add_job(
        check_and_send_status,
        "interval",
        hours=1,
        args=[bot, chat_id],
    )

    scheduler.start()


async def main():
    log.info("Bot starting")
    bot = Bot(config.tgbot.token,
              default=DefaultBotProperties(parse_mode="HTML"))

    chat_id = -559707673
    await on_scheduler(bot, chat_id)

    # Keep the bot running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
