import os

from dotenv import load_dotenv

load_dotenv()

parent_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
assets_folder = os.path.join(parent_dir, 'assets')

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
HEADLESS = True
DEBUG = os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

proxy = {
    "server": os.getenv("PROXY"),
    "username": os.getenv("PROXY_USER"),
    "password": os.getenv("PROXY_PASSWORD"),
}

settings = {
    "proxy": proxy,
    "headless": HEADLESS,
    "debug": DEBUG
}
