from urllib.request import urlretrieve
from pathlib import Path


class URL:
    def __init__(self, url: str) -> None:
        self.url = url

    def download_image(self, file_path: Path) -> None:
        urlretrieve(self.url, str(file_path))

    def __str__(self) -> str:
        return self.url
