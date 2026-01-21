Project overview

- Purpose: Build an autonomous TikTok content bot. Long term it will read a schedule, fetch data and images, render a video, create descriptions, and upload to TikTok. Current focus is image fetching plus image-to-video rendering.
- Design: Modular port/adapter style so future database, storage, scheduler, and TikTok integrations can plug in without rewrites. Workflows orchestrate; adapters talk to external systems.

How it works (end-to-end)

- Image fetch flow: `scripts/fetch_images.py` builds an ImageFetchRequest, calls the fetch_images workflow, and the ICrawlerImageFetcher downloads images into `assets/images/<keyword>`.
- Render flow: `scripts/render.py` builds a RenderRequest, calls the build_video workflow, applies slideshow timing rules from hardcoded values in `src/tiktok_bot/utils/timing_table.py` (clamped 3-10 images, fade fixed at 0.2s), optionally embeds random background music from `assets/music` (enabled by default), and the MoviePyRenderer renders an MP4 (default `outputs/renders/render.mp4`).
- Fetch + render: `scripts/fetch_and_render.py` runs the fetch flow then the render flow with the same keyword, outputting `outputs/renders/<keyword>.mp4`.
- Schedule helper: `scripts/fetch_missing_images.py` reads `schedule.csv`, downloads missing images for rows without images, and updates the `Has images` column to `YES`.
- Random location fetch + render: `scripts/fetch_random_location.py` calls `/api/v1/social-media`, downloads `imageUrls` into `assets/images/<name>`, and renders `outputs/renders/<name>.mp4`.

Key folders and file relationships

- Domain (data models): `src/tiktok_bot/domain/models.py`
  - RenderConfig, RenderRequest, and ImageFetchRequest are the core data contracts passed between layers.
- Ports (interfaces/protocols): `src/tiktok_bot/ports/video.py`, `src/tiktok_bot/ports/image_fetcher.py`
  - VideoRenderer defines the render API used by workflows.
  - ImageFetcher defines the download API used by workflows.
- Adapters (implementations):
  - `src/tiktok_bot/adapters/video/moviepy_impl.py` implements VideoRenderer using MoviePy. It crops to 1080x1920 (9:16), optionally adds a random music track from `assets/music` (trimmed or looped to match video length), and renders MP4. It includes a Pillow 10+ compatibility shim.
  - `src/tiktok_bot/adapters/image/icrawler_impl.py` implements ImageFetcher using icrawler and supports Bing/Google/Baidu.
- Workflows (orchestration):
  - `src/tiktok_bot/workflows/build_video.py` ties a RenderRequest to a VideoRenderer.
  - `src/tiktok_bot/workflows/fetch_images.py` ties an ImageFetchRequest to an ImageFetcher.
- Utils:
  - `src/tiktok_bot/utils/paths.py` handles image discovery, safe folder names, and relative path resolution.
  - `src/tiktok_bot/utils/config.py` reads `config.ini` render defaults and the server base URL.
  - `src/tiktok_bot/utils/schedule.py` loads/saves the CSV schedule and parses truthy values.
  - `src/tiktok_bot/utils/timing_table.py` defines the hardcoded slideshow timing table and resolves per-image durations with 3-10 clamping and a fixed 0.2s fade.
- Scripts (CLI entrypoints):
  - `scripts/render.py`, `scripts/fetch_images.py`, `scripts/fetch_and_render.py`, `scripts/fetch_missing_images.py`, `scripts/fetch_random_location.py` wire CLI args to workflows or server calls and rendering.

Project data files

- `config.ini`: default render settings (TikTok-friendly defaults) and the server base URL; CLI args override these.
- `schedule.csv`: schedule table with columns Name, Run at, Description, Has images, Uploaded.
- `tiktok_slideshow_timing_table.xlsx`: reference table for timing values (not read at runtime).
- `assets/music`: optional background music files (mp3/m4a/etc).
- `assets/images`: input image folders (ignored by git).
- `outputs/renders`: rendered videos (ignored by git).

Environment notes

- Use Python 3.12. Python 3.14 fails to install Pillow wheels on Windows.
- Activate the project venv before running scripts: `./.venv/Scripts/Activate.ps1`.

Agent maintenance

- If you change code behavior, file relationships, or scripts/configs, update this document to match the new reality.
