'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

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

type Tag = {
  id: number;
  name: string;
  videos_count: number;
};

type AnimeTitleOption = {
  id: number;
  title: string;
  title_kana?: string | null;
  title_en?: string | null;
  videos_count: number;
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

function stopYoutubeVideo(iframe: HTMLIFrameElement | null) {
  iframe?.contentWindow?.postMessage(
    JSON.stringify({
      event: 'command',
      func: 'stopVideo',
      args: [],
    }),
    'https://www.youtube.com'
  );
}

function stopAllYoutubeVideos() {
  document
    .querySelectorAll<HTMLIFrameElement>('iframe[data-youtube-player="true"]')
    .forEach((iframe) => stopYoutubeVideo(iframe));
}

function VideoCard({ video }: { video: Video }) {
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const episodeLabel = getEpisodeLabel(video);
  const publishedAt = formatDate(video.published_at);
  const freeUntilAt = formatDate(video.free_until_at);

  useEffect(() => {
    const iframe = iframeRef.current;

    if (!iframe) {
      return undefined;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) {
          stopYoutubeVideo(iframe);
        }
      },
      {
        threshold: 0.1,
      }
    );

    observer.observe(iframe);

    return () => {
      stopYoutubeVideo(iframe);
      observer.disconnect();
    };
  }, []);

  return (
    <article className="overflow-hidden rounded-2xl border border-pink-100 bg-white shadow-sm">
      <div className="aspect-video w-full bg-neutral-100">
        <iframe
          ref={iframeRef}
          className="h-full w-full"
          src={`https://www.youtube.com/embed/${video.youtube_video_id}?enablejsapi=1`}
          title={video.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
          data-youtube-player="true"
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
            <span className="rounded-full border border-sky-100 bg-sky-50 px-2 py-1 text-sky-700">{episodeLabel}</span>
          )}
          {publishedAt && (
            <span className="rounded-full border border-emerald-100 bg-emerald-50 px-2 py-1 text-emerald-700">
              公開日 {publishedAt}
            </span>
          )}
          {freeUntilAt && (
            <span className="rounded-full border border-rose-100 bg-rose-50 px-2 py-1 text-rose-700">
              無料期限 {freeUntilAt}
            </span>
          )}
        </div>

        {video.channel_title && (
          <p className="text-xs text-neutral-500">{video.channel_title}</p>
        )}
      </div>
    </article>
  );
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
    <nav className="flex flex-col gap-3 rounded-2xl border border-pink-100 bg-white/95 p-4 text-sm text-neutral-700 shadow-sm sm:flex-row sm:items-center sm:justify-between">
      <p>
        {pagination.total === 0
          ? '0件'
          : `${pagination.total}件中 ${pagination.from}-${pagination.to}件を表示`}
      </p>

      <div className="flex items-center gap-2">
        <button
          type="button"
          className="rounded-full border border-pink-200 bg-pink-50 px-4 py-2 text-pink-700 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:bg-neutral-50 disabled:text-neutral-400"
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
          className="rounded-full border border-pink-200 bg-pink-50 px-4 py-2 text-pink-700 disabled:cursor-not-allowed disabled:border-neutral-200 disabled:bg-neutral-50 disabled:text-neutral-400"
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
  const [tags, setTags] = useState<Tag[]>([]);
  const [titleOptions, setTitleOptions] = useState<AnimeTitleOption[]>([]);
  const [selectedTagId, setSelectedTagId] = useState<number | null>(null);
  const [selectedTitle, setSelectedTitle] = useState<AnimeTitleOption | null>(null);
  const [titleSearch, setTitleSearch] = useState('');
  const [page, setPage] = useState(1);
  const [isUrlFilterReady, setIsUrlFilterReady] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const id = Number(params.get('anime_title_id'));
    const title = params.get('title');

    if (id && title) {
      setSelectedTitle({
        id,
        title,
        videos_count: 0,
      });
      setTitleSearch(title);
      setPage(1);
    }

    setIsUrlFilterReady(true);
  }, []);

  useEffect(() => {
    fetch(`${API_URL}/api/videos/tags`)
      .then((res) => {
        if (!res.ok) {
          throw new Error('タグの取得に失敗しました');
        }

        return res.json();
      })
      .then((data: Tag[]) => {
        setTags(data);
      })
      .catch(() => {
        setTags([]);
      });
  }, []);

  useEffect(() => {
    const timerId = window.setTimeout(() => {
      const params = new URLSearchParams();

      if (titleSearch.trim() !== '') {
        params.set('q', titleSearch.trim());
      }

      fetch(`${API_URL}/api/videos/titles?${params.toString()}`)
        .then((res) => {
          if (!res.ok) {
            throw new Error('タイトル候補の取得に失敗しました');
          }

          return res.json();
        })
        .then((data: AnimeTitleOption[]) => {
          setTitleOptions(data);
        })
        .catch(() => {
          setTitleOptions([]);
        });
    }, 250);

    return () => window.clearTimeout(timerId);
  }, [titleSearch]);

  useEffect(() => {
    if (!isUrlFilterReady) {
      return;
    }

    stopAllYoutubeVideos();
    setIsLoading(true);

    const params = new URLSearchParams({
      page: String(page),
    });

    if (selectedTagId) {
      params.set('tag_id', String(selectedTagId));
    }

    if (selectedTitle) {
      params.set('anime_title_id', String(selectedTitle.id));
    }

    fetch(`${API_URL}/api/videos?${params.toString()}`)
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
  }, [page, selectedTagId, selectedTitle, isUrlFilterReady]);

  function selectTag(tagId: number | null) {
    stopAllYoutubeVideos();
    setSelectedTagId(tagId);
    setPage(1);
  }

  function selectTitle(title: AnimeTitleOption | null) {
    stopAllYoutubeVideos();
    setSelectedTitle(title);
    setTitleSearch(title?.title ?? '');
    setPage(1);

    if (!title && typeof window !== 'undefined') {
      window.history.replaceState(null, '', window.location.pathname);
    }
  }

  return (
    <main
      className="min-h-screen bg-white bg-cover bg-fixed bg-center px-5 py-8 text-neutral-950 sm:px-8"
      style={{ backgroundImage: "url('/background/ip-background.svg')" }}
    >
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 space-y-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex flex-col gap-3">
              <h1 className="flex items-center gap-3 text-3xl font-bold">
                <Image
                  className="rounded-2xl object-cover shadow-sm"
                  src="/icon/cat.png"
                  alt=""
                  width={56}
                  height={56}
                  priority
                />
                <span>推しアニ見っけ！</span>
              </h1>
            </div>

            <div className="flex max-w-3xl flex-wrap gap-2">
              <button
                type="button"
                className={`rounded-full border px-4 py-2 text-sm shadow-sm ${
                  selectedTagId === null
                    ? 'border-pink-500 bg-pink-500 text-white'
                    : 'border-pink-200 bg-pink-50 text-pink-700 hover:border-pink-400'
                }`}
                onClick={() => selectTag(null)}
              >
                すべて
              </button>
              {tags.map((tag) => (
                <button
                  key={tag.id}
                  type="button"
                  className={`rounded-full border px-4 py-2 text-sm shadow-sm ${
                    selectedTagId === tag.id
                      ? 'border-pink-500 bg-pink-500 text-white'
                      : 'border-pink-200 bg-pink-50 text-pink-700 hover:border-pink-400'
                  }`}
                  onClick={() => selectTag(tag.id)}
                >
                  {tag.name} ({tag.videos_count})
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div className="relative w-full max-w-xl">
              <div className="mt-2 flex gap-2">
                <input
                  id="anime-title-search"
                  className="min-w-0 flex-1 rounded-full border border-pink-200 bg-white/95 px-4 py-2 text-sm outline-none focus:border-pink-500"
                  type="search"
                  value={titleSearch}
                  placeholder="タイトルを検索"
                  onChange={(event) => {
                    setTitleSearch(event.target.value);
                    if (selectedTitle) {
                      setSelectedTitle(null);
                      setPage(1);
                    }
                  }}
                />
                {selectedTitle && (
                  <button
                    type="button"
                    className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm text-slate-700"
                    onClick={() => selectTitle(null)}
                  >
                    解除
                  </button>
                )}
              </div>

              {titleSearch.trim() !== '' && titleOptions.length > 0 && !selectedTitle && (
                <div className="absolute left-0 right-0 top-full z-20 mt-2 max-h-72 overflow-y-auto rounded-2xl border border-pink-100 bg-white shadow-lg">
                  {titleOptions.map((title) => (
                    <button
                      key={title.id}
                      type="button"
                      className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left text-sm hover:bg-pink-50"
                      onClick={() => selectTitle(title)}
                    >
                      <span>{title.title}</span>
                      <span className="shrink-0 text-xs text-neutral-500">{title.videos_count}件</span>
                    </button>
                  ))}
                </div>
              )}

              {selectedTitle && (
                <p className="mt-2 text-sm text-neutral-600">
                  {selectedTitle.title} で絞り込み中
                </p>
              )}
            </div>

            <Link
              className="w-fit shrink-0 rounded-full border border-sky-200 bg-sky-50 px-4 py-2 text-sm text-sky-700 shadow-sm hover:border-sky-400"
              href="/titles"
            >
              タイトル一覧
            </Link>
          </div>
        </header>

        {isLoading && <p className="text-neutral-600">動画を読み込み中です。</p>}

        {errorMessage && (
          <p className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
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
          {videos.map((video) => (
            <VideoCard key={video.id} video={video} />
          ))}
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
