import asyncio

from src.framework import repeat_scrape_until_suc, scrape_url_list
from src.utils.logger import logger
from .storage import get_urls_collection, get_products_collection


def _generate_category_pagination_urls(num_pages, category_url):
    for page_num in range(1, num_pages + 1):
        yield f"{category_url}{page_num}"


async def _get_number_of_pages(browser, category_url):
    try:
        page = await repeat_scrape_until_suc(browser, f"{category_url}0", "h1.tests-product-name", retries=20)
    except Exception as e:
        logger.error(f"Couldn't get the number of pages {e}")
        return 0

    paginator = await page.query_selector('xpath=//*[@id="products-list"]/div[2]/nav[2]/ul')
    try:
        paginator_elements = await paginator.query_selector_all('xpath=child::*')
    except:
        return 1
    paginator_elements = [await paginator_element.inner_text() for paginator_element in paginator_elements]

    if not paginator_elements:
        number_of_pages = 0
    elif paginator_elements[-1] == '':
        number_of_pages = int(paginator_elements[-2])
    else:
        number_of_pages = int(paginator_elements[-1])

    await page.close()
    return number_of_pages


async def _parse_urls_from_page(page):
    elements = await page.query_selector_all(".button-a")
    tasks = [element.get_attribute('href') for element in elements]
    links = await asyncio.gather(*tasks)
    urls_collection = get_urls_collection()
    for link in links:
        urls_collection.update_one(
            {"url": link},
            {"$set": {"url": link}},
            upsert=True
        )

    return links


async def scrape_product_urls(browser, category_url):
    number_of_pages = await _get_number_of_pages(browser, category_url)
    await scrape_url_list(
        browser,
        _generate_category_pagination_urls(number_of_pages, category_url),
        ".tests-breadcrumbs",
        _parse_urls_from_page,
        chunk_size=10
    )


def _extract_urls_from_collection(col):
    return [url.get('url') for url in col.find({}, {"_id": 0, "url": 1})]


def get_stored_products_urls():
    urls_collection = get_urls_collection()
    products_urls = set(_extract_urls_from_collection(urls_collection))
    return products_urls


def get_not_scraped_product_urls():
    urls_collection = get_urls_collection()
    products_collection = get_products_collection()
    all_urls = set(_extract_urls_from_collection(urls_collection))
    done_urls = set(_extract_urls_from_collection(products_collection))

    all_urls = all_urls
    all_urls = all_urls - done_urls
    return all_urls
