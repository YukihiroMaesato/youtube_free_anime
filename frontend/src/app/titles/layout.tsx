import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "タイトル一覧",
  description:
    "YouTubeで無料公開されているアニメ動画を、作品タイトルの五十音・英字別に探せるタイトル一覧です。",
  alternates: {
    canonical: "/titles",
  },
  openGraph: {
    title: "タイトル一覧",
    description:
      "YouTubeで無料公開されているアニメ動画を、作品タイトルの五十音・英字別に探せるタイトル一覧です。",
    url: "/titles",
  },
};

export default function TitlesLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
