'use client';

import Link from 'next/link';
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

  return (
    <main className="min-h-screen bg-white px-5 py-8 text-neutral-950 sm:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold">タイトル一覧</h1>
            <p className="mt-2 text-sm text-neutral-600">タイトルを選ぶと動画一覧へ戻ります。</p>
          </div>
          <Link className="w-fit border border-neutral-300 px-3 py-2 text-sm text-neutral-700" href="/">
            動画一覧へ戻る
          </Link>
        </header>

        {isLoading && <p className="text-neutral-600">タイトルを読み込み中です。</p>}

        {errorMessage && (
          <p className="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {errorMessage}
          </p>
        )}

        {!isLoading && !errorMessage && activeGroups.length === 0 && (
          <p className="text-neutral-600">表示できるタイトルがありません。</p>
        )}

        {activeGroups.length > 0 && (
          <nav className="sticky top-0 z-10 mb-8 flex flex-wrap gap-2 border-b border-neutral-200 bg-white py-3">
            {activeGroups.map((group) => (
              <a
                key={group}
                className="border border-neutral-300 px-3 py-2 text-sm text-neutral-700 hover:border-neutral-900 hover:text-neutral-950"
                href={`#${group}`}
              >
                {group}
              </a>
            ))}
          </nav>
        )}

        <div className="space-y-10">
          {activeGroups.map((group) => (
            <section key={group} id={group} className="scroll-mt-20">
              <h2 className="mb-4 border-b border-neutral-200 pb-2 text-xl font-semibold">{group}</h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {groupedTitles[group].map((title) => (
                  <Link
                    key={title.id}
                    className="flex items-center justify-between gap-4 border border-neutral-200 px-4 py-3 text-sm hover:border-neutral-900"
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
