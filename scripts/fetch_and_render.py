import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CONFIG_PATH = ROOT / "config.ini"

from tiktok_bot.adapters.image.icrawler_impl import ICrawlerImageFetcher
from tiktok_bot.adapters.video.moviepy_impl import MoviePyRenderer
from tiktok_bot.domain.models import RenderConfig
from tiktok_bot.utils.config import load_render_config
from tiktok_bot.utils.paths import resolve_relative
from tiktok_bot.workflows.build_video import build_video
from tiktok_bot.workflows.fetch_images import fetch_images


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download images for a keyword and render a video."
    )
    parser.add_argument("name", help="Keyword and folder name.")
    parser.add_argument(
        "--provider",
        choices=["bing", "google", "baidu"],
        default="bing",
        help="Image search provider.",
    )
    parser.add_argument(
        "--max-num",
        type=int,
        default=30,
        help="Maximum number of images to download.",
    )
    parser.add_argument(
        "--output-base",
        default=str(ROOT / "assets" / "images"),
        help="Base directory for downloaded images.",
    )
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--fps", type=int, default=None)
    parser.add_argument("--image-duration", type=float, default=None)
    parser.add_argument("--fade-duration", type=float, default=None)
    return parser.parse_args()


def _resolve_output_path(path: Path) -> Path:
    if path.suffix.lower() != ".mp4":
        if path.suffix == "":
            return path / "render.mp4"
        return path.with_suffix(".mp4")
    return path


def main() -> None:
    args = _parse_args()
    name = args.name
    output_base = resolve_relative(Path(args.output_base), ROOT)

    fetcher = ICrawlerImageFetcher(provider=args.provider)
    images = fetch_images(
        query=name,
        output_base_dir=output_base,
        fetcher=fetcher,
        max_num=args.max_num,
        output_dir_name=name,
    )
    if not images:
        raise RuntimeError("No images were downloaded.")

    file_config, _ = load_render_config(CONFIG_PATH)
    config = RenderConfig(
        width=args.width if args.width is not None else file_config.width,
        height=args.height if args.height is not None else file_config.height,
        fps=args.fps if args.fps is not None else file_config.fps,
        image_duration=(
            args.image_duration
            if args.image_duration is not None
            else file_config.image_duration
        ),
        fade_duration=(
            args.fade_duration if args.fade_duration is not None else file_config.fade_duration
        ),
    )

    output_path = _resolve_output_path(
        resolve_relative(Path("outputs") / "renders" / f"{name}.mp4", ROOT)
    )
    renderer = MoviePyRenderer()
    build_video(
        image_dir=output_base / name,
        output_path=output_path,
        renderer=renderer,
        config=config,
    )
    print(f"Wrote video to {output_path}")


if __name__ == "__main__":
    main()
