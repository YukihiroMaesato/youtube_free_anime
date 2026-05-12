import os
import socket
import ssl
import time
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# --- 設定項目 ---
HOST = "generativelanguage.googleapis.com"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# 2026年の推奨デフォルト: gemini-3.1-flash-lite
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
API_VERSION = "v1beta"  # 最新機能を使う場合は v1beta、安定版は v1

SEP = "=" * 60

def section(title: str):
    print(f"\n{SEP}\n{title}\n{SEP}")

def ok(msg):    print(f"  ✅ {msg}")
def ng(msg):    print(f"  ❌ {msg}")
def warn(msg):  print(f"  ⚠️  {msg}")
def info(msg):  print(f"  ℹ️  {msg}")

# ---------------------------------------------------------------------------
# 1. 環境変数とモデル名の確認
# ---------------------------------------------------------------------------
section("1. 環境変数とモデル設定の確認")

if GEMINI_API_KEY:
    masked = GEMINI_API_KEY[:6] + "..." + GEMINI_API_KEY[-4:]
    ok(f"GEMINI_API_KEY: {masked}")
else:
    ng("GEMINI_API_KEY が未設定です（.env または環境変数を確認してください）")

info(f"使用予定モデル: {GEMINI_MODEL}")
info(f"APIバージョン : {API_VERSION}")

# 2026年時点の主要モデルリスト
KNOWN_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash",
    "gemini-3.1-pro",
    "gemini-2.0-flash", # 旧モデル互換用
]

if GEMINI_MODEL not in KNOWN_MODELS:
    warn(f"'{GEMINI_MODEL}' はスクリプト内の既知リストにありません。")
    info(f"  推奨される最新モデル: {', '.join(KNOWN_MODELS)}")
else:
    ok("モデル名は最新の定義と一致しています。")


# ---------------------------------------------------------------------------
# 2. ネットワーク層の確認 (DNS / TCP / TLS)
# ---------------------------------------------------------------------------
section("2. ネットワーク接続確認")

# DNS 解決
try:
    t0 = time.time()
    infos = socket.getaddrinfo(HOST, 443)
    ip = infos[0][4][0]
    ok(f"DNS解決成功: {HOST} -> {ip} ({time.time()-t0:.3f}s)")
except Exception as e:
    ng(f"DNS 解決失敗: {e}")

# TCP/TLS ハンドシェイク
try:
    t0 = time.time()
    ctx = ssl.create_default_context()
    # タイムアウトは少し長めに設定
    with socket.create_connection((HOST, 443), timeout=10) as raw:
        with ctx.wrap_socket(raw, server_hostname=HOST) as s:
            elapsed = time.time() - t0
            ok(f"TLS 接続成功 ({elapsed:.3f}s) - Cipher: {s.cipher()[0]}")
except Exception as e:
    ng(f"HTTPS(Port 443) 接続失敗: {e}")
    info("  ヒント: 社内プロキシやファイアウォール、VPNが通信を遮断していないか確認してください。")


# ---------------------------------------------------------------------------
# 3. APIキーの有効性と利用可能モデルの取得
# ---------------------------------------------------------------------------
section("3. APIキー検証 (models.list)")

if not GEMINI_API_KEY:
    info("APIキーがないためスキップします。")
else:
    url = f"https://{HOST}/{API_VERSION}/models?key={GEMINI_API_KEY}"
    try:
        t0 = time.time()
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            models = [m["name"].split("/")[-1] for m in data.get("models", [])]
            ok(f"APIキーは有効です。利用可能なモデルを {len(models)} 件取得しました。")
            
            if GEMINI_MODEL in models:
                ok(f"指定モデル '{GEMINI_MODEL}' はこのアカウントで使用可能です。")
            else:
                warn(f"指定モデル '{GEMINI_MODEL}' がリストに見当たりません。")
                info(f"  利用可能リスト(一部): {models[:5]}")
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode()
        ng(f"モデルリスト取得失敗 (HTTP {status})")
        if status == 403:
            info("  原因: APIキーが無効か、Google AI Studioでプロジェクトが制限されています。")
        info(f"  レスポンス詳細: {body}")
    except Exception as e:
        ng(f"エラー発生: {e}")


# ---------------------------------------------------------------------------
# 4. 実際の推論テスト
# ---------------------------------------------------------------------------
section(f"4. 推論テスト ({GEMINI_MODEL})")

if not GEMINI_API_KEY:
    info("APIキーがないためスキップします。")
else:
    endpoint = f"https://{HOST}/{API_VERSION}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    # シンプルなテスト用ペイロード
    payload = {
        "contents": [{
            "parts": [{"text": "疎通確認です。OKとだけ返してください。"}]
        }],
        "generationConfig": {
            "maxOutputTokens": 10,
            "temperature": 0.0
        }
    }
    
    try:
        t0 = time.time()
        req = urllib.request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_data = json.loads(resp.read().decode())
            answer = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
            elapsed = time.time() - t0
            ok(f"推論成功! 応答時間: {elapsed:.3f}s")
            info(f"モデルの応答: {answer}")
            
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read().decode()
        if status == 429:
            ng("HTTP 429: レート制限(Quota)に達しました。")
            info("  無料枠の制限(1分間に15リクエスト等)にかかっている可能性があります。")
        elif status == 404:
            ng("HTTP 404: モデル名が正しくないか、APIバージョンが対応していません。")
        else:
            ng(f"HTTP {status} エラーが発生しました。")
        info(f"  詳細: {body}")
    except Exception as e:
        ng(f"予期せぬエラー: {e}")

section("診断完了")