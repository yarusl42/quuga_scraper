import datetime
from typing import Dict, Union

from mongoengine import Document, EnumField, BooleanField, DateTimeField

from src.framework.CNPI_scraper.models.enums import Status


class BaseDocument(Document):
    meta: Dict[str, Union[bool, str]] = {'allow_inheritance': True,
                                         'abstract': True,
                                         'strict': False}

    status = EnumField(Status, default=Status.PENDING)
    scrape = BooleanField(default=True)

    created_at = DateTimeField()
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    is_archived = BooleanField(default=False)

    @property
    def str_id(self):
        return str(self.id)

    def __repr__(self):
        return '{} {}'.format(self.__class__.__name__, self.str_id)

    def update(self, *args, **kwargs):
        if kwargs.get('prevent_update_date') is not True:
            kwargs['updated_at'] = datetime.datetime.utcnow()

        if not kwargs.get('status'):
            kwargs['status'] = Status.PENDING

        res = super().update(*args, **kwargs)

        return res

    def save(self, *args, **kwargs):
        if not self.status:
            self.status = Status.PENDING

        if not self.created_at:
            self.created_at = datetime.datetime.utcnow()
        if kwargs.get('prevent_update_date') is not True:
            self.updated_at = datetime.datetime.utcnow()

        res = super(BaseDocument, self).save(*args, **kwargs)

        return res

    def get_message_type(self):
        if self.is_deleted:
            message_type = 'deleted'
        elif self.created_at:
            message_type = 'updated'
        else:
            message_type = 'created'
        return message_type

    def to_dict(self, include_deleted=False):
        dic = self.to_mongo().to_dict()
        dic.pop('_cls')
        dic['id'] = dic.pop('_id', None)
        if not include_deleted:
            dic.pop('is_deleted', None)
        return dic

    def set_if_empty(self, attr, value):
        if not getattr(self, attr):
            setattr(self, attr, value)
