# Rutiva - System Architecture

This document provides detailed technical architecture, database schema, API contracts, and data flows for the Rutiva platform.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [API Contracts](#api-contracts)
4. [Data Flows](#data-flows)
5. [Security Model](#security-model)
6. [Infrastructure](#infrastructure)
7. [Integration Points](#integration-points)

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Client Layer                          │
│  ┌─────────────────────┐    ┌──────────────────────┐    │
│  │   Web Application   │    │  Mobile Application  │    │
│  │     (Next.js)       │    │  (React Native)      │    │
│  └──────────┬──────────┘    └──────────┬───────────┘    │
│             │                           │                 │
└─────────────┼───────────────────────────┼────────────────┘
              │                           │
              │    HTTPS/REST API         │
              └───────────┬───────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│                  Application Layer                        │
│             ┌────────────────────────┐                   │
│             │   FastAPI Backend      │                   │
│             │   (Uvicorn ASGI)       │                   │
│             └──────────┬─────────────┘                   │
└────────────────────────┼───────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐  ┌───▼────┐  ┌────────▼─────────┐
│   PostgreSQL   │  │ Redis  │  │  External APIs   │
│   Database     │  │ Cache  │  │ (OpenAI, AWS,    │
│                │  │        │  │  PayFast, etc.)  │
└────────────────┘  └────────┘  └──────────────────┘
```

### Component Architecture

#### Frontend (Web)

```
apps/web/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Auth routes (login, register)
│   ├── (shop)/              # Shop routes
│   ├── (study)/             # Study routes (library, timetables)
│   ├── (library)/           # User library
│   ├── cart/                # Shopping cart
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Landing page
├── components/              # React components
│   ├── layout/             # Header, Footer, Navigation
│   └── ui/                 # Button, Input, Card, etc.
├── lib/                    # Shared utilities
│   ├── api.ts              # Axios client with interceptors
│   ├── store.ts            # Zustand state management
│   └── utils.ts            # Helper functions
├── hooks/                  # Custom React hooks
├── types/                  # TypeScript type definitions
└── public/                 # Static assets
```

**Key Technologies:**
- Next.js 14 (React Server Components + Client Components)
- TypeScript for type safety
- Tailwind CSS for styling
- React Query for server state caching
- Zustand for client state
- Axios for API calls

#### Backend (API)

```
backend/
├── app/
│   ├── main.py                  # FastAPI application entry
│   ├── core/
│   │   ├── config.py            # Settings (Pydantic BaseSettings)
│   │   ├── database.py          # SQLAlchemy async engine
│   │   └── security.py          # JWT, password hashing, OTP
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py              # User, UserRole, OTPCode, ParentChild
│   │   ├── product.py           # Subject, Product, Bundle
│   │   ├── order.py             # Order, OrderItem, UserLibrary, PromoCode
│   │   ├── timetable.py         # Timetable, TimetableProgress
│   │   ├── tutor.py             # TutorSubscription, ChatSession, ChatMessage
│   │   ├── school.py            # School, SchoolAdmin, SchoolOrder, SchoolLicense
│   │   └── questions.py         # (Phase 4) QuestionPaper, Question, etc.
│   ├── api/
│   │   ├── deps.py              # Dependency injection (get_db, get_current_user)
│   │   └── v1/                  # API v1 routes
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── products.py      # Product catalog
│   │       ├── cart.py          # Shopping cart
│   │       ├── library.py       # User library
│   │       ├── timetable.py     # Study timetables
│   │       ├── chat.py          # AI tutor
│   │       ├── users.py         # User profile
│   │       └── questions.py     # (Phase 4) Past questions
│   ├── schemas/                 # Pydantic schemas (request/response)
│   └── services/                # Business logic
│       ├── ai_service.py        # RutivaBot AI integration
│       ├── timetable_generator.py  # Study schedule generation
│       └── delivery_service.py  # S3 content delivery
└── alembic/                     # Database migrations
```

**Key Technologies:**
- FastAPI (async Python web framework)
- SQLAlchemy 2.0 (async ORM)
- Pydantic v2 (data validation)
- asyncpg (PostgreSQL async driver)
- Alembic (schema migrations)
- JWT for authentication
- Bcrypt for password hashing

#### Mobile (React Native)

```
apps/mobile/
├── app/                         # Expo Router
│   ├── (auth)/                  # Auth screens
│   ├── (tabs)/                  # Main tab navigation
│   │   ├── shop/                # Product catalog
│   │   ├── library/             # User library
│   │   ├── study/               # Timetables
│   │   ├── tutor/               # AI chat
│   │   └── profile/             # User profile
│   ├── _layout.tsx              # Root layout
│   └── index.tsx                # Entry point
├── components/                  # Reusable components
├── lib/                         # Shared lib (API, store, utils)
├── assets/                      # Images, fonts
├── app.json                     # Expo configuration
└── package.json
```

**Key Technologies:**
- React Native with Expo
- Expo Router (file-based navigation)
- Zustand (state management)
- React Native Paper (UI components)
- NativeWind (Tailwind for React Native)
- react-native-pdf (PDF viewing)

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│    users    │────────▶│  user_roles  │
│             │         │   (enum)     │
└──────┬──────┘         └──────────────┘
       │
       │ 1:N
       │
       ▼
┌──────────────────┐
│  parent_children │
│  (link table)    │
└──────────────────┘

┌─────────────┐         ┌──────────────┐
│  subjects   │────────▶│   products   │
│             │  1:N    │              │
└─────────────┘         └──────┬───────┘
                               │
                               │ M:N
                               │
                        ┌──────▼────────┐
                        │  bundle_prods │
                        │  (link table) │
                        └──────┬────────┘
                               │
                        ┌──────▼───────┐
                        │   bundles    │
                        └──────────────┘

┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    users    │────────▶│    orders    │────────▶│ order_items │
│             │  1:N    │              │  1:N    │             │
└─────────────┘         └──────┬───────┘         └─────────────┘
                               │
                               │ 1:N
                               │
                        ┌──────▼───────┐
                        │ promo_codes  │
                        └──────────────┘

┌─────────────┐         ┌──────────────┐
│    users    │────────▶│ user_library │
│             │  1:N    │              │
└─────────────┘         └──────────────┘
                               │
                               │ N:1
                               │
                        ┌──────▼───────┐
                        │   products   │
                        └──────────────┘

┌─────────────┐         ┌──────────────┐         ┌───────────────────┐
│    users    │────────▶│  timetables  │────────▶│timetable_progress │
│             │  1:N    │              │  1:N    │                   │
└─────────────┘         └──────────────┘         └───────────────────┘

┌─────────────┐         ┌──────────────────┐
│    users    │────────▶│tutor_subscriptions│
│             │  1:1    │                  │
└─────────────┘         └──────────────────┘

┌─────────────┐         ┌──────────────┐         ┌───────────────┐
│    users    │────────▶│chat_sessions │────────▶│chat_messages  │
│             │  1:N    │              │  1:N    │               │
└─────────────┘         └──────────────┘         └───────────────┘

┌─────────────┐         ┌──────────────┐
│   schools   │────────▶│school_admins │
│             │  1:N    │              │
└─────────────┘         └──────┬───────┘
       │                       │
       │ 1:N                   │ N:1
       │                       │
┌──────▼───────┐         ┌─────▼────────┐
│school_orders │         │    users     │
└──────┬───────┘         └──────────────┘
       │
       │ 1:N
       │
┌──────▼────────┐
│school_licenses│
└───────────────┘
```

### Core Tables

#### Users & Authentication

**users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255),
  phone VARCHAR(20),

  -- User type and academic info
  role VARCHAR(50) NOT NULL,  -- student, parent, school_admin, super_admin
  grade INTEGER CHECK (grade >= 6 AND grade <= 12),  -- NULL for parents/admins
  province VARCHAR(50),  -- South African provinces

  -- Account status
  is_active BOOLEAN DEFAULT TRUE,
  is_verified BOOLEAN DEFAULT FALSE,
  email_verified_at TIMESTAMP,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,

  INDEX idx_users_email (email),
  INDEX idx_users_role (role),
  INDEX idx_users_grade (grade)
);
```

**otp_codes**
```sql
CREATE TABLE otp_codes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  code VARCHAR(6) NOT NULL,
  purpose VARCHAR(50) NOT NULL,  -- email_verification, password_reset, login

  expires_at TIMESTAMP NOT NULL,
  used_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_otp_email (email),
  INDEX idx_otp_code (code),
  CHECK (expires_at > created_at)
);
```

**parent_children**
```sql
CREATE TABLE parent_children (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  parent_id UUID REFERENCES users(id) ON DELETE CASCADE,
  child_id UUID REFERENCES users(id) ON DELETE CASCADE,

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE (parent_id, child_id),
  INDEX idx_parent_children_parent (parent_id),
  INDEX idx_parent_children_child (child_id)
);
```

#### Products & Catalog

**subjects**
```sql
CREATE TABLE subjects (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(100) NOT NULL UNIQUE,  -- Mathematics, Physical Sciences, etc.
  code VARCHAR(20) UNIQUE,  -- MATH, PHYS, etc.
  description TEXT,
  icon_url VARCHAR(500),

  is_active BOOLEAN DEFAULT TRUE,
  display_order INTEGER DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_subjects_code (code)
);
```

**products**
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sku VARCHAR(50) UNIQUE NOT NULL,  -- MATH-GR10-T1-2025

  -- Product info
  subject_id UUID REFERENCES subjects(id),
  grade INTEGER NOT NULL CHECK (grade >= 6 AND grade <= 12),
  term INTEGER CHECK (term >= 1 AND term <= 4),
  year INTEGER NOT NULL,

  title VARCHAR(255) NOT NULL,
  description TEXT,

  -- Content
  content_json JSONB,  -- Units, topics, estimated hours
  pdf_url VARCHAR(500),
  thumbnail_url VARCHAR(500),
  answer_key_url VARCHAR(500),
  formula_sheet_url VARCHAR(500),

  -- Pricing
  price_cents INTEGER NOT NULL,  -- Store in cents to avoid float issues
  sale_price_cents INTEGER,
  currency VARCHAR(3) DEFAULT 'ZAR',

  -- Metadata
  is_active BOOLEAN DEFAULT TRUE,
  is_featured BOOLEAN DEFAULT FALSE,
  total_pages INTEGER,
  estimated_hours INTEGER,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_products_sku (sku),
  INDEX idx_products_subject (subject_id),
  INDEX idx_products_grade (grade),
  INDEX idx_products_term (term),
  INDEX idx_products_year (year),
  INDEX idx_products_featured (is_featured)
);
```

**bundles**
```sql
CREATE TABLE bundles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  sku VARCHAR(50) UNIQUE NOT NULL,  -- BUNDLE-GR10-ALLYEAR-2025

  title VARCHAR(255) NOT NULL,
  description TEXT,

  grade INTEGER CHECK (grade >= 6 AND grade <= 12),
  bundle_type VARCHAR(50),  -- full_year, all_subjects, subject_year

  price_cents INTEGER NOT NULL,
  sale_price_cents INTEGER,
  currency VARCHAR(3) DEFAULT 'ZAR',
  discount_percentage INTEGER,

  thumbnail_url VARCHAR(500),
  is_active BOOLEAN DEFAULT TRUE,
  is_featured BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_bundles_sku (sku),
  INDEX idx_bundles_grade (grade)
);
```

**bundle_products (join table)**
```sql
CREATE TABLE bundle_products (
  bundle_id UUID REFERENCES bundles(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id) ON DELETE CASCADE,

  PRIMARY KEY (bundle_id, product_id),
  INDEX idx_bundle_products_bundle (bundle_id),
  INDEX idx_bundle_products_product (product_id)
);
```

#### Orders & Commerce

**orders**
```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_number VARCHAR(50) UNIQUE NOT NULL,  -- RV-20250119-0001
  user_id UUID REFERENCES users(id),

  -- Order details
  status VARCHAR(50) NOT NULL,  -- pending, paid, failed, refunded, cancelled
  payment_provider VARCHAR(50),  -- payfast, yoco, eft, free
  payment_id VARCHAR(255),  -- Provider transaction ID

  -- Pricing
  subtotal_cents INTEGER NOT NULL,
  discount_cents INTEGER DEFAULT 0,
  total_cents INTEGER NOT NULL,
  currency VARCHAR(3) DEFAULT 'ZAR',

  -- Promo code
  promo_code_id UUID REFERENCES promo_codes(id),

  -- Payment metadata
  payment_data JSONB,  -- Store provider-specific data

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  paid_at TIMESTAMP,
  cancelled_at TIMESTAMP,

  INDEX idx_orders_user (user_id),
  INDEX idx_orders_number (order_number),
  INDEX idx_orders_status (status),
  INDEX idx_orders_created (created_at DESC)
);
```

**order_items**
```sql
CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,

  product_id UUID REFERENCES products(id),
  bundle_id UUID REFERENCES bundles(id),

  item_type VARCHAR(50) NOT NULL,  -- product, bundle
  title VARCHAR(255) NOT NULL,
  sku VARCHAR(50) NOT NULL,

  quantity INTEGER DEFAULT 1,
  unit_price_cents INTEGER NOT NULL,
  total_price_cents INTEGER NOT NULL,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_order_items_order (order_id),
  CHECK ((product_id IS NOT NULL AND bundle_id IS NULL) OR
         (product_id IS NULL AND bundle_id IS NOT NULL))
);
```

**promo_codes**
```sql
CREATE TABLE promo_codes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code VARCHAR(50) UNIQUE NOT NULL,

  discount_type VARCHAR(50) NOT NULL,  -- percentage, fixed_amount
  discount_value INTEGER NOT NULL,  -- Percentage (1-100) or cents amount

  max_uses INTEGER,
  current_uses INTEGER DEFAULT 0,

  valid_from TIMESTAMP,
  valid_until TIMESTAMP,

  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_promo_code (code),
  CHECK (discount_value > 0),
  CHECK (current_uses <= max_uses OR max_uses IS NULL)
);
```

**user_library**
```sql
CREATE TABLE user_library (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  order_id UUID REFERENCES orders(id),

  -- Access tracking
  download_count INTEGER DEFAULT 0,
  last_accessed TIMESTAMP,
  progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),

  -- Content status
  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE (user_id, product_id),
  INDEX idx_library_user (user_id),
  INDEX idx_library_product (product_id)
);
```

#### Timetables

**timetables**
```sql
CREATE TABLE timetables (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),

  title VARCHAR(255),

  -- Configuration
  exam_date DATE NOT NULL,
  study_days_per_week INTEGER NOT NULL CHECK (study_days_per_week >= 1 AND study_days_per_week <= 7),
  hours_per_session NUMERIC(3,1) NOT NULL CHECK (hours_per_session > 0),
  preferred_time VARCHAR(50),  -- morning, afternoon, evening, flexible
  pace VARCHAR(50),  -- relaxed, normal, intensive

  -- Generated schedule
  schedule_json JSONB NOT NULL,  -- Weekly breakdown with sessions

  -- Progress
  total_sessions INTEGER DEFAULT 0,
  completed_sessions INTEGER DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_timetables_user (user_id),
  INDEX idx_timetables_product (product_id),
  INDEX idx_timetables_exam_date (exam_date)
);
```

**timetable_progress**
```sql
CREATE TABLE timetable_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timetable_id UUID REFERENCES timetables(id) ON DELETE CASCADE,

  session_number INTEGER NOT NULL,
  topic VARCHAR(255),

  -- Progress tracking
  completed_at TIMESTAMP,
  time_spent_minutes INTEGER,
  difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 5),
  understanding_rating INTEGER CHECK (understanding_rating >= 1 AND understanding_rating <= 5),
  notes TEXT,

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE (timetable_id, session_number),
  INDEX idx_progress_timetable (timetable_id)
);
```

#### AI Tutor

**tutor_subscriptions**
```sql
CREATE TABLE tutor_subscriptions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) UNIQUE,

  plan VARCHAR(50) NOT NULL,  -- starter, standard, unlimited
  status VARCHAR(50) NOT NULL,  -- active, inactive, cancelled

  -- Limits
  questions_limit INTEGER,  -- NULL for unlimited
  questions_used INTEGER DEFAULT 0,

  -- Billing
  monthly_price_cents INTEGER NOT NULL,
  currency VARCHAR(3) DEFAULT 'ZAR',

  -- Renewal
  current_period_start DATE NOT NULL,
  current_period_end DATE NOT NULL,
  auto_renew BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_tutor_sub_user (user_id),
  INDEX idx_tutor_sub_status (status)
);
```

**chat_sessions**
```sql
CREATE TABLE chat_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  title VARCHAR(255),

  -- Context
  grade INTEGER,
  subject VARCHAR(100),
  topic VARCHAR(255),

  -- Metadata
  message_count INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_chat_sessions_user (user_id),
  INDEX idx_chat_sessions_created (created_at DESC)
);
```

**chat_messages**
```sql
CREATE TABLE chat_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,

  role VARCHAR(50) NOT NULL,  -- user, assistant, system
  content TEXT NOT NULL,

  -- Metadata
  tokens INTEGER,
  flagged BOOLEAN DEFAULT FALSE,
  flag_reason VARCHAR(255),

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_chat_messages_session (session_id),
  INDEX idx_chat_messages_created (created_at)
);
```

#### Schools

**schools**
```sql
CREATE TABLE schools (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  name VARCHAR(255) NOT NULL,
  emis_number VARCHAR(50) UNIQUE,  -- South African school ID
  province VARCHAR(50),
  district VARCHAR(100),

  contact_email VARCHAR(255),
  contact_phone VARCHAR(20),
  address TEXT,

  is_active BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_schools_emis (emis_number),
  INDEX idx_schools_province (province)
);
```

**school_admins**
```sql
CREATE TABLE school_admins (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  role VARCHAR(50) NOT NULL,  -- admin, teacher

  created_at TIMESTAMP DEFAULT NOW(),

  UNIQUE (school_id, user_id),
  INDEX idx_school_admins_school (school_id),
  INDEX idx_school_admins_user (user_id)
);
```

**school_orders**
```sql
CREATE TABLE school_orders (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  school_id UUID REFERENCES schools(id),
  order_number VARCHAR(50) UNIQUE NOT NULL,

  number_of_licenses INTEGER NOT NULL,
  price_per_license_cents INTEGER NOT NULL,
  total_cents INTEGER NOT NULL,
  currency VARCHAR(3) DEFAULT 'ZAR',

  status VARCHAR(50) NOT NULL,
  payment_provider VARCHAR(50),

  created_at TIMESTAMP DEFAULT NOW(),
  paid_at TIMESTAMP,

  INDEX idx_school_orders_school (school_id),
  INDEX idx_school_orders_number (order_number)
);
```

**school_licenses**
```sql
CREATE TABLE school_licenses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  school_order_id UUID REFERENCES school_orders(id),

  license_code VARCHAR(20) UNIQUE NOT NULL,
  product_id UUID REFERENCES products(id),

  claimed_by_user_id UUID REFERENCES users(id),
  claimed_at TIMESTAMP,

  is_active BOOLEAN DEFAULT TRUE,
  expires_at DATE,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_licenses_code (license_code),
  INDEX idx_licenses_school_order (school_order_id),
  INDEX idx_licenses_claimed_by (claimed_by_user_id)
);
```

### Phase 4: Questions Tables

**question_papers**
```sql
CREATE TABLE question_papers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  title VARCHAR(255) NOT NULL,  -- "2024 June Mathematics Paper 1"
  subject_id UUID REFERENCES subjects(id),
  grade INTEGER NOT NULL CHECK (grade >= 6 AND grade <= 12),
  year INTEGER NOT NULL,
  exam_type VARCHAR(50),  -- june, november, exemplar, trial
  province VARCHAR(50),  -- national, gauteng, western_cape, etc.

  -- Metadata
  total_marks INTEGER,
  time_limit_minutes INTEGER,

  -- Resources
  pdf_url VARCHAR(500),
  memo_url VARCHAR(500),  -- Memorandum

  is_published BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_papers_subject (subject_id),
  INDEX idx_papers_grade (grade),
  INDEX idx_papers_year (year),
  INDEX idx_papers_exam_type (exam_type)
);
```

**questions**
```sql
CREATE TABLE questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  paper_id UUID REFERENCES question_papers(id),
  product_id UUID REFERENCES products(id),  -- Link to study guide

  question_number VARCHAR(10),  -- "1.1", "2.3.2"
  question_text TEXT NOT NULL,
  question_image_url VARCHAR(500),

  -- Classification
  subject_id UUID REFERENCES subjects(id) NOT NULL,
  grade INTEGER NOT NULL CHECK (grade >= 6 AND grade <= 12),
  topic VARCHAR(255),
  subtopic VARCHAR(255),
  caps_reference VARCHAR(100),

  question_type VARCHAR(50) NOT NULL,  -- multiple_choice, short_answer, long_answer, essay, calculation
  difficulty VARCHAR(50) DEFAULT 'medium',  -- easy, medium, hard

  -- Scoring
  marks INTEGER NOT NULL,
  time_estimate_minutes INTEGER,

  -- Answer
  correct_answer TEXT,
  answer_explanation TEXT,
  answer_image_url VARCHAR(500),

  -- Tags
  tags JSONB DEFAULT '[]',

  is_published BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_questions_paper (paper_id),
  INDEX idx_questions_subject (subject_id),
  INDEX idx_questions_grade (grade),
  INDEX idx_questions_topic (topic),
  INDEX idx_questions_difficulty (difficulty),
  INDEX idx_questions_type (question_type),
  INDEX idx_questions_tags USING GIN (tags)
);
```

**question_options**
```sql
CREATE TABLE question_options (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  question_id UUID REFERENCES questions(id) ON DELETE CASCADE,

  option_letter VARCHAR(1) NOT NULL,  -- A, B, C, D
  option_text TEXT NOT NULL,
  is_correct BOOLEAN DEFAULT FALSE,

  INDEX idx_options_question (question_id)
);
```

**user_question_attempts**
```sql
CREATE TABLE user_question_attempts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id),

  user_answer TEXT,
  is_correct BOOLEAN,
  marks_earned INTEGER,
  time_spent_seconds INTEGER,

  -- AI feedback
  ai_feedback TEXT,

  attempted_at TIMESTAMP DEFAULT NOW(),

  INDEX idx_attempts_user (user_id),
  INDEX idx_attempts_question (question_id),
  INDEX idx_attempts_attempted (attempted_at DESC)
);
```

**practice_sessions**
```sql
CREATE TABLE practice_sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,

  title VARCHAR(255),
  mode VARCHAR(50),  -- topic_practice, exam_simulation, weak_areas

  -- Filters used
  filters JSONB,

  -- Statistics
  total_questions INTEGER DEFAULT 0,
  correct_answers INTEGER DEFAULT 0,
  total_marks INTEGER DEFAULT 0,
  marks_earned INTEGER DEFAULT 0,
  time_spent_seconds INTEGER DEFAULT 0,

  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,

  INDEX idx_practice_user (user_id),
  INDEX idx_practice_started (started_at DESC)
);
```

### Database Indexes Summary

**Critical Indexes:**
- All foreign keys have indexes
- Email lookups: `idx_users_email`
- Product filtering: `idx_products_grade`, `idx_products_subject`, `idx_products_term`
- Order lookups: `idx_orders_number`, `idx_orders_user`
- Question filtering: `idx_questions_grade`, `idx_questions_subject`, `idx_questions_topic`
- JSONB tags: GIN index on `questions.tags`

---

## API Contracts

### Base URL
**Development:** `http://localhost:8000/api/v1`
**Production:** `https://api.rutiva.co.za/api/v1`

### Authentication

All authenticated endpoints require:
```
Authorization: Bearer <access_token>
```

**Token Refresh:**
When access token expires (15 min), use refresh endpoint:
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response:
{
  "access_token": "new_token",
  "token_type": "bearer"
}
```

### API Endpoints

#### Authentication (`/auth`)

**POST /auth/register**
```http
Request:
{
  "email": "student@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "student",
  "grade": 10,
  "province": "Gauteng"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "student@example.com",
  "full_name": "John Doe",
  "role": "student",
  "grade": 10,
  "is_verified": false
}
```

**POST /auth/login**
```http
Request:
{
  "email": "student@example.com",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "access_token": "eyJ0eXAiOiJKV1Q...",
  "refresh_token": "eyJ0eXAiOiJKV1Q...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "student@example.com",
    "full_name": "John Doe",
    "role": "student",
    "grade": 10
  }
}
```

**POST /auth/otp/request**
```http
Request:
{
  "email": "student@example.com",
  "purpose": "email_verification"
}

Response: 200 OK
{
  "message": "OTP sent to email"
}
```

**POST /auth/otp/verify**
```http
Request:
{
  "email": "student@example.com",
  "code": "123456",
  "purpose": "email_verification"
}

Response: 200 OK
{
  "message": "Email verified successfully"
}
```

#### Products (`/products`)

**GET /products**
```http
Query Params:
?grade=10&subject=math&term=1&is_featured=true&skip=0&limit=20

Response: 200 OK
{
  "total": 45,
  "items": [
    {
      "id": "uuid",
      "sku": "MATH-GR10-T1-2025",
      "title": "Grade 10 Mathematics Term 1",
      "subject": {
        "id": "uuid",
        "name": "Mathematics",
        "code": "MATH"
      },
      "grade": 10,
      "term": 1,
      "year": 2025,
      "price_cents": 9900,
      "sale_price_cents": 7900,
      "thumbnail_url": "https://...",
      "is_featured": true
    }
  ]
}
```

**GET /products/{sku}**
```http
Response: 200 OK
{
  "id": "uuid",
  "sku": "MATH-GR10-T1-2025",
  "title": "Grade 10 Mathematics Term 1",
  "description": "Comprehensive CAPS-aligned...",
  "subject": { "id": "uuid", "name": "Mathematics", "code": "MATH" },
  "grade": 10,
  "term": 1,
  "year": 2025,
  "price_cents": 9900,
  "sale_price_cents": 7900,
  "content_json": {
    "units": [
      {
        "title": "Algebraic Expressions",
        "topics": ["Factorisation", "Simplification"],
        "hours": 12
      }
    ]
  },
  "total_pages": 120,
  "estimated_hours": 40
}
```

#### Cart (`/cart`)

**GET /cart**
```http
Response: 200 OK
{
  "items": [
    {
      "id": "uuid",
      "product": { "sku": "MATH-GR10-T1-2025", "title": "..." },
      "quantity": 1,
      "unit_price_cents": 9900,
      "total_price_cents": 9900
    }
  ],
  "subtotal_cents": 9900,
  "discount_cents": 0,
  "total_cents": 9900
}
```

**POST /cart/items**
```http
Request:
{
  "product_sku": "MATH-GR10-T1-2025",
  "quantity": 1
}

Response: 201 Created
{
  "id": "uuid",
  "product": { ... },
  "quantity": 1
}
```

**POST /cart/promo**
```http
Request:
{
  "code": "SAVE20"
}

Response: 200 OK
{
  "code": "SAVE20",
  "discount_type": "percentage",
  "discount_value": 20,
  "discount_cents": 1980,
  "new_total_cents": 7920
}
```

**POST /checkout**
```http
Request:
{
  "payment_provider": "payfast",
  "promo_code": "SAVE20"
}

Response: 200 OK
{
  "order_id": "uuid",
  "order_number": "RV-20250119-0001",
  "total_cents": 7920,
  "payment_url": "https://www.payfast.co.za/eng/process?..."
}
```

#### Library (`/library`)

**GET /library**
```http
Response: 200 OK
{
  "items": [
    {
      "id": "uuid",
      "product": {
        "sku": "MATH-GR10-T1-2025",
        "title": "Grade 10 Mathematics Term 1",
        "thumbnail_url": "..."
      },
      "progress_percentage": 45,
      "download_count": 3,
      "last_accessed": "2025-01-15T10:30:00Z"
    }
  ]
}
```

**GET /library/{product_id}/download**
```http
Response: 200 OK
{
  "download_url": "https://rutiva-content.s3.af-south-1.amazonaws.com/...",
  "expires_at": "2025-01-19T21:00:00Z"
}
```

#### Timetables (`/timetables`)

**POST /timetables**
```http
Request:
{
  "product_id": "uuid",
  "exam_date": "2025-06-15",
  "study_days_per_week": 5,
  "hours_per_session": 2.5,
  "preferred_time": "afternoon",
  "pace": "normal"
}

Response: 201 Created
{
  "id": "uuid",
  "title": "Grade 10 Mathematics Study Plan",
  "exam_date": "2025-06-15",
  "total_sessions": 48,
  "schedule_json": {
    "weeks": [
      {
        "week_number": 1,
        "sessions": [
          {
            "session_number": 1,
            "topic": "Algebraic Expressions - Introduction",
            "hours": 2.5,
            "date": "2025-01-20"
          }
        ]
      }
    ]
  }
}
```

**POST /timetables/{id}/sessions/complete**
```http
Request:
{
  "session_number": 1,
  "time_spent_minutes": 140,
  "difficulty_rating": 3,
  "understanding_rating": 4,
  "notes": "Struggled with factorisation but got it eventually"
}

Response: 200 OK
{
  "session_number": 1,
  "completed_at": "2025-01-20T16:30:00Z"
}
```

#### Chat (`/chat`)

**POST /chat/sessions**
```http
Request:
{
  "title": "Help with Algebra",
  "grade": 10,
  "subject": "Mathematics",
  "topic": "Factorisation"
}

Response: 201 Created
{
  "id": "uuid",
  "title": "Help with Algebra",
  "grade": 10,
  "subject": "Mathematics"
}
```

**POST /chat/sessions/{id}/messages**
```http
Request:
{
  "content": "How do I factorise x² + 5x + 6?"
}

Response: 200 OK
{
  "id": "uuid",
  "role": "assistant",
  "content": "Great question! Let me guide you through factorising x² + 5x + 6...",
  "tokens": 85
}
```

**GET /chat/usage**
```http
Response: 200 OK
{
  "plan": "standard",
  "questions_limit": 100,
  "questions_used": 23,
  "questions_remaining": 77,
  "current_period_end": "2025-02-19"
}
```

### Error Responses

**Standard Error Format:**
```http
{
  "detail": "Error message",
  "error_code": "INVALID_CREDENTIALS",
  "status_code": 401
}
```

**Common Status Codes:**
- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 422: Unprocessable Entity (Pydantic validation error)
- 500: Internal Server Error

---

## Data Flows

### 1. User Registration & Authentication Flow

```
┌────────┐                  ┌────────────┐                  ┌──────────┐
│ Client │                  │   Backend  │                  │ Database │
└───┬────┘                  └─────┬──────┘                  └────┬─────┘
    │                             │                              │
    │ POST /auth/register         │                              │
    ├────────────────────────────►│                              │
    │ {email, password, ...}      │                              │
    │                             │ Hash password (bcrypt)       │
    │                             │ Create user record           │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │                             │ Generate OTP                 │
    │                             ├─────────────────────────────►│
    │                             │ Insert otp_codes             │
    │                             │                              │
    │                             │ Send OTP email (SMTP)        │
    │                             │                              │
    │◄────────────────────────────┤                              │
    │ {user_id, email, ...}       │                              │
    │                             │                              │
    │ POST /auth/otp/verify       │                              │
    ├────────────────────────────►│                              │
    │ {email, code}               │ Query otp_codes              │
    │                             ├─────────────────────────────►│
    │                             │ Validate code & expiry       │
    │                             │                              │
    │                             │ Mark user.is_verified=true   │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │◄────────────────────────────┤                              │
    │ {message: "Verified"}       │                              │
    │                             │                              │
    │ POST /auth/login            │                              │
    ├────────────────────────────►│                              │
    │ {email, password}           │ Query users by email         │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │                             │ Verify password (bcrypt)     │
    │                             │ Generate JWT (access+refresh)│
    │                             │                              │
    │                             │ Update last_login            │
    │                             ├─────────────────────────────►│
    │                             │                              │
    │◄────────────────────────────┤                              │
    │ {access_token, refresh_token, user}                        │
    │                             │                              │
```

### 2. Product Purchase Flow

```
┌────────┐       ┌────────────┐       ┌──────────┐       ┌──────────┐
│ Client │       │   Backend  │       │ Database │       │ PayFast  │
└───┬────┘       └─────┬──────┘       └────┬─────┘       └────┬─────┘
    │                  │                   │                   │
    │ GET /products    │                   │                   │
    ├─────────────────►│ Query products    │                   │
    │                  ├──────────────────►│                   │
    │◄─────────────────┤                   │                   │
    │ {products[]}     │                   │                   │
    │                  │                   │                   │
    │ POST /cart/items │                   │                   │
    ├─────────────────►│ Create cart item  │                   │
    │ {product_sku}    ├──────────────────►│                   │
    │◄─────────────────┤                   │                   │
    │                  │                   │                   │
    │ POST /cart/promo │                   │                   │
    ├─────────────────►│ Validate promo    │                   │
    │ {code}           ├──────────────────►│                   │
    │◄─────────────────┤ Calculate discount│                   │
    │                  │                   │                   │
    │ POST /checkout   │                   │                   │
    ├─────────────────►│ Create order      │                   │
    │ {payment_provider}├─────────────────►│                   │
    │                  │ Insert order+items│                   │
    │                  │                   │                   │
    │                  │ Generate PayFast URL                  │
    │                  ├──────────────────────────────────────►│
    │◄─────────────────┤                   │                   │
    │ {payment_url}    │                   │                   │
    │                  │                   │                   │
    │ User redirected  │                   │                   │
    │ to PayFast       │                   │                   │
    ├──────────────────────────────────────────────────────────►
    │                  │                   │                   │
    │                  │ Webhook: payment complete             │
    │                  │◄──────────────────────────────────────┤
    │                  │ Verify signature  │                   │
    │                  │ Update order.status='paid'            │
    │                  ├──────────────────►│                   │
    │                  │                   │                   │
    │                  │ Add to user_library                   │
    │                  ├──────────────────►│                   │
    │                  │                   │                   │
    │ Redirect back    │                   │                   │
    │◄─────────────────┤                   │                   │
    │ GET /library     │                   │                   │
    ├─────────────────►│ Query user_library│                   │
    │                  ├──────────────────►│                   │
    │◄─────────────────┤                   │                   │
    │ {library items}  │                   │                   │
```

### 3. AI Tutor Chat Flow

```
┌────────┐       ┌────────────┐       ┌──────────┐       ┌───────────┐
│ Client │       │   Backend  │       │ Database │       │  OpenAI   │
└───┬────┘       └─────┬──────┘       └────┬─────┘       └─────┬─────┘
    │                  │                   │                    │
    │ POST /chat/sessions                  │                    │
    ├─────────────────►│ Create session    │                    │
    │ {title, grade}   ├──────────────────►│                    │
    │◄─────────────────┤                   │                    │
    │ {session_id}     │                   │                    │
    │                  │                   │                    │
    │ POST /sessions/{id}/messages         │                    │
    ├─────────────────►│                   │                    │
    │ {content: "..."}│                   │                    │
    │                  │ Check subscription limit              │
    │                  ├──────────────────►│                    │
    │                  │ Get chat history  │                    │
    │                  ├──────────────────►│                    │
    │                  │                   │                    │
    │                  │ Build AI prompt with context          │
    │                  │ (grade, subject, chat history)        │
    │                  │                   │                    │
    │                  │ Call OpenAI API   │                    │
    │                  ├────────────────────────────────────────►
    │                  │                   │                    │
    │                  │◄────────────────────────────────────────
    │                  │ {AI response, tokens}                 │
    │                  │                   │                    │
    │                  │ Save user message │                    │
    │                  ├──────────────────►│                    │
    │                  │ Save AI response  │                    │
    │                  ├──────────────────►│                    │
    │                  │                   │                    │
    │                  │ Update subscription.questions_used++  │
    │                  ├──────────────────►│                    │
    │                  │                   │                    │
    │◄─────────────────┤                   │                    │
    │ {AI message}     │                   │                    │
```

### 4. Timetable Generation Flow

```
┌────────┐       ┌────────────┐       ┌──────────┐
│ Client │       │   Backend  │       │ Database │
└───┬────┘       └─────┬──────┘       └────┬─────┘
    │                  │                   │
    │ POST /timetables │                   │
    ├─────────────────►│                   │
    │ {product_id,     │ Get product       │
    │  exam_date,      ├──────────────────►│
    │  study_days,     │ {content_json}    │
    │  hours, ...}     │                   │
    │                  │                   │
    │                  │ TimetableGenerator.generate()
    │                  │ - Calculate available weeks
    │                  │ - Distribute topics across sessions
    │                  │ - Account for pace (relaxed/intensive)
    │                  │ - Generate weekly breakdown
    │                  │                   │
    │                  │ Create timetable  │
    │                  ├──────────────────►│
    │                  │ {schedule_json}   │
    │                  │                   │
    │◄─────────────────┤                   │
    │ {timetable with  │                   │
    │  full schedule}  │                   │
    │                  │                   │
    │ GET /timetables/{id}/ical            │
    ├─────────────────►│ Query timetable   │
    │                  ├──────────────────►│
    │                  │                   │
    │                  │ Generate iCal format
    │                  │ (VCALENDAR with VEVENTs)
    │                  │                   │
    │◄─────────────────┤                   │
    │ ical file        │                   │
    │ (download)       │                   │
```

---

## Security Model

### Authentication & Authorization

**JWT Token Structure:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "student",
  "exp": 1642617600,  # Expiry timestamp
  "type": "access"    # or "refresh"
}
```

**Token Lifecycle:**
- Access token: 15 minutes expiry
- Refresh token: 7 days expiry
- Tokens signed with HS256 + SECRET_KEY
- Refresh token can generate new access token

**Role-Based Access Control (RBAC):**
```python
# Example endpoint protection
@router.get("/admin/users")
async def list_users(
    current_user: User = Depends(require_role("super_admin"))
):
    ...
```

**Roles:**
- `student` - Standard learner account
- `parent` - Parent monitoring children
- `school_admin` - School administrator/teacher
- `super_admin` - Platform administrator

### Password Security

**Hashing:**
- Algorithm: bcrypt
- Cost factor: 12 (2^12 iterations)
- Auto-salted

**Password Requirements:**
- Minimum 8 characters
- Must include: uppercase, lowercase, number
- Optional: special character

### Data Protection

**At Rest:**
- Database: PostgreSQL with encryption at rest (via hosting provider)
- S3: Server-side encryption (SSE-S3)
- Sensitive fields: No additional encryption (rely on DB encryption)

**In Transit:**
- HTTPS/TLS 1.3 in production
- Certificate from Let's Encrypt
- HSTS headers enabled

**Secrets Management:**
- Environment variables via .env files (local)
- AWS Secrets Manager or similar (production)
- Never commit secrets to git

### Input Validation

**Frontend:**
- Zod schemas for all forms
- Client-side validation before API calls
- XSS prevention (React auto-escapes)

**Backend:**
- Pydantic models for all requests
- Type validation
- Length limits
- Regex patterns for formats (email, phone)
- SQL injection prevention (ORM only, no raw SQL)

### API Security

**Rate Limiting:**
```python
# Example rates
/auth/login: 5 requests per 15 minutes per IP
/auth/register: 3 requests per hour per IP
/api/*: 100 requests per minute per user
```

**CORS:**
```python
allowed_origins = [
    "http://localhost:3000",      # Dev web
    "exp://localhost:19000",      # Dev mobile
    "https://rutiva.co.za",       # Production web
    "rutiva://",                  # Production mobile
]
```

**Headers:**
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Content-Security-Policy: (defined)
- Strict-Transport-Security: max-age=31536000

### Payment Security

**PayFast Integration:**
- Webhook signature verification
- HTTPS callback URLs only
- Order amount verification
- Idempotency (prevent duplicate processing)

**PCI Compliance:**
- No credit card data stored
- Payment processing via PayFast (PCI-compliant)
- Webhooks over HTTPS

### File Upload Security (Future)

**If file uploads added:**
- Whitelist file types (PDF, JPG, PNG only)
- Max file size: 10MB
- Virus scanning (ClamAV)
- S3 bucket policies (private by default)
- Signed URLs for downloads (time-limited)

---

## Infrastructure

### Development Environment

**Local Stack:**
```
┌─────────────────────────────────────────┐
│         Developer Machine               │
│                                         │
│  ┌──────────────┐   ┌────────────────┐ │
│  │  Next.js     │   │  React Native  │ │
│  │  :3000       │   │  Expo Go       │ │
│  └──────┬───────┘   └────────────────┘ │
│         │                               │
│         │ HTTP                          │
│         ▼                               │
│  ┌──────────────┐                      │
│  │  FastAPI     │                      │
│  │  :8000       │                      │
│  └──────┬───────┘                      │
│         │                               │
│    ┌────┼────┐                         │
│    │    │    │                         │
│  ┌─▼──┐ │  ┌─▼────┐                   │
│  │ PG │ │  │Redis │                   │
│  │5432│ │  │ 6379 │                   │
│  └────┘ │  └──────┘                   │
│         │                               │
│         ▼                               │
│    ┌─────────┐                         │
│    │ AWS S3  │ (via AWS CLI)           │
│    └─────────┘                         │
└─────────────────────────────────────────┘
```

**Setup Commands:**
```bash
# Database
createdb rutiva
cd backend && alembic upgrade head

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (web)
cd apps/web
npm install
npm run dev  # Runs on :3000

# Frontend (mobile)
cd apps/mobile
npm install
npx expo start
```

### Production Environment (Recommended)

```
┌────────────────────────────────────────────────────────┐
│                     Internet                            │
└───────────────────────┬────────────────────────────────┘
                        │
                    DNS (rutiva.co.za)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌───────────────┐ ┌────────────┐ ┌────────────────┐
│   Vercel      │ │   Vercel   │ │  Mobile Apps   │
│   (Web App)   │ │  (API)     │ │  (App Stores)  │
│   Next.js     │ │  or EC2    │ │                │
└───────────────┘ └─────┬──────┘ └────────────────┘
                        │
                  ┌─────┼──────┐
                  │     │      │
           ┌──────▼─┐ ┌─▼────┐ │
           │AWS RDS │ │Redis │ │
           │  PG    │ │Cache │ │
           └────────┘ └──────┘ │
                                │
                         ┌──────▼──────┐
                         │   AWS S3    │
                         │  (Content)  │
                         └─────────────┘
```

**Components:**

**Web Hosting (Next.js):**
- Platform: Vercel (recommended) or Netlify
- Auto-deploy from GitHub
- Edge functions for API routes
- CDN distribution

**Backend Hosting:**
- Option 1: Vercel Serverless Functions (easiest)
- Option 2: AWS EC2 (t3.medium or larger)
- Option 3: DigitalOcean Droplet
- Option 4: Railway.app

**Database:**
- AWS RDS PostgreSQL (db.t3.micro for start)
- Automated backups (daily)
- Multi-AZ for production

**Cache:**
- AWS ElastiCache Redis or Upstash Redis
- Used for session storage, API caching

**Storage:**
- AWS S3 (af-south-1 region)
- Bucket: rutiva-content
- CloudFront CDN (optional for faster delivery)

**Email:**
- SendGrid, AWS SES, or Postmark
- Transactional emails (OTP, receipts, password reset)

**Monitoring:**
- Sentry (error tracking)
- Vercel Analytics (web performance)
- Uptime monitoring (UptimeRobot)

### Deployment Process

**Web (Next.js):**
```bash
# Automated via Vercel GitHub integration
git push origin main
# Auto-deploys to production
```

**Backend:**
```bash
# Manual (EC2 example)
git pull origin main
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
pm2 restart rutiva-api
```

**Mobile:**
```bash
# Build for production
cd apps/mobile
eas build --platform ios
eas build --platform android

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

---

## Integration Points

### External APIs

**OpenAI (AI Tutor):**
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Model: GPT-4 or GPT-3.5-turbo
- Authentication: API key in headers
- Usage: RutivaBot chat, question explanations

**DeepSeek (Alternative AI):**
- Endpoint: `https://api.deepseek.com/v1/chat/completions`
- Lower cost alternative to OpenAI
- Same interface as OpenAI API

**PayFast:**
- Endpoint: `https://www.payfast.co.za/eng/process`
- Webhooks: `https://api.rutiva.co.za/api/v1/webhooks/payfast`
- Signature verification required
- ITN (Instant Transaction Notification)

**Yoco:**
- Endpoint: `https://online.yoco.com/v1/charges`
- Webhooks: `https://api.rutiva.co.za/api/v1/webhooks/yoco`
- API key authentication

**AWS S3:**
- Endpoint: `https://s3.af-south-1.amazonaws.com`
- Bucket: `rutiva-content`
- Authentication: AWS credentials
- SDK: boto3 (Python)

**SMTP (Email):**
- Provider: SendGrid, AWS SES, etc.
- Port: 587 (TLS) or 465 (SSL)
- Authentication: Username/password or API key

---

**Last Updated:** 2025-01-19
**Document Version:** 1.0
**Next Review:** After Phase 2 completion (add rebrand changes)
