from pathlib import Path
from typing import Optional

from ..domain.models import RenderConfig, RenderRequest
from ..ports.video import VideoRenderer
from ..utils.paths import list_image_files


def build_video(
    image_dir: Path,
    output_path: Path,
    renderer: VideoRenderer,
    config: Optional[RenderConfig] = None,
) -> Path:
    if config is None:
        config = RenderConfig()

    images = list_image_files(image_dir)
    if not images:
        raise ValueError(f"No images found in {image_dir}")

    request = RenderRequest(images=images, output_path=output_path, config=config)
    return renderer.render(request)
