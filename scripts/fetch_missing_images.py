import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tiktok_bot.adapters.image.icrawler_impl import ICrawlerImageFetcher
from tiktok_bot.utils.paths import list_image_files, resolve_relative
from tiktok_bot.utils.schedule import find_field, is_truthy, load_schedule, save_schedule
from tiktok_bot.workflows.fetch_images import fetch_images


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch images for schedule rows missing images."
    )
    parser.add_argument(
        "--csv",
        default=str(ROOT / "schedule.csv"),
        help="Path to schedule CSV.",
    )
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
        help="Maximum number of images to download per row.",
    )
    parser.add_argument(
        "--output-base",
        default=str(ROOT / "assets" / "images"),
        help="Base directory for downloaded images.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    csv_path = resolve_relative(Path(args.csv), ROOT)
    output_base = resolve_relative(Path(args.output_base), ROOT)

    fieldnames, rows = load_schedule(csv_path)
    name_key = find_field(fieldnames, ["Name"])
    has_images_key = find_field(fieldnames, ["Has images", "Has Images", "HasImages"])

    fetcher = ICrawlerImageFetcher(provider=args.provider)
    updated = 0

    for row in rows:
        name = (row.get(name_key) or "").strip()
        if not name:
            continue
        has_images_value = row.get(has_images_key, "")
        if is_truthy(has_images_value):
            continue

        output_dir = output_base / name
        if output_dir.exists() and list_image_files(output_dir):
            row[has_images_key] = "YES"
            updated += 1
            continue

        try:
            images = fetch_images(
                query=name,
                output_base_dir=output_base,
                fetcher=fetcher,
                max_num=args.max_num,
                output_dir_name=name,
            )
            if images:
                row[has_images_key] = "YES"
                updated += 1
        except Exception as exc:
            print(f"Failed to fetch images for '{name}': {exc}")

    if updated:
        save_schedule(csv_path, fieldnames, rows)

    print(f"Updated {updated} rows in {csv_path}")


if __name__ == "__main__":
    main()
