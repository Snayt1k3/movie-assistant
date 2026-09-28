import asyncio

from aiogram import Bot, Dispatcher

from config import settings


async def main() -> None:
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
