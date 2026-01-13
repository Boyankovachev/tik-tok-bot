import configparser
from pathlib import Path
from typing import Optional, Tuple

from ..domain.models import RenderConfig


def load_render_config(config_path: Path) -> Tuple[RenderConfig, Optional[str]]:
    defaults = RenderConfig()
    if not config_path.exists():
        return defaults, None

    parser = configparser.ConfigParser()
    parser.read(config_path)
    section = parser["render"] if parser.has_section("render") else {}

    def _get_value(key: str, cast, default):
        if key not in section:
            return default
        try:
            return cast(section.get(key))
        except (TypeError, ValueError):
            return default

    config = RenderConfig(
        width=_get_value("width", int, defaults.width),
        height=_get_value("height", int, defaults.height),
        fps=_get_value("fps", int, defaults.fps),
        image_duration=_get_value("image_duration", float, defaults.image_duration),
        fade_duration=_get_value("fade_duration", float, defaults.fade_duration),
    )
    output = section.get("output") if "output" in section else None
    return config, output
