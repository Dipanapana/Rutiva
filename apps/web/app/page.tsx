'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  BookOpen,
  Calendar,
  CheckCircle,
  Clock,
  Download,
  GraduationCap,
  Lightbulb,
  Target,
  TrendingUp,
  Users,
  Zap,
  ArrowRight,
  Star,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 },
};

const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export default function LandingPage() {
  return (
    <>
      <Header />
      <main>
        {/* Hero Section */}
        <section className="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white py-20 lg:py-32">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center rounded-full bg-primary-100 px-4 py-1.5 text-sm font-medium text-primary-700 mb-6">
                <Star className="mr-1.5 h-4 w-4" />
                Trusted by 5,000+ SA learners
              </span>

              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl lg:text-6xl">
                Finally, a study guide that
                <span className="block text-primary-600">actually gets your child ready for exams.</span>
              </h1>

              <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600 sm:text-xl">
                CAPS-aligned term guides with week-by-week plans. No guesswork.
                Just results.
              </p>

              <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/shop">
                  <Button size="lg" className="w-full sm:w-auto">
                    Browse Study Guides
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="#how-it-works">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    See How It Works
                  </Button>
                </Link>
              </div>

              {/* Trust Badges */}
              <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>CAPS-aligned</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Download className="h-5 w-5 text-primary-500" />
                  <span>Instant download</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="h-5 w-5 text-accent-500" />
                  <span>Personalized timetables</span>
                </div>
              </div>
            </motion.div>
          </div>

          {/* Background decoration */}
          <div className="absolute inset-0 -z-10 overflow-hidden">
            <div className="absolute -top-40 -right-40 h-80 w-80 rounded-full bg-primary-200 opacity-20 blur-3xl" />
            <div className="absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-secondary-200 opacity-20 blur-3xl" />
          </div>
        </section>

        {/* Problem Section */}
        <section className="py-20 bg-gray-50">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center mb-12"
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Sound familiar?
              </h2>
            </motion.div>

            <motion.div
              className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {[
                {
                  problem: 'You bought the textbook.',
                  result: "They still don't know what to study.",
                },
                {
                  problem: 'You printed past papers.',
                  result: "They don't know where to start.",
                },
                {
                  problem: 'You hired a tutor.',
                  result: "R400/hour later, they're still lost.",
                },
                {
                  problem: 'You searched YouTube.',
                  result: '3 hours of "studying" = nothing learned.',
                },
              ].map((item, index) => (
                <motion.div
                  key={index}
                  className="rounded-2xl bg-white p-6 shadow-sm border border-gray-100"
                  variants={fadeInUp}
                >
                  <p className="font-semibold text-gray-900">{item.problem}</p>
                  <p className="mt-2 text-gray-500">{item.result}</p>
                </motion.div>
              ))}
            </motion.div>

            <motion.p
              className="mt-12 text-center text-xl font-medium text-primary-600"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
            >
              What if your child had a clear roadmap?
            </motion.p>
          </div>
        </section>

        {/* Solution Section */}
        <section className="py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center mb-16"
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Introducing RUTA Study Guides
              </h2>
              <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
                Complete term study packs with everything your child needs to succeed.
              </p>
            </motion.div>

            <div className="grid gap-8 lg:grid-cols-2">
              {/* What's Included */}
              <motion.div
                className="rounded-2xl bg-gradient-to-br from-primary-50 to-secondary-50 p-8"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <h3 className="text-xl font-bold text-gray-900 mb-6">
                  Each guide includes:
                </h3>
                <ul className="space-y-4">
                  {[
                    { icon: BookOpen, text: 'Complete term syllabus breakdown' },
                    { icon: Calendar, text: 'Week-by-week study plan' },
                    { icon: Lightbulb, text: 'Worked examples for every topic' },
                    { icon: Target, text: 'Practice problems with answers' },
                    { icon: GraduationCap, text: 'Exam tips from top teachers' },
                    { icon: Download, text: 'Formula sheets and summaries' },
                  ].map((item, index) => (
                    <li key={index} className="flex items-start space-x-3">
                      <item.icon className="h-6 w-6 text-primary-600 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{item.text}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>

              {/* Custom Timetable */}
              <motion.div
                className="rounded-2xl bg-gradient-to-br from-accent-50 to-primary-50 p-8"
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
              >
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  PLUS: Custom Study Timetable
                </h3>
                <p className="text-gray-600 mb-6">
                  Our AI generates a personalized schedule based on your exam date.
                </p>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 rounded-lg bg-white p-4 shadow-sm">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-100">
                      <span className="font-bold text-accent-600">1</span>
                    </div>
                    <span className="text-gray-700">Tell us when the exam is</span>
                  </div>
                  <div className="flex items-center space-x-3 rounded-lg bg-white p-4 shadow-sm">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-100">
                      <span className="font-bold text-accent-600">2</span>
                    </div>
                    <span className="text-gray-700">We build a personalized schedule</span>
                  </div>
                  <div className="flex items-center space-x-3 rounded-lg bg-white p-4 shadow-sm">
                    <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent-100">
                      <span className="font-bold text-accent-600">3</span>
                    </div>
                    <span className="text-gray-700">Your child knows exactly what to study, every day</span>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-20 bg-gray-50">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center mb-16"
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                How It Works
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                From purchase to exam success in 5 simple steps
              </p>
            </motion.div>

            <motion.div
              className="grid gap-8 md:grid-cols-5"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {[
                {
                  step: 1,
                  title: 'Choose',
                  description: "Select your child's grade and subjects",
                  icon: Target,
                },
                {
                  step: 2,
                  title: 'Purchase',
                  description: 'Buy the term guide (instant download)',
                  icon: Download,
                },
                {
                  step: 3,
                  title: 'Schedule',
                  description: 'Generate a personalized timetable',
                  icon: Calendar,
                },
                {
                  step: 4,
                  title: 'Study',
                  description: 'Follow the daily plan',
                  icon: BookOpen,
                },
                {
                  step: 5,
                  title: 'Succeed',
                  description: 'Walk into the exam confident',
                  icon: GraduationCap,
                },
              ].map((item, index) => (
                <motion.div
                  key={index}
                  className="text-center"
                  variants={fadeInUp}
                >
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary-100">
                    <item.icon className="h-8 w-8 text-primary-600" />
                  </div>
                  <div className="mb-2 text-sm font-semibold text-primary-600">
                    Step {item.step}
                  </div>
                  <h3 className="font-bold text-gray-900">{item.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center mb-16"
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                Simple, Fair Pricing
              </h2>
              <p className="mt-4 text-lg text-gray-600">
                One-time purchase. No subscriptions. Yours forever.
              </p>
            </motion.div>

            <motion.div
              className="grid gap-8 md:grid-cols-3"
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
            >
              {/* Individual Guide */}
              <motion.div
                className="rounded-2xl border border-gray-200 bg-white p-8"
                variants={fadeInUp}
              >
                <h3 className="text-lg font-semibold text-gray-900">Individual Guide</h3>
                <p className="mt-2 text-sm text-gray-500">One subject, one term</p>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-gray-900">R149</span>
                </div>
                <ul className="mt-6 space-y-3">
                  {[
                    'Complete term syllabus',
                    'Week-by-week breakdown',
                    'Practice problems & answers',
                    'Custom study timetable',
                    'PDF download',
                  ].map((feature, i) => (
                    <li key={i} className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/shop" className="block mt-8">
                  <Button variant="outline" className="w-full">
                    Browse Guides
                  </Button>
                </Link>
              </motion.div>

              {/* Term Bundle - Featured */}
              <motion.div
                className="rounded-2xl border-2 border-primary-500 bg-white p-8 relative"
                variants={fadeInUp}
              >
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 rounded-full bg-primary-500 px-4 py-1 text-sm font-medium text-white">
                  Most Popular
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Term Bundle</h3>
                <p className="mt-2 text-sm text-gray-500">All subjects, one term</p>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-gray-900">R449</span>
                  <span className="ml-2 text-sm text-gray-500 line-through">R596</span>
                </div>
                <p className="text-sm text-green-600 font-medium">Save R147</p>
                <ul className="mt-6 space-y-3">
                  {[
                    'All 4 core subjects',
                    'Complete term coverage',
                    'Integrated study schedule',
                    'Priority support',
                    'Bonus exam tips',
                  ].map((feature, i) => (
                    <li key={i} className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/shop/bundles" className="block mt-8">
                  <Button className="w-full">Get Bundle</Button>
                </Link>
              </motion.div>

              {/* Full Year */}
              <motion.div
                className="rounded-2xl border border-gray-200 bg-white p-8"
                variants={fadeInUp}
              >
                <h3 className="text-lg font-semibold text-gray-900">Full Year</h3>
                <p className="mt-2 text-sm text-gray-500">One subject, all 4 terms</p>
                <div className="mt-6">
                  <span className="text-4xl font-bold text-gray-900">R449</span>
                  <span className="ml-2 text-sm text-gray-500 line-through">R596</span>
                </div>
                <p className="text-sm text-green-600 font-medium">Save 25%</p>
                <ul className="mt-6 space-y-3">
                  {[
                    'Terms 1-4 complete',
                    'Year-long study plan',
                    'Quarterly assessments',
                    'Exam preparation',
                    'All resources included',
                  ].map((feature, i) => (
                    <li key={i} className="flex items-center space-x-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link href="/shop" className="block mt-8">
                  <Button variant="outline" className="w-full">
                    View Options
                  </Button>
                </Link>
              </motion.div>
            </motion.div>

            {/* School Pricing CTA */}
            <motion.div
              className="mt-12 text-center"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
            >
              <p className="text-gray-600">
                School or bulk purchase?{' '}
                <Link href="/schools" className="text-primary-600 font-medium hover:underline">
                  Contact us for special pricing
                </Link>
              </p>
            </motion.div>
          </div>
        </section>

        {/* Optional Add-on: AI Tutor */}
        <section className="py-20 bg-gradient-to-br from-secondary-50 to-primary-50">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="text-center"
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              variants={fadeInUp}
            >
              <span className="inline-flex items-center rounded-full bg-secondary-100 px-4 py-1.5 text-sm font-medium text-secondary-700 mb-4">
                <Zap className="mr-1.5 h-4 w-4" />
                Optional Add-on
              </span>
              <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                RutaBot AI Tutor
              </h2>
              <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
                Stuck on a concept? Ask RutaBot. 24/7 AI tutor that explains, not just answers.
              </p>

              <div className="mt-8 flex flex-wrap justify-center gap-4">
                {[
                  { plan: 'Starter', questions: '15/month', price: 'R49' },
                  { plan: 'Standard', questions: '40/month', price: 'R89' },
                  { plan: 'Unlimited', questions: 'Unlimited', price: 'R149' },
                ].map((tier, index) => (
                  <div
                    key={index}
                    className="rounded-xl bg-white p-6 shadow-sm text-center min-w-[160px]"
                  >
                    <div className="font-semibold text-gray-900">{tier.plan}</div>
                    <div className="mt-1 text-2xl font-bold text-primary-600">{tier.price}</div>
                    <div className="mt-1 text-sm text-gray-500">{tier.questions}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-20">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <motion.div
              className="rounded-3xl bg-gradient-to-r from-primary-600 to-secondary-600 p-12 text-center text-white"
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
            >
              <h2 className="text-3xl font-bold sm:text-4xl">
                Give your child the roadmap to results.
              </h2>
              <p className="mt-4 text-lg text-white/80 max-w-xl mx-auto">
                Join thousands of South African learners who are studying smarter, not harder.
              </p>
              <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link href="/shop">
                  <Button
                    size="lg"
                    className="bg-white text-primary-600 hover:bg-gray-100 w-full sm:w-auto"
                  >
                    Browse Guides by Grade
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/schools">
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white text-white hover:bg-white/10 w-full sm:w-auto"
                  >
                    Schools: Request Quote
                  </Button>
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
