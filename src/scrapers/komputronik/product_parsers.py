import json
from collections import OrderedDict

from src.utils.logger import logger


async def parse_multi_image_gallery(gallery_element):
    images_elements = await gallery_element.query_selector_all(".max-w-full")
    logger.debug("start image_element.get_attribute('src')")
    images_links = [await image_element.get_attribute('src') for image_element in images_elements]
    logger.debug("end image_element.get_attribute('src')")
    active_element = await gallery_element.query_selector(".carousel__slide--active")
    active_element = await active_element.query_selector(".max-w-full")
    active_image_link = await active_element.get_attribute('src')
    active_index = images_links.index(active_image_link)
    return images_links, active_index


async def parse_one_image_gallery(page):
    active_element = await page.query_selector(".carousel img")
    images_links = [await active_element.get_attribute('src')]
    return images_links, 0


async def parse_gallery(page):
    gallery_element = await page.query_selector('[ng-if="$ctrl.showNavigation && !$ctrl.isMobileView"]')
    if gallery_element:
        images_links, active_index = await parse_multi_image_gallery(gallery_element)
    else:
        images_links, active_index = await parse_one_image_gallery(page)

    gallery = {
        "gallery": {
            "images": images_links,
            "main_image_index": active_index
        },
        "local_gallery": {
            "images": [],
            "main_image_index": active_index
        }
    }
    return gallery


async def parse_shipping_details(page):
    shipping_element = await page.query_selector('ktr-product-availability')
    logger.debug("start page data")
    availability = await shipping_element.get_attribute("availability")
    has_free_shipping = await shipping_element.get_attribute("has-free-shipping")
    is_buyable = await shipping_element.get_attribute("is-buyable")
    logger.debug("end page data")

    shipping_details = {
        "shipping_details": json.loads(availability),
        "has_free_shipping": True if has_free_shipping == "1" else False,
        "is_buyable": True if is_buyable == "1" else False
    }
    return shipping_details


async def parse_specs(page):
    specs_element = await page.query_selector(".tests-full-specification")
    if not specs_element:
        return {"specs": OrderedDict()}

    specs = []
    specs_tables = await specs_element.query_selector_all('xpath=child::*')
    for specs_table in specs_tables:
        rows = await specs_table.query_selector_all('xpath=child::*')
        table_header_element = rows.pop(0)
        table_header = await table_header_element.inner_text()
        parsed_table = []
        for row in rows:
            cells = await row.query_selector_all('xpath=child::*')
            key = await cells[0].inner_text()
            value = await cells[1].inner_text()
            parsed_table.append((key, value))

        specs.append((table_header, parsed_table))

    specs = {"specs": OrderedDict(specs)}
    return specs


async def parse_custom_code(page, selector):
    custom_code = await page.query_selector(selector)
    if not custom_code:
        return ""
    return await custom_code.inner_html()


async def parse_producer_description(page):
    custom_code = await parse_custom_code(page, "#p-content-producer-desc .custom-code")
    description = {
        "producer_description": custom_code
    }
    return description


async def parse_description(page):
    custom_code = await parse_custom_code(page, "#p-content-product-desc .custom-code")
    description = {
        "description": custom_code
    }
    return description


async def parse_ratings(page):
    res = {
        "rating": 0,
        "reviews_by_stars": []
    }
    ratings_element = await page.query_selector('[ng-if="$ctrl.commentsInfo.count > 0"]')
    if not ratings_element:
        return res
    ratings_element_children = await ratings_element.query_selector_all('xpath=child::*')
    rating_element = await ratings_element_children[0].query_selector("div")
    rating = float(await rating_element.inner_text())

    reviews_number_elements = await ratings_element_children[1].query_selector_all('xpath=child::*')
    reviews_number = []
    for stars, review_number in enumerate(reviews_number_elements[::-1]):
        amount_of_reviews = await review_number.inner_text()
        amount_of_reviews = int(amount_of_reviews.split()[1])
        reviews_number.append((stars + 1, amount_of_reviews))

    res["rating"] = rating
    res["reviews_by_stars"] = reviews_number
    return res


async def parse_general_info(page):
    payment_info_element = await page.query_selector('[layer-name="layerProductInstallment"]')
    logger.debug("start payment_info_element.get_attribute")
    if payment_info_element is None:
        return {"is_buyable": False}
    else:
        payment_info = await payment_info_element.get_attribute("layer-params")
    logger.debug("end payment_info_element.get_attribute")
    payment_info = json.loads(payment_info)

    if "grenke_installment_calculator" in payment_info:
        del payment_info["grenke_installment_calculator"]
    if "installment_payments" in payment_info:
        del payment_info["installment_payments"]
    if "intervalConfig" in payment_info:
        del payment_info["intervalConfig"]
    if "frontPath" in payment_info:
        del payment_info["frontPath"]

    return payment_info
