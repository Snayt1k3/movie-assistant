import argparse
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from jobs.tmdb_changes import sync_tmdb_changes
from jobs.tmdb_import import import_tmdb_catalog

JOBS = {
    "import_tmdb": import_tmdb_catalog,
    "sync_tmdb_changes": sync_tmdb_changes,
}


async def run_scheduler() -> None:
    scheduler = AsyncIOScheduler(timezone="UTC")
    # выгрузка TMDB за прошлый день готова к 8:00 UTC
    scheduler.add_job(import_tmdb_catalog, "cron", hour=9, max_instances=1, coalesce=True)
    # новые серии идущих сериалов должны попадать в календарь без большой задержки
    scheduler.add_job(sync_tmdb_changes, "cron", hour="*/6", max_instances=1, coalesce=True)
    scheduler.start()
    await asyncio.Event().wait()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    parser = argparse.ArgumentParser(description="Запустить планировщик или одну задачу")
    parser.add_argument("job", nargs="?", choices=JOBS, help="выполнить задачу один раз и выйти")
    parser.add_argument("--limit", type=int, help="сколько тайтлов каждого типа обработать")
    args = parser.parse_args()

    if args.job:
        asyncio.run(JOBS[args.job](limit=args.limit))
    else:
        asyncio.run(run_scheduler())


if __name__ == "__main__":
    main()
