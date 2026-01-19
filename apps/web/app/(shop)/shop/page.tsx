'use client';

import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Search, Filter, BookOpen, ShoppingCart, Star } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { productsApi, cartApi } from '@/lib/api';
import { formatPrice, getSubjectColor } from '@/lib/utils';
import { useCartStore } from '@/lib/store';

interface Product {
  id: string;
  sku: string;
  title: string;
  description: string;
  subject_code: string;
  subject_name: string;
  grade: number;
  term: number;
  year: number;
  price_zar: number;
  sale_price_zar: number | null;
  is_on_sale: boolean;
  current_price: number;
  discount_percent?: number;
  thumbnail_url: string | null;
  total_weeks?: number;
  total_study_hours?: number;
  is_published: boolean;
}

interface Subject {
  code: string;
  name: string;
  product_count: number;
}

export default function ShopPage() {
  const [selectedGrade, setSelectedGrade] = useState<number | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const { setCart } = useCartStore();

  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['products', selectedGrade, selectedSubject, searchQuery],
    queryFn: () =>
      productsApi.list({
        grade: selectedGrade || undefined,
        subject: selectedSubject || undefined,
        search: searchQuery || undefined,
      }),
  });

  const { data: subjectsData } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => productsApi.listSubjects(),
  });

  const products: Product[] = productsData?.data?.products || [];
  const subjects = subjectsData?.data || [];

  const grades = [10, 11, 12];

  const handleAddToCart = async (productId: string) => {
    try {
      await cartApi.addItem(productId);
      const cartResponse = await cartApi.get();
      setCart(cartResponse.data.items, cartResponse.data.total_zar);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    }
  };

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        {/* Hero */}
        <section className="bg-gradient-to-r from-primary-600 to-secondary-600 py-12 text-white">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold sm:text-4xl">Study Guides</h1>
            <p className="mt-2 text-white/80">
              CAPS-aligned guides for Grades 10-12. Choose your grade and subject.
            </p>
          </div>
        </section>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Filters */}
          <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            {/* Grade Filter */}
            <div className="flex flex-wrap gap-2">
              <Button
                variant={selectedGrade === null ? 'primary' : 'outline'}
                size="sm"
                onClick={() => setSelectedGrade(null)}
              >
                All Grades
              </Button>
              {grades.map((grade) => (
                <Button
                  key={grade}
                  variant={selectedGrade === grade ? 'primary' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedGrade(grade)}
                >
                  Grade {grade}
                </Button>
              ))}
            </div>

            {/* Search */}
            <div className="relative w-full lg:w-72">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                type="search"
                placeholder="Search guides..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Subject Filter */}
          <div className="mb-8 flex flex-wrap gap-2">
            <Button
              variant={selectedSubject === null ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setSelectedSubject(null)}
            >
              All Subjects
            </Button>
            {subjects.map((subject: Subject) => (
              <Button
                key={subject.code}
                variant={selectedSubject === subject.code ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => setSelectedSubject(subject.code)}
              >
                {subject.name} ({subject.product_count})
              </Button>
            ))}
          </div>

          {/* Products Grid */}
          {productsLoading ? (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="h-80 animate-pulse rounded-2xl bg-gray-200"
                />
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="py-12 text-center">
              <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-semibold text-gray-900">
                No guides found
              </h3>
              <p className="mt-2 text-gray-500">
                Try adjusting your filters or search query.
              </p>
            </div>
          ) : (
            <motion.div
              className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {products.map((product) => (
                <motion.div
                  key={product.id}
                  className="group rounded-2xl border border-gray-200 bg-white overflow-hidden transition-shadow hover:shadow-lg"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-[4/3] bg-gray-100">
                    {product.thumbnail_url ? (
                      <img
                        src={product.thumbnail_url}
                        alt={product.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div
                        className="flex h-full w-full items-center justify-center"
                        style={{ backgroundColor: `${getSubjectColor(product.subject_code)}20` }}
                      >
                        <BookOpen
                          className="h-16 w-16"
                          style={{ color: getSubjectColor(product.subject_code) }}
                        />
                      </div>
                    )}

                    {/* Badges */}
                    {product.is_on_sale && product.discount_percent && (
                      <div className="absolute left-3 top-3">
                        <span className="inline-flex items-center rounded-full bg-green-500 px-2.5 py-0.5 text-xs font-medium text-white">
                          {product.discount_percent}% OFF
                        </span>
                      </div>
                    )}

                    {/* Subject Tag */}
                    <span
                      className="absolute right-3 top-3 rounded-full px-2.5 py-0.5 text-xs font-medium text-white"
                      style={{ backgroundColor: getSubjectColor(product.subject_code) }}
                    >
                      {product.subject_name}
                    </span>
                  </div>

                  {/* Content */}
                  <div className="p-4">
                    <div className="mb-1 text-sm text-gray-500">
                      Grade {product.grade} | Term {product.term}
                    </div>
                    <Link href={`/shop/${product.sku}`}>
                      <h3 className="font-semibold text-gray-900 line-clamp-2 hover:text-primary-600">
                        {product.title}
                      </h3>
                    </Link>
                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {product.description}
                    </p>

                    {/* Price & Action */}
                    <div className="mt-4 flex items-center justify-between">
                      <div>
                        <span className="text-lg font-bold text-gray-900">
                          {formatPrice(product.current_price)}
                        </span>
                        {product.is_on_sale && (
                          <span className="ml-2 text-sm text-gray-400 line-through">
                            {formatPrice(product.price_zar)}
                          </span>
                        )}
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleAddToCart(product.id)}
                      >
                        <ShoppingCart className="mr-1 h-4 w-4" />
                        Add
                      </Button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </main>
      <Footer />
    </>
  );
}
