'use client';

import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

type Video = {
  id: number;
  youtube_video_id: string;
  title: string;
  published_at: string | null;
  free_until_at: string | null;
  video_type: string | null;
  episode_number: number | null;
  episode_start: number | null;
  episode_end: number | null;
  season_number: number | null;
  anime_title: string | null;
  channel_title: string | null;
};

type PaginatedVideos = {
  data: Video[];
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
  from: number | null;
  to: number | null;
};

function formatDate(value: string | null) {
  if (!value) {
    return null;
  }

  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value));
}

function getEpisodeLabel(video: Video) {
  if (video.episode_start && video.episode_end) {
    return `${video.episode_start}話-${video.episode_end}話`;
  }

  if (video.episode_number) {
    return `${video.episode_number}話`;
  }

  return video.video_type;
}

function Pagination({
  pagination,
  onPageChange,
}: {
  pagination: PaginatedVideos;
  onPageChange: (page: number) => void;
}) {
  const isFirstPage = pagination.current_page <= 1;
  const isLastPage = pagination.current_page >= pagination.last_page;

  return (
    <nav className="flex flex-col gap-3 border border-neutral-200 bg-white p-4 text-sm text-neutral-700 sm:flex-row sm:items-center sm:justify-between">
      <p>
        {pagination.total === 0
          ? '0件'
          : `${pagination.total}件中 ${pagination.from}-${pagination.to}件を表示`}
      </p>

      <div className="flex items-center gap-2">
        <button
          type="button"
          className="border border-neutral-300 px-3 py-2 text-neutral-800 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:text-neutral-400"
          onClick={() => onPageChange(pagination.current_page - 1)}
          disabled={isFirstPage}
        >
          前へ
        </button>
        <span className="px-2">
          {pagination.current_page} / {pagination.last_page}
        </span>
        <button
          type="button"
          className="border border-neutral-300 px-3 py-2 text-neutral-800 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:text-neutral-400"
          onClick={() => onPageChange(pagination.current_page + 1)}
          disabled={isLastPage}
        >
          次へ
        </button>
      </div>
    </nav>
  );
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [pagination, setPagination] = useState<PaginatedVideos | null>(null);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);

    fetch(`${API_URL}/api/videos?page=${page}`)
      .then((res) => {
        if (!res.ok) {
          throw new Error('動画データの取得に失敗しました');
        }

        return res.json();
      })
      .then((data: PaginatedVideos) => {
        setVideos(data.data);
        setPagination(data);
        setErrorMessage(null);
      })
      .catch((err) => {
        setErrorMessage(err.message);
        setVideos([]);
        setPagination(null);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [page]);

  return (
    <main className="min-h-screen bg-white px-5 py-8 text-neutral-950 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold">無料公開中アニメ</h1>
        </header>

        {isLoading && <p className="text-neutral-600">動画を読み込み中です。</p>}

        {errorMessage && (
          <p className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {errorMessage}
          </p>
        )}

        {!isLoading && !errorMessage && videos.length === 0 && (
          <p className="text-neutral-600">表示できる動画がありません。</p>
        )}

        {!isLoading && !errorMessage && pagination && (
          <div className="mb-6">
            <Pagination pagination={pagination} onPageChange={setPage} />
          </div>
        )}

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((video) => {
            const episodeLabel = getEpisodeLabel(video);
            const publishedAt = formatDate(video.published_at);
            const freeUntilAt = formatDate(video.free_until_at);

            return (
              <article key={video.id} className="overflow-hidden border border-neutral-200 bg-white">
                <div className="aspect-video w-full bg-neutral-100">
                  <iframe
                    className="h-full w-full"
                    src={`https://www.youtube.com/embed/${video.youtube_video_id}`}
                    title={video.title}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                  />
                </div>

                <div className="space-y-3 p-4">
                  <div>
                    <h2 className="line-clamp-2 text-base font-semibold leading-6">{video.title}</h2>
                    {video.anime_title && (
                      <p className="mt-1 text-sm text-neutral-600">{video.anime_title}</p>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 text-xs text-neutral-600">
                    {episodeLabel && (
                      <span className="border border-neutral-200 px-2 py-1">{episodeLabel}</span>
                    )}
                    {publishedAt && (
                      <span className="border border-neutral-200 px-2 py-1">公開日 {publishedAt}</span>
                    )}
                    {freeUntilAt && (
                      <span className="border border-neutral-200 px-2 py-1">無料期限 {freeUntilAt}</span>
                    )}
                  </div>

                  {video.channel_title && (
                    <p className="text-xs text-neutral-500">{video.channel_title}</p>
                  )}
                </div>
              </article>
            );
          })}
        </div>

        {!isLoading && !errorMessage && pagination && (
          <div className="mt-6">
            <Pagination pagination={pagination} onPageChange={setPage} />
          </div>
        )}
      </div>
    </main>
  );
}
