import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

CONFIG_PATH = ROOT / "config.ini"
DEFAULT_ENDPOINT = "api/v1/social-media/location/random"

from tiktok_bot.adapters.video.moviepy_impl import MoviePyRenderer
from tiktok_bot.utils.config import load_render_config, load_server_base_url
from tiktok_bot.utils.paths import SUPPORTED_IMAGE_EXTS, resolve_relative, safe_dir_name
from tiktok_bot.workflows.build_video import build_video


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a random location from the configured server endpoint."
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override the server base URL from config.ini.",
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
        help=f"Endpoint path to call (default: {DEFAULT_ENDPOINT}).",
    )
    return parser.parse_args()


def _build_url(base_url: str, endpoint: str) -> str:
    base = base_url.rstrip("/") + "/"
    return urljoin(base, endpoint.lstrip("/"))


def _choose_extension(url: str, content_type: str) -> str:
    ext = Path(urlparse(url).path).suffix.lower()
    if ext in SUPPORTED_IMAGE_EXTS:
        return ext
    content_type = content_type.lower()
    if "png" in content_type:
        return ".png"
    if "webp" in content_type:
        return ".webp"
    if "bmp" in content_type:
        return ".bmp"
    if "tiff" in content_type:
        return ".tiff"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    return ".jpg"


def _download_images(image_urls: list[str], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    for index, url in enumerate(image_urls, start=1):
        if not url:
            continue
        request = Request(url, headers={"Accept": "image/*"})
        try:
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "")
                ext = _choose_extension(url, content_type)
                output_path = output_dir / f"{index:03d}{ext}"
                output_path.write_bytes(response.read())
        except (HTTPError, URLError) as exc:
            print(f"Failed to download {url}: {exc}", file=sys.stderr)
            continue
        downloaded.append(output_path)
    return downloaded


def main() -> None:
    args = _parse_args()
    base_url = args.base_url or load_server_base_url(CONFIG_PATH)
    if not base_url:
        raise SystemExit(
            "Server base URL is not configured. Set [server].base_url in config.ini or pass --base-url."
        )

    url = _build_url(base_url, args.endpoint)
    request = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise SystemExit(f"Request failed: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise SystemExit(f"Request failed: {exc.reason}") from exc

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print(payload)
        return

    if not isinstance(data, dict):
        raise SystemExit("Unexpected response shape. Expected a JSON object.")

    name = data.get("name")
    image_urls = data.get("imageUrls")
    if not name or not isinstance(image_urls, list):
        raise SystemExit("Response is missing name or imageUrls.")

    output_dir_name = safe_dir_name(name)
    images_dir = ROOT / "assets" / "images" / output_dir_name
    downloaded = _download_images(image_urls, images_dir)
    if not downloaded:
        raise SystemExit("No images were downloaded from imageUrls.")

    render_config, _ = load_render_config(CONFIG_PATH)
    render_config = replace(
        render_config, music_dir=resolve_relative(render_config.music_dir, ROOT)
    )
    output_path = ROOT / "outputs" / "renders" / f"{output_dir_name}.mp4"
    renderer = MoviePyRenderer()
    build_video(
        image_dir=images_dir,
        output_path=output_path,
        renderer=renderer,
        config=render_config,
    )
    print(f"Saved {len(downloaded)} images to {images_dir}")
    print(f"Wrote video to {output_path}")


if __name__ == "__main__":
    main()
