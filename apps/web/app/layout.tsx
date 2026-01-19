import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Rutiva - Your Roadmap to Results',
  description:
    'CAPS-aligned study guides with detailed course breakdowns and personalized study timetables for South African learners.',
  keywords: [
    'study guides',
    'CAPS',
    'South Africa',
    'education',
    'matric',
    'exam prep',
    'mathematics',
    'science',
  ],
  authors: [{ name: 'Rutiva Education' }],
  openGraph: {
    title: 'Rutiva - Your Roadmap to Results',
    description:
      'CAPS-aligned study guides with detailed course breakdowns and personalized study timetables.',
    url: 'https://rutiva.co.za',
    siteName: 'Rutiva',
    locale: 'en_ZA',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Rutiva - Your Roadmap to Results',
    description:
      'CAPS-aligned study guides with detailed course breakdowns and personalized study timetables.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-white antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
