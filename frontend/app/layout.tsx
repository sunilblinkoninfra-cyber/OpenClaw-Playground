import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Clawdbot - Cloud IDE with AI',
  description: 'Zero installation friction cloud IDE with integrated AI agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
