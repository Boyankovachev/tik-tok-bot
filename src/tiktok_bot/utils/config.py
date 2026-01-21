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

    def _get_bool(key: str, default: bool) -> bool:
        if key not in section:
            return default
        value = section.get(key)
        if value is None:
            return default
        value = value.strip().lower()
        if value in ("1", "true", "yes", "y", "on"):
            return True
        if value in ("0", "false", "no", "n", "off"):
            return False
        return default

    def _get_path(key: str, default: Path) -> Path:
        if key not in section:
            return default
        value = section.get(key)
        if value is None:
            return default
        value = value.strip()
        return Path(value) if value else default

    config = RenderConfig(
        width=_get_value("width", int, defaults.width),
        height=_get_value("height", int, defaults.height),
        fps=_get_value("fps", int, defaults.fps),
        image_duration=_get_value("image_duration", float, defaults.image_duration),
        fade_duration=_get_value("fade_duration", float, defaults.fade_duration),
        include_music=_get_bool("include_music", defaults.include_music),
        music_dir=_get_path("music_dir", defaults.music_dir),
    )
    output = section.get("output") if "output" in section else None
    return config, output


def load_server_base_url(config_path: Path) -> Optional[str]:
    if not config_path.exists():
        return None

    parser = configparser.ConfigParser()
    parser.read(config_path)
    if not parser.has_section("server"):
        return None

    base_url = parser["server"].get("base_url", "").strip()
    return base_url or None
