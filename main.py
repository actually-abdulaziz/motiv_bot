import asyncio
from motiv_loader_bot import app as app_loader
from motiv_random_bot import app as app_random

async def main():
    await asyncio.gather(
        app_loader.run_polling(),
        app_random.run_polling()
    )

if __name__ == "__main__":
    asyncio.run(main())