import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "わくわくアニメ巡礼、推しアニ見っけ！",
  description: "YouTubeで無料公開されているアニメ動画を探しやすくまとめるサイトです。",
  icons: {
    icon: "/favicon/title_icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen">
          {children}
          <footer className="border-t border-sky-100 bg-white/95">
            <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-6 text-sm text-neutral-600 sm:flex-row sm:items-center sm:justify-between sm:px-8">
              <p className="min-w-0 truncate">© {new Date().getFullYear()} わくわくアニメ巡礼、推しアニ見っけ！</p>
              <nav className="flex flex-wrap gap-x-4 gap-y-2">
                <Link className="text-sky-700 hover:text-sky-900" href="/">
                  トップ
                </Link>
                <Link className="text-sky-700 hover:text-sky-900" href="/about">
                  このサイトについて
                </Link>
              </nav>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
