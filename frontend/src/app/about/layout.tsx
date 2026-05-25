import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "このサイトについて",
  description:
    "わくわくアニメ巡礼、推しアニ見っけ！の概要、できること、掲載情報の注意点をまとめたページです。",
  alternates: {
    canonical: "/about",
  },
  openGraph: {
    title: "このサイトについて",
    description:
      "わくわくアニメ巡礼、推しアニ見っけ！の概要、できること、掲載情報の注意点をまとめたページです。",
    url: "/about",
  },
};

export default function AboutLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
