from typing import Callable, Any, Dict

from mongoengine import Document, QuerySet

from .parsers import ImageParser
from .scrapers import ImagesScraper


async def scrape_images(
        target: str = "",
        Image: Document = None,
        products: QuerySet = None,
        extract_urls: Callable = None,
        preprocess: Callable = None,
        skip_condition: Callable = None,
        validate_image_integrity: Callable = None,
        config: Dict[str, Any] = None

):
    image_parser = ImageParser(
        target=target,
        extract_urls=extract_urls,
        preprocess=preprocess,
        skip_condition=skip_condition,
        validate_image_integrity=validate_image_integrity
    )
    image_scraper = ImagesScraper(Image=Image, image_parser=image_parser, config=config)
    await image_scraper.scrape(products)
