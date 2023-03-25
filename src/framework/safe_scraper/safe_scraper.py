import asyncio

from fake_useragent import UserAgent

from src.utils.helpers import generator_split_to_chunks
from src.utils.logger import logger

ua = UserAgent()


async def is_element_visible(page, selector):
    element = await page.query_selector(selector)
    if not element:
        return False
    return await element.is_visible()


async def check_suc_criteria(page, elm_visible_when_suc):
    for elm in elm_visible_when_suc:
        if await is_element_visible(page, elm):
            return True
    return False


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
        return

    try:
        await scrape_method(page)
    except Exception as e:
        logger.error(f"Failed to scrape page SCRAPEERROR:{url} {e}")
    finally:
        await page.close()


async def goto_url(browser, url, elm_visible_when_suc):
    logger.info(f"Opening new page {url}")
    page = await browser.new_page()
    await page.set_extra_http_headers({"User-Agent": ua.random})

    try:
        logger.info(f"Scraping {url}")
        await page.goto(url)
    except Exception as e:
        await page.close()
        raise e

    is_suc_element_visible = await check_suc_criteria(page, elm_visible_when_suc)
    if not is_suc_element_visible:
        logger.debug(f"Element is not visible {url}, criteria: {elm_visible_when_suc}")
        await page.close()
        raise Exception(f"Element is not visible {url}")

    return page


async def repeat_scrape_until_suc(browser, url, elm_visible_when_suc, retries=1, iteration=0):
    try:
        page = await goto_url(browser, url, elm_visible_when_suc)
    except Exception as e:
        iteration += 1
        if iteration >= retries:
            await page.close()
            raise e
        page = await repeat_scrape_until_suc(browser, url, elm_visible_when_suc, retries=retries, iteration=iteration)

    return page


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
