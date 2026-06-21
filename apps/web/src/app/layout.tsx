import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PanelFlow | reader.hflow",
  description: "Private self-hosted reader infrastructure status.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
