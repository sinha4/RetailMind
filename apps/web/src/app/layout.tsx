import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RetailMind",
  description: "Shopping that remembers what matters to you.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

