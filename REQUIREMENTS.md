# Rutiva - Requirements Document

This document outlines all functional and non-functional requirements for the Rutiva EdTech platform transformation and expansion.

---

## Table of Contents

1. [Current Features](#current-features)
2. [Phase 1: GSD Framework Setup](#phase-1-gsd-framework-setup)
3. [Phase 2: Rutiva Rebrand](#phase-2-rutiva-rebrand)
4. [Phase 3: Mobile Application](#phase-3-mobile-application)
5. [Phase 4: Past Questions Integration](#phase-4-past-questions-integration)
6. [Non-Functional Requirements](#non-functional-requirements)
7. [Acceptance Criteria](#acceptance-criteria)

---

## Current Features

### Documented Existing Functionality (As of 2025-01-19)

#### 1. User Authentication & Authorization

**Features:**
- User registration with role selection (student, parent, school_admin)
- Email/password login with JWT authentication
- OTP-based email verification
- Password reset flow via email
- Refresh token mechanism (15min access, 7-day refresh)
- Role-based access control (RBAC)
- Parent-child account linking

**API Endpoints:**
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/otp/request`
- `POST /api/v1/auth/otp/verify`
- `POST /api/v1/auth/password/reset`

**Acceptance Criteria:**
- ✓ Users can register with email/password
- ✓ Email verification via OTP works
- ✓ JWT tokens auto-refresh on expiry
- ✓ Password reset flow functional
- ✓ Role-based permissions enforced

#### 2. Product Catalog & E-Commerce

**Features:**
- Browse study guides by grade (6-12), subject, term
- Product detail pages with previews
- Bundle offerings (full year, all subjects)
- Subject filtering
- Search functionality
- Featured products
- Dynamic pricing with sale support
- Product SKUs (format: MATH-GR10-T1-2025)

**API Endpoints:**
- `GET /api/v1/products` (with filters: grade, subject, term)
- `GET /api/v1/products/{sku}`
- `GET /api/v1/products/grade/{grade}`
- `GET /api/v1/products/subjects`
- `GET /api/v1/products/bundles`

**Acceptance Criteria:**
- ✓ Products filterable by grade, subject, term
- ✓ Product detail pages display correctly
- ✓ Bundles show included products
- ✓ Pricing displays correctly (regular/sale)

#### 3. Shopping Cart & Checkout

**Features:**
- Add/remove items from cart
- View cart summary
- Apply promo codes (percentage/fixed discounts)
- Multiple payment providers (PayFast, Yoco, EFT)
- Order creation and tracking
- Order number generation (format: RV-YYYYMMDD-XXXX)
- Payment status management

**API Endpoints:**
- `GET /api/v1/cart`
- `POST /api/v1/cart/items`
- `DELETE /api/v1/cart/items/{id}`
- `POST /api/v1/cart/promo`
- `POST /api/v1/checkout`

**Acceptance Criteria:**
- ✓ Cart persists across sessions
- ✓ Promo codes validate correctly
- ✓ Checkout creates orders
- ✓ Payment webhooks process correctly
- ✓ Users receive order confirmation

#### 4. User Library

**Features:**
- View purchased study guides
- Download PDFs from S3
- Track reading progress per guide
- Download history
- Mark sections as complete

**API Endpoints:**
- `GET /api/v1/library`
- `GET /api/v1/library/{product_id}`
- `GET /api/v1/library/{product_id}/download`
- `POST /api/v1/library/{product_id}/progress`

**Acceptance Criteria:**
- ✓ Purchased products appear in library
- ✓ PDF downloads work from S3
- ✓ Progress tracking saves correctly
- ✓ Download limits enforced (if applicable)

#### 5. Personalized Study Timetables

**Features:**
- Generate custom study schedule based on:
  - Exam date
  - Study days per week
  - Hours per session
  - Preferred time of day
  - Learning pace (relaxed/normal/intensive)
- Week-by-week breakdown with topics
- Session progress tracking:
  - Mark sessions complete
  - Rate difficulty (1-5)
  - Rate understanding (1-5)
  - Time spent tracking
  - Session notes
- iCal export for calendar apps
- Multiple timetables per user

**API Endpoints:**
- `POST /api/v1/timetables`
- `GET /api/v1/timetables`
- `GET /api/v1/timetables/{id}`
- `PATCH /api/v1/timetables/{id}`
- `POST /api/v1/timetables/{id}/sessions/complete`
- `DELETE /api/v1/timetables/{id}`
- `GET /api/v1/timetables/{id}/ical`

**Acceptance Criteria:**
- ✓ Timetable generation factors in all parameters
- ✓ Schedule aligns with exam date
- ✓ Sessions marked complete persist
- ✓ iCal export imports to Google Calendar/Outlook
- ✓ Progress statistics calculate correctly

#### 6. AI Tutor (RutivaBot)

**Features:**
- Context-aware tutoring by grade/subject
- Socratic questioning method
- Safety guardrails:
  - No direct exam answers
  - Age-appropriate content
  - No inappropriate topics
- Subscription tiers:
  - Starter: 15 questions/month (R15)
  - Standard: 100 questions/month (R40)
  - Unlimited: Unlimited (R80)
- Chat session management
- Question usage tracking
- Token usage monitoring
- Content flagging system

**API Endpoints:**
- `GET /api/v1/chat/plans`
- `GET /api/v1/chat/usage`
- `POST /api/v1/chat/sessions`
- `GET /api/v1/chat/sessions`
- `GET /api/v1/chat/sessions/{id}`
- `POST /api/v1/chat/sessions/{id}/messages`
- `GET /api/v1/chat/sessions/{id}/messages`

**Acceptance Criteria:**
- ✓ AI responds appropriately for grade level
- ✓ Subscription limits enforced
- ✓ Safety guardrails prevent inappropriate content
- ✓ Chat history persists
- ✓ Usage tracking accurate

#### 7. User Profile & Statistics

**Features:**
- View/edit profile:
  - Name, email, phone
  - Grade (6-12)
  - Province (South African provinces)
- User statistics:
  - Total purchases
  - Study hours
  - Completed sessions
  - Current streak
- Parent-child linking
- Account settings

**API Endpoints:**
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET /api/v1/users/me/stats`

**Acceptance Criteria:**
- ✓ Profile updates save correctly
- ✓ Statistics calculate accurately
- ✓ Parent can view child's progress

#### 8. School Management (Bulk Licensing)

**Features:**
- School registration (EMIS number, province)
- Bulk license generation
- Per-learner pricing
- License code claiming
- School admin dashboard
- Teacher accounts
- Invoice generation

**Database Tables:**
- `schools` - School information
- `school_admins` - Admin/teacher roles
- `school_orders` - Bulk purchases
- `school_licenses` - Claimable license codes

**Acceptance Criteria:**
- ✓ Schools can purchase bulk licenses
- ✓ Learners can claim licenses with codes
- ✓ Admins can view license usage
- ✓ Invoices generate correctly

---

## Phase 1: GSD Framework Setup

### Requirement ID: P1-R1 - Documentation Infrastructure

**User Story:**
As a development team, we need comprehensive documentation so that we can maintain context and onboard new team members efficiently.

**Features:**
1. PROJECT.md - Technical overview and conventions
2. REQUIREMENTS.md - This document
3. ROADMAP.md - Phased implementation plan
4. STATE.md - Real-time progress tracking
5. ARCHITECTURE.md - Detailed system design

**Acceptance Criteria:**
- [ ] All 5 documentation files created
- [ ] Documentation is comprehensive and accurate
- [ ] New team members can set up environment using docs alone
- [ ] Git workflow clearly documented
- [ ] Team can reference docs instead of asking questions

**Priority:** Critical
**Dependencies:** None

---

## Phase 2: Rutiva Rebrand

### Requirement ID: P2-R1 - Complete Code Rebrand

**User Story:**
As a business owner, I need the application rebranded from RUTA to Rutiva across all code and configuration so that we can launch under the new name.

**Features:**
1. Update all 53+ files containing "ruta" references
2. Change application name in package.json files
3. Update API metadata and descriptions
4. Change UI text (headers, footers, branding)
5. Update order number prefix (RT- → RV-)
6. Update AI system prompts

**Files to Update:**
- Root package.json
- apps/web/package.json
- apps/web/app/layout.tsx
- apps/web/components/layout/{header.tsx, footer.tsx}
- backend/app/core/config.py
- backend/app/main.py
- backend/.env.example
- And 40+ more (see exploration results)

**Acceptance Criteria:**
- [ ] All user-facing text says "Rutiva" not "RUTA"
- [ ] Application name updated in all configs
- [ ] No "ruta" references in UI
- [ ] AI tutor refers to itself as "RutivaBot"
- [ ] Order numbers use RV- prefix

**Priority:** Critical
**Dependencies:** None

### Requirement ID: P2-R2 - Database Migration

**User Story:**
As a platform operator, I need the database renamed from "ruta" to "rutiva" so that infrastructure aligns with the new branding.

**Features:**
1. Backup current database
2. Create new "rutiva" database
3. Migrate all data
4. Update connection strings
5. Test all database operations
6. Maintain rollback capability for 1 week

**Acceptance Criteria:**
- [ ] Database backup created successfully
- [ ] All data migrated without loss
- [ ] All queries work with new database
- [ ] Connection strings updated in all environments
- [ ] Zero data loss during migration
- [ ] Rollback procedure documented

**Priority:** Critical
**Dependencies:** P2-R1 (code changes)
**Risk:** High (data loss potential)

### Requirement ID: P2-R3 - S3 Bucket Migration

**User Story:**
As a content manager, I need S3 content moved from "ruta-content" to "rutiva-content" so that URLs align with new branding.

**Features:**
1. Create new S3 bucket: rutiva-content
2. Copy all objects from ruta-content
3. Configure bucket policies and CORS
4. Update Next.js config with new hostname
5. Update content references
6. Test file downloads

**Acceptance Criteria:**
- [ ] New bucket created in af-south-1 region
- [ ] All files copied successfully
- [ ] Bucket policies match old bucket
- [ ] PDFs download correctly from new bucket
- [ ] No broken image links
- [ ] Old bucket kept for 1-week rollback

**Priority:** Critical
**Dependencies:** P2-R1 (config changes)
**Risk:** Medium (file access disruption)

### Requirement ID: P2-R4 - Email Domain Update

**User Story:**
As a user, I need to receive emails from @rutiva.co.za instead of @ruta.co.za so that branding is consistent.

**Features:**
1. Configure @rutiva.co.za in SMTP provider
2. Update FROM_EMAIL in config
3. Update email templates
4. Test email delivery (OTP, password reset, receipts)

**Acceptance Criteria:**
- [ ] @rutiva.co.za domain configured
- [ ] Test emails deliver successfully
- [ ] OTP emails work
- [ ] Password reset emails work
- [ ] Purchase receipts work
- [ ] No emails going to spam

**Priority:** High
**Dependencies:** P2-R1 (config changes)
**Risk:** Medium (email delivery issues)

---

## Phase 3: Mobile Application

### Requirement ID: P3-R1 - Mobile App Foundation

**User Story:**
As a mobile user, I need a React Native app so that I can access Rutiva on my smartphone.

**Features:**
1. Initialize Expo project in apps/mobile/
2. Configure app.json (name, bundle ID, icons)
3. Set up Expo Router navigation
4. Create shared lib (API client, Zustand stores)
5. Build UI component library (Button, Input, Card, etc.)

**Tech Stack:**
- React Native with Expo
- TypeScript
- Expo Router (file-based navigation)
- Zustand (state management)
- React Native Paper (UI components)
- NativeWind (Tailwind for React Native)

**Acceptance Criteria:**
- [ ] Expo project initializes without errors
- [ ] App runs on iOS simulator
- [ ] App runs on Android emulator
- [ ] Navigation structure in place
- [ ] Shared lib reusable across screens
- [ ] UI components styled consistently

**Priority:** Critical
**Dependencies:** P2 complete (stable API)

### Requirement ID: P3-R2 - Mobile Authentication

**User Story:**
As a mobile user, I need to log in and register so that I can access my account on mobile.

**Features:**
1. Login screen (email/password)
2. Registration screen (student/parent)
3. OTP verification screen
4. Password reset flow
5. Auth state persistence with AsyncStorage
6. Biometric auth (Touch ID/Face ID) - Future

**Screens:**
- app/(auth)/login.tsx
- app/(auth)/register.tsx
- app/(auth)/verify-otp.tsx
- app/(auth)/reset-password.tsx

**Acceptance Criteria:**
- [ ] Users can register via mobile
- [ ] Users can log in via mobile
- [ ] OTP verification works
- [ ] Password reset functional
- [ ] Auth state persists across app restarts
- [ ] JWT tokens refresh automatically

**Priority:** Critical
**Dependencies:** P3-R1 (mobile foundation)

### Requirement ID: P3-R3 - Mobile Product Catalog

**User Story:**
As a mobile user, I need to browse and purchase study guides so that I can buy content on my phone.

**Features:**
1. Product listing with filters (grade, subject, term)
2. Product detail view
3. Bundle listings
4. Search functionality
5. Add to cart
6. Cart management
7. Promo code application
8. Checkout flow
9. Payment WebView (PayFast/Yoco)

**Screens:**
- app/(tabs)/shop/index.tsx
- app/(tabs)/shop/[sku].tsx
- app/cart.tsx
- app/checkout.tsx
- app/payment-webview.tsx

**Acceptance Criteria:**
- [ ] Product listing loads and filters work
- [ ] Product details display correctly
- [ ] Cart functionality matches web
- [ ] Promo codes apply
- [ ] Checkout creates orders
- [ ] Payment WebView processes payments
- [ ] Order confirmation shown

**Priority:** Critical
**Dependencies:** P3-R2 (auth required for purchases)

### Requirement ID: P3-R4 - Mobile Library & PDF Viewing

**User Story:**
As a mobile user, I need to view and download my purchased study guides so that I can study on my phone.

**Features:**
1. Library listing (purchased products)
2. PDF viewer integration (react-native-pdf)
3. Offline PDF downloads
4. Progress tracking
5. Search library

**Screens:**
- app/(tabs)/library/index.tsx
- app/(tabs)/library/[id].tsx
- app/(tabs)/library/reader/[id].tsx

**Acceptance Criteria:**
- [ ] Library shows purchased products
- [ ] PDFs render correctly
- [ ] Users can download PDFs for offline viewing
- [ ] Progress tracking syncs with backend
- [ ] PDF viewer has zoom, scroll, page navigation

**Priority:** Critical
**Dependencies:** P3-R2 (auth)

### Requirement ID: P3-R5 - Mobile Study Timetables

**User Story:**
As a mobile user, I need to create and track study timetables so that I can manage my study schedule on mobile.

**Features:**
1. Timetable listing
2. Create timetable wizard
3. Timetable detail view with calendar
4. Mark sessions complete
5. Track time spent, difficulty, understanding
6. Add session notes
7. Export to device calendar (iCal)
8. Push notifications for study sessions

**Screens:**
- app/(tabs)/study/index.tsx
- app/(tabs)/study/create.tsx
- app/(tabs)/study/[id].tsx
- app/(tabs)/study/calendar.tsx

**Acceptance Criteria:**
- [ ] Users can create timetables on mobile
- [ ] All timetable parameters supported
- [ ] Sessions marked complete sync with backend
- [ ] Calendar view displays schedule
- [ ] iCal export works
- [ ] Push notifications trigger on time

**Priority:** High
**Dependencies:** P3-R2 (auth)

### Requirement ID: P3-R6 - Mobile AI Tutor

**User Story:**
As a mobile user, I need to chat with RutivaBot so that I can get tutoring help on my phone.

**Features:**
1. Chat interface
2. Message input with send button
3. AI typing indicator
4. Chat history
5. Session management (create, view, list)
6. Subscription status display
7. Usage tracking (questions remaining)

**Screens:**
- app/(tabs)/tutor/index.tsx (sessions list)
- app/(tabs)/tutor/chat/[id].tsx (chat interface)
- app/(tabs)/tutor/subscription.tsx

**Acceptance Criteria:**
- [ ] Users can send messages to AI
- [ ] AI responses display correctly
- [ ] Chat history loads
- [ ] Subscription limits enforced
- [ ] Usage tracking accurate
- [ ] Chat sessions persist

**Priority:** High
**Dependencies:** P3-R2 (auth)

### Requirement ID: P3-R7 - Mobile User Profile

**User Story:**
As a mobile user, I need to view and edit my profile so that I can manage my account on mobile.

**Features:**
1. Profile display (name, email, grade, province)
2. Edit profile
3. User statistics (study hours, purchases, etc.)
4. Logout
5. Settings

**Screens:**
- app/(tabs)/profile/index.tsx
- app/(tabs)/profile/edit.tsx
- app/(tabs)/profile/stats.tsx
- app/(tabs)/profile/settings.tsx

**Acceptance Criteria:**
- [ ] Profile displays correctly
- [ ] Users can edit profile
- [ ] Statistics match web version
- [ ] Logout clears auth state
- [ ] Settings save correctly

**Priority:** Medium
**Dependencies:** P3-R2 (auth)

### Requirement ID: P3-R8 - Mobile Backend API Extensions

**User Story:**
As a mobile developer, I need additional API endpoints to support mobile-specific features.

**Features:**
1. Device registration (for push notifications)
2. Notification settings
3. App version check (force update)

**New Endpoints:**
```
POST /api/v1/users/devices
GET /api/v1/users/me/notification-settings
PATCH /api/v1/users/me/notification-settings
GET /api/v1/app/version
```

**Database Changes:**
- New table: user_devices
- Add column: users.notification_settings (JSONB)

**Acceptance Criteria:**
- [ ] Device registration saves Expo push tokens
- [ ] Notification settings CRUD works
- [ ] App version check returns correct version
- [ ] Force update logic implemented

**Priority:** Medium
**Dependencies:** P3-R5 (for push notifications)

---

## Phase 4: Past Questions Integration

### Requirement ID: P4-R1 - Question Database Schema

**User Story:**
As a platform operator, I need a database schema for past questions so that we can store and organize question papers.

**Features:**
1. QuestionPaper model (paper metadata)
2. Question model (individual questions)
3. QuestionOption model (MCQ options)
4. UserQuestionAttempt model (practice tracking)
5. PracticeSession model (session metadata)

**Database Tables:**
```sql
question_papers (id, title, subject_id, grade, year, exam_type, province, total_marks, time_limit_minutes, pdf_url, memo_url)

questions (id, paper_id, product_id, question_number, question_text, question_image_url, subject_id, grade, topic, subtopic, caps_reference, question_type, difficulty, marks, time_estimate_minutes, correct_answer, answer_explanation, answer_image_url, tags)

question_options (id, question_id, option_letter, option_text, is_correct)

user_question_attempts (id, user_id, question_id, user_answer, is_correct, marks_earned, time_spent_seconds, ai_feedback, attempted_at)

practice_sessions (id, user_id, title, mode, filters, total_questions, correct_answers, total_marks, marks_earned, time_spent_seconds, started_at, completed_at)
```

**Acceptance Criteria:**
- [ ] All models created with proper relationships
- [ ] Database migration runs successfully
- [ ] Indexes added for filtering (grade, subject, topic)
- [ ] Constraints enforced (foreign keys, not null)

**Priority:** Critical
**Dependencies:** None

### Requirement ID: P4-R2 - Question Data Collection

**User Story:**
As a content manager, I need a process to collect and digitize past question papers so that we can populate the database.

**Sources:**
1. Department of Basic Education (DBE) - National papers
2. Provincial Education Departments - 9 provinces
3. School partnerships - Past papers upload portal

**Process:**
1. Download PDFs from sources
2. OCR if needed (Google Cloud Vision, Tesseract)
3. Manual digitization by educators
4. Structure as JSON (questions, options, answers, metadata)
5. Quality review (2-person verification)
6. Tag with CAPS topics
7. Import to database

**Initial Scope:**
- Grades 10-12: Math, Physical Sciences, Life Sciences, English
- 2020-2024 papers (5 years)
- Target: 5,000-15,000 questions

**Acceptance Criteria:**
- [ ] OCR pipeline set up and tested
- [ ] Import scripts created and tested
- [ ] Quality review process documented
- [ ] First 500 questions digitized and imported
- [ ] CAPS topic tagging complete
- [ ] Educator sign-off on quality

**Priority:** High
**Dependencies:** P4-R1 (database schema)

### Requirement ID: P4-R3 - Question Practice API

**User Story:**
As a developer, I need API endpoints to support question practice features.

**Features:**
1. List/search questions (filter: grade, subject, topic, difficulty)
2. Get question details
3. Submit question attempt
4. Get random questions for practice
5. List question papers
6. Get paper with all questions
7. Download original PDF
8. Create practice session
9. Complete practice session
10. Get user analytics

**API Endpoints:**
```
GET /api/v1/questions/papers
GET /api/v1/questions/papers/{id}
GET /api/v1/questions/papers/{id}/download
GET /api/v1/questions
GET /api/v1/questions/{id}
POST /api/v1/questions/{id}/attempt
GET /api/v1/questions/random
POST /api/v1/practice/sessions
GET /api/v1/practice/sessions/{id}
POST /api/v1/practice/sessions/{id}/complete
GET /api/v1/practice/analytics
```

**Acceptance Criteria:**
- [ ] All endpoints implemented
- [ ] Filtering works correctly
- [ ] Attempt submission scores correctly
- [ ] Random questions don't repeat in session
- [ ] Analytics calculations accurate
- [ ] Pagination implemented for lists

**Priority:** Critical
**Dependencies:** P4-R1 (database), P4-R2 (data)

### Requirement ID: P4-R4 - Practice Modes

**User Story:**
As a student, I need different ways to practice questions so that I can study effectively.

**Features:**
1. Topic Practice:
   - Select grade → subject → topic
   - 10-20 questions on that topic
   - Immediate feedback
   - View solutions after attempt

2. Exam Simulation:
   - Select full past paper
   - Timed practice (matches real exam)
   - No feedback until completion
   - Mark breakdown and solutions at end

3. Weak Areas Practice:
   - AI identifies weak topics from past attempts
   - Recommends targeted practice
   - Adaptive difficulty

4. Daily Challenge (Future):
   - 5 random questions daily
   - Gamification (streaks, leaderboard)

**Acceptance Criteria:**
- [ ] Topic practice mode functional
- [ ] Exam simulation timer works
- [ ] Weak areas detection accurate
- [ ] Solutions display correctly
- [ ] Progress saves between sessions

**Priority:** High
**Dependencies:** P4-R3 (API)

### Requirement ID: P4-R5 - AI Tutor Integration for Questions

**User Story:**
As a student, I need AI help with question explanations so that I can understand my mistakes.

**Features:**
1. AI explains question solutions step-by-step
2. AI identifies common mistakes
3. AI recommends practice questions based on weak areas
4. AI generates similar questions
5. AI links to relevant study guide sections

**New AI Endpoints:**
```
POST /api/v1/questions/{id}/explain
POST /api/v1/chat/sessions/{id}/recommend-questions
POST /api/v1/questions/generate-similar
```

**System Prompt Updates:**
- RutivaBot can explain past exam questions
- Provide step-by-step solutions
- Identify common mistakes
- Link to study guide sections

**Acceptance Criteria:**
- [ ] AI explanations are accurate
- [ ] Step-by-step solutions clear
- [ ] Question recommendations relevant
- [ ] Similar questions similar difficulty
- [ ] Study guide links work

**Priority:** High
**Dependencies:** P4-R3 (questions API)

### Requirement ID: P4-R6 - Practice UI (Web & Mobile)

**User Story:**
As a student, I need an interface to practice questions on web and mobile.

**Features (Web):**
1. Practice mode selection page
2. Topic practice interface
3. Exam simulation interface
4. Analytics dashboard
5. Question card component
6. Answer input component
7. Progress indicators
8. Results card

**Features (Mobile):**
- Mirror web functionality
- Touch-optimized interface
- Offline support for downloaded papers

**Screens (Web):**
- apps/web/app/(study)/practice/page.tsx
- apps/web/app/(study)/practice/topic/page.tsx
- apps/web/app/(study)/practice/exam/[id]/page.tsx
- apps/web/app/(study)/practice/analytics/page.tsx

**Screens (Mobile):**
- apps/mobile/app/(tabs)/practice/index.tsx
- apps/mobile/app/(tabs)/practice/topic.tsx
- apps/mobile/app/(tabs)/practice/exam/[id].tsx
- apps/mobile/app/(tabs)/practice/analytics.tsx

**Acceptance Criteria:**
- [ ] UI matches design mockups
- [ ] Question display works on all screen sizes
- [ ] Answer submission smooth
- [ ] Results display clearly
- [ ] Analytics charts informative
- [ ] Mobile UI touch-friendly

**Priority:** High
**Dependencies:** P4-R3 (API), P3 (mobile foundation)

---

## Non-Functional Requirements

### Performance

**NFR-1: Response Times**
- API response time < 200ms (p95)
- Page load time < 2 seconds
- Mobile app launch < 3 seconds
- PDF download initiation < 1 second

**NFR-2: Scalability**
- Support 10,000 concurrent users
- Database handles 1M+ questions
- Handle 100,000 practice sessions/day

**NFR-3: Availability**
- 99.9% uptime SLA
- Planned maintenance < 2 hours/month
- Graceful degradation if services unavailable

### Security

**NFR-4: Authentication**
- JWT tokens with short expiry (15min access, 7-day refresh)
- Passwords hashed with bcrypt (cost factor 12)
- OTP expires after 10 minutes
- Rate limiting on auth endpoints (5 attempts/15min)

**NFR-5: Data Protection**
- HTTPS/TLS 1.3 in production
- Sensitive data encrypted at rest
- User data not shared without consent
- GDPR/POPIA compliance

**NFR-6: Input Validation**
- All user input validated (frontend + backend)
- SQL injection prevention (ORM only)
- XSS prevention (sanitize HTML)
- CSRF protection

### Usability

**NFR-7: Accessibility**
- WCAG 2.1 Level AA compliance
- Screen reader support
- Keyboard navigation
- Color contrast ratios meet standards

**NFR-8: Mobile Responsiveness**
- Web works on screens 320px+
- Mobile app works on iOS 13+ and Android 8+
- Touch targets ≥ 44x44px

**NFR-9: Internationalization**
- Support English and Afrikaans (Phase 2 future)
- Date/time in South African format
- Currency in ZAR

### Maintainability

**NFR-10: Code Quality**
- TypeScript strict mode enabled
- Python type hints required
- Code coverage ≥ 70% (when tests added)
- ESLint/Pylint checks passing

**NFR-11: Documentation**
- All API endpoints documented (OpenAPI)
- README in each package
- Inline code comments for complex logic
- Architecture diagrams up to date

**NFR-12: Monitoring**
- Error tracking (Sentry or similar)
- Performance monitoring (New Relic or similar)
- User analytics (privacy-compliant)
- Logging (structured JSON logs)

---

## Acceptance Criteria

### Phase 1: GSD Framework

**Definition of Done:**
- [ ] PROJECT.md created and reviewed
- [ ] REQUIREMENTS.md (this file) complete
- [ ] ROADMAP.md with timeline created
- [ ] STATE.md initialized with current state
- [ ] ARCHITECTURE.md with system design complete
- [ ] Git workflow documented and tested
- [ ] Team can reference docs instead of asking questions

### Phase 2: Rutiva Rebrand

**Definition of Done:**
- [ ] All 53+ files with "ruta" updated
- [ ] Database renamed and migrated (zero data loss)
- [ ] S3 bucket migrated (all files accessible)
- [ ] Email domain updated and tested
- [ ] All critical user flows pass testing
- [ ] No console errors in production
- [ ] Rollback procedures documented

### Phase 3: Mobile Application

**Definition of Done:**
- [ ] Mobile app runs on iOS and Android
- [ ] All features have ≥95% parity with web
- [ ] Critical flows tested end-to-end
- [ ] App submitted to TestFlight/Play Store
- [ ] Beta testing shows <5% crash rate
- [ ] Performance metrics met (launch time, responsiveness)
- [ ] User feedback incorporated

### Phase 4: Past Questions

**Definition of Done:**
- [ ] Database schema complete with migrations
- [ ] 5,000+ questions imported and verified
- [ ] All practice modes functional
- [ ] AI explanations accurate (educator reviewed)
- [ ] Analytics calculations verified
- [ ] UI works on web and mobile
- [ ] Performance acceptable with full dataset
- [ ] User testing shows >80% satisfaction

---

**Last Updated:** 2025-01-19
**Document Version:** 1.0
**Status:** Phase 1 in progress
