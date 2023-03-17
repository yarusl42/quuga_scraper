import asyncio
import os

from src.config import USER_AGENT
from src.utils.db import db
from src.utils.helpers import generator_split_to_chunks
from src.utils.logger import logger

failed_collection = db['failed']


async def is_element_visible(page, selector):
    element = await page.query_selector(selector)
    if not element:
        return False
    return await element.is_visible()


async def _scrape_url_list_helper(browser, scrape_method, elm_visible_when_suc, url='', retries=10):
    try:
        page = await repeat_scrape_until_suc(
            browser,
            url,
            elm_visible_when_suc,
            retries=retries
        )
    except Exception as e:
        logger.error(f"Failed to reach page SCRAPEERROR:{url} {e}")
        failed_collection.update_one({"url": url}, {"$set": {"url": url}}, upsert=True)
        await page.close()
        return

    try:
        await scrape_method(page)
    except Exception as e:
        logger.error(f"Failed to scrape page SCRAPEERROR:{url} {e}")
        failed_collection.update_one({"url": url}, {"$set": {"url": url}}, upsert=True)

    await page.close()


async def check_suc_criteria(page, elm_visible_when_suc):
    if isinstance(elm_visible_when_suc, str):
        return await is_element_visible(page, elm_visible_when_suc)

    for elm in elm_visible_when_suc:
        if await is_element_visible(page, elm):
            return True
    return False


async def scrape_page(browser, url, elm_visible_when_suc):
    logger.debug(f"Opening new page {url}")
    page = await browser.new_page()
    await page.set_extra_http_headers({"User-Agent": USER_AGENT})

    try:
        logger.debug(f"Scraping {url}")
        await page.goto(url)
        # await page.wait_for_event('load')
    except Exception as e:
        logger.debug(f"Error while scraping page {url}")
        await page.close()
        raise e

    is_suc_element_visible = await check_suc_criteria(page, elm_visible_when_suc)
    if not is_suc_element_visible:
        logger.debug(f"Element is not visible {url}")
        await page.close()
        raise Exception(f"Element is not visible {url}")

    return page


async def safe_scrape_page(browser, url, elm_visible_when_suc, retries=1, iteration=0):
    try:
        page = await scrape_page(browser, url, elm_visible_when_suc)
    except Exception as e:
        iteration += 1
        if iteration >= retries:
            await page.close()
            raise e
        page = await safe_scrape_page(browser, url, elm_visible_when_suc, retries=retries, iteration=iteration)

    return page


async def repeat_scrape_until_suc(browser, url, elm_visible_when_suc, retries=-1):
    return await safe_scrape_page(browser, url, elm_visible_when_suc, retries=retries)


async def take_screenshot_method(page, screenshot_path):
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    await page.screenshot(path=screenshot_path)


async def scrape_url_list(browser, url_list, elm_visible_when_suc, scrape_method, chunk_size=20, retries=10):
    url_list = list(url_list)
    for chunk in generator_split_to_chunks(url_list, chunk_size):
        tasks = []
        for url in chunk:
            awaitable = _scrape_url_list_helper(
                browser,
                scrape_method,
                elm_visible_when_suc=elm_visible_when_suc,
                url=url,
                retries=retries
            )
            tasks.append(awaitable)
        await asyncio.gather(*tasks)


async def scrape_page_screenshot(browser, url, elm_visible_when_suc, n_iterations=10):
    for i in range(n_iterations):
        print(i)

        async def scrape_method(page, screenshot_num=i):
            return await take_screenshot_method(page, f'screenshot{screenshot_num}.png')

        scrape_page_awaitable = scrape_page(
            browser,
            url,
            elm_visible_when_suc,
            scrape_method
        )
        try:
            await scrape_page_awaitable
            break
        except Exception as e:
            logger.debug(e)
