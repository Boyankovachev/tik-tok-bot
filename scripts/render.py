import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CONFIG_PATH = ROOT / "config.ini"

from tiktok_bot.adapters.video.moviepy_impl import MoviePyRenderer
from tiktok_bot.domain.models import RenderConfig
from tiktok_bot.utils.config import load_render_config
from tiktok_bot.workflows.build_video import build_video
from tiktok_bot.utils.paths import resolve_relative


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a TikTok-style video from a folder of images."
    )
    parser.add_argument(
        "--input-dir",
        default=str(ROOT / "assets" / "images"),
        help="Directory containing input images.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path or directory.",
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
    input_dir = resolve_relative(Path(args.input_dir), ROOT)
    file_config, file_output = load_render_config(CONFIG_PATH)
    output_raw = args.output or file_output or str(ROOT / "outputs" / "renders" / "render.mp4")
    output_path = _resolve_output_path(resolve_relative(Path(output_raw), ROOT))
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
    renderer = MoviePyRenderer()
    build_video(
        image_dir=input_dir,
        output_path=output_path,
        renderer=renderer,
        config=config,
    )
    print(f"Wrote video to {output_path}")


if __name__ == "__main__":
    main()
