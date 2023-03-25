import asyncio
from typing import Dict, List, Union, Awaitable, Any

from mongoengine import Document, QuerySet
from mongoengine import Q
from playwright.async_api import Browser
from playwright.async_api import Page, async_playwright

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.models.enums import Status
from src.framework.CNPI_scraper.parsers import CategoryNodeParsers
from src.framework.CNPI_scraper.success_criteria import SuccessCriteria
from src.framework.safe_scraper import repeat_scrape_until_suc
from src.utils.logger import logger


class CNBuilder:
    def __init__(
            self,
            parsers: CategoryNodeParsers,
            data_manager: DataManager,
            criteria: SuccessCriteria,
            config: Dict[str, Any] = {}
    ):
        self.browser: Browser = None
        self.parsers: CategoryNodeParsers = parsers
        self.criteria: SuccessCriteria = criteria
        self.data_manager: DataManager = data_manager
        self.config: Dict[str, Any] = config

    def set_categories_settings(self, categories_objects: List[Dict[str, Any]]):
        if not self.data_manager:
            return
        for category_object in categories_objects:
            self.data_manager.update_category(category_object)

    def cleanup(self):
        if not self.data_manager:
            return
        nodes = self.data_manager.Node.objects.all()
        for node in nodes:
            node.parents = node.pending_parents
            node.pending_parents = []
            node.save()

        self.data_manager.Category.objects(build_tree=True, status=Status.PENDING).update(set__status=Status.DONE)

    async def scrape_node(self, page: Page, category: Document, depth: int):
        node_object: Dict[str, Any] = await self.parsers.parse_node_object(page)
        if not self.data_manager:
            return []

        try:
            node_object['status'] = Status.PENDING
            self.data_manager.update_node(category=category, node_object=node_object)
        except Exception as e:
            category_id = None
            if category and category.id:
                category_id = category_id
                node = self.data_manager.Node(parents=[category.id], status=Status.ERROR)
                node.save()

            logger.error(f"Couldn't save node. depth: {depth}. Parent: {category_id}. {e}")

        await page.close()
        return []

    async def parse_category_info(self, page: Page, category: Document):
        if not self.data_manager:
            return

        category_object = await self.parsers.parse_category_object(page)
        category_object['url'] = category.url
        category_object['parent'] = category.parent
        self.data_manager.update_category(category_object)

    async def scrape_category(self, page: Page, category: Document, depth: int):
        await self.parse_category_info(page, category)
        category_urls = await self.parsers.get_categories_urls(page)
        await page.close()

        categories = []
        for category_url in category_urls:
            child_category_object = {
                "url": category_url,
                "parent": category.id,
                "scrape": category.scrape,
                "build_tree": category.build_tree,
                "depth": depth,
                "status": Status.PENDING
            }
            if not self.data_manager:
                continue
            try:
                child_category = self.data_manager.update_category(child_category_object)
            except Exception as e:
                category_id = None

                if category and category.id:
                    category_id = category.id
                    self.data_manager.Category.update_category({  # TODO: fix that
                        "url": category_url,
                        "parent": category_id,
                        "status": Status.ERROR
                    })

                logger.error(
                    f"Couldn't save category. Is category None: {category is None}, depth: {depth}. Parent: {category_id}. {e}")
                continue
            categories.append(child_category)

        return categories

    async def get_page_type(self, category_url: str) -> Union[str, None]:
        node_criteria: str = self.criteria.get_node_criteria()
        category_suc: str = self.criteria.get_category_suc()
        scrapers_suc: List[str] = [category_suc, node_criteria]
        try:
            page: Page = await repeat_scrape_until_suc(self.browser, category_url, scrapers_suc, retries=20)
            for scraper_suc in scrapers_suc:
                els = await page.query_selector_all(scraper_suc)
                if len(els):
                    return scraper_suc, page
        except:
            raise Exception(f"Couldn't find a scraper for category {category_url}")

    async def get_scrape_function(self, page_type: str):
        if page_type == self.criteria.get_category_suc():
            return self.scrape_category
        if page_type == self.criteria.get_node_criteria():
            return self.scrape_node

    async def scrape_category_or_node(self, category: Document, depth: int):
        page_type, page = await self.get_page_type(category.url)
        if None:
            logger.error(f"Couldn't find out the page type for category: {category.str_id}. depth: {depth}")
            category.status = Status.ERROR
            category.depth = depth
            category.save()
        else:
            scrape_function: Awaitable = await self.get_scrape_function(page_type)
            return await scrape_function(page, category, depth)

    async def scrape_categories(self, categories: List[Document], depth=0):
        tasks = []
        children = []
        for category in categories:
            tasks.append(self.scrape_category_or_node(category, depth))

        if tasks:
            children = await asyncio.gather(*tasks)

        for child in children:
            if child:
                await self.scrape_categories(child, depth=depth + 1)

    async def build(self, categories_objects: List[Dict], retries: int = 20):
        self.set_categories_settings(categories_objects)

        status_values: List[str] = [Status.PENDING, Status.ERROR]
        if not self.data_manager:
            return []

        categories: List[Document] = self.data_manager.Category.objects.filter(
            build_tree=True,
            status__in=status_values,
            parent=None
        )

        async with async_playwright() as playwright_instance:
            browser: Browser = await playwright_instance.chromium.launch(
                headless=self.config.get('headless', True), proxy=self.config.get('proxy', None)
            )
            self.browser: Browser = browser
            while retries:
                await self.scrape_categories(categories)

                if not self.data_manager:
                    return

                categories: QuerySet[Document] = self.data_manager.Category.objects.filter(
                    Q(status__in=status_values) & Q(url__exists=True) & Q(url__ne='')
                )
                if not categories:
                    break
                retries -= 1

            if not retries:
                logger.debug("Coulnd't scrape some failed urls")
            self.cleanup()

            await browser.close()
