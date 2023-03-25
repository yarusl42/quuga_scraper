from typing import Any, Dict

from playwright.async_api import Browser

from src.framework.CNPI_scraper.data_manager.data_manager import DataManager
from src.framework.CNPI_scraper.parsers import ProductParsers
from src.framework.CNPI_scraper.success_criteria import SuccessCriteria


class ProductScraperBase:
    def __init__(
            self,
            product_parser: ProductParsers = None,
            criteria: SuccessCriteria = None,
            data_manager: DataManager = None,
            config: Dict[str, Any] = None
    ):
        self.browser: Browser = None
        self.product_parser: ProductParsers = product_parser
        self.criteria: SuccessCriteria = criteria
        self.data_manager: DataManager = data_manager
        self.config: Dict[str, Any] = None
        if config:
            self.config = config
