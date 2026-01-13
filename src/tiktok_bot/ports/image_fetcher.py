from pathlib import Path
from typing import Protocol, Sequence

from ..domain.models import ImageFetchRequest


class ImageFetcher(Protocol):
    def fetch(self, request: ImageFetchRequest) -> Sequence[Path]:
        """Fetch images based on the request and return the saved files."""
        raise NotImplementedError
