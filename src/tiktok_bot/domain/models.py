from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class RenderConfig:
    width: int = 1080
    height: int = 1920
    fps: int = 30
    image_duration: float = 2.0
    fade_duration: float = 0.2


@dataclass(frozen=True)
class RenderRequest:
    images: Sequence[Path]
    output_path: Path
    config: RenderConfig


@dataclass(frozen=True)
class ImageFetchRequest:
    query: str
    output_dir: Path
    max_num: int = 30
