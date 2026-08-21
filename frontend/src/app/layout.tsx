import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from '@/components/providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#FFFFFF' },
    { media: '(prefers-color-scheme: dark)', color: '#0B0E13' },
  ],
};

export const metadata: Metadata = {
  title: 'VanniDub AI — Automated Video Dubbing Pipeline',
  description:
    'Translate and dub YouTube videos into natural English speech with AI without re-encoding the video track. High-speed local processing with live pipeline tracking.',
  keywords: ['AI Dubbing', 'Video Translation', 'TTS', 'Whisper', 'IndicTrans2', 'Video Dubbing'],
  authors: [{ name: 'VanniDub AI Team' }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable} suppressHydrationWarning>
      <body className="min-h-screen text-[var(--color-text)] font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
