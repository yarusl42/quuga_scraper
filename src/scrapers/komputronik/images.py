import os

from src.utils.helpers import create_parent_dirs_dirpath
from src.utils.logger import logger
from src.utils.retriever import Retriever
from .storage import get_products_collection


def get_images_from_doc(document):
    gallery = document.get('gallery', None)
    if gallery is None:
        logger.error(f"BROKENDOC: Couldn't find gallery for {document['_id']}")
        return None

    images = gallery.get('images', None)
    if images is None:
        logger.error(f"BROKENDOC: Couldn't find images in gallery of document {document['_id']}")
        return None

    if images is None:
        logger.error(f"BROKENDOC: Couldn't find images in gallery of document {document['_id']}")
        return None

    if not images:
        logger.error(f"BROKENDOC: No images found for {document['_id']}")
        return None

    if any([img is None for img in images]):
        logger.error(f"BROKENDOC: faulty images in {document['_id']}")
        return None

    return images


def get_image_urls(collection):
    res = []
    for document in collection.find():
        images = get_images_from_doc(document)
        if images is None:
            continue

        res += images
    return res


def filter_images(images_urls):
    images_urls = [img.replace('product-picture/4/', 'product-picture/6/')
                   for img in images_urls
                   if not img.startswith("https://img.youtube.com")]

    return list(set(images_urls))


def filter_downloaded_urls(downloaded_files, urls):
    downloaded_filenames = set(os.path.basename(f) for f in downloaded_files)
    return [url for url in urls if os.path.basename(url) not in downloaded_filenames]


async def retrieve_files(proxy, target_folder, images_urls, callback):
    retriever = Retriever(
        languages=("pl", "de"),
        lang_percentage=(9, 1)
    )
    await retriever.many_download_to_folder(
        target_folder,
        images_urls,
        callback=callback,
        max_attempts=10,
        chunk_size=200)


def image_versions_generator(image_url):
    yield image_url.replace('product-picture/6/', 'product-picture/4/')
    yield image_url.replace('product-picture/4/', 'product-picture/6/')


def save_image_path_to_db_callback(image_url, image_path):
    collection = get_products_collection()
    for image_url_version in image_versions_generator(image_url):
        for doc in collection.find({"gallery.images": {"$elemMatch": {"$eq": image_url_version}}}):
            if "local_gallery" not in doc:
                doc["local_gallery"] = {}
            if "images" not in doc["local_gallery"]:
                doc["local_gallery"]["images"] = []

            doc["local_gallery"]["images"].append(image_path)
            collection.replace_one({"_id": doc["_id"]}, doc)


async def skip_downloaded_download_images(proxy, target_folder):
    create_parent_dirs_dirpath(target_folder)
    products_collection = get_products_collection()
    images_urls = get_image_urls(products_collection)
    images_urls = filter_images(images_urls)

    downloaded_files = os.listdir(target_folder)
    images_urls = filter_downloaded_urls(downloaded_files, images_urls)
    await retrieve_files(proxy, target_folder, images_urls, save_image_path_to_db_callback)


async def download_images(proxy, target_folder):
    products_collection = get_products_collection()
    images_urls = get_image_urls(products_collection)
    images_urls = filter_images(images_urls)

    await retrieve_files(proxy, target_folder, images_urls, save_image_path_to_db_callback)
