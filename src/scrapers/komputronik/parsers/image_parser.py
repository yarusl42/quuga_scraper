import os

from config.config import assets_folder


def is_valid_url(url):
    if url.startswith("https://static.komputronik.pl/"):
        return True
    return False


def skip_condition(url):
    return not is_valid_url(url)


def filter_images(images_urls):
    return set(images_urls)


def filter_downloaded_urls(downloaded_files, urls):
    downloaded_filenames = set(os.path.basename(f) for f in downloaded_files)
    return [url for url in urls if os.path.basename(url) not in downloaded_filenames]


def extract_products_urls(products):
    res = []
    for product in products:
        if not (product.gallery and isinstance(product.gallery, dict)):
            continue
        images = product.gallery.get('images', [])
        if not (images and isinstance(images, list)):
            continue
        res += images
    return res


def extract_urls(products):
    images_lists = extract_products_urls(products)
    images_lists = filter_images(images_lists)
    downloaded_files = os.listdir(assets_folder)
    images_lists = filter_downloaded_urls(downloaded_files, images_lists)
    return images_lists
