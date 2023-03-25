from urllib.parse import urljoin

from config.komputronik.config import BASE_URL


def create_absolute_url(relative_url):
    return urljoin(BASE_URL, relative_url)
