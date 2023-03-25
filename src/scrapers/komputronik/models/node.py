from mongoengine import ReferenceField, ListField, EnumField, IntField, StringField

from src.framework.CNPI_scraper.models.base_document import BaseDocument
from src.framework.CNPI_scraper.models.enums import Status
from .category import CategoryKomputronik
from ..utils.get_absolute_url import create_absolute_url


class NodeKomputronik(BaseDocument):
    url = StringField(required=True)
    parents = ListField(ReferenceField(CategoryKomputronik), default=[])
    pending_parents = ListField(ReferenceField(CategoryKomputronik), default=[])
    status = EnumField(Status, default=Status.PENDING)
    product_counter = IntField(default=0)
    name = StringField()

    class NodeKomputronik(BaseDocument):
        url = StringField(required=True)
        parents = ListField(ReferenceField(CategoryKomputronik), default=[])
        pending_parents = ListField(ReferenceField(CategoryKomputronik), default=[])
        status = EnumField(Status, default=Status.PENDING)
        product_counter = IntField(default=0)
        name = StringField()

        def update(self, **kwargs):
            current_url = kwargs.get('url', None) or self.url
            if current_url and current_url.startswith('/'):
                current_url = create_absolute_url(current_url)
                kwargs['url'] = current_url

            res = super(NodeKomputronik, self).update(**kwargs)

            return res

        def save(self, *args, **kwargs):
            if self.url and self.url.startswith('/'):
                self.url = create_absolute_url(self.url)

            res = super(NodeKomputronik, self).save(*args, **kwargs)
            return res
