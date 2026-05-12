import json
import logging
import os
import time
from datetime import datetime, timezone

from google import genai
from google.genai import errors, types
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# ロガー設定
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [gemini_parser] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(_handler)
    logger.setLevel(logging.DEBUG)

# ---------------------------------------------------------------------------
# 設定
# ---------------------------------------------------------------------------
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemma-4-31b-it")

# レート制限対策 (15 RPM = 4秒以上の間隔)
REQUEST_INTERVAL = 4.5
_last_request_time: float = 0.0

# 429 リトライ設定
RETRY_MAX_COUNT    = 5
RETRY_WAIT_SECONDS = 20

# ---------------------------------------------------------------------------
# API クライアント初期化
# ---------------------------------------------------------------------------
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY が未設定です。")
    _client = None
else:
    _client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# プロンプト定義
# ---------------------------------------------------------------------------
_SYSTEM_PROMPT = """\
あなたはアニメ動画情報の構造化アシスタントです。
YouTube の動画タイトルと説明文から、指定された JSON 形式で情報を抽出してください。
**JSON のみ**を返してください。前置き・後書き・コードブロック記号は不要です。

## 抽出フィールド
- episode_number  : 単話番号（整数）。一挙配信の場合は null
- episode_start   : 一挙配信の開始話（整数）。単話の場合は null
- episode_end     : 一挙配信の終了話（整数）。単話の場合は null
- season_number   : シーズン番号（整数）。不明なら 1
- video_type      : "episode" | "episode_batch" | "pv" | "other"
- free_until_at   : 配信期限。ISO 8601 形式（例: "2026-06-30T23:59:59+09:00"）。不明なら null
- ip_title        : 作品の正式タイトル（IP名）を文字列で返す。
                    動画タイトル・説明文・チャンネル名から、アニメ・漫画・ゲーム等の
                    作品名と判断できるものを抽出する。
                    抽出の優先順位:
                      1. 「」や『』で囲まれた文字列（例:「妖怪ウォッチ」→ "妖怪ウォッチ"）
                      2. 括弧がなくても、話数・期間限定・公式などのキーワードを除いた
                         残りの語句から作品名と推定できるもの
                         例: "第1話～第12話 彼女が公爵邸に行った理由 期間限定本編配信"
                             → "彼女が公爵邸に行った理由"
                      3. チャンネル名がそのまま作品名である場合はそれを使う
                    判別できない場合は null

## ルール
- 期限の年が不明な場合、現在の日付 {today} を基準に補完してください（過去の日付にならないよう注意）。
- 時刻不明な場合は 23:59:59 (+09:00) とします。
- 期間限定とだけあって具体的な日付が読めない場合、free_until_at は null にします。
"""

# ---------------------------------------------------------------------------
# 関数
# ---------------------------------------------------------------------------

def _default_result() -> dict:
    return {
        "episode_number": None,
        "episode_start":  None,
        "episode_end":    None,
        "season_number":  1,
        "video_type":     "other",
        "free_until_at":  None,
        "ip_title":       None,
    }


def _call_api(user_message: str, system_prompt: str) -> dict:
    """
    1回分の API 呼び出し。
    429 (ClientError, code=429) は呼び出し元でリトライするため raise する。
    """
    response = _client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,
            response_mime_type="application/json",
        ),
    )

    result = json.loads(response.text)

    if not result.get("season_number"):
        result["season_number"] = 1

    result.setdefault("ip_title", None)

    return result


def extract_video_info(title: str, description: str) -> dict:
    """
    google-genai を使用して動画情報を抽出する。

    - 通常の間隔制御: REQUEST_INTERVAL 秒の最小間隔
    - 429 発生時: RETRY_WAIT_SECONDS 秒待機して最大 RETRY_MAX_COUNT 回リトライ
    """
    global _last_request_time

    if not _client:
        logger.error("API クライアントが初期化されていません。GEMINI_API_KEY を確認してください。")
        return _default_result()

    # --- レート制限対策: 前回リクエストから一定時間待機 ---
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        wait = REQUEST_INTERVAL - elapsed
        logger.debug("レート制限回避のため待機中... (%.1fs)", wait)
        time.sleep(wait)

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    system_prompt = _SYSTEM_PROMPT.replace("{today}", today_str)
    user_message = f"タイトル: {title}\n\n説明文:\n{description[:1000]}"

    # --- リトライループ ---
    for attempt in range(1, RETRY_MAX_COUNT + 1):
        try:
            logger.debug(
                "Gemini API リクエスト送信 [試行 %d/%d]: %s",
                attempt, RETRY_MAX_COUNT, title[:50],
            )
            _last_request_time = time.time()
            result = _call_api(user_message, system_prompt)
            logger.debug("Gemini API 成功 [試行 %d/%d]", attempt, RETRY_MAX_COUNT)
            return result

        except errors.ClientError as e:
            if e.code == 429:
                # 429 Too Many Requests
                if attempt < RETRY_MAX_COUNT:
                    logger.warning(
                        "429 レート制限超過 [試行 %d/%d] → %d秒後にリトライします",
                        attempt, RETRY_MAX_COUNT, RETRY_WAIT_SECONDS,
                    )
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    logger.error(
                        "429 レート制限超過 [試行 %d/%d] → リトライ上限に達しました。",
                        attempt, RETRY_MAX_COUNT,
                    )
            else:
                # 400 (InvalidArgument) 等、リトライしても解決しないクライアントエラー
                logger.error(
                    "クライアントエラー (HTTP %d): %s",
                    e.code, e.message,
                )
                break

        except errors.ServerError as e:
            # 5xx: サーバー側の一時障害はリトライ対象
            if attempt < RETRY_MAX_COUNT:
                logger.warning(
                    "サーバーエラー (HTTP %d) [試行 %d/%d] → %d秒後にリトライします: %s",
                    e.code, attempt, RETRY_MAX_COUNT, RETRY_WAIT_SECONDS, e.message,
                )
                time.sleep(RETRY_WAIT_SECONDS)
            else:
                logger.error(
                    "サーバーエラー (HTTP %d) [試行 %d/%d] → リトライ上限に達しました。",
                    e.code, attempt, RETRY_MAX_COUNT,
                )

        except json.JSONDecodeError as e:
            logger.error(
                "JSONパース失敗: %s / 生テキスト: %r",
                e,
                locals().get("response", None) and response.text[:200],
            )
            break

        except Exception as e:
            logger.error("予期せぬエラーが発生しました: %s", e)
            logger.debug("エラー詳細:", exc_info=True)
            break

    return _default_result()