'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useEffect, useMemo, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '';

type AnimeTitle = {
  id: number;
  title: string;
  title_kana: string | null;
  title_en: string | null;
  videos_count: number;
};

const GROUPS = [
  'あ行',
  'か行',
  'さ行',
  'た行',
  'な行',
  'は行',
  'ま行',
  'や行',
  'ら行',
  'わ行',
  'A-D',
  'E-H',
  'I-L',
  'M-P',
  'Q-T',
  'U-Z',
  'その他',
] as const;

function toHiragana(value: string) {
  return value.replace(/[ァ-ン]/g, (char) => String.fromCharCode(char.charCodeAt(0) - 0x60));
}

function getTitleGroup(title: AnimeTitle) {
  const source = toHiragana((title.title_kana || title.title).trim());
  const first = source.charAt(0).toUpperCase();

  if ('あいうえお'.includes(first)) return 'あ行';
  if ('かきくけこがぎぐげご'.includes(first)) return 'か行';
  if ('さしすせそざじずぜぞ'.includes(first)) return 'さ行';
  if ('たちつてとだぢづでど'.includes(first)) return 'た行';
  if ('なにぬねの'.includes(first)) return 'な行';
  if ('はひふへほばびぶべぼぱぴぷぺぽ'.includes(first)) return 'は行';
  if ('まみむめも'.includes(first)) return 'ま行';
  if ('やゆよ'.includes(first)) return 'や行';
  if ('らりるれろ'.includes(first)) return 'ら行';
  if ('わをん'.includes(first)) return 'わ行';

  const englishFirst = (title.title_en || title.title).trim().charAt(0).toUpperCase();

  if (englishFirst >= 'A' && englishFirst <= 'D') return 'A-D';
  if (englishFirst >= 'E' && englishFirst <= 'H') return 'E-H';
  if (englishFirst >= 'I' && englishFirst <= 'L') return 'I-L';
  if (englishFirst >= 'M' && englishFirst <= 'P') return 'M-P';
  if (englishFirst >= 'Q' && englishFirst <= 'T') return 'Q-T';
  if (englishFirst >= 'U' && englishFirst <= 'Z') return 'U-Z';

  if (first >= 'A' && first <= 'D') return 'A-D';
  if (first >= 'E' && first <= 'H') return 'E-H';
  if (first >= 'I' && first <= 'L') return 'I-L';
  if (first >= 'M' && first <= 'P') return 'M-P';
  if (first >= 'Q' && first <= 'T') return 'Q-T';
  if (first >= 'U' && first <= 'Z') return 'U-Z';

  return 'その他';
}

export default function TitlesPage() {
  const [titles, setTitles] = useState<AnimeTitle[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/videos/titles?all=1`)
      .then((res) => {
        if (!res.ok) {
          throw new Error('タイトル一覧の取得に失敗しました');
        }

        return res.json();
      })
      .then((data: AnimeTitle[]) => {
        setTitles(data);
        setErrorMessage(null);
      })
      .catch((err) => {
        setErrorMessage(err.message);
        setTitles([]);
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  const groupedTitles = useMemo(() => {
    return titles.reduce<Record<string, AnimeTitle[]>>((groups, title) => {
      const group = getTitleGroup(title);
      groups[group] = [...(groups[group] ?? []), title];
      return groups;
    }, {});
  }, [titles]);

  const activeGroups = GROUPS.filter((group) => groupedTitles[group]?.length);
  const visibleGroups = selectedGroup ? activeGroups.filter((group) => group === selectedGroup) : activeGroups;

  return (
    <main
      className="min-h-screen bg-white bg-cover bg-fixed bg-center px-5 py-8 text-neutral-950 sm:px-8"
      style={{ backgroundImage: "url('/background/ip-background.svg')" }}
    >
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col gap-3">
          <h1 className="flex items-center gap-1 text-3xl font-bold">
            <Image
              className="rounded-2xl object-cover shadow-sm"
              src="/icon/cat.png"
              alt=""
              width={1536}
              height={1024}
              sizes="64px"
              style={{ width: '64px', height: '64px' }}
              priority
            />
            <Image
              className="rounded-2xl object-contain shadow-sm"
              src="/background/title.png"
              alt=""
              width={3721}
              height={268}
              sizes="(max-width: 640px) 280px, 420px"
              style={{ height: '64px', width: '650px' }}
              priority
            />
          </h1>
        </div>
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <h1 className="text-2xl font-bold">タイトル一覧</h1>
          <Link
            className="w-fit rounded-full border border-sky-200 bg-sky-50 px-4 py-2 text-sm text-sky-700 shadow-sm hover:border-sky-400"
            href="/"
          >
            動画一覧へ戻る
          </Link>
        </header>

        {isLoading && <p className="text-neutral-600">タイトルを読み込み中です。</p>}

        {errorMessage && (
          <p className="rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {errorMessage}
          </p>
        )}

        {!isLoading && !errorMessage && activeGroups.length === 0 && (
          <p className="text-neutral-600">表示できるタイトルがありません。</p>
        )}

        {activeGroups.length > 0 && (
          <nav className="sticky top-0 z-10 mb-8 flex flex-wrap gap-2 rounded-2xl border border-sky-100 bg-white/95 p-3 shadow-sm">
            <button
              type="button"
              className={`rounded-full border px-4 py-2 text-sm shadow-sm ${selectedGroup === null
                  ? 'border-emerald-600 bg-emerald-600 text-white'
                  : 'border-sky-200 bg-sky-50 text-sky-700 hover:border-sky-400'
                }`}
              onClick={() => setSelectedGroup(null)}
            >
              すべて
            </button>
            {activeGroups.map((group) => (
              <button
                key={group}
                type="button"
                className={`rounded-full border px-4 py-2 text-sm shadow-sm ${selectedGroup === group
                    ? 'border-emerald-600 bg-emerald-600 text-white'
                    : 'border-sky-200 bg-sky-50 text-sky-700 hover:border-sky-400'
                  }`}
                onClick={() => setSelectedGroup(group)}
              >
                {group}
              </button>
            ))}
          </nav>
        )}

        <div className="space-y-10">
          {visibleGroups.map((group) => (
            <section key={group} id={group} className="scroll-mt-20">
              <h2 className="mb-4 border-b border-sky-100 pb-2 text-xl font-semibold">{group}</h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {groupedTitles[group].map((title) => (
                  <Link
                    key={title.id}
                    className="flex items-center justify-between gap-4 rounded-2xl border border-sky-100 bg-white/95 px-4 py-3 text-sm shadow-sm hover:border-sky-400"
                    href={`/?anime_title_id=${title.id}&title=${encodeURIComponent(title.title)}`}
                  >
                    <span>{title.title}</span>
                    <span className="shrink-0 text-xs text-neutral-500">{title.videos_count}件</span>
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
      </div>
    </main>
  );
}
