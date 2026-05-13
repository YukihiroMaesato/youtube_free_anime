<?php

namespace App\Http\Controllers;

use App\Http\Requests\VideoIndexRequest;
use App\Http\Requests\VideoTitleIndexRequest;
use App\Models\AnimeTitle;
use App\Models\Tag;
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

        if (!empty($validated['tag_id'])) {
            $query->whereHas('tags', function ($tagQuery) use ($validated) {
                $tagQuery->where('tags.id', $validated['tag_id']);
            });
        }

        if (!empty($validated['anime_title_id'])) {
            $query->where('anime_title_id', $validated['anime_title_id']);
        }

        $videos = $query->paginate(20)
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

    public function tags(): JsonResponse
    {
        $tags = Tag::query()
            ->withCount('videos')
            ->has('videos')
            ->orderBy('name')
            ->get(['id', 'name'])
            ->map(function (Tag $tag) {
                return [
                    'id' => $tag->id,
                    'name' => $tag->name,
                    'videos_count' => $tag->videos_count,
                ];
            });

        return response()->json($tags);
    }

    public function titles(VideoTitleIndexRequest $request): JsonResponse
    {
        $validated = $request->validated();
        $keyword = trim((string) ($validated['q'] ?? ''));
        $limit = !empty($validated['all']) ? null : 20;

        $titles = AnimeTitle::query()
            ->withCount('videos')
            ->has('videos')
            ->when($keyword !== '', function ($query) use ($keyword) {
                $query->where(function ($titleQuery) use ($keyword) {
                    $titleQuery
                        ->where('title', 'like', "%{$keyword}%")
                        ->orWhere('normalized_title', 'like', "%{$keyword}%")
                        ->orWhere('title_kana', 'like', "%{$keyword}%")
                        ->orWhere('title_en', 'like', "%{$keyword}%");
                });
            })
            ->orderByRaw('COALESCE(title_kana, title)')
            ->when($limit !== null, function ($query) use ($limit) {
                $query->limit($limit);
            })
            ->get(['id', 'title', 'title_kana', 'title_en'])
            ->map(function (AnimeTitle $title) {
                return [
                    'id' => $title->id,
                    'title' => $title->title,
                    'title_kana' => $title->title_kana,
                    'title_en' => $title->title_en,
                    'videos_count' => $title->videos_count,
                ];
            });

        return response()->json($titles);
    }
}
