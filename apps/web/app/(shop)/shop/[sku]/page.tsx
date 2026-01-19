'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  BookOpen,
  Calendar,
  Clock,
  CheckCircle,
  ShoppingCart,
  ArrowLeft,
  Download,
  FileText,
  Target,
  Lightbulb,
  TrendingUp,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { productsApi, cartApi } from '@/lib/api';
import { formatPrice, getSubjectColor, getTermLabel } from '@/lib/utils';
import { useCartStore } from '@/lib/store';

interface Unit {
  unit_number: number;
  title: string;
  weeks_allocated: number;
  topics: Topic[];
}

interface Topic {
  topic_id: string;
  title: string;
  week: number;
  hours: number;
  content_sections: ContentSection[];
  key_formulas?: string[];
  common_mistakes?: string[];
  exam_tips?: string[];
  key_concepts: KeyConcept[];
  worked_examples: WorkedExample[];
  practice_problems: PracticeProblem[];
}

interface ContentSection {
  section: string;
  title: string;
  concepts: string[];
  worked_examples: number;
  practice_problems: number;
  difficulty?: string;
}

interface KeyConcept {
  concept: string;
  definition: string;
  importance: string;
}

interface WorkedExample {
  example_number: number;
  problem: string;
  solution: string;
  difficulty: string;
}

interface PracticeProblem {
  problem_number: number;
  question: string;
  difficulty: string;
  marks?: number;
}

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
  current_price: number;
  is_on_sale: boolean;
  thumbnail_url: string | null;
  total_weeks: number;
  total_study_hours: number;
  content_json: {
    guide_id: string;
    subject: string;
    subject_name: string;
    grade: number;
    term: number;
    year: number;
    total_weeks: number;
    total_hours: number;
    units: Unit[];
  };
}

