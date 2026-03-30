import os
import asyncio
import logging

from rich.console import Console
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

from src.db.models import Base
from src.db.engine import localSession, engine

from src import router as main_router

logging.basicConfig(level=logging.INFO, filename="logs\\runtimeLog.log", filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
console = Console()
TOKEN = os.getenv("BOT")

async def startup():

    logging.info("The bot just has started")

    bot = Bot(TOKEN)
    dp = Dispatcher()

    dp["db_pool"] = localSession

    Base.metadata.create_all(engine)

    dp.include_router(main_router)

    console.print(f"[bold green]BOT ID: {bot.id}\n" \
                  f"BOT TOKEN: {TOKEN}[bold green]\n" \
                   "The bot is now ready to use!") 

    await bot.delete_webhook(True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(startup())