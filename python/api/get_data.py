import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_videos_with_channels()-> dict | None:
    
    headers = {
        "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN")
    }

    url = f"{os.getenv('LARAVEL_API_URL')}/api/internal/videos/showMany"

    try:
        response = requests.get(
            url,
            headers=headers,
            allow_redirects=False
        )

        response.raise_for_status()
        
        # JSONデータをパースして返す
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None