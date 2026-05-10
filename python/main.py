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

# -----------------------------------------------------------------------
# 対象チャンネル設定
# 複数チャンネルを処理したい場合はここにエントリを追加する
# -----------------------------------------------------------------------
CHANNELS = [
    {
        "youtube_channel_id": "UC9iC5kXiHNJCCDjEi1lD3UA",
        "is_official": True,
        "country_code": "JP",
    },
]

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


def process_channel(channel_cfg: dict, dry_run: bool, use_bulk: bool) -> None:
    channel_id = channel_cfg["youtube_channel_id"]
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
    parsed_videos = [parse_video(v) for v in raw_videos]

    # チャンネル情報は最初の動画から補完する
    first = parsed_videos[0]
    channel_data = {
        "youtube_channel_id": channel_id,
        "name": first.get("channel_name", ""),
        "url": first.get("channel_url", f"https://www.youtube.com/channel/{channel_id}"),
        "is_official": channel_cfg.get("is_official", True),
        "country_code": channel_cfg.get("country_code"),
    }

    # --- 3. dry-run モード: 結果を表示するだけ ---
    if dry_run:
        logging.info("[dry-run] チャンネル情報:")
        logging.info(json.dumps(channel_data, ensure_ascii=False, indent=2))
        logging.info("[dry-run] 動画 (%d 件):", len(parsed_videos))
        for v in parsed_videos:
            logging.info(json.dumps(v, ensure_ascii=False, indent=2))
            logging.info("-" * 40)
        return

    # --- 4. Laravel API に送信 ---
    # if use_bulk:
    #     # 一括送信（推奨）
    #     result = db.bulk_sync(channel_data, parsed_videos)
    #     if result:
    #         logging.info("[bulk_sync] レスポンス: %s", json.dumps(result, ensure_ascii=False))
    #     else:
    #         logging.error("[bulk_sync] 送信に失敗しました。")
    #         sys.exit(1)

    # else:
    #     # 個別送信
    #     ch_result = db.upsert_channel(channel_data)
    #     if not ch_result:
    #         logging.error("チャンネルの upsert に失敗しました。処理を中断します。")
    #         sys.exit(1)

    #     success = 0
    #     fail = 0
    #     for video in parsed_videos:
    #         result = db.upsert_video(video)
    #         if result:
    #             success += 1
    #         else:
    #             fail += 1

    #     logging.info("動画 upsert 完了 → 成功: %d 件 / 失敗: %d 件", success, fail)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube RSS → Laravel API 同期")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="API に送信せず、パース結果を標準出力に表示する",
    )
    parser.add_argument(
        "--bulk",
        action="store_true",
        default=True,
        help="bulk_sync エンドポイントを使う（デフォルト）",
    )
    parser.add_argument(
        "--individual",
        action="store_true",
        default=False,
        help="チャンネルと動画を個別に upsert する",
    )
    args = parser.parse_args()

    use_bulk = not args.individual

    for channel_cfg in CHANNELS:
        process_channel(
            channel_cfg=channel_cfg,
            dry_run=args.dry_run,
            use_bulk=use_bulk,
        )

    logging.info("全チャンネルの処理が完了しました。")


if __name__ == "__main__":
    main()