import argparse
import json
import sys
import os
import time

from services.logger import logger

from services.youtube_data_api_3 import add_video_durations
from services.rss_fetcher import fetch_youtube_rss, RSSFetchError
from services.parser import parse_video
from api.get_data import get_videos_with_channels
from api.post_video import post_videos_bulk


RSS_BASE_URL = "https://www.youtube.com/feeds/videos.xml"

RSS_RETRY_MAX_COUNT = 20
RSS_RETRY_WAIT_SECONDS = 15


def build_rss_url(channel_id: str) -> str:
    return f"{RSS_BASE_URL}?channel_id={channel_id}"


def fetch_rss_with_retry(rss_url: str) -> list:
    for attempt in range(1, RSS_RETRY_MAX_COUNT + 1):
        try:
            return fetch_youtube_rss(rss_url)

        except RSSFetchError as e:
            if attempt < RSS_RETRY_MAX_COUNT:
                time.sleep(RSS_RETRY_WAIT_SECONDS)
            else:
                logger.exception(
                    "RSS取得失敗 HTTP %d url=%s",
                    e.status_code,
                    rss_url,
                )

        except Exception:
            logger.exception(
                "RSS取得で予期せぬエラー url=%s",
                rss_url,
            )
            break

    return []


def process_channel(channel: dict, video_ids: set) -> None:
    try:
        channel_id = channel["youtube_channel_id"]

        rss_url = build_rss_url(channel_id)

        raw_videos = fetch_rss_with_retry(rss_url)

        if not raw_videos:
            return

        parsed_videos = [
            parse_video(v)
            for v in raw_videos
            if v.get("youtube_video_id") not in video_ids
        ]

        if len(parsed_videos) == 0:
            return

        parsed_videos = add_video_durations(parsed_videos)

        post_videos_bulk(parsed_videos)

    except Exception:
        logger.exception(
            "チャンネル処理中にエラー channel_id=%s",
            channel.get("youtube_channel_id")
        )


def main() -> None:
    try:
        logger.info("処理開始 main")
        
        channels = get_videos_with_channels()

        video_ids = set()

        for channel in channels:
            for video in channel['videos']:
                video_ids.add(video['youtube_video_id'])

        for channel in channels:
            process_channel(channel, video_ids)

    except Exception:
        logger.exception("main処理で致命的エラー")


if __name__ == "__main__":
    main()