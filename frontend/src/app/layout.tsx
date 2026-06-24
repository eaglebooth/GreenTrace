import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GreenTrace",
  description: "Dynamic carbon-credit certification powered by GenLayer AI audits.",
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
