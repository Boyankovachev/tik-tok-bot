from dataclasses import replace
from pathlib import Path
from typing import Optional

from ..domain.models import RenderConfig, RenderRequest
from ..ports.video import VideoRenderer
from ..utils.paths import list_image_files
from ..utils.timing_table import (
    DEFAULT_FADE_DURATION,
    SLIDESHOW_IMAGE_DURATIONS,
    resolve_image_duration,
)


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

    image_duration = resolve_image_duration(
        len(images), SLIDESHOW_IMAGE_DURATIONS, config.image_duration
    )
    config = replace(
        config,
        image_duration=image_duration,
        fade_duration=DEFAULT_FADE_DURATION,
    )

    request = RenderRequest(images=images, output_path=output_path, config=config)
    return renderer.render(request)
