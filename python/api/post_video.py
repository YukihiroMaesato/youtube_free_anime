import os
import requests

from dotenv import load_dotenv

load_dotenv()

def post_videos_bulk(videos: list[dict]) -> None:
  headers = {
      "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN"),
      "Content-Type": "application/json",
  }

  url = f"{os.getenv('LARAVEL_API_URL')}/api/internal/videos/bulk-store"

  response = requests.post(
      url,
      json=videos,
      headers=headers
  )
