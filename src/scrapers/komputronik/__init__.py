from .models import Category, Node
from src.scrapers.komputronik.parsers.category_parsers import get_categories_urls, parse_title_field
from src.scrapers.komputronik.parsers.node_parsers import parse_product_counter
from .utils.get_absolute_url import create_absolute_url


