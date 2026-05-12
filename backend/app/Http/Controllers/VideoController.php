<?php

namespace App\Http\Controllers;

use App\Http\Requests\VideoIndexRequest;
use App\Models\Video;
use Illuminate\Http\JsonResponse;

class VideoController extends Controller
{
    public function index(VideoIndexRequest $request): JsonResponse
    {
        $validated = $request->validated();

        $query = Video::with(['animeTitle', 'youtubeChannel'])
            ->orderByDesc('published_at');

        if (!empty($validated['video_type'])) {
            $query->where('video_type', $validated['video_type']);
        }

        $videos = $query->paginate(30)
            ->through(function (Video $video) {
                return [
                    'id' => $video->id,
                    'youtube_video_id' => $video->youtube_video_id,
                    'title' => $video->title,
                    'thumbnail_url' => $video->thumbnail_url,
                    'published_at' => optional($video->published_at)->toISOString(),
                    'free_until_at' => optional($video->free_until_at)->toISOString(),
                    'video_type' => $video->video_type,
                    'episode_number' => $video->episode_number,
                    'episode_start' => $video->episode_start,
                    'episode_end' => $video->episode_end,
                    'season_number' => $video->season_number,
                    'anime_title' => $video->animeTitle?->title,
                    'channel_title' => $video->youtubeChannel?->name,
                ];
            });

        return response()->json($videos);
    }
}
