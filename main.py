import asyncio

import mongoengine

from src.framework.CNPI_scraper.models.enums import Status
from src.scrapers.komputronik.scrape import init_scraper, scrape_images
from src.utils.logger import logger
from src.scrapers.komputronik.models import Product, Image
from config.config import assets_folder
mongoengine.connect("quuga")


SCRAPE_FRESH = True


async def main():
    if SCRAPE_FRESH:
        scraper = init_scraper()
        await scraper.scrape(
            chunk_size=22,
            batch_size=384,
            total_limit=384,
            retries=15
        )
    #
    # products = Product.objects.filter(status=Status.DONE)
    # await scrape_images(target=assets_folder, Image=Image, products=products)


if __name__ == "__main__":
    logger.debug("Starting...")
    asyncio.get_event_loop().run_until_complete(main())
    logger.debug("Screenshot has been taken")
