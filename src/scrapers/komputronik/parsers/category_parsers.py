import asyncio

from playwright.async_api import Page


async def get_categories_urls(page: Page):
    catalog = await page.query_selector(".view-category-full")
    elements = await catalog.query_selector_all('[onclick="return false;"]')
    tasks = [element.get_attribute('href') for element in elements]
    category_urls = await asyncio.gather(*tasks)
    return category_urls


async def parse_title_field(page: Page):
    name_element = await page.query_selector("h1")
    name = await name_element.inner_text()
    return name
