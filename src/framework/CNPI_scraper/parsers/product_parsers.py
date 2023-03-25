from typing import Dict, Any, List, Tuple, Awaitable

from playwright.async_api import Page

from .base_parser import BaseParsers


class ProductParsers(BaseParsers):
    def __init__(self, parse_pagination, parse_product_cards, parsers=[]):
        super(BaseParsers, self).__init__()
        self.parsers: List[Tuple[str, Awaitable]] = parsers
        self.parse_pagination: Awaitable = parse_pagination
        self.parse_product_cards: Awaitable = parse_product_cards

    async def parse_product(self, page: Page) -> Dict[str, Any]:
        return await self.simple_parse(self.parsers, page)
