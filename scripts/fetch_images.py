import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tiktok_bot.adapters.image.icrawler_impl import ICrawlerImageFetcher
from tiktok_bot.workflows.fetch_images import fetch_images


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download images for a keyword using icrawler."
    )
    parser.add_argument("query", help="Search keyword, e.g. 'sunset beach'")
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
    parser.add_argument(
        "--output-dir-name",
        default=None,
        help="Optional folder name under the base directory.",
    )
    return parser.parse_args()


def _resolve_path(path_str: str, root: Path) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        return root / path
    return path


def main() -> None:
    args = _parse_args()
    output_base_dir = _resolve_path(args.output_base, ROOT)
    fetcher = ICrawlerImageFetcher(provider=args.provider)
    images = fetch_images(
        query=args.query,
        output_base_dir=output_base_dir,
        fetcher=fetcher,
        max_num=args.max_num,
        output_dir_name=args.output_dir_name,
    )
    if images:
        print(f"Downloaded {len(images)} images to {images[0].parent}")
    else:
        print("No images were downloaded.")


if __name__ == "__main__":
    main()
