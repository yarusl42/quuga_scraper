from typing import List, Union, Any, Dict

from mongoengine import Document
from playwright.async_api import Page, Browser
from playwright.async_api import async_playwright

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.models.enums import Status
from src.framework.CNPI_scraper.parsers import ProductParsers
from ...success_criteria import SuccessCriteria
from src.framework.safe_scraper import repeat_scrape_until_suc, scrape_url_list
from src.utils.logger import logger
from .product_scraper_base import ProductScraperBase


class ProductCardsScraper(ProductScraperBase):
    def __init__(
            self,
            product_parser: ProductParsers = None,
            criteria: SuccessCriteria = None,
            data_manager: DataManager = None,
            config: Dict[str, Any] = None
    ):
        super().__init__(product_parser=product_parser, criteria=criteria, data_manager=data_manager, config=config)

    async def parse_urls_from_page(self, page: Page, node: Document) -> None:
        links: List[str] = await self.product_parser.parse_product_cards(page)

        if not self.data_manager:
            return

        for link in links:
            product_object = {
                'url': link,
                'status': Status.PENDING,
                'parent': node.id,
                'scrape': node.scrape
            }
            try:
                self.data_manager.Product.objects.get(url=link)
                continue
            except:
                pass

            try:
                self.data_manager.update_product(product_object)
            except Exception as e:
                logger.debug(f"Couldn't scrape product card. Product url: {page.url}")
                product = self.data_manager.Product.objects.get(url=link)
                if product:
                    product.status = Status.ERROR
                    product.save()

                logger.debug(f"Couldn't scrape product. Error: {e}. Link: {link}")

    async def goto_node(self, node: Document) -> Union[Page, None]:
        try:
            page: Page = await repeat_scrape_until_suc(self.browser, node.url, [self.criteria.get_node_criteria()],
                                                       retries=20)
            return page
        except Exception as e:
            logger.error(f"Couldn't go to node_url: {node.id} {e}")
            return None

    async def scrape_product_urls(self, node: Document) -> None:
        page: Page = await self.goto_node(node)
        pagination: List[str] = await self.product_parser.parse_pagination(page)
        await page.close()

        async def _parse_urls_from_page(current_page: Page = page, current_node: Document = node):
            await self.parse_urls_from_page(current_page, current_node)

        await scrape_url_list(
            self.browser,
            pagination,
            [self.criteria.get_node_criteria()],
            _parse_urls_from_page,
            chunk_size=10
        )

    async def scrape_product_cards(self, node: Document) -> None:
        async with async_playwright() as playwright_instance:
            browser: Browser = await playwright_instance.chromium.launch(
                headless=self.config.get('headless', None),
                proxy=self.config.get('proxy', None)
            )

            self.browser: Browser = browser
            await self.scrape_product_urls(node)
            await self.browser.close()
