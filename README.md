Tik Tok bot plan:

Part 1:

- create a scheduled based service
  a.k.a Date and Time | Id of entity to post about | Type of entity to post about

Part 2:

- read data from my db -> post description and captions etc...
- read images from my storage and save the images in the needed folder.

Part 3:

- Combine the images into a tik-tok worthy video

Part 4:

- Create the description using template + the fetched data
- Using the description and the video upload it to tiktok

Step 3 quick start (image to video):

1. Install deps:
   pip install -r requirements.txt
2. Drop images into:
   assets/images
3. Render:
   python scripts/render.py

Output defaults to:
outputs/renders/render.mp4

Defaults live in:
config.ini

Image download quick start (keyword to images):

1. Install deps:
   pip install -r requirements.txt
2. Download images:
   python scripts/fetch_images.py "sunset beach"

Images will be saved under:
assets/images/<keyword>

Fetch + render quick start:

1. Install deps:
   pip install -r requirements.txt
2. Download + render:
   python scripts/fetch_and_render.py "sunset beach"

Output video:
outputs/renders/<keyword>.mp4

Common options:

- --output outputs/renders/my_video.mp4
- --image-duration 3.0
- --fade-duration 0.5
- --width 1080 --height 1920 --fps 30

AI agent note:

When an AI agent changes this codebase, it must also update AGENTS.md to describe
the new behavior, file relationships, and any new scripts or configs that were
added or modified.
