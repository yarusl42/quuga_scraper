products_collection = None
urls_collection = None


def get_urls_collection():
    return urls_collection


def get_products_collection():
    return products_collection


def set_urls_collection(collection):
    global urls_collection
    urls_collection = collection


def set_products_collection(collection):
    global products_collection
    products_collection = collection


