from __future__ import annotations

from typing import Mapping

MIN_IMAGE_COUNT = 3
MAX_IMAGE_COUNT = 10
DEFAULT_FADE_DURATION = 0.2

SLIDESHOW_IMAGE_DURATIONS: dict[int, float] = {
    3: 3.8,
    4: 3.1,
    5: 2.6,
    6: 2.3,
    7: 2.1,
    8: 1.95,
    9: 1.85,
    10: 1.75,
}


def resolve_image_duration(
    image_count: int, timing_table: Mapping[int, float], fallback: float
) -> float:
    if image_count <= 0:
        raise ValueError("Image count must be positive.")
    if not timing_table:
        return fallback
    clamped = min(max(image_count, MIN_IMAGE_COUNT), MAX_IMAGE_COUNT)
    if clamped not in timing_table:
        raise ValueError(f"Timing table missing duration for {clamped} images.")
    return timing_table[clamped]
