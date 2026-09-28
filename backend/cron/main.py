import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # scheduler.add_job(deliver_notifications, "interval", minutes=1)
    scheduler.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
