import asyncio
import os
import random
from urllib.parse import urlparse

import aiohttp

from src.utils.logger import logger
from .headers import user_agents, default_headers
from ..helpers import generator_split_to_chunks, create_parent_dirs


class Retriever:
    def __init__(
            self,
            proxy={},
            languages=[],
            lang_percentage=(),
            set_user_agent=True,
            set_headers=True,
            should_create_parent_dirs=True
    ):
        self.should_create_parent_dirs = should_create_parent_dirs
        self.proxy_auth = self._get_proxy(proxy)
        self.proxy_host = self._get_proxy_server(proxy)
        self.with_proxy = (self.proxy_auth and self.proxy_host)
        self.headers = self._generate_headers(set_headers, set_user_agent, languages, lang_percentage)

    @staticmethod
    def _get_proxy_server(proxy_dict):
        if not proxy_dict:
            return None
        proxy_host = proxy_dict.get('server')
        proxy_host = "http://" + proxy_host.lstrip('https://').lstrip('http://')
        return proxy_host

    @staticmethod
    def _get_proxy(proxy_dict):
        proxy_username = proxy_dict.get('username')
        proxy_password = proxy_dict.get('password')
        if proxy_username and proxy_password:
            return aiohttp.BasicAuth(login=proxy_username, password=proxy_password)
        return None

    @staticmethod
    def _generate_headers(set_headers, set_user_agent, languages, lang_percentage):
        new_headers = {}
        if set_headers:
            new_headers.update(default_headers)

        if set_user_agent:
            user_agent = random.choice(user_agents)
            user_agent_headers = {'User-Agent': user_agent}
            new_headers.update(user_agent_headers)

        if languages:
            lang_headers = {}
            if len(languages) > 1:
                lang_headers['Accept-Language'] = \
                    f"{','.join(languages)};q={random.randint(lang_percentage[1], lang_percentage[0]) / 10}"
            else:
                lang_headers['Accept-Language'] = f"{languages[0]}"
            new_headers.update(lang_headers)

        return new_headers

    @staticmethod
    async def _write_content_to_file(response, file_path):
        with open(file_path, 'wb') as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)

    @staticmethod
    async def _safe_download(file_path, file_url, download_method, max_attempts=1):
        for i in range(max_attempts):
            try:
                logger.info(f"Attempting to download file from {file_url}")
                res = await download_method(file_path, file_url)
                logger.info(f"File downloaded successfully from {file_url}")
                return res
            except Exception as e:
                logger.warning(f"Attempt {i + 1} failed: {e}")
        logger.error(f"All {max_attempts} attempts failed to download the file from {file_url}")
        return None

    async def _proxy_download(self, file_path, file_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, proxy=self.proxy_host, proxy_auth=self.proxy_auth,
                                   headers=self.headers) as response:
                if self.should_create_parent_dirs:
                    create_parent_dirs(file_path)

                await self._write_content_to_file(response, file_path)
                return file_path

    async def _no_proxy_download(self, file_path, file_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url, headers=self.headers) as response:
                if self.should_create_parent_dirs:
                    create_parent_dirs(file_path)

                await self._write_content_to_file(response, file_path)
                return file_path

    async def _download(self, file_path, file_url):
        if self.with_proxy:
            return await self._proxy_download(file_path, file_url)
        else:
            return await self._no_proxy_download(file_path, file_url)

    async def _download_to_folder(self, folder_path, file_url):
        filename = os.path.basename(urlparse(file_url).path)
        file_path = os.path.join(folder_path, filename)

        return await self._download(file_path, file_url)

    async def download_to_folder(self, folder_path, file_url, max_attempts=1):
        return await self._safe_download(folder_path, file_url, self._download_to_folder, max_attempts=max_attempts)

    async def download(self, file_path, file_url, max_attempts=1):
        return await self._safe_download(file_path, file_url, self._download, max_attempts=max_attempts)

    async def many_download_to_folder(self, folder_path, file_urls, callback=None, max_attempts=1, chunk_size=10):
        downloaded = []
        for chunk in generator_split_to_chunks(file_urls, chunk_size):
            tasks = []
            for file_url in chunk:
                async def download_method(_file_url=""):
                    new_path = await self.download_to_folder(folder_path, _file_url, max_attempts=max_attempts)
                    if callback:
                        callback(_file_url, new_path)

                task = download_method(_file_url=file_url)
                tasks.append(task)

            downloaded_chunk = await asyncio.gather(*tasks)
            downloaded.append(downloaded_chunk)
