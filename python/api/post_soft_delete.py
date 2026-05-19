import os
from urllib.parse import quote
from datetime import datetime

import requests
from dotenv import load_dotenv

from services.logger import logger

load_dotenv()


def soft_delete_videos() -> dict:
    try:
        logger.info("soft_delete_videos 開始")
        
        headers = {
            "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN"),
            "Content-Type": "application/json",
        }

        now = datetime.now().isoformat()

        encoded_datetime = quote(now)

        url = (
            f"{os.getenv('LARAVEL_API_URL')}"
            f"/api/internal/videos/{encoded_datetime}/soft-delete"
        )

        response = requests.post(
            url,
            headers=headers,
            allow_redirects=False,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    except requests.HTTPError:
        logger.exception(
            "soft_delete_videos HTTPエラー url=%s",
            url
        )
        raise

    except requests.RequestException:
        logger.exception(
            "soft_delete_videos リクエストエラー url=%s",
            url
        )
        raise

    except Exception:
        logger.exception(
            "soft_delete_videos 予期せぬエラー"
        )
        raise


if __name__ == "__main__":
    try:
        result = soft_delete_videos()

    except Exception:
        logger.exception(
            "soft_delete_videos 実行失敗"
        )