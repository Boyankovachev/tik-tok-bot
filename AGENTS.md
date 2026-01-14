Project overview

- Purpose: Build an autonomous TikTok content bot. It will eventually read a schedule, fetch data/images, render a video, create descriptions, and upload to TikTok. Current focus is step 3 (image-to-video) plus image fetching.
- Design: Modular, port/adapter style so future DB/storage/scheduler/tiktok integrations can plug in without rewrites. Workflows orchestrate; adapters talk to external systems.

Current features

- Image download via icrawler based on a keyword.
- Video rendering from a folder of images using MoviePy with 9:16 framing.
- CSV schedule for planned posts with a helper script to fill missing images.

Key folders and how they relate

- src/tiktok_bot/domain: data models for render and fetch requests.
  - models.py: RenderConfig/RenderRequest and ImageFetchRequest.
- src/tiktok_bot/ports: interfaces (protocols) for adapters.
  - video.py: VideoRenderer interface for rendering.
  - image_fetcher.py: ImageFetcher interface for downloading images.
- src/tiktok_bot/adapters: concrete implementations.
  - video/moviepy_impl.py: MoviePyRenderer that crops to 1080x1920 and renders mp4.
  - image/icrawler_impl.py: ICrawlerImageFetcher that downloads images via Bing/Google/Baidu.
- src/tiktok_bot/workflows: orchestration logic.
  - build_video.py: takes a folder of images + config and calls a VideoRenderer.
  - fetch_images.py: takes a keyword and calls an ImageFetcher, placing images in a folder.
- src/tiktok_bot/utils:
  - paths.py: image discovery, safe folder names, resolving relative paths.
  - config.py: reads config.ini render defaults.
  - schedule.py: CSV loading/saving and simple truthy parsing for schedule updates.

Scripts (CLI entrypoints)

- scripts/render.py: render a video from assets/images using config.ini defaults; CLI overrides available.
- scripts/fetch_images.py: download images for a keyword into assets/images/<keyword>.
- scripts/fetch_and_render.py: download then render to outputs/renders/<keyword>.mp4.
- scripts/fetch_missing_images.py: scan schedule.csv, download missing images, and update Has images to YES.

Project data files

- config.ini: default render settings (TikTok-friendly defaults).
- schedule.csv: schedule table with columns Name, Run at, Description, Has images, Uploaded.
- assets/images: input image folders (ignored by git).
- outputs/renders: rendered videos (ignored by git).

Workflow notes

- Image folders are expected under assets/images/<name>. The <name> is the keyword or schedule Name.
- Video output goes to outputs/renders/<name>.mp4 or a custom path.
- MoviePy relies on Pillow; a compatibility shim exists in moviepy_impl.py for Pillow 10+.

Environment notes

- Use Python 3.12. Python 3.14 fails to install Pillow wheels on Windows.
- Activate the project venv before running scripts: .\.venv\Scripts\Activate.ps1.
