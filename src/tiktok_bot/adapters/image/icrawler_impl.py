from pathlib import Path
from typing import Sequence

from icrawler.builtin import BaiduImageCrawler, BingImageCrawler, GoogleImageCrawler

from ...domain.models import ImageFetchRequest
from ...ports.image_fetcher import ImageFetcher
from ...utils.paths import list_image_files

_CRAWLERS = {
    "bing": BingImageCrawler,
    "google": GoogleImageCrawler,
    "baidu": BaiduImageCrawler,
}


class ICrawlerImageFetcher(ImageFetcher):
    def __init__(self, provider: str = "bing") -> None:
        if provider not in _CRAWLERS:
            raise ValueError(f"Unsupported provider: {provider}")
        self._provider = provider

    def fetch(self, request: ImageFetchRequest) -> Sequence[Path]:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        crawler_cls = _CRAWLERS[self._provider]
        crawler = crawler_cls(storage={"root_dir": str(request.output_dir)})
        crawler.crawl(keyword=request.query, max_num=request.max_num)
        return list_image_files(request.output_dir)
