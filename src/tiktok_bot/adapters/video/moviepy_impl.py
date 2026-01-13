from pathlib import Path

from moviepy.editor import ImageClip, concatenate_videoclips

from ...domain.models import RenderRequest
from ...ports.video import VideoRenderer


class MoviePyRenderer(VideoRenderer):
    def render(self, request: RenderRequest) -> Path:
        _ensure_pillow_compat()
        config = request.config
        if not request.images:
            raise ValueError("No images provided for rendering.")

        clips = []
        try:
            for image_path in request.images:
                clip = ImageClip(str(image_path))
                clip = _cover_and_center(clip, config.width, config.height)
                clip = clip.set_duration(config.image_duration)
                if config.fade_duration > 0:
                    clip = clip.fadein(config.fade_duration).fadeout(config.fade_duration)
                clips.append(clip)

            video = concatenate_videoclips(clips, method="compose")
            output_path = request.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            video.write_videofile(
                str(output_path),
                fps=config.fps,
                codec="libx264",
                audio=False,
                preset="medium",
            )
            video.close()
            return output_path
        finally:
            for clip in clips:
                try:
                    clip.close()
                except Exception:
                    pass


def _cover_and_center(clip: ImageClip, target_w: int, target_h: int) -> ImageClip:
    w, h = clip.size
    scale = max(target_w / w, target_h / h)
    clip = clip.resize(scale)
    return clip.crop(
        x_center=clip.w / 2,
        y_center=clip.h / 2,
        width=target_w,
        height=target_h,
    )


def _ensure_pillow_compat() -> None:
    try:
        from PIL import Image
    except Exception:
        return

    if not hasattr(Image, "ANTIALIAS"):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
