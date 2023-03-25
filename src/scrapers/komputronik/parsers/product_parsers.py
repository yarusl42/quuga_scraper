import json
from collections import OrderedDict

from src.scrapers.komputronik.parsers.helpers import parse_multi_image_gallery, \
    parse_one_image_gallery, parse_custom_code, parse_specs_tables
from src.utils.logger import logger


async def parse_gallery(page):
    try:
        gallery_element = await page.query_selector('[ng-if="$ctrl.showNavigation && !$ctrl.isMobileView"]')
        if gallery_element:
            images_links, active_index = await parse_multi_image_gallery(gallery_element)
        else:
            images_links, active_index = await parse_one_image_gallery(page)

        gallery = {
            "gallery": {
                "images": images_links,
                "main_image_index": active_index
            }
        }
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return gallery


async def parse_shipping_details(page):
    try:
        shipping_element = await page.query_selector('ktr-product-availability')
        availability = await shipping_element.get_attribute("availability")
        has_free_shipping = await shipping_element.get_attribute("has-free-shipping")

        shipping_details = {
            "shipping_details": json.loads(availability),
            "has_free_shipping": True if has_free_shipping == "1" else False,
        }
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return shipping_details


async def parse_specs(page):
    try:
        specs_element = await page.query_selector(".tests-full-specification")
        if not specs_element:
            return {"specs": OrderedDict()}
        specs_tables = await specs_element.query_selector_all('xpath=child::*')
        res = await parse_specs_tables(specs_tables)
        specs = {"specs": OrderedDict(res)}
    except Exception as e:
        logger.error(f"{e}")
        contents = [await specs_table.inner_html() for specs_table in specs_tables]
        raise Exception(e)
    return specs


async def parse_ratings(page):
    res = {
        "rating": 0,
        "reviews_by_stars": []
    }
    try:
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
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return res


async def parse_is_buyable(page):
    res = {}
    try:
        payment_info_element = await page.query_selector('[layer-name="layerProductInstallment"]')
        if payment_info_element is None:
            return {"is_buyable": False}

        shipping_element = await page.query_selector('ktr-product-availability')
        is_buyable = await shipping_element.get_attribute("is-buyable")
        res = {
            "is_buyable": True if is_buyable == "1" else False
        }
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return res


async def parse_general_info(page):
    payment_info = {}
    try:
        payment_info_element = await page.query_selector('[layer-name="layerProductInstallment"]')
        if payment_info_element is None:
            return {}
        else:
            payment_info = await payment_info_element.get_attribute("layer-params")
        payment_info = json.loads(payment_info)

        if "grenke_installment_calculator" in payment_info:
            del payment_info["grenke_installment_calculator"]
        if "installment_payments" in payment_info:
            del payment_info["installment_payments"]
        if "intervalConfig" in payment_info:
            del payment_info["intervalConfig"]
        if "frontPath" in payment_info:
            del payment_info["frontPath"]
        if "isCompany" in payment_info:
            payment_info['is_company'] = payment_info["isCompany"]
            del payment_info["isCompany"]
        if "amount" in payment_info:
            payment_info['price'] = payment_info['amount']
            del payment_info['amount']

    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return payment_info


async def parse_producer_description(page):
    try:
        custom_code = await parse_custom_code(page, "#p-content-producer-desc .custom-code")
        res = {
            "producer_description": custom_code
        }
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return res


async def parse_description(page):
    try:
        custom_code = await parse_custom_code(page, "#p-content-product-desc .custom-code")
        res = {
            "description": custom_code
        }
    except Exception as e:
        logger.error(f"{e}")
        raise Exception(e)
    return res
