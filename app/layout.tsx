import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const metadata: Metadata = {
  title: "베리챗 상점 - VeryMap",
  description: "베리챗 상점 정보를 국가/지역별로 쉽게 찾아보세요",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <head>
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9785548375633558"
          crossOrigin="anonymous"
        />
      </head>
      <body className="antialiased bg-gray-50 overflow-x-hidden">
        <div className="max-w-full overflow-x-hidden">
          {children}
        </div>
      </body>
    </html>
  );
}
