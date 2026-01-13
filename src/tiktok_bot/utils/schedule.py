import csv
from pathlib import Path
from typing import Iterable, List, Tuple


def load_schedule(csv_path: Path) -> Tuple[List[str], List[dict]]:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"No headers found in {csv_path}")
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames), rows


def save_schedule(csv_path: Path, fieldnames: Iterable[str], rows: Iterable[dict]) -> None:
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_header(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def find_field(fieldnames: Iterable[str], candidates: Iterable[str]) -> str:
    normalized = {normalize_header(name): name for name in fieldnames}
    for candidate in candidates:
        key = normalize_header(candidate)
        if key in normalized:
            return normalized[key]
    raise KeyError(f"Missing required column: {', '.join(candidates)}")


def is_truthy(value: str) -> bool:
    if value is None:
        return False
    cleaned = value.strip().lower()
    return cleaned in {"yes", "true", "1", "y"}