export default function ProductDetailPage() {
  const params = useParams();
  const sku = params.sku as string;
  const { setCart } = useCartStore();

  const { data: productData, isLoading } = useQuery({
    queryKey: ['product', sku],
    queryFn: () => productsApi.getBySku(sku),
  });

  const product: Product | undefined = productData?.data;

  const handleAddToCart = async () => {
    if (!product) return;

    try {
      await cartApi.addItem(product.id);
      const cartResponse = await cartApi.get();
      setCart(cartResponse.data.items, cartResponse.data.total_zar);
    } catch (error) {
      console.error('Failed to add to cart:', error);
    }
  };

  if (isLoading) {
    return (
      <>
        <Header />
        <main className="min-h-screen bg-gray-50 py-12">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="animate-pulse space-y-8">
              <div className="h-8 w-48 bg-gray-200 rounded" />
              <div className="h-64 bg-gray-200 rounded-2xl" />
              <div className="h-96 bg-gray-200 rounded-2xl" />
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (!product) {
    return (
      <>
        <Header />
        <main className="min-h-screen bg-gray-50 py-12">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
            <BookOpen className="mx-auto h-16 w-16 text-gray-400" />
            <h1 className="mt-4 text-2xl font-bold text-gray-900">
              Study Guide Not Found
            </h1>
            <p className="mt-2 text-gray-600">
              The study guide you're looking for doesn't exist.
            </p>
            <Link href="/shop" className="mt-6 inline-block">
              <Button>Browse All Guides</Button>
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  const content = product.content_json;
  const totalTopics = content.units.reduce((sum, unit) => sum + unit.topics.length, 0);
  const totalConcepts = content.units.reduce(
    (sum, unit) => sum + unit.topics.reduce((s, t) => s + (t.key_concepts?.length || 0), 0),
    0
  );

  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        {/* Breadcrumb */}
        <div className="border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
            <Link
              href="/shop"
              className="flex items-center text-sm text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Study Guides
            </Link>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          {/* Product Header */}
          <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200">
            <div className="grid gap-8 lg:grid-cols-3">
              {/* Left: Image/Icon */}
              <div className="lg:col-span-1">
                <div
                  className="flex aspect-[4/3] w-full items-center justify-center rounded-xl"
                  style={{ backgroundColor: `${getSubjectColor(product.subject_code)}20` }}
                >
                  <BookOpen
                    className="h-24 w-24"
                    style={{ color: getSubjectColor(product.subject_code) }}
                  />
                </div>

                {/* Stats */}
                <div className="mt-6 space-y-3">
                  <div className="flex items-center space-x-3 text-sm">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-600">
                      {content.total_weeks} weeks • {getTermLabel(product.term)} {product.year}
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <Clock className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-600">
                      {content.total_hours} study hours
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <FileText className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-600">
                      {content.units.length} units • {totalTopics} topics
                    </span>
                  </div>
                  <div className="flex items-center space-x-3 text-sm">
                    <Lightbulb className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-600">
                      {totalConcepts} key concepts
                    </span>
                  </div>
                </div>
              </div>

              {/* Right: Details */}
              <div className="lg:col-span-2">
                <span
                  className="inline-block rounded-full px-3 py-1 text-sm font-medium text-white"
                  style={{ backgroundColor: getSubjectColor(product.subject_code) }}
                >
                  {product.subject_name}
                </span>

                <h1 className="mt-4 text-3xl font-bold text-gray-900">
                  {product.title}
                </h1>

                <p className="mt-4 text-lg text-gray-600">{product.description}</p>

                {/* What's Included */}
                <div className="mt-6 rounded-xl bg-gray-50 p-6">
                  <h3 className="font-semibold text-gray-900 mb-4">
                    What's Included:
                  </h3>
                  <ul className="space-y-2">
                    {[
                      'Complete term syllabus breakdown',
                      'Week-by-week study plan',
                      'Worked examples for every topic',
                      'Practice problems with solutions',
                      'Key formulas and summaries',
                      'Exam tips from expert teachers',
                      'Custom study timetable generator',
                    ].map((item, i) => (
                      <li key={i} className="flex items-start space-x-2 text-sm">
                        <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-gray-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Price & CTA */}
                <div className="mt-8 flex items-center justify-between border-t border-gray-200 pt-6">
                  <div>
                    <div className="text-3xl font-bold text-gray-900">
                      {formatPrice(product.current_price)}
                    </div>
                    {product.is_on_sale && product.sale_price_zar && (
                      <div className="text-sm text-gray-500 line-through">
                        {formatPrice(product.price_zar)}
                      </div>
                    )}
                    <div className="mt-1 text-sm text-gray-500">
                      One-time purchase • Instant download
                    </div>
                  </div>
                  <Button size="lg" onClick={handleAddToCart} className="gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    Add to Cart
                  </Button>
                </div>
              </div>
            </div>
          </div>

          {/* Course Content */}
          <div className="mt-8">
            <div className="rounded-2xl bg-white p-8 shadow-sm border border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Course Content
              </h2>

              <div className="space-y-6">
                {content.units.map((unit, unitIndex) => (
                  <motion.div
                    key={unit.unit_number}
                    className="border border-gray-200 rounded-xl overflow-hidden"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: unitIndex * 0.1 }}
                  >
                    {/* Unit Header */}
                    <div
                      className="p-6"
                      style={{ backgroundColor: `${getSubjectColor(product.subject_code)}10` }}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            Unit {unit.unit_number}: {unit.title}
                          </h3>
                          <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                            <span>{unit.weeks_allocated} weeks</span>
                            <span>•</span>
                            <span>{unit.topics.length} topics</span>
                          </div>
                        </div>
                        <Target
                          className="h-6 w-6"
                          style={{ color: getSubjectColor(product.subject_code) }}
                        />
                      </div>
                    </div>

                    {/* Topics */}
                    <div className="divide-y divide-gray-200">
                      {unit.topics.map((topic, topicIndex) => (
                        <div key={topic.topic_id} className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h4 className="font-medium text-gray-900">
                                {topicIndex + 1}. {topic.title}
                              </h4>
                              <div className="mt-1 flex items-center space-x-3 text-sm text-gray-500">
                                <span>Week {topic.week}</span>
                                <span>•</span>
                                <span>{topic.hours}h</span>
                                {topic.key_concepts && (
                                  <>
                                    <span>•</span>
                                    <span>{topic.key_concepts.length} concepts</span>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Content Sections */}
                          {topic.content_sections && topic.content_sections.length > 0 && (
                            <div className="mt-4 space-y-2">
                              {topic.content_sections.map((section, sectionIndex) => (
                                <div
                                  key={sectionIndex}
                                  className="rounded-lg bg-gray-50 p-4"
                                >
                                  <div className="font-medium text-gray-900 text-sm">
                                    {section.section} {section.title}
                                  </div>
                                  <div className="mt-2 flex flex-wrap gap-2">
                                    {section.concepts.map((concept, i) => (
                                      <span
                                        key={i}
                                        className="inline-flex items-center rounded-full bg-white px-2.5 py-0.5 text-xs text-gray-700 border border-gray-200"
                                      >
                                        {concept}
                                      </span>
                                    ))}
                                  </div>
                                  <div className="mt-2 text-xs text-gray-500">
                                    {section.worked_examples} worked examples •{' '}
                                    {section.practice_problems} practice problems
                                    {section.difficulty && ` • ${section.difficulty}`}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Key Concepts Preview */}
                          {topic.key_concepts && topic.key_concepts.length > 0 && (
                            <div className="mt-4">
                              <div className="text-sm font-medium text-gray-700 mb-2">
                                Key Concepts:
                              </div>
                              <div className="space-y-2">
                                {topic.key_concepts.slice(0, 3).map((concept, i) => (
                                  <div key={i} className="text-sm text-gray-600">
                                    <span className="font-medium">{concept.concept}:</span>{' '}
                                    {concept.definition}
                                  </div>
                                ))}
                                {topic.key_concepts.length > 3 && (
                                  <div className="text-sm text-gray-500 italic">
                                    +{topic.key_concepts.length - 3} more concepts
                                  </div>
                                )}
                              </div>
                            </div>
                          )}

                          {/* Exam Tips */}
                          {topic.exam_tips && topic.exam_tips.length > 0 && (
                            <div className="mt-4 rounded-lg bg-accent-50 p-4 border border-accent-200">
                              <div className="flex items-center space-x-2 text-sm font-medium text-accent-900 mb-2">
                                <TrendingUp className="h-4 w-4" />
                                <span>Exam Tips</span>
                              </div>
                              <ul className="space-y-1">
                                {topic.exam_tips.map((tip, i) => (
                                  <li key={i} className="text-sm text-accent-800">
                                    • {tip}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom CTA */}
          <div className="mt-8 rounded-2xl bg-gradient-to-r from-primary-600 to-secondary-600 p-8 text-white text-center">
            <h2 className="text-2xl font-bold">
              Ready to start your study journey?
            </h2>
            <p className="mt-2 text-white/80">
              Get instant access to the complete study guide and personalized timetable.
            </p>
            <div className="mt-6 flex items-center justify-center gap-4">
              <div className="text-3xl font-bold">
                {formatPrice(product.current_price)}
              </div>
              <Button
                size="lg"
                onClick={handleAddToCart}
                className="bg-white text-primary-600 hover:bg-gray-100"
              >
                <ShoppingCart className="mr-2 h-5 w-5" />
                Add to Cart
              </Button>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
