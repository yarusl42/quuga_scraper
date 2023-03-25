from typing import Dict, List, Any, Callable, Tuple, Awaitable

from mongoengine import Document

from src.framework.CNPI_scraper.scrapers import CNBuilder
from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from .parsers import CategoryNodeParsers
from .success_criteria import SuccessCriteria


async def scrape_categories(
        init_objects: List[Dict[str, Any]],
        create_absolute_url: Callable,
        documents: Dict[str, Document],
        parsers: Dict[str, List[Tuple[str, Awaitable]]],
        criteria: Dict[str, Dict[str, Any]],
        get_categories_urls: Awaitable,
        config: Dict[str, Any] = {}
):
    parsers_object = CategoryNodeParsers(
        category_parsers=parsers['category'],
        node_parsers=parsers['node'],
        get_categories_urls=get_categories_urls
    )
    data_manager = DataManager(
        create_absolute_url=create_absolute_url,
        Category=documents['category'],
        Node=documents['node']
    )
    criteria_object = SuccessCriteria(
        category_criteria=criteria['category'],
        node_criteria=criteria['node']
    )

    category_structure = CNBuilder(
        parsers=parsers_object,
        data_manager=data_manager,
        criteria=criteria_object,
        config=config
    )
    await category_structure.build(init_objects)
