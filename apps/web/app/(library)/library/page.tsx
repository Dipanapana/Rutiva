'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import {
  BookOpen,
  Download,
  Calendar,
  Clock,
  TrendingUp,
  ExternalLink,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { libraryApi, userApi } from '@/lib/api';
import { useAuthStore } from '@/lib/store';
import { formatPrice, getSubjectColor } from '@/lib/utils';

interface LibraryItem {
  id: string;
  product_id: string;
  sku: string;
  title: string;
  subject_code: string;
  subject_name: string;
  grade: number;
  term: number;
  year: number;
  thumbnail_url: string | null;
  progress_percent: number;
  download_count: number;
  purchased_at: string;
  last_accessed_at: string | null;
}

export default function LibraryPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const { data: libraryData, isLoading: libraryLoading } = useQuery({
    queryKey: ['library'],
    queryFn: () => libraryApi.list(),
    enabled: isAuthenticated,
  });

  const { data: statsData } = useQuery({
    queryKey: ['user-stats'],
    queryFn: () => userApi.getStats(),
    enabled: isAuthenticated,
  });

  const items: LibraryItem[] = libraryData?.data || [];
  const stats = statsData?.data || {
    purchased_guides: 0,
    active_timetables: 0,
    study_streak: 0,
    total_study_hours: 0,
  };

  const handleDownload = async (productId: string) => {
    try {
      const response = await libraryApi.getDownloadUrl(productId);
      window.open(response.data.url, '_blank');
    } catch (error) {
      console.error('Failed to get download URL:', error);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        {/* Hero */}
        <section className="bg-gradient-to-r from-primary-600 to-secondary-600 py-12 text-white">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold sm:text-4xl">
              Welcome back, {user?.first_name}!
            </h1>
            <p className="mt-2 text-white/80">
              Access your purchased study guides and track your progress.
            </p>
          </div>
        </section>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Stats */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                label: 'Study Guides',
                value: stats.purchased_guides,
                icon: BookOpen,
                color: 'bg-primary-100 text-primary-600',
              },
              {
                label: 'Active Timetables',
                value: stats.active_timetables,
                icon: Calendar,
                color: 'bg-secondary-100 text-secondary-600',
              },
              {
                label: 'Study Streak',
                value: `${stats.study_streak} days`,
                icon: TrendingUp,
                color: 'bg-accent-100 text-accent-600',
              },
              {
                label: 'Study Hours',
                value: `${stats.total_study_hours}h`,
                icon: Clock,
                color: 'bg-green-100 text-green-600',
              },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="rounded-2xl bg-white p-6 shadow-sm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className={`inline-flex rounded-lg p-3 ${stat.color}`}>
                  <stat.icon className="h-6 w-6" />
                </div>
                <div className="mt-4 text-2xl font-bold text-gray-900">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </motion.div>
            ))}
          </div>

          {/* Library Items */}
          <h2 className="mb-6 text-xl font-bold text-gray-900">My Study Guides</h2>

          {libraryLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="h-64 animate-pulse rounded-2xl bg-gray-200"
                />
              ))}
            </div>
          ) : items.length === 0 ? (
            <div className="rounded-2xl bg-white p-12 text-center shadow-sm">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                No guides yet
              </h3>
              <p className="mt-2 text-gray-500">
                Browse our study guides and start your learning journey.
              </p>
              <Link href="/shop" className="mt-6 inline-block">
                <Button>Browse Study Guides</Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((item, index) => (
                <motion.div
                  key={item.id}
                  className="rounded-2xl bg-white overflow-hidden shadow-sm"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-video bg-gray-100">
                    {item.thumbnail_url ? (
                      <img
                        src={item.thumbnail_url}
                        alt={item.title || 'Study Guide'}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div
                        className="flex h-full w-full items-center justify-center"
                        style={{
                          backgroundColor: `${getSubjectColor(item.subject_code || 'default')}20`,
                        }}
                      >
                        <BookOpen
                          className="h-12 w-12"
                          style={{ color: getSubjectColor(item.subject_code || 'default') }}
                        />
                      </div>
                    )}

                    {/* Progress bar */}
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200">
                      <div
                        className="h-full bg-primary-500 transition-all"
                        style={{ width: `${item.progress_percent}%` }}
                      />
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <div className="mb-1 text-sm text-gray-500">
                      Grade {item.grade} | Term {item.term}
                    </div>
                    <h3 className="font-semibold text-gray-900 line-clamp-2">
                      {item.title}
                    </h3>

                    <div className="mt-2 flex items-center justify-between text-sm text-gray-500">
                      <span>{item.progress_percent}% complete</span>
                      <span
                        className="rounded-full px-2 py-0.5 text-xs font-medium text-white"
                        style={{
                          backgroundColor: getSubjectColor(item.subject_code || 'default'),
                        }}
                      >
                        {item.subject_name}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="mt-4 flex gap-2">
                      <Link href={`/guide/${item.product_id}`} className="flex-1">
                        <Button variant="outline" className="w-full" size="sm">
                          <ExternalLink className="mr-1 h-4 w-4" />
                          Open
                        </Button>
                      </Link>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => handleDownload(item.product_id)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Link href={`/guide/${item.product_id}/timetable`}>
                        <Button variant="ghost" size="sm">
                          <Calendar className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
