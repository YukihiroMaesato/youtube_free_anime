import requests
import feedparser

class RSSFetchError(Exception):
    """RSS取得時のHTTPエラー"""
    def __init__(self, status_code: int, url: str):
        self.status_code = status_code
        self.url = url
        super().__init__(f"HTTP {status_code}: {url}")

def fetch_youtube_rss(feed_url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(
        feed_url,
        headers=headers,
        timeout=30
    )

    if response.status_code != 200:
        raise RSSFetchError(response.status_code, feed_url)

    feed = feedparser.parse(response.text)
    videos = []

    # チャンネル名（トップレベルから取得）
    channel_name = getattr(feed.feed, "title", "")

    for entry in feed.entries:
        # --- 修正ポイント: 各 entry から channel_id を取得 ---
        # entry の yt_channelid を優先し、なければ feed のものを使用
        ch_id = getattr(entry, "yt_channelid", None) or getattr(feed.feed, "yt_channelid", None)
        
        # UC で始まっていない場合は付与する（念のための処理）
        if ch_id and not ch_id.startswith("UC"):
            ch_id = "UC" + ch_id

        thumbnail_url = None
        if hasattr(entry, "media_thumbnail"):
            thumbnail_url = entry.media_thumbnail[0]["url"]

        # YouTubeの概要欄は media_description か summary に入る
        description = getattr(entry, "media_description", getattr(entry, "summary", ""))

        video = {
            "youtube_video_id": getattr(entry, "yt_videoid", None),
            "youtube_channel_id": ch_id, # ここで UC... が確定
            "channel_name": channel_name,
            "title": getattr(entry, "title", ""),
            "published_at": getattr(entry, "published", ""),
            "link": getattr(entry, "link", ""),
            "description": description,
            "thumbnail_url": thumbnail_url
        }
        videos.append(video)

    return videos