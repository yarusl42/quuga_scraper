from typing import Dict, Any, List

from mongoengine import Document

from src.framework.CNPI_scraper.models.enums import Status
from src.framework.CNPI_scraper.parsers.image_parser import ImageParser
from src.utils.lang_header.lang_header import LangHeader
from src.utils.retriever import Retriever


class ImagesScraper:
    def __init__(
            self,
            Image: Document,
            image_parser: ImageParser,
            lang_header_object: LangHeader = None,
            config: Dict[str, Any] = None
    ):
        self.image_parser = image_parser
        self.Image = Image
        self.retriever = Retriever(
            languages=lang_header_object
        )
        if config:
            self.config = config
        else:
            self.config = {}

    def update_image(self, image_object: Dict[str, Any]) -> None:
        try:
            image = self.Image.objects.get(origin=image_object['origin'])
            image.status = image_object['status']
            image.save()
        except Exception as e:
            image = self.Image(**image_object)
            image.save()

    def get_image_object(self, image_url: str, new_path: str):
        image_url, new_path = self.image_parser.preprocess(image_url, new_path)
        image_object = {
            'origin': image_url,
            'target': new_path,
            'status': Status.DONE,
        }

        is_image_valid: bool = self.image_parser.validate_image_integrity(new_path)

        if not is_image_valid:
            image_object['target'] = None

        if not (image_url and is_image_valid):
            image_object['status'] = Status.ERROR
        return image_object

    def save_image(self, image_url: str, new_path: str):
        image_object: Dict[str, Any] = self.get_image_object(image_url, new_path)
        self.update_image(image_object)

    async def scrape(self, products: List[Document], max_attempts: int = 10, chunk_size: int = 200):
        images_urls: List[str] = list(self.image_parser.extract_urls(products))
        skip_urls: List[str] = []
        for image_url in images_urls:
            if self.image_parser.skip_condition(image_url):
                skip_urls.append(image_url)

        images_urls: set = set(images_urls) - set(skip_urls)
        await self.retriever.many_download_to_folder(
            self.image_parser.target,
            images_urls,
            callback=self.save_image,
            max_attempts=max_attempts,
            chunk_size=chunk_size
        )
