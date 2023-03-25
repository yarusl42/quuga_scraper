from typing import Callable, Any, List, Tuple


class ImageParser:
    def __init__(
            self,
            target,
            extract_urls: Callable = None,
            preprocess: Callable = None,
            skip_condition: Callable = None,
            validate_image_integrity: Callable = None
    ):
        self.target: str = target
        self._skip_condition = skip_condition
        self._extract_urls = extract_urls
        self._preprocess = preprocess
        self._validate_image_integrity = validate_image_integrity

    def skip_condition(self, url: str) -> bool:
        if self._skip_condition:
            return self._skip_condition(url)
        return False

    def extract_urls(self, items: List[Any]) -> List[str]:
        if self._extract_urls:
            return self._extract_urls(items)
        return []

    def preprocess(self, image_url: str, new_path: str) -> Tuple[str, str]:
        if self._preprocess:
            return self._preprocess(image_url, new_path)
        return image_url, new_path

    def validate_image_integrity(self, image_path: str) -> bool:
        if self._validate_image_integrity:
            return self._validate_image_integrity(image_path)
        return True
