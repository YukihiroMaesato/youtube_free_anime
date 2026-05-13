import os
import requests
from urllib.parse import quote
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


def soft_delete_videos() -> dict:
    headers = {
        "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN"),
        "Content-Type": "application/json",
    }
    
    now = datetime.now().isoformat()
    
    # URLエンコード
    encoded_datetime = quote(now)
    
    print(f"Soft deleting videos at {encoded_datetime}...")

    url = (
        f"{os.getenv('LARAVEL_API_URL')}"
        f"/api/internal/videos/{encoded_datetime}/soft-delete"
    )

    response = requests.post(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    result = soft_delete_videos()

    print(result)