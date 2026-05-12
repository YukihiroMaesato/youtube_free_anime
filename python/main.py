"""
YouTube RSS → Laravel API 同期スクリプト

使い方:
    python main.py                    # デフォルトチャンネルを1件処理
    python main.py --dry-run          # API送信せずにパース結果を表示
    python main.py --bulk             # bulk_sync エンドポイントを使う（デフォルト）
    python main.py --individual       # チャンネル・動画を個別に upsert する
"""

import argparse
import json
import sys
import os
import logging
import time
from datetime import datetime

from services.rss_fetcher import fetch_youtube_rss, RSSFetchError
from services.parser import parse_video
import services.db as db
from api.get_data import get_videos_with_channels
from api.post_video import post_videos_bulk

# -----------------------------------------------------------------------
# 対象チャンネル設定
# 複数チャンネルを処理したい場合はここにエントリを追加する
# -----------------------------------------------------------------------
# CHANNELS = [
#     {
#         "youtube_channel_id": "UC9iC5kXiHNJCCDjEi1lD3UA",
#         "is_official": True,
#         "country_code": "JP",
#     },
# ]

RSS_BASE_URL = "https://www.youtube.com/feeds/videos.xml"

# RSS リトライ設定
RSS_RETRY_MAX_COUNT    = 20
RSS_RETRY_WAIT_SECONDS = 15

# ログ設定：日付付きのファイル名を作成
log_filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def build_rss_url(channel_id: str) -> str:
    return f"{RSS_BASE_URL}?channel_id={channel_id}"


def fetch_rss_with_retry(rss_url: str) -> list:
    """
    RSS を取得する。404 / 500 の場合は RSS_RETRY_WAIT_SECONDS 秒待機して
    最大 RSS_RETRY_MAX_COUNT 回までリトライする。

    Returns
    -------
    list
        動画リスト（全試行失敗時は空リスト）
    """
    for attempt in range(1, RSS_RETRY_MAX_COUNT + 1):
        try:
            videos = fetch_youtube_rss(rss_url)
            if attempt > 1:
                logging.info("RSS取得成功 [試行 %d/%d]", attempt, RSS_RETRY_MAX_COUNT)
            return videos

        except RSSFetchError as e:
            if attempt < RSS_RETRY_MAX_COUNT:
                logging.warning(
                    "RSS取得失敗 HTTP %d [試行 %d/%d] → %d秒後にリトライします  url=%s",
                    e.status_code, attempt, RSS_RETRY_MAX_COUNT,
                    RSS_RETRY_WAIT_SECONDS, rss_url,
                )
                time.sleep(RSS_RETRY_WAIT_SECONDS)
            else:
                logging.error(
                    "RSS取得失敗 HTTP %d [試行 %d/%d] → リトライ上限に達しました  url=%s",
                    e.status_code, attempt, RSS_RETRY_MAX_COUNT, rss_url,
                )

        except Exception as e:
            # 404/500 以外の予期せぬエラーはリトライせず即終了
            logging.error("RSS取得で予期せぬエラーが発生しました: %s", e)
            break

    return []


def process_channel(channel: dict, video_ids: set) -> None:
    channel_id = channel["youtube_channel_id"]
    rss_url = build_rss_url(channel_id)

    logging.info("=" * 60)
    logging.info("チャンネル処理開始: %s", channel_id)
    logging.info("RSS URL: %s", rss_url)
    logging.info("=" * 60)

    # --- 1. RSS 取得（リトライあり）---
    raw_videos = fetch_rss_with_retry(rss_url)
    logging.info("取得件数: %d", len(raw_videos))

    if not raw_videos:
        logging.warning("動画が取得できませんでした。スキップします。")
        return

    # --- 2. パース ---
    parsed_videos = [
        parse_video(v)
        for v in raw_videos
        if v.get("youtube_video_id") not in video_ids
    ]

    if len(parsed_videos) == 0:
        return
    # チャンネル情報は最初の動画から補完する
    
    first = parsed_videos[0]
    channel_data = {
        "youtube_channel_id": channel_id,
        "name": first.get("channel_name", ""),
        "url": first.get("channel_url", f"https://www.youtube.com/channel/{channel_id}"),
        "is_official": channel.get("is_official", True),
        "country_code": channel.get("country_code"),
    }

    
    logging.info("[dry-run] チャンネル情報:")
    logging.info(json.dumps(channel_data, ensure_ascii=False, indent=2))
    logging.info("[dry-run] 動画 (%d 件):", len(parsed_videos))
    post_videos_bulk(parsed_videos)
    for video in parsed_videos:
        logging.info(json.dumps(video, ensure_ascii=False, indent=2))
        logging.info("-" * 40)
    return

def main() -> None:
    
    channels = get_videos_with_channels()
    
    video_ids = set()  # 空の集合を作る

    for channel in channels:    
        for video in channel['videos']:     
            video_ids.add(video['youtube_video_id']) 

    for channel in channels:
        process_channel(channel,video_ids)

    logging.info("全チャンネルの処理が完了しました。")


if __name__ == "__main__":
    main()