from mongoengine import Document, QuerySet

from config.config import HEADLESS, PROXY
from config.komputronik.config import category_criteria, node_criteria, product_criteria, categories
from src.framework.CNPI_scraper.scrape_category import scrape_categories as _scrape_categories
from src.framework.CNPI_scraper.scrape_images import scrape_images as _scrape_images
from src.framework.CNPI_scraper.scrape_products import explore_urls as _explore_urls
from src.framework.CNPI_scraper.scrape_products import init_scraper as _init_scraper
from src.framework.CNPI_scraper.scrape_products import scrape_products as _scrape_products
from src.scrapers.komputronik.models import Category, Node, Product
from src.scrapers.komputronik.parsers.category_parsers import parse_title_field, get_categories_urls
from src.scrapers.komputronik.parsers.explore_products_urls import parse_pagination, parse_product_cards
from src.scrapers.komputronik.parsers.image_parser import extract_urls, skip_condition
from src.scrapers.komputronik.parsers.node_parsers import parse_product_counter
from src.scrapers.komputronik.parsers.product_parsers import \
    parse_gallery, parse_shipping_details, \
    parse_specs, parse_ratings, \
    parse_is_buyable, parse_general_info, \
    parse_producer_description, parse_description
from src.scrapers.komputronik.utils.get_absolute_url import create_absolute_url

criteria = {
    "category": category_criteria,
    "node": node_criteria,
    "product": product_criteria
}
config = {'headless': HEADLESS, 'proxy': PROXY}

parsers = [
    parse_gallery, parse_shipping_details,
    parse_specs, parse_ratings,
    parse_is_buyable, parse_general_info,
    parse_producer_description, parse_description
]


async def scrape_categories():
    documents = {
        "category": Category,
        "node": Node,
    }

    category_node_parsers = {
        "category": [("name", parse_title_field)],
        "node": [("product_counter", parse_product_counter)],
    }

    await _scrape_categories(
        categories,
        create_absolute_url,
        documents,
        category_node_parsers,
        criteria,
        get_categories_urls,
        config
    )


async def explore_urls(node):
    return await _explore_urls(
        node,
        Product,
        criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers,
        config
    )


async def scrape_products(node):
    return await _scrape_products(
        node,
        Product,
        criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers,
        config
    )


def init_scraper():
    return _init_scraper(
        Node,
        Product,
        criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers,
        config
    )


async def scrape_images(target: str = "", Image: Document = None, products: QuerySet = None):
    return await _scrape_images(
        target=target,
        Image=Image,
        products=products,
        extract_urls=extract_urls,
        preprocess=None,
        skip_condition=skip_condition,
        validate_image_integrity=None,
        config=config
    )
