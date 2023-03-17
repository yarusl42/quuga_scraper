import asyncio

from src.scrapers.komputronik import scrape_category_products_list
from src.utils.logger import logger

BASE_URL = "https://www.komputronik.pl/category/1596/telefony.html?showBuyActiveOnly=0&p="
BASE_URL = "https://www.komputronik.pl/category/18499/smartwatche-i-zegarki.html?showBuyActiveOnly=0&p="
BASE_URL = "https://www.komputronik.pl/category/10243/akcesoria-do-telefonow-gsm.html?showBuyActiveOnly=0&p="
# BASE_URL = "https://www.komputronik.pl/category/8923/tablety.html?showBuyActiveOnly=0&p="
# BASE_URL = "https://www.komputronik.pl/category/8011/czytniki-ebook.html?showBuyActiveOnly=0&p="
BASE_URL = "https://www.komputronik.pl/category/6334/nawigacja-piesza.html?showBuyActiveOnly=0&p="
SCRAPE_FRESH = True


async def main():
    urls = [
        "https://www.komputronik.pl/product/743850/garmin-venu-2-plus-szary.html",
        "https://www.komputronik.pl/product/796411/polar-ignite-3-czarny-s-l.html"
    ]
    await scrape_category_products_list(urls)
    # await scrape_category("pedestrian_navigation", BASE_URL, scrape_fresh=SCRAPE_FRESH)


# async def main():
#     async with async_playwright() as playwright_instance:
#         browser = await playwright_instance.chromium.launch(
#             headless=HEADLESS,
#             proxy=proxy
#         )
#
#         await scrape_page_screenshot(
#             browser=browser,
#             url='https://www.ceneo.pl/Smartfony;0020-30-0-0-49.htm',
#             elm_visible_when_suc='.header__favourites'
#         )
#         await browser.close()


# https://sklep.kfd.pl/kfd-premium-pre-workout-500-g-p-6502.html
# https://www.orange.pl/esklep/smartfony/samsung/samsung-galaxy-s23-5g-256gb

# https://scrapfly.io/blog/web-scraping-with-playwright-and-python/
if __name__ == "__main__":
    logger.debug("Starting...")
    asyncio.get_event_loop().run_until_complete(main())
    logger.debug("Screenshot has been taken")

#
# https://sklep.kfd.pl/kfd-premium-pre-workout-500-g-p-6502.html
# https://www.orange.pl/esklep/smartfony/samsung/samsung-galaxy-s23-5g-256gb

# https://scrapfly.io/blog/web-scraping-with-playwright-and-python/
