from mongoengine import StringField

from src.framework.CNPI_scraper.models.base_document import BaseDocument


class ImageKomputronik(BaseDocument):
    origin = StringField()
    target = StringField()
