from typing import Any, Dict, List, Tuple, Awaitable

from playwright.async_api import Page

from .base_parser import BaseParsers


class CategoryNodeParsers(BaseParsers):
    def __init__(
            self,
            category_parsers: List[Tuple[str, Awaitable]],
            node_parsers: List[Tuple[str, Awaitable]],
            get_categories_urls: Awaitable
    ):
        super(BaseParsers, self).__init__()
        self.get_categories_urls = get_categories_urls
        self.node_parsers = node_parsers
        self.category_parsers = category_parsers

    async def parse_category_object(self, page: Page) -> Dict[str, Any]:
        return await self.parse_object(self.category_parsers, page)

    async def parse_node_object(self, page: Page) -> Dict[str, Any]:
        return await self.parse_object(self.node_parsers, page)
