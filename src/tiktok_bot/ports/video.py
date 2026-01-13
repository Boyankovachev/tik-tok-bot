from pathlib import Path
from typing import Protocol

from ..domain.models import RenderRequest


class VideoRenderer(Protocol):
    def render(self, request: RenderRequest) -> Path:
        """Render a video from the provided request."""
        raise NotImplementedError
