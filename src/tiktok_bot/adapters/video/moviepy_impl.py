import random
from pathlib import Path

from moviepy.audio.fx.all import audio_loop
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

from ...domain.models import RenderRequest
from ...ports.video import VideoRenderer

SUPPORTED_AUDIO_EXTS = {".mp3", ".m4a", ".aac", ".wav", ".flac", ".ogg", ".opus"}


class MoviePyRenderer(VideoRenderer):
    def render(self, request: RenderRequest) -> Path:
        _ensure_pillow_compat()
        config = request.config
        if not request.images:
            raise ValueError("No images provided for rendering.")

        clips = []
        video = None
        audio_clip = None
        audio_source = None
        try:
            for image_path in request.images:
                clip = ImageClip(str(image_path))
                clip = _cover_and_center(clip, config.width, config.height)
                clip = clip.set_duration(config.image_duration)
                if config.fade_duration > 0:
                    clip = clip.fadein(config.fade_duration).fadeout(config.fade_duration)
                clips.append(clip)

            video = concatenate_videoclips(clips, method="compose")
            if config.include_music:
                audio_source, audio_clip = _build_audio_clip(
                    config.music_dir, video.duration
                )
                if audio_clip is not None:
                    video = video.set_audio(audio_clip)

            output_path = request.output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            write_kwargs = {
                "fps": config.fps,
                "codec": "libx264",
                "audio": audio_clip is not None,
                "preset": "medium",
            }
            if audio_clip is not None:
                write_kwargs["audio_codec"] = "aac"
            video.write_videofile(str(output_path), **write_kwargs)
            return output_path
        finally:
            if video is not None:
                try:
                    video.close()
                except Exception:
                    pass
            if audio_clip is not None and audio_clip is not audio_source:
                try:
                    audio_clip.close()
                except Exception:
                    pass
            if audio_source is not None:
                try:
                    audio_source.close()
                except Exception:
                    pass
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


def _build_audio_clip(
    music_dir: Path, target_duration: float
) -> tuple[AudioFileClip | None, AudioFileClip | None]:
    music_path = _choose_music_file(music_dir)
    if music_path is None:
        return None, None
    try:
        source = AudioFileClip(str(music_path))
    except Exception:
        return None, None
    print(f"Selected music: {music_path}")
    if target_duration <= 0:
        return source, source
    if source.duration is None:
        return source, source
    if source.duration >= target_duration:
        return source, source.subclip(0, target_duration)
    try:
        looped = source.fx(audio_loop, duration=target_duration)
        return source, looped
    except Exception:
        return source, source


def _choose_music_file(music_dir: Path) -> Path | None:
    if not music_dir.exists():
        return None
    candidates = [
        path
        for path in music_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_AUDIO_EXTS
    ]
    if not candidates:
        return None
    return random.choice(candidates)
