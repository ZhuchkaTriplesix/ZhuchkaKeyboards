import asyncio
from aiogram import Bot, Dispatcher
from handlers import client
from config import cfg


async def main():
    bot = Bot(cfg.TOKEN)
    dp = Dispatcher()
    dp.include_routers(client.router)  # routers add
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Start error")
