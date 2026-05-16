'use client';

import Link from 'next/link';

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-white px-5 py-10 text-neutral-950 sm:px-8">
      <div className="mx-auto max-w-3xl space-y-8">
        <header className="space-y-3">
          <h1 className="text-3xl font-bold">このサイトについて</h1>
          <p className="text-sm text-neutral-600">
            「わくわくアニメ巡礼、推しアニ見っけ！」は、YouTubeで無料公開されているアニメ動画を探しやすくまとめるサイトです。
          </p>
        </header>

        <section className="space-y-3 rounded-2xl border border-sky-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold">できること</h2>
          <ul className="list-disc space-y-2 pl-5 text-sm text-neutral-700">
            <li>タグで絞り込み</li>
            <li>タイトルで検索・絞り込み</li>
            <li>公開日・無料期限などの情報を確認</li>
          </ul>
        </section>

        <section className="space-y-2 text-sm text-neutral-700">
          <h2 className="text-lg font-semibold">ご注意</h2>
          <p>
            掲載内容は取得タイミングにより変わる場合があります。動画の視聴可否や最新情報は、各YouTubeページでご確認ください。
          </p>
        </section>

        <div>
          <Link
            href="/"
            className="inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-4 py-2 text-sm text-sky-700 shadow-sm hover:border-sky-400"
          >
            トップに戻る
          </Link>
        </div>
      </div>
    </main>
  );
}

