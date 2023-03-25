from mongoengine import StringField, ReferenceField, BooleanField, IntField

from src.framework.CNPI_scraper.models.base_document import BaseDocument
from src.scrapers.komputronik.utils.get_absolute_url import create_absolute_url


class CategoryKomputronik(BaseDocument):
    name = StringField()
    parent = ReferenceField('self')
    url = StringField(required=True, unique=False)
    build_tree = BooleanField(default=True)
    depth = IntField()

    def update(self, **kwargs):
        current_url = kwargs.get('url', None) or self.url
        if current_url and current_url.startswith('/'):
            current_url = create_absolute_url(current_url)
            kwargs['url'] = current_url

        res = super(CategoryKomputronik, self).update(**kwargs)

        return res

    def save(self, *args, **kwargs):
        if self.url and self.url.startswith('/'):
            self.url = create_absolute_url(self.url)

        res = super(CategoryKomputronik, self).save(*args, **kwargs)
        return res
