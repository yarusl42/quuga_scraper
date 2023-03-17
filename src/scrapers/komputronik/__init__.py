from playwright.async_api import async_playwright

from src.config import HEADLESS, assets_folder, proxy
from src.utils.db import db
from .images import download_images, skip_downloaded_download_images
from .products import scrape_products, scrape_products_without_saving
from .storage import set_urls_collection, set_products_collection
from .urls import scrape_product_urls, get_not_scraped_product_urls, get_stored_products_urls


def set_storage_collections(category_name):
    set_urls_collection(db[f"{category_name}_urls"])
    set_products_collection(db[category_name])


async def scrape_urls_fresh(browser, category_url):
    await scrape_product_urls(browser, category_url)
    products_urls = get_stored_products_urls()
    return products_urls


async def scrape_urls_not_fresh(a, b):
    products_urls = get_not_scraped_product_urls()
    return products_urls


def get_scrape_urls_func(scrape_fresh):
    if scrape_fresh:
        return scrape_urls_fresh
    return scrape_urls_not_fresh


def get_download_images_func(scrape_fresh):
    if scrape_fresh:
        return download_images
    return skip_downloaded_download_images


async def scrape_category(category_name, category_url, scrape_fresh=False):
    async with async_playwright() as playwright_instance:
        browser = await playwright_instance.chromium.launch(
            headless=HEADLESS,
            proxy=proxy
        )

        set_storage_collections(category_name)

        scrape_urls = get_scrape_urls_func(scrape_fresh)
        products_urls = await scrape_urls(browser, category_url)

        await scrape_products(browser, products_urls)

        download_images_func = get_download_images_func(scrape_fresh)
        await download_images_func(proxy, assets_folder)
        await browser.close()


async def scrape_category_products_list(products_urls):
    async with async_playwright() as playwright_instance:
        browser = await playwright_instance.chromium.launch(
            headless=HEADLESS,
            proxy=proxy
        )
        await scrape_products_without_saving(browser, products_urls)
        await browser.close()
