"""
Laravel API クライアント
YouTube RSS から取得したデータを Laravel の API に送信する
"""

import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

LARAVEL_API_BASE_URL = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8000")
LARAVEL_API_KEY = os.getenv("LARAVEL_API_KEY", "")

TIMEOUT = 30


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": LARAVEL_API_KEY,
    }


def upsert_channel(channel_data: dict) -> dict | None:
    """
    チャンネル情報を Laravel API に upsert する

    Parameters
    ----------
    channel_data : dict
        {
            "youtube_channel_id": str,
            "name": str,
            "url": str,
            "is_official": bool,
            "country_code": str | None,
        }

    Returns
    -------
    dict | None
        レスポンス JSON（失敗時は None）
    """
    url = f"{LARAVEL_API_BASE_URL}/api/channels/upsert"

    payload = {
        "youtube_channel_id": channel_data["youtube_channel_id"],
        "name": channel_data["name"],
        "url": channel_data["url"],
        "is_official": channel_data.get("is_official", True),
        "country_code": channel_data.get("country_code"),
        "last_fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        print(f"[channel] upsert 成功: {channel_data['youtube_channel_id']}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[channel] HTTP エラー: {e.response.status_code} {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[channel] 通信エラー: {e}")

    return None


def upsert_video(video_data: dict) -> dict | None:
    """
    動画情報を Laravel API に upsert する

    Parameters
    ----------
    video_data : dict
        parse_video() の返り値に fetched_at を加えたもの

    Returns
    -------
    dict | None
        レスポンス JSON（失敗時は None）
    """
    url = f"{LARAVEL_API_BASE_URL}/api/videos/upsert"

    payload = {
        "youtube_video_id": video_data["youtube_video_id"],
        "youtube_channel_id": video_data["youtube_channel_id"],
        "title": video_data["title"],
        "normalized_title": video_data.get("normalized_title"),
        "description": video_data.get("description"),
        "thumbnail_url": video_data.get("thumbnail_url"),
        "published_at": video_data.get("published_at"),
        "video_type": video_data.get("video_type", "other"),
        "is_free": video_data.get("is_free", True),
        "is_official": video_data.get("is_official", True),
        "language_code": video_data.get("language_code"),
        "free_until_at": video_data.get("free_until_at"),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "tags": video_data.get("tags", []),
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        print(f"[video] upsert 成功: {video_data['youtube_video_id']}")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[video] HTTP エラー: {e.response.status_code} {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[video] 通信エラー: {e}")

    return None


def bulk_sync(channel_data: dict, videos: list[dict]) -> dict | None:
    """
    チャンネル + 動画一覧をまとめて Laravel API に送信する（一括同期）

    upsert_channel / upsert_video を個別に呼ぶ代わりに
    このエンドポイントが Laravel 側に実装されている場合に使用する

    Parameters
    ----------
    channel_data : dict
        upsert_channel と同じ形式
    videos : list[dict]
        parse_video() の返り値のリスト

    Returns
    -------
    dict | None
    """
    url = f"{LARAVEL_API_BASE_URL}/api/rss/sync"

    payload = {
        "channel": {
            "youtube_channel_id": channel_data["youtube_channel_id"],
            "name": channel_data["name"],
            "url": channel_data["url"],
            "is_official": channel_data.get("is_official", True),
            "country_code": channel_data.get("country_code"),
            "last_fetched_at": datetime.now(timezone.utc).isoformat(),
        },
        "videos": [
            {
                "youtube_video_id": v["youtube_video_id"],
                "youtube_channel_id": v["youtube_channel_id"],
                "title": v["title"],
                "normalized_title": v.get("normalized_title"),
                "description": v.get("description"),
                "thumbnail_url": v.get("thumbnail_url"),
                "published_at": v.get("published_at"),
                "video_type": v.get("video_type", "other"),
                "is_free": v.get("is_free", True),
                "is_official": v.get("is_official", True),
                "language_code": v.get("language_code"),
                "free_until_at": v.get("free_until_at"),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "tags": v.get("tags", []),
            }
            for v in videos
        ],
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_headers(),
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        print(f"[bulk_sync] 成功: {len(videos)} 件")
        return response.json()

    except requests.exceptions.HTTPError as e:
        print(f"[bulk_sync] HTTP エラー: {e.response.status_code} {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[bulk_sync] 通信エラー: {e}")

    return None