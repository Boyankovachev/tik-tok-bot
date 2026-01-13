from pathlib import Path
from typing import Optional, Sequence

from ..domain.models import ImageFetchRequest
from ..ports.image_fetcher import ImageFetcher
from ..utils.paths import safe_dir_name


def fetch_images(
    query: str,
    output_base_dir: Path,
    fetcher: ImageFetcher,
    max_num: int = 30,
    output_dir_name: Optional[str] = None,
) -> Sequence[Path]:
    if not query.strip():
        raise ValueError("Query must be a non-empty string.")

    folder_name = output_dir_name or safe_dir_name(query)
    output_dir = output_base_dir / folder_name
    request = ImageFetchRequest(query=query, output_dir=output_dir, max_num=max_num)
    return fetcher.fetch(request)
