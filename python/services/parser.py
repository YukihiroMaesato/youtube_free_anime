"""
RSS エントリを Laravel API 送信用 dict に変換するパーサー

処理の優先順位:
  1. 正規表現で確実に取れる情報を先に抽出
  2. 取れなかった項目 or free_until_at は Gemini API に問い合わせる
"""

import re
import logging

from services.normalizer import normalize_title
from services.gemini_parser import extract_video_info

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# チルダ系文字をまとめて扱う正規表現パターン
# ---------------------------------------------------------------------------
_TILDE = r"[~〜～]"

# 「第X話～第Y話」
_RE_EPISODE_RANGE = re.compile(
    rf"第(\d+)話\s*{_TILDE}\s*第(\d+)話"
)

# 「第X話」（単体）
_RE_EPISODE_SINGLE = re.compile(r"第(\d+)話")

# 「#X」（単体・一挙なし）
_RE_EPISODE_HASH = re.compile(r"#(\d+)")

# シーズン番号
_RE_SEASON = re.compile(
    r"(\d+)\s*(?:期|nd Season|rd Season|th Season)|[Ss]eason\s*(\d+)|\bS(\d+)\b"
)

# PV / トレーラー
_RE_PV = re.compile(r"\bPV\b|ティザー|予告|トレーラー")

# タイトル中にチルダ（一挙配信判定用）
_RE_TILDE_IN_TITLE = re.compile(_TILDE)


# ---------------------------------------------------------------------------
# 内部ヘルパー
# ---------------------------------------------------------------------------

def _determine_video_type(title: str) -> str:
    if _RE_TILDE_IN_TITLE.search(title):
        return "episode_batch"
    if _RE_PV.search(title):
        return "pv"
    if _RE_EPISODE_SINGLE.search(title) or _RE_EPISODE_HASH.search(title):
        return "episode"
    return "other"


def _extract_episode_range(title: str) -> tuple[int | None, int | None]:
    m = _RE_EPISODE_RANGE.search(title)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None, None


def _extract_episode_number(title: str) -> int | None:
    m = _RE_EPISODE_SINGLE.search(title)
    if m:
        return int(m.group(1))
    m = _RE_EPISODE_HASH.search(title)
    if m:
        return int(m.group(1))
    return None


def _extract_season_number(title: str) -> int | None:
    m = _RE_SEASON.search(title)
    if not m:
        return None
    for g in m.groups():
        if g is not None:
            return int(g)
    return None


def _extract_tags(title: str) -> list[str]:
    tags: list[str] = []
    if "期間限定" in title:
        tags.append("期間限定")
    if "公式" in title:
        tags.append("公式")
    if _RE_TILDE_IN_TITLE.search(title):
        tags.append("一挙")
    if _RE_PV.search(title):
        tags.append("PV")
    if "ノーカット" in title:
        tags.append("ノーカット")
    return tags


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def parse_video(entry: dict) -> dict:
    """
    RSS エントリを Laravel API 送信用 dict に変換する
    """
    title: str = entry.get("title", "")
    description: str = entry.get("description", "")

    normalized_title = normalize_title(title)
    tags = _extract_tags(title)

    # --- 正規表現で抽出できる情報 ---
    video_type = _determine_video_type(title)
    season_number = _extract_season_number(title)

    episode_number: int | None = None
    episode_start: int | None = None
    episode_end: int | None = None

    if video_type == "episode_batch":
        episode_start, episode_end = _extract_episode_range(title)
    elif video_type == "episode":
        episode_number = _extract_episode_number(title)

    # --- Gemini API に問い合わせ ---
    gemini_result = extract_video_info(title, description)

    ip_title = gemini_result.get("ip_title", "")
    ip_title_kana = gemini_result.get("ip_title_kana")
    
    # 正規表現で取れなかった場合のみ Gemini の結果を採用
    if episode_start is None:
        episode_start = gemini_result.get("episode_start")
    if episode_end is None:
        episode_end = gemini_result.get("episode_end")
    if episode_number is None and video_type == "episode":
        episode_number = gemini_result.get("episode_number")
    
    if season_number is None:
        season_number = gemini_result.get("season_number") or 1

    free_until_at = gemini_result.get("free_until_at")

    # video_type が other の場合も Gemini の判定を優先
    if video_type == "other":
        video_type = gemini_result.get("video_type", "other")

    # 最終フォールバック
    if season_number is None:
        season_number = 1

    # チャンネルIDの取得とURL生成
    youtube_channel_id: str = entry.get("youtube_channel_id", "")
    channel_url = (
        f"https://www.youtube.com/channel/{youtube_channel_id}"
        if youtube_channel_id
        else ""
    )

    return {
        # --- 動画識別 ---
        "youtube_video_id": entry.get("youtube_video_id"),
        "youtube_channel_id": youtube_channel_id,

        # --- チャンネル情報 ---
        "channel_name": entry.get("channel_name"),
        "channel_url": channel_url,

        # --- 動画情報 ---
        "title": title,
        "ip_title": ip_title,
        "ip_title_kana": ip_title_kana,
        "normalized_title": normalized_title,
        "description": description,
        "thumbnail_url": entry.get("thumbnail_url"),
        "published_at": entry.get("published_at"),
        "free_until_at": free_until_at,

        # --- 分類 ---
        "video_type": video_type,
        "is_official": True,
        "is_free": True,
        "language_code": "ja",

        # --- 話数・シーズン情報 ---
        "episode_number": episode_number,
        "episode_start": episode_start,
        "episode_end": episode_end,
        "season_number": season_number,

        # --- タグ ---
        "tags": tags,
    }
