import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { GoogleAnalytics } from "@next/third-parties/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://simpletk202.com";
const siteName = "わくわくアニメ巡礼、推しアニ見っけ！";
const siteDescription =
  "YouTubeで無料公開されているアニメ動画を、タグ・タイトル・公開終了日から探しやすくまとめるサイトです。";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  applicationName: siteName,
  title: {
    default: siteName,
    template: `%s | ${siteName}`,
  },
  description: siteDescription,
  keywords: [
    "無料アニメ",
    "YouTube アニメ",
    "期間限定 アニメ",
    "公式アニメ",
    "アニメ配信",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    type: "website",
    locale: "ja_JP",
    url: "/",
    siteName,
    title: siteName,
    description: siteDescription,
    images: [
      {
        url: "/background/title.png",
        width: 3721,
        height: 268,
        alt: siteName,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: siteName,
    description: siteDescription,
    images: ["/background/title.png"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
  icons: {
    icon: "/favicon/title_icon.png",
    apple: "/favicon/title_icon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const gaId = process.env.NEXT_PUBLIC_GA_ID;

  const isGAEnabled =
    process.env.NODE_ENV === "production" &&
    !!gaId;
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: siteName,
    url: siteUrl,
    description: siteDescription,
    inLanguage: "ja",
  };

  return (
    <html lang="ja">
      <body className={inter.className}>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
        />
        <div className="min-h-screen">
          {children}

          <footer className="border-t border-sky-100 bg-white/95">
            <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-6 text-sm text-neutral-600 sm:flex-row sm:items-center sm:justify-between sm:px-8">
              <p className="min-w-0 truncate">
                © {new Date().getFullYear()} わくわくアニメ巡礼、推しアニ見っけ！
              </p>

              <nav className="flex flex-wrap gap-x-4 gap-y-2">
                <Link
                  className="text-sky-700 hover:text-sky-900"
                  href="/"
                >
                  トップ
                </Link>

                <Link
                  className="text-sky-700 hover:text-sky-900"
                  href="/about"
                >
                  このサイトについて
                </Link>
              </nav>
            </div>
          </footer>
        </div>

        {isGAEnabled && (
          <GoogleAnalytics gaId={gaId} />
        )}
      </body>
    </html>
  );
}
