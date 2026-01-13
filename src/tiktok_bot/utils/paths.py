from pathlib import Path

SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def list_image_files(directory: Path) -> list[Path]:
    if not directory.exists():
        raise FileNotFoundError(f"Image directory does not exist: {directory}")

    files = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTS
    ]
    return sorted(files, key=lambda path: path.name.lower())


def safe_dir_name(value: str) -> str:
    cleaned = "".join(ch for ch in value.strip() if ch.isalnum() or ch in (" ", "-", "_"))
    cleaned = cleaned.replace(" ", "-").strip("-_")
    return cleaned or "images"


def resolve_relative(path: Path, root: Path) -> Path:
    if not path.is_absolute():
        return root / path
    return path
