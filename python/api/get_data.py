import os
import requests
from dotenv import load_dotenv
from services.logger import logger

load_dotenv()

def get_videos_with_channels() -> list:
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
        # HTTPエラーが発生した場合は例外をスロー
        response.raise_for_status()

        # --- ここにエラー判定を仕込む ---
        if not response.text.strip():
            logger.error("APIレスポンスが空です (レスポンスボディが空)")
            return []
        
        # JSONデコード自体のエラーを捕捉する
        try:
            return response.json()
        except ValueError:
            logger.error(f"JSONパースエラー: レスポンス内容がJSONではありません。内容: {response.text[:100]}")
            return []
        # ------------------------------

    except requests.exceptions.RequestException as e:
        logger.exception("API通信エラー url=%s", url)
        return []