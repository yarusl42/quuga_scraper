import asyncio


async def parse_product_counter(page):
    while True:

        product_counter_element = await page.query_selector(".tests-product-count")
        product_counter_raw = await product_counter_element.inner_text()
        try:
            product_counter = int(product_counter_raw.split()[0].lstrip('('))
            return product_counter
        except:
            await asyncio.sleep(3)
