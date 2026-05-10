import os
import requests

from dotenv import load_dotenv

load_dotenv()

headers = {
    "X-Internal-Token": os.getenv("PYTHON_INTERNAL_API_TOKEN"),
    "Content-Type": "application/json",
}

url = f"{os.getenv('LARAVEL_API_URL')}/api/internal/videos/bulk-store"

data = [
    {
  "youtube_video_id": "5Vd2fiFSv9s",
  "youtube_channel_id": "UC9iC5kXiHNJCCDjEi1lD3UA",
  "channel_name": "アニメタイムズ公式 / Anime Times Official",
  "channel_url": "https://www.youtube.com/channel/UC9iC5kXiHNJCCDjEi1lD3UA",
  "title": "【公式】「彼女が公爵邸に行った理由」第5話『彼女が連れ去られた理由』期間限定本編配信",
  "ip_title": "彼女が公爵邸に行った理由",
  "normalized_title": "「彼女が公爵邸に行った理由」『彼女が連れ去られた理由』期間限定本編配信",
  "description": "Amazon Prime Videoチャンネル『アニメタイムズ』にて\n「彼女が公爵邸に行った理由」絶賛配信中！\nhttps://amzn.to/4eVYkod\n\n▼アニメタイムズへのご意見・ご感想はこちら\nhttps://docs.google.com/forms/d/1V0oQz1eW7q43vSGow5ghd0MjzNWQ6mATPBDBhXlW9o4/viewform?edit_requested=true\n\n『アニメタイムズ』YouTubeチャンネルでは、期間限定でアニメや舞台の本編動画を毎月100本以上公開中！\n本編配信は期間限定ですので、見逃さないよう、チャンネル登録お願いします。\nhttps://www.youtube.com/@animetimes-ch/\n\n\n「彼女が公爵邸に行った理由」（全12話）を期間限定配信！\n 第5話『彼女が連れ去られた理由』：2026年5月8日(金)17:00～ 2026年6月8日(月)16:59\n (本動画は、アニメ製作委員会の許諾を得ている公式配信です) \n\n■Amazon Prime Video チャンネル「アニメタイムズ」とは\n今話題の人気作品や懐かしい名作アニメまで、劇場版、テレビシリーズ、OVAなど、様々なカテゴリーのアニメ作品が見放題となるアニメ専門チャンネル。\nチャンネル価格： 598円(税込)\n30日間無料トライアル実施中\n※Amazonプライム会員への登録が必要です。 ※日本国内からのみ視聴が可能です\nhttps://amzn.to/3sQynk8\n\n\n■全体あらすじ\n突然、謎の死を迎えた「凛子」は、小説の中の富豪の娘「レリアナ」として転生する。しかし、レリアナは脇役であり、近いうちに命を落とす運命だった。レリアナを殺害するのは、婚約者である「ブルックス」である。そのことを小説のストーリーで知っている「レリアナ／凛子」は、彼との婚約破棄を目論む。そこで彼女は王国の実力者である王位継承序列1位の公爵「ノア」に近づき、ある取引を申し込む。それは「6ヶ月の間だけ婚約者のふりをしてほしい」というものだった。果たして2人の取引で、彼女は死の運命から逃れることはできるのか！？\n\n■スタッフ\n原作:「彼女が公爵邸に行った理由」（FLOS COMIC／KADOKAWA刊）\n漫画:Whale\n原作:Milcha\n監督:山元隼一\nシリーズ構成:広田光毅\nキャラクターデザイン:橋本治奈\nプロップデザイン:枝松 聖\n美術監督:加藤賢司\n色彩設計:日比智恵子\n撮影監督:船越雄弦\n3DCG:渡辺哲也\n編集:茶圓一郎\n音響監督:えびなやすのり\n音響制作:グロービジョン\n音楽:井内啓二\n音楽制作:ランティス\nアニメーション制作:颱風グラフィックス\n\n■キャスト\nレリアナ・マクミラン\n花咲凛子:宮本侑芽\nノアボルステア・ウィンナイト:梅原裕一郎\nアダム・テイラー:梅田修一朗\nキース・ウエスタンバーグ:土岐隼一\nヒーカー・デミント:石田 彰\nジャスティン・シャマル:杉田智和\nビビアン・シャマル:矢野優美華\nシアトリヒ・ニューリアル・チェイモス:諏訪部順一\n\n©Whale・Milcha 2017／D&amp;C MEDIA／「彼女が公爵邸に行った理由」製作委員会\n\n#アニメ本編 #アニメフル #アニメタイムズ",
  "thumbnail_url": "https://i2.ytimg.com/vi/5Vd2fiFSv9s/hqdefault.jpg",
  "published_at": "2026-05-08T08:00:09+00:00",
  "free_until_at": "2026-06-08T16:59:00+09:00",
  "video_type": "episode",
  "is_official": True,
  "is_free": True,
  "language_code": "ja",
  "episode_number": 5,
  "episode_start": None,
  "episode_end": None,
  "season_number": 1,
  "tags": [
    "期間限定",
    "公式"
  ]
}
]

response = requests.post(
    url,
    json=data,
    headers=headers
)

print("status:", response.status_code)
print(response.text)