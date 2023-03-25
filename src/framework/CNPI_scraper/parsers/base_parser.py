import asyncio
from collections import ChainMap
from typing import Awaitable, List, Tuple, Dict, Any

from playwright.async_api import Page


class BaseParsers:
    @staticmethod
    async def parse(parser: Awaitable, field: str, page: Page):
        res = await parser(page)
        return {field: res}

    async def parse_object(self, parsers: List[Tuple[str, Awaitable]], page: Page) -> Dict[str, Any]:
        tasks = []
        for field, parser in parsers:
            tasks.append(self.parse(parser, field, page))

        result = await asyncio.gather(*tasks)
        return dict(ChainMap(*result))

    @staticmethod
    async def simple_parse(parsers: List[Awaitable], page: Page) -> Dict[str, Any]:
        result = await asyncio.gather(*[parser(page) for parser in parsers])
        return dict(ChainMap(*result))
