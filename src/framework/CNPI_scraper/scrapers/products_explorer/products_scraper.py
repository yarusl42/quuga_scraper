import asyncio
from typing import Dict, Any

from mongoengine import Document, Q
from mongoengine import QuerySet
from playwright.async_api import Browser
from playwright.async_api import async_playwright

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.models.enums import Status
from src.framework.CNPI_scraper.parsers import ProductParsers
from src.framework.safe_scraper import goto_url
from src.utils.helpers import generator_split_to_chunks
from src.utils.logger import logger
from .product_scraper_base import ProductScraperBase
from ...success_criteria import SuccessCriteria


class ProductsScraper(ProductScraperBase):
    def __init__(
            self,
            product_parser: ProductParsers = None,
            criteria: SuccessCriteria = None,
            data_manager: DataManager = None,
            config: Dict[str, Any] = None
    ):
        super().__init__(product_parser=product_parser, criteria=criteria, data_manager=data_manager, config=config)

    async def parse_product(self, page) -> None:
        await asyncio.sleep(5)
        status = Status.DONE
        product_object = {}
        try:
            product_object = await self.product_parser.parse_product(page)
        except Exception as e:
            logger.error(f"Couldn't parse product {page.url}. Error: {e}")
            status = status.ERROR

        await page.close()
        if not self.data_manager:
            return

        product_object['url'] = page.url
        product_object['status'] = status

        return product_object

    def get_scrapable_products(self, node, limit=None) -> QuerySet:
        if not self.data_manager:
            return []
        status_values = [Status.PENDING, Status.ERROR, Status.DONE]
        query = \
            Q(status__in=status_values) & \
            Q(url__exists=True) & Q(url__ne='') & \
            Q(scrape=True) & Q(parent=node.id)
        result = self.data_manager.Product.objects.filter(query)
        if limit is not None:
            result = result.limit(limit)
        return result

    def save_product(self, product_object, url):
        if not product_object:
            product_object = {
                'url': url,
                'status': Status.ERROR
            }

        try:
            self.data_manager.update_product(product_object)
        except Exception as e:
            logger.error(f"Save scrape product. Product url: {url}. Error: {e}")
            try:
                product = self.data_manager.Product.objects.get(url=url)
                if product:
                    product.status = Status.ERROR
                    product.save()
            except Exception as e:
                logger.error(f"Couldn't save exception. Product url: {url}. Error: {e}")

    async def scrape_product(self, url=''):
        product_object = {}
        page = None
        try:
            page = await goto_url(self.browser, url, [self.criteria.get_product_suc()])
            product_object = await self.parse_product(page)
        except:
            pass

        if page:
            await page.close()

        self.save_product(product_object, url)

    async def scrape_links(self, urls, chunk_size: int = 15):
        for chunk in generator_split_to_chunks(urls, chunk_size):
            tasks = []
            for url in chunk:
                tasks.append(self.scrape_product(url=url))
            await asyncio.gather(*tasks)

    async def scrape_batch(
            self,
            node: Document,
            products: QuerySet,
            retries: int = 1,
            chunk_size: int = 15
    ) -> None:
        async with async_playwright() as playwright_instance:
            browser: Browser = await playwright_instance.chromium.launch(
                headless=self.config.get('headless', None),
                proxy=self.config.get('proxy', None)
            )

            self.browser: Browser = browser

            ids = [product.id for product in products]

            while retries:
                retries -= 1
                products = self.data_manager.Product.objects(id__in=ids, status__in=[Status.PENDING, Status.ERROR])
                if not products:
                    break

                await self.scrape_links([product.url for product in products], chunk_size=chunk_size)
                # await scrape_url_list(
                #     self.browser,
                #     [product.url for product in products],
                #     [self.criteria.get_product_suc()],
                #     self.parse_product,
                #     chunk_size=chunk_size,
                #     retries=20
                # )

            await browser.close()

            products = self.data_manager.Product.objects(id__in=ids, status=Status.ERROR)
            if products:
                products.update(set__status=Status.DONEERROR)
            node.status = Status.DONE
            node.save()

    async def scrape_products(
            self,
            node: Document,
            retries: int = 1,
            chunk_size: int = 15,
            batch_size: int = 384,
            total_limit: int = None
    ) -> None:
        scrapable_products = self.get_scrapable_products(node, limit=total_limit)

        for products in generator_split_to_chunks(scrapable_products, batch_size):
            await self.scrape_batch(
                node,
                products,
                retries=retries,
                chunk_size=chunk_size
            )
