from typing import List, Dict, Any, Awaitable, Callable

from mongoengine import Document

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.parsers import ProductParsers
from src.framework.CNPI_scraper.scrapers import ProductsExplorer
from src.framework.CNPI_scraper.scrapers.products_explorer.product_cards_scraper import ProductCardsScraper
from src.framework.CNPI_scraper.scrapers.products_explorer.products_scraper import ProductsScraper
from src.framework.CNPI_scraper.success_criteria import SuccessCriteria


def init_helper_classes(
        Node: Document,
        Product: Document,
        _criteria: Dict[str, Dict[str, Any]],
        create_absolute_url: Callable,
        parse_pagination: Awaitable,
        parse_product_cards: Awaitable,
        parsers: List[Awaitable],
):
    data_manager = DataManager(
        create_absolute_url=create_absolute_url,
        Product=Product,
        Node=Node
    )
    criteria_object = SuccessCriteria(
        category_criteria=_criteria['category'],
        node_criteria=_criteria['node'],
        product_criteria=_criteria['product']
    )
    product_parser = ProductParsers(
        parse_pagination=parse_pagination,
        parse_product_cards=parse_product_cards,
        parsers=parsers
    )
    return data_manager, criteria_object, product_parser


async def explore_urls(
        node: Document,
        Product: Document,
        _criteria: Dict[str, Dict[str, Any]],
        create_absolute_url: Callable,
        parse_pagination: Awaitable,
        parse_product_cards: Awaitable,
        parsers: List[Awaitable],
        config: Dict[str, Any] = {}
):
    data_manager, criteria_object, product_parser = init_helper_classes(
        None,
        Product,
        _criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers
    )

    explorer = ProductCardsScraper(product_parser, criteria_object, data_manager, config)
    await explorer.scrape_product_cards(node)


async def scrape_products(
        node: Document,
        Product: Document,
        _criteria: Dict[str, Dict[str, Any]],
        create_absolute_url: Callable,
        parse_pagination: Awaitable,
        parse_product_cards: Awaitable,
        parsers: List[Awaitable],
        config: Dict[str, Any] = {}
):
    data_manager, criteria_object, product_parser = init_helper_classes(
        None,
        Product,
        _criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers
    )

    explorer = ProductsScraper(product_parser, criteria_object, data_manager, config)
    await explorer.scrape_products(node)


def init_scraper(
        Node: Document,
        Product: Document,
        _criteria: Dict[str, Dict[str, Any]],
        create_absolute_url: Callable,
        parse_pagination: Awaitable,
        parse_product_cards: Awaitable,
        parsers: List[Awaitable],
        config: Dict[str, Any] = {}
):
    data_manager, criteria_object, product_parser = init_helper_classes(
        Node,
        Product,
        _criteria,
        create_absolute_url,
        parse_pagination,
        parse_product_cards,
        parsers
    )

    return ProductsExplorer(product_parser, criteria_object, data_manager, config)
