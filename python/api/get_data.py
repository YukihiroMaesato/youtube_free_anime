import os
import requests
from dotenv import load_dotenv

load_dotenv()


headers = {
    "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN")
}

url = "http://nginx_youtube_free_anime/api/internal/videos/showMany"

response = requests.get(
    url,
    headers=headers
)

print("status:", response.status_code)
print("headers:", response.headers)
print("text:")
print(response.text)