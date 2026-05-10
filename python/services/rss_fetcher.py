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
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        feed_url,
        headers=headers,
        timeout=30
    )

    print("status:", response.status_code)

    if response.status_code in (404, 500):
        raise RSSFetchError(response.status_code, feed_url)

    feed = feedparser.parse(response.text)

    videos = []

    channel_name = getattr(feed.feed, "title", "")

    youtube_channel_id = getattr(
        feed.feed,
        "yt_channelid",
        None
    )

    for entry in feed.entries:

        thumbnail_url = None

        if hasattr(entry, "media_thumbnail"):
            thumbnail_url = (
                entry.media_thumbnail[0]["url"]
            )

        video = {
            "youtube_video_id": getattr(
                entry,
                "yt_videoid",
                None
            ),

            "youtube_channel_id": youtube_channel_id,

            "channel_name": channel_name,

            "title": getattr(entry, "title", ""),

            "published_at": getattr(
                entry,
                "published",
                ""
            ),

            "link": getattr(entry, "link", ""),

            "description": getattr(
                entry,
                "summary",
                ""
            ),

            "thumbnail_url": thumbnail_url,
        }

        videos.append(video)

    return videos