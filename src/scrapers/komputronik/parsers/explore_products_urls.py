import asyncio
from urllib.parse import urljoin


def generate_category_pagination_urls(num_pages, node_url):
    for page_num in range(1, num_pages + 1):
        yield urljoin(node_url, f"?showBuyActiveOnly=0&p={page_num}")


async def get_number_of_pages(page):
    paginator = await page.query_selector('xpath=//*[@id="products-list"]/div[2]/nav[2]/ul')
    try:
        paginator_elements = await paginator.query_selector_all('xpath=child::*')
    except:
        return 1
    paginator_elements = [await paginator_element.inner_text() for paginator_element in paginator_elements]
    await page.close()

    if not paginator_elements:
        number_of_pages = 0
    elif paginator_elements[-1] == '':
        number_of_pages = int(paginator_elements[-2])
    else:
        number_of_pages = int(paginator_elements[-1])

    return number_of_pages


async def parse_pagination(page):
    number_of_pages = await get_number_of_pages(page)
    return list(generate_category_pagination_urls(number_of_pages, page.url))


async def parse_product_cards(page):
    elements = await page.query_selector_all(".button-a")
    tasks = [element.get_attribute('href') for element in elements]
    links = await asyncio.gather(*tasks)
    return links
