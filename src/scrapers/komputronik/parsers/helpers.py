async def parse_multi_image_gallery(gallery_element):
    images_elements = await gallery_element.query_selector_all(".max-w-full")
    images_links = [await image_element.get_attribute('src') for image_element in images_elements]
    active_element = await gallery_element.query_selector(".carousel__slide--active")
    active_element = await active_element.query_selector(".max-w-full")
    active_image_link = await active_element.get_attribute('src')
    active_index = images_links.index(active_image_link)
    images_links = [image_link.replace('product-picture/4/', 'product-picture/6/') for image_link in images_links]
    return images_links, active_index


async def parse_one_image_gallery(page):
    active_element = await page.query_selector(".carousel img")
    images_links = [await active_element.get_attribute('src')]
    return images_links, 0


async def parse_custom_code(page, selector):
    custom_code = await page.query_selector(selector)
    if not custom_code:
        return ""
    return await custom_code.inner_html()


async def parse_specs_table_header(row):
    table_header = await row.inner_text()
    return table_header


async def parse_cells(cells):
    key = await cells[0].inner_text()
    value = await cells[1].inner_text()
    if "\n\n" in value:
        value = [val for val in value.split("\n\n") if val]
    return key, value


async def parse_specs_table_content(rows):
    parsed_table = []
    for row in rows:
        try:
            cells = await row.query_selector_all('xpath=child::*')
            parsed_table.append(await parse_cells(cells))
        except:
            raise Exception("You missed somthing again. Spec table not parsing")

    return parsed_table


async def check_if_table(rows):
    if len(rows) != 2:
        return False

    try:
        classes = await rows[0].evaluate('el => el.className')
    except Exception as e:
        return False

    if not (
            "font-semibold" in classes or \
            "odd:bg-gray-porcelain" in classes or \
            "even:bg-white" in classes
    ):
        return False

    return True


async def check_single_row_table(rows):
    if len(rows) == 2:
        classes = await rows[0].evaluate('el => el.className')
        if "relative" in classes:
            return True
    return False


async def parse_specs_table(children):
    table_header_element = children.pop(0)
    table_header = await parse_specs_table_header(table_header_element)
    rows = await children[0].query_selector_all('xpath=child::*')
    if await check_single_row_table(rows):
        try:
            parsed_table = [await parse_cells(rows)]
        except Exception as e:
            raise Exception(e)
    else:
        try:
            parsed_table = await parse_specs_table_content(rows)
        except Exception as e:
            raise Exception(e)

    return table_header, parsed_table


async def parse_specs_tables(specs_tables):
    specs = []
    for specs_table in specs_tables:
        children = await specs_table.query_selector_all('xpath=child::*')
        if await check_if_table(children):
            specs.append(await parse_specs_table(children))
        else:
            specs += await parse_specs_tables(children)

    return specs
