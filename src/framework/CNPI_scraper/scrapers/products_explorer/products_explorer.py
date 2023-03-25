from typing import Dict, Any

from mongoengine import Document

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.parsers import ProductParsers
from ...success_criteria import SuccessCriteria
from .product_scraper_base import ProductScraperBase
from .product_cards_scraper import ProductCardsScraper
from .products_scraper import ProductsScraper
from src.framework.CNPI_scraper.models.enums import Status


class ProductsExplorer(ProductScraperBase):
    def __init__(
            self,
            product_parser: ProductParsers = None,
            criteria: SuccessCriteria = None,
            data_manager: DataManager = None,
            config: Dict[str, Any] = None,
    ):
        super().__init__(product_parser=product_parser, criteria=criteria, data_manager=data_manager, config=config)

    async def scrape_products_cards(self, node: Document):
        product_card_scraper = ProductCardsScraper(
            product_parser=self.product_parser,
            criteria=self.criteria,
            data_manager=self.data_manager,
            config=self.config)
        await product_card_scraper.scrape_product_cards(node)

    async def scrape_products(
            self, node: Document,
            chunk_size: int = 15,
            batch_size: int = 384,
            total_limit: int = None,
            retries: int = 10
    ):
        products_scraper = ProductsScraper(
            product_parser=self.product_parser,
            criteria=self.criteria,
            data_manager=self.data_manager,
            config=self.config)
        await products_scraper.scrape_products(
            node,
            chunk_size=chunk_size,
            batch_size=batch_size,
            total_limit=total_limit,
            retries=retries)

    async def scrape_node(
            self,
            node: Document,
            chunk_size: int = 15,
            batch_size: int = 384,
            total_limit: int = None,
            retries: int = 10
    ) -> None:
        await self.scrape_products_cards(node)
        await self.scrape_products(
            node,
            chunk_size=chunk_size,
            batch_size=batch_size,
            total_limit=total_limit,
            retries=retries
        )

    async def scrape(
            self,
            chunk_size: int = 15,
            batch_size: int = 384,
            total_limit: int = None,
            retries: int = 10
    ) -> None:
        nodes = self.data_manager.Node.objects.filter(scrape=True, status=Status.PENDING)
        for node in nodes:
            await self.scrape_node(
                node,
                chunk_size=chunk_size,
                batch_size=batch_size,
                total_limit=total_limit,
                retries=retries
            )
