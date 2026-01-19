'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import {
  BookOpen,
  ChevronRight,
  ChevronDown,
  Calendar,
  Clock,
  Lightbulb,
  AlertCircle,
  TrendingUp,
  CheckCircle2,
  FileText,
  ArrowLeft,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';
import { libraryApi } from '@/lib/api';
import { getSubjectColor, getTermLabel } from '@/lib/utils';

interface Topic {
  topic_id: string;
  title: string;
  week: number;
  hours: number;
  overview?: {
    description: string;
    key_learning_points: string[];
  };
  key_concepts?: Array<{
    concept_name: string;
    definition: string;
    formula?: string | null;
    example?: string;
  }>;
  worked_examples?: Array<{
    example_number: number;
    difficulty: string;
    problem: string;
    solution: any;
    answer?: string;
  }>;
  common_mistakes?: Array<{
    mistake: string;
    why_wrong: string;
    how_to_avoid: string;
  }>;
  exam_tips?: string[];
  content_sections?: Array<{
    section: string;
    title: string;
    concepts: string[];
  }>;
  key_formulas?: string[];
}

interface Unit {
  unit_number: number;
  title: string;
  weeks_allocated: number;
  topics: Topic[];
}

export default function StudyGuideViewerPage() {
  const params = useParams();
  const productId = params.id as string;
  const [expandedUnit, setExpandedUnit] = useState<number | null>(1);
  const [expandedTopic, setExpandedTopic] = useState<string | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');

  const { data: libraryData, isLoading } = useQuery({
    queryKey: ['library-item', productId],
    queryFn: () => libraryApi.getItem(productId),
  });

  if (isLoading) {
    return (
      <>
        <Header />
        <main className="min-h-screen bg-gray-50 py-8">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="animate-pulse space-y-8">
              <div className="h-8 w-64 bg-gray-200 rounded" />
              <div className="h-96 bg-gray-200 rounded-2xl" />
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  if (!libraryData?.data) {
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
              This study guide is not in your library.
            </p>
            <Link href="/library" className="mt-6 inline-block">
              <Button>Back to Library</Button>
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  // Extract data from API response
  const item = libraryData.data;
  const content = item.content_json || {};
  const units = (content.units || []) as Unit[];
  const subject_code = item.subject_code;
  const currentTopic = units.flatMap((u) => u.topics).find((t) => t.topic_id === expandedTopic);

  // Render main content
  return (
    <>
      <Header />
      <main className="min-h-screen bg-gray-50">
        {/* Top Navigation */}
        <div className="sticky top-16 z-40 border-b border-gray-200 bg-white">
          <div className="mx-auto max-w-7xl px-4 py-3 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between">
              <Link
                href="/library"
                className="flex items-center text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Library
              </Link>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  {item.progress_percent}% complete
                </span>
                <Link href={`/library/${productId}/timetable`}>
                  <Button variant="outline" size="sm">
                    <Calendar className="mr-1 h-4 w-4" />
                    Study Timetable
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            {/* Sidebar - Table of Contents */}
            <div className="lg:col-span-4 xl:col-span-3">
              <div className="sticky top-32 rounded-2xl bg-white p-6 shadow-sm">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Contents
                </h2>

                <div className="space-y-2">
                  {units.map((unit) => (
                    <div key={unit.unit_number}>
                      <button
                        onClick={() =>
                          setExpandedUnit(
                            expandedUnit === unit.unit_number ? null : unit.unit_number
                          )
                        }
                        className="flex w-full items-center justify-between rounded-lg p-3 text-left transition-colors hover:bg-gray-50"
                      >
                        <div className="flex items-center space-x-3">
                          {expandedUnit === unit.unit_number ? (
                            <ChevronDown className="h-4 w-4 flex-shrink-0" />
                          ) : (
                            <ChevronRight className="h-4 w-4 flex-shrink-0" />
                          )}
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              Unit {unit.unit_number}
                            </div>
                            <div className="text-xs text-gray-500 line-clamp-1">
                              {unit.title}
                            </div>
                          </div>
                        </div>
                      </button>

                      <AnimatePresence>
                        {expandedUnit === unit.unit_number && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="ml-7 mt-1 space-y-1"
                          >
                            {unit.topics.map((topic) => (
                              <button
                                key={topic.topic_id}
                                onClick={() => {
                                  setExpandedTopic(topic.topic_id);
                                  setActiveSection('overview');
                                }}
                                className={`block w-full rounded-md px-3 py-2 text-left text-sm transition-colors ${
                                  expandedTopic === topic.topic_id
                                    ? 'bg-primary-50 text-primary-700 font-medium'
                                    : 'text-gray-600 hover:bg-gray-50'
                                }`}
                              >
                                {topic.title}
                              </button>
                            ))}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Main Content */}
            <div className="mt-8 lg:col-span-8 lg:mt-0 xl:col-span-9">
              {!currentTopic ? (
                <div className="rounded-2xl bg-white p-12 text-center shadow-sm">
                  <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-4 text-lg font-semibold text-gray-900">
                    Select a topic to begin
                  </h3>
                  <p className="mt-2 text-gray-500">
                    Choose a topic from the table of contents on the left
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Topic Header */}
                  <div className="rounded-2xl bg-white p-8 shadow-sm">
                    <div className="flex items-start justify-between">
                      <div>
                        <h1 className="text-3xl font-bold text-gray-900">
                          {currentTopic.title}
                        </h1>
                        <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                          <span className="flex items-center">
                            <Calendar className="mr-1 h-4 w-4" />
                            Week {currentTopic.week}
                          </span>
                          <span className="flex items-center">
                            <Clock className="mr-1 h-4 w-4" />
                            {currentTopic.hours}h
                          </span>
                        </div>
                      </div>
                      <div
                        className="rounded-full px-4 py-2 text-sm font-medium text-white"
                        style={{ backgroundColor: getSubjectColor(subject_code) }}
                      >
                        {item.subject_name}
                      </div>
                    </div>

                    {/* Section Tabs */}
                    <div className="mt-6 border-b border-gray-200">
                      <div className="flex space-x-6">
                        {[
                          { id: 'overview', label: 'Overview', icon: FileText },
                          { id: 'concepts', label: 'Key Concepts', icon: Lightbulb },
                          {id: 'examples', label: 'Examples', icon: CheckCircle2 },
                          { id: 'mistakes', label: 'Common Mistakes', icon: AlertCircle },
                          { id: 'tips', label: 'Exam Tips', icon: TrendingUp },
                        ].map((section) => {
                          const Icon = section.icon;
                          return (
                            <button
                              key={section.id}
                              onClick={() => setActiveSection(section.id)}
                              className={`flex items-center space-x-2 border-b-2 px-1 py-3 text-sm font-medium transition-colors ${
                                activeSection === section.id
                                  ? 'border-primary-500 text-primary-600'
                                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                              }`}
                            >
                              <Icon className="h-4 w-4" />
                              <span>{section.label}</span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  </div>

                  {/* Section Content */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeSection}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.2 }}
                      className="rounded-2xl bg-white p-8 shadow-sm"
                    >
                      {/* Overview */}
                      {activeSection === 'overview' && currentTopic.overview && (
                        <div>
                          <h2 className="text-xl font-semibold text-gray-900 mb-4">
                            Topic Overview
                          </h2>
                          <p className="text-gray-700 leading-relaxed mb-6">
                            {currentTopic.overview.description}
                          </p>
                          {currentTopic.overview.key_learning_points && (
                            <>
                              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                                Key Learning Points
                              </h3>
                              <ul className="space-y-2">
                                {currentTopic.overview.key_learning_points.map((point, i) => (
                                  <li key={i} className="flex items-start">
                                    <CheckCircle2 className="mr-2 h-5 w-5 flex-shrink-0 text-green-500 mt-0.5" />
                                    <span className="text-gray-700">{point}</span>
                                  </li>
                                ))}
                              </ul>
                            </>
                          )}
                        </div>
                      )}

                      {/* Key Concepts */}
                      {activeSection === 'concepts' && currentTopic.key_concepts && (
                        <div className="space-y-6">
                          <h2 className="text-xl font-semibold text-gray-900">
                            Key Concepts
                          </h2>
                          {currentTopic.key_concepts.map((concept, i) => (
                            <div
                              key={i}
                              className="rounded-lg border border-gray-200 p-6"
                            >
                              <h3 className="text-lg font-semibold text-gray-900">
                                {concept.concept_name}
                              </h3>
                              <p className="mt-2 text-gray-700">{concept.definition}</p>
                              {concept.formula && (
                                <div className="mt-3 rounded-md bg-gray-50 p-3 font-mono text-sm">
                                  {concept.formula}
                                </div>
                              )}
                              {concept.example && (
                                <div className="mt-3 text-sm text-gray-600">
                                  <span className="font-medium">Example: </span>
                                  {concept.example}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Worked Examples */}
                      {activeSection === 'examples' && currentTopic.worked_examples && (
                        <div className="space-y-6">
                          <h2 className="text-xl font-semibold text-gray-900">
                            Worked Examples
                          </h2>
                          {currentTopic.worked_examples.map((example) => (
                            <div
                              key={example.example_number}
                              className="rounded-lg border border-gray-200 p-6"
                            >
                              <div className="flex items-start justify-between">
                                <h3 className="text-lg font-semibold text-gray-900">
                                  Example {example.example_number}
                                </h3>
                                <span
                                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                                    example.difficulty === 'easy'
                                      ? 'bg-green-100 text-green-700'
                                      : example.difficulty === 'medium'
                                      ? 'bg-yellow-100 text-yellow-700'
                                      : 'bg-red-100 text-red-700'
                                  }`}
                                >
                                  {example.difficulty}
                                </h3>
                              </div>
                              <div className="mt-3 rounded-md bg-blue-50 p-4">
                                <p className="text-gray-900 font-medium">Problem:</p>
                                <p className="mt-1 text-gray-700">{example.problem}</p>
                              </div>
                              {example.solution && (
                                <div className="mt-4 space-y-2">
                                  <p className="font-medium text-gray-900">Solution:</p>
                                  {Array.isArray(example.solution) ? (
                                    example.solution.map((step: any, i: number) => (
                                      <div key={i} className="ml-4 text-gray-700">
                                        <span className="font-medium">Step {step.step}:</span>{' '}
                                        {step.explanation}
                                        {step.working && (
                                          <div className="mt-1 rounded bg-gray-50 p-2 font-mono text-sm">
                                            {step.working}
                                          </div>
                                        )}
                                      </div>
                                    ))
                                  ) : (
                                    <div className="ml-4 text-gray-700">
                                      {example.solution}
                                    </div>
                                  )}
                                </div>
                              )}
                              {example.answer && (
                                <div className="mt-4 rounded-md bg-green-50 p-3">
                                  <span className="font-medium text-green-900">Answer: </span>
                                  <span className="text-green-800">{example.answer}</span>
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Common Mistakes */}
                      {activeSection === 'mistakes' && currentTopic.common_mistakes && (
                        <div className="space-y-4">
                          <h2 className="text-xl font-semibold text-gray-900">
                            Common Mistakes to Avoid
                          </h2>
                          {currentTopic.common_mistakes.map((mistake, i) => (
                            <div
                              key={i}
                              className="rounded-lg border-l-4 border-red-500 bg-red-50 p-6"
                            >
                              <h3 className="font-semibold text-red-900">
                                {mistake.mistake}
                              </h3>
                              <p className="mt-2 text-sm text-red-800">
                                <span className="font-medium">Why this is wrong: </span>
                                {mistake.why_wrong}
                              </p>
                              <p className="mt-2 text-sm text-red-800">
                                <span className="font-medium">How to avoid: </span>
                                {mistake.how_to_avoid}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Exam Tips */}
                      {activeSection === 'tips' && currentTopic.exam_tips && (
                        <div className="space-y-4">
                          <h2 className="text-xl font-semibold text-gray-900">
                            Exam Tips & Strategies
                          </h2>
                          <div className="grid gap-4 md:grid-cols-2">
                            {currentTopic.exam_tips.map((tip, i) => (
                              <div
                                key={i}
                                className="rounded-lg border-l-4 border-green-500 bg-green-50 p-4"
                              >
                                <div className="flex items-start">
                                  <TrendingUp className="mr-3 h-5 w-5 flex-shrink-0 text-green-600 mt-0.5" />
                                  <p className="text-sm text-green-900">{tip}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Key Formulas */}
                      {currentTopic.key_formulas && currentTopic.key_formulas.length > 0 && (
                        <div className="mt-8 rounded-lg bg-purple-50 p-6">
                          <h3 className="text-lg font-semibold text-purple-900 mb-4">
                            Key Formulas
                          </h3>
                          <div className="space-y-2">
                            {currentTopic.key_formulas.map((formula, i) => (
                              <div
                                key={i}
                                className="rounded bg-white p-3 font-mono text-sm text-gray-900"
                              >
                                {formula}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
