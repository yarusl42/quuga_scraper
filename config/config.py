import os

from dotenv import load_dotenv

load_dotenv()

parent_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
assets_folder = os.path.join(parent_dir, 'assets')

HEADLESS = True
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

PROXY = {
    "server": os.getenv("PROXY"),
    "username": os.getenv("PROXY_USER"),
    "password": os.getenv("PROXY_PASSWORD"),
}

SETTINGS = {
    "proxy": PROXY,
    "headless": HEADLESS,
    "debug": DEBUG
}

categories_collection = "categories"
nodes_collection = "nodes"
products_collection = "products"
temp_nodes_collection = "temp_nodes"
