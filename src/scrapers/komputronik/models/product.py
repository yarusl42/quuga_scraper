from mongoengine import \
    StringField, ReferenceField, \
    IntField, DictField, \
    BooleanField, FloatField, \
    ListField

from src.framework.CNPI_scraper.models.base_document import BaseDocument
from src.scrapers.komputronik.utils.get_absolute_url import create_absolute_url
from .category import CategoryKomputronik


class ProductKomputronik(BaseDocument):
    name = StringField()
    parent = ReferenceField(CategoryKomputronik)
    url = StringField(required=True, unique=False)
    price = IntField()
    description = StringField()
    producer_description = StringField()
    gallery = DictField()
    has_free_shipping = BooleanField()
    is_company = BooleanField()
    is_buyable = BooleanField()
    leaseLink = DictField()
    productId = IntField()
    rating = FloatField()
    reviews_by_stars = ListField()
    shipping_details = DictField()
    specs = DictField()

    def update(self, **kwargs):
        current_url = kwargs.get('url', None) or self.url
        if current_url and current_url.startswith('/'):
            current_url = create_absolute_url(current_url)
            kwargs['url'] = current_url

        res = super(ProductKomputronik, self).update(**kwargs)

        return res

    def save(self, *args, **kwargs):
        if self.url and self.url.startswith('/'):
            self.url = create_absolute_url(self.url)

        res = super(ProductKomputronik, self).save(*args, **kwargs)
        return res
