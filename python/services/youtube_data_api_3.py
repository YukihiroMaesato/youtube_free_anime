import isodate  # 再生時間のパース用: pip install isodate
import os
from googleapiclient.discovery import build

from dotenv import load_dotenv

load_dotenv()

def add_video_durations(parsed_videos: list[dict]) -> list[dict]:
    """
    parsed_videos のリストを受け取り、YouTube API を叩いて 
    video_duration (int: 秒) を各要素に追加して返す
    """
    if not parsed_videos:
        return []
    
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    
    # youtube_video_id のリストを作成
    video_ids = [v["youtube_video_id"] for v in parsed_videos if v.get("youtube_video_id")]
    
    # API は一度に最大50件まで取得可能なので、50件ずつのチャンクに分ける
    duration_map = {}
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i : i + 50]
        
        request = youtube.videos().list(
            part="contentDetails",
            id=",".join(chunk)
        )
        response = request.execute()

        for item in response.get("items", []):
            vid = item["id"]
            # ISO 8601 形式 (PT1H2M10S) を秒数に変換
            iso_duration = item["contentDetails"]["duration"]
            duration_seconds = int(isodate.parse_duration(iso_duration).total_seconds())
            duration_map[vid] = duration_seconds

    # 元のリストに反映
    for video in parsed_videos:
        video_id = video.get("youtube_video_id")
        # 取得できなかった場合は 0 または None
        video["video_duration"] = duration_map.get(video_id, 0)

    return parsed_videos