import asyncio
from motiv_loader_bot import app as app_loader
from motiv_random_bot import app as app_random

async def main():
    await app_loader.initialize()
    await app_random.initialize()

    await app_loader.start()
    await app_random.start()

    # Важно: start_polling НЕ блокирует, можно вызывать обе
    await asyncio.gather(
        app_loader.updater.start_polling(),
        app_random.updater.start_polling()
    )

    # блокируем, чтобы не выйти сразу
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
