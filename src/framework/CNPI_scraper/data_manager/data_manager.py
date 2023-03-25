from typing import Callable, Any, Dict, List

from bson import ObjectId
from mongoengine import Document


# noinspection PyCallingNonCallable
class DataManager:
    def __init__(
            self,
            create_absolute_url: Callable = None,
            Category: Document = None,
            Node: Document = None,
            Product: Document = None
    ):
        self.create_absolute_url = create_absolute_url
        self.Category = Category
        self.Node = Node
        self.Product = Product

    def update_category(self, category_object: Dict[str, Any]) -> Document:
        category_object['url']: str = self.create_absolute_url(category_object.get('url'))
        try:
            category: Document = self.Category.objects.get(
                url=category_object.get('url'),
                parent=category_object.get('parent', None)
            )
            category.update(upsert=True, **category_object)
            return category
        except self.Category.DoesNotExist:
            category: Document = self.Category(**category_object)
            category.save()
            return category

    def update_product(self, product_object: Dict[str, Any]) -> Document:
        current_url: str = self.create_absolute_url(product_object.get('url', None))
        try:
            product: Document = self.Product.objects.get(
                url=current_url,
            )
            product.update(**product_object)
            return product
        except self.Product.DoesNotExist:
            product_object['url'] = current_url
            product = self.Product(**product_object)
            product.save()
            return product

    def update_node(self, category: Document, node_object: Dict[str, Any]) -> Document:
        current_url: str = self.create_absolute_url(category.url)
        try:
            node: Document = self.Node.objects.get(
                url=current_url,
            )
            pending_parents: List[ObjectId] = node.pending_parents
            if category.id not in pending_parents:
                pending_parents.append(category.id)
            node.update(**node_object, pending_parents=pending_parents)
            return node
        except self.Node.DoesNotExist:
            node: Document = self.Node(**node_object, name=category.name, url=current_url,
                                       pending_parents=[category.id])
            node.save()
            return node
