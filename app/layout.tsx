import type { Metadata } from "next";
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
      <body className="antialiased bg-gray-50">
        {children}
      </body>
    </html>
  );
}
