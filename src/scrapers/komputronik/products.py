import asyncio
from collections import ChainMap

from src.framework import scrape_url_list
from src.scrapers.komputronik.product_parsers import \
    parse_general_info, parse_gallery, parse_shipping_details, \
    parse_specs, parse_description, parse_producer_description, \
    parse_ratings
from .storage import get_products_collection


async def _get_page_url(page):
    return {"url": await page.evaluate('() => document.location.href')}


async def scrape_product_info(page):
    await asyncio.sleep(10)
    tasks = [
        parse_general_info(page),
        parse_gallery(page),
        parse_shipping_details(page),
        parse_specs(page),
        parse_description(page),
        parse_producer_description(page),
        parse_ratings(page),
        _get_page_url(page)
    ]
    res = await asyncio.gather(*tasks)
    await page.close()
    return res


async def scrape_product(page):
    res = await scrape_product_info(page)
    res = dict(ChainMap(*res))
    products_collection = get_products_collection()
    myquery = {"url": res["url"]}
    set_query = {"$set": res}
    products_collection.update_one(myquery, set_query, upsert=True)


async def scrape_product_without_saving(page):
    res = await scrape_product_info(page)

    print(res)


async def scrape_products_without_saving(browser, urls):
    await scrape_url_list(
        browser,
        urls,
        ['#subcategories', '.tests-other-products'],
        scrape_product_without_saving,
        chunk_size=15,
        retries=20
    )


async def scrape_products(browser, urls):
    await scrape_url_list(
        browser,
        urls,
        ['#subcategories', '.tests-other-products'],
        scrape_product,
        chunk_size=15,
        retries=20
    )
