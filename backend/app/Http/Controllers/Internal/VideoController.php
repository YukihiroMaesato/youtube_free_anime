<?php

namespace App\Http\Controllers\Internal;

use App\Http\Controllers\Controller;
use App\Models\AnimeTitle;
use App\Models\Tag;
use App\Models\Video;
use App\Models\YoutubeChannel;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

class VideoController extends Controller
{
    // 動画とチャンネルの関連を含めて全件取得する
    public function showMany(Request $request): JsonResponse
    {
        $channels = YoutubeChannel::with('videos')
            ->get()
            ->map(function ($channel) {
                return [
                    'youtube_channel_id' => $channel->youtube_channel_id,
                    'is_official' => $channel->is_official,
                    'country_code' => $channel->country_code,

                    'videos' => $channel->videos->map(function ($video) {
                        return [
                            'youtube_video_id' => $video->youtube_video_id,
                        ];
                    }),
                ];
            });

        return response()->json($channels);
    }

    /**
     * Python から受け取った動画データを一括保存する
     *
     * ポイント:
     *   - YoutubeChannel / AnimeTitle / Tag は数値IDではなく
     *     文字列の自然キーで firstOrCreate するため、
     *     シーダー再投入後も外部キーが正しく解決される
     *   - Video は youtube_video_id で upsert（冪等）
     *   - タグは syncWithoutDetaching で追記（既存タグを外さない）
     */
    public function bulkStore(Request $request): JsonResponse
    {
        $videos = $request->all();

        if (empty($videos)) {
            return response()->json(['success' => false, 'message' => 'データが空です'], 422);
        }

        $savedCount  = 0;
        $errorVideos = [];

        Log::error('[VideoController::bulkStore] データ受信', ['count' => count($videos)]);

        foreach ($videos as $data) {
            try {
                DB::transaction(function () use ($data, &$savedCount) {

                    // --------------------------------------------------
                    // 1. YoutubeChannel
                    //    データは手動投入済みのため、文字列IDで取得するだけ
                    //    存在しない場合は例外を投げてこの動画をスキップ
                    // --------------------------------------------------
                    $channel = YoutubeChannel::where(
                        'youtube_channel_id',
                        $data['youtube_channel_id']
                    )->first();

                    if (!$channel) {
                        throw new \RuntimeException(
                            "youtube_channel_id '{$data['youtube_channel_id']}' が見つかりません。"
                                . " youtube_channels テーブルに手動で登録してください。"
                        );
                    }

                    $channel->update(['last_fetched_at' => now()]);

                    // --------------------------------------------------
                    // 2. AnimeTitle（ip_title）
                    //    title（文字列）で解決
                    //    → シーダー再投入でも数値IDに依存しない
                    //    ip_title が null のときは紐付けしない
                    // --------------------------------------------------
                    $animeTitleId = null;

                    // VideoController.php

                    if (!empty($data['ip_title'])) {
                        $animeTitle = AnimeTitle::firstOrCreate(
                            [
                                'title' => $data['ip_title'],
                            ],
                            [
                                // 最大値を取得して+1（レコードがない場合は1になる）
                                'id'               => (AnimeTitle::max('id') ?? 0) + 1,
                                'normalized_title' => $data['ip_title'],
                            ]
                        );
                        $animeTitleId = $animeTitle->id;
                    }

                    // --------------------------------------------------
                    // 3. Video upsert
                    //    youtube_video_id をユニークキーとして upsert
                    //    anime_title_id / youtube_channel_id は
                    //    上で取得した数値IDを使う
                    // --------------------------------------------------
                    $video = Video::updateOrCreate(
                        [
                            'youtube_video_id' => $data['youtube_video_id'],
                        ],
                        [
                            'youtube_channel_id' => $channel->id,
                            'anime_title_id'     => $animeTitleId,

                            'title'            => $data['title'],
                            'normalized_title' => $data['normalized_title'] ?? null,
                            'description'      => $data['description']      ?? null,
                            'thumbnail_url'    => $data['thumbnail_url']    ?? null,

                            'published_at'  => $data['published_at']  ?? null,
                            'free_until_at' => $data['free_until_at'] ?? null,

                            'video_type'    => $data['video_type']    ?? null,
                            'language_code' => $data['language_code'] ?? 'ja',

                            'is_free'     => $data['is_free']     ?? true,
                            'is_official' => $data['is_official'] ?? true,

                            'episode_number' => $data['episode_number'] ?? null,
                            'episode_start'  => $data['episode_start']  ?? null,
                            'episode_end'    => $data['episode_end']    ?? null,
                            'season_number'  => $data['season_number']  ?? null,

                            'fetched_at' => now(),
                        ]
                    );

                    // --------------------------------------------------
                    // 4. Tags
                    //    name（文字列）で firstOrCreate
                    //    → シーダー再投入でも数値IDに依存しない
                    //    syncWithoutDetaching で既存タグを残しつつ追記
                    // --------------------------------------------------
                    if (!empty($data['tags']) && is_array($data['tags'])) {
                        $tagIds = collect($data['tags'])
                            ->map(fn(string $name) => Tag::firstOrCreate(['name' => $name])->id)
                            ->toArray();

                        $video->tags()->syncWithoutDetaching($tagIds);
                    }

                    $savedCount++;
                });
            } catch (\Throwable $e) {
                $videoId = $data['youtube_video_id'] ?? 'unknown';
                Log::error('[VideoController::bulkStore] 保存失敗', [
                    'youtube_video_id' => $videoId,
                    'error'            => $e->getMessage(),
                ]);
                $errorVideos[] = $videoId;
            }
        }

        return response()->json([
            'success'       => empty($errorVideos),
            'saved_count'   => $savedCount,
            'error_count'   => count($errorVideos),
            'error_video_ids' => $errorVideos,
        ]);
    }
}
