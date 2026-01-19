# Rutiva - Implementation Roadmap

This document outlines the phased implementation timeline for transforming RUTA into Rutiva.

**Total Duration:** 10 weeks
**Start Date:** 2025-01-20 (Week 1)
**Target Completion:** 2025-03-31 (Week 10)

---

## Timeline Overview

| Phase | Duration | Dates | Complexity | Risk | Status |
|-------|----------|-------|------------|------|--------|
| Phase 1: GSD Setup | Week 1 | Jan 20-26 | Low | Low | 🟡 In Progress |
| Phase 2: Rebrand | Week 2 | Jan 27 - Feb 2 | Medium | Medium | ⚪ Not Started |
| Phase 3: Mobile App | Weeks 3-6 | Feb 3 - Mar 2 | High | High | ⚪ Not Started |
| Phase 4: Questions | Weeks 7-10 | Mar 3-31 | Medium | Medium | ⚪ Not Started |

**Legend:**
- 🟢 Complete
- 🟡 In Progress
- 🔴 Blocked
- ⚪ Not Started

---

## Phase 1: GSD Framework Setup (Week 1)

### Goal
Establish documentation infrastructure for long-term maintainability and context management.

### Timeline: January 20-26, 2025

### Milestones

#### M1.1: Core Documentation Complete (Day 1-2)
**Tasks:**
1. ✅ Create PROJECT.md with tech stack and architecture overview
2. ✅ Create REQUIREMENTS.md with feature specifications
3. 🟡 Create ROADMAP.md (this document)
4. ⚪ Create STATE.md for implementation tracking
5. ⚪ Create ARCHITECTURE.md with system design details

**Deliverables:**
- 5 comprehensive documentation files
- Git workflow documented

**Dependencies:** None

**Risk Assessment:** Low
- No code changes
- No infrastructure changes
- Straightforward documentation work

#### M1.2: Workflow Validation (Day 3)
**Tasks:**
1. Review all documentation for completeness
2. Test git workflow with sample commits
3. Validate that new team members can set up environment using docs
4. Get team sign-off on documentation

**Deliverables:**
- Reviewed and approved documentation
- Tested git workflow

**Success Criteria:**
- [ ] All 5 docs complete and peer-reviewed
- [ ] Git workflow tested
- [ ] Team can navigate docs easily
- [ ] Context management approach defined

---

## Phase 2: Rutiva Rebrand (Week 2)

### Goal
Complete transformation from RUTA to Rutiva across code, infrastructure, and branding without breaking functionality.

### Timeline: January 27 - February 2, 2025

### Milestones

#### M2.1: Code Changes Complete (Day 1-3)
**Tasks:**

**Priority 1 - Configuration (Day 1):**
1. Update root package.json
2. Update backend/app/core/config.py
3. Update backend/.env.example
4. Update backend/app/main.py
5. Update apps/web/package.json

**Priority 2 - UI & Branding (Day 2):**
6. Update apps/web/app/layout.tsx (metadata)
7. Update apps/web/components/layout/header.tsx
8. Update apps/web/components/layout/footer.tsx
9. Update apps/web/next.config.js

**Priority 3 - Content & Services (Day 3):**
10. Update content/sample-guide.json
11. Update backend/app/api/v1/timetable.py
12. Update backend/app/models/order.py (order prefix)
13. Update backend/app/services/ai_service.py (AI prompts)
14. Update any remaining files from search results

**Deliverables:**
- All 53+ files updated
- Atomic git commits per change
- Updated .env.example files

**Dependencies:** Phase 1 complete

#### M2.2: Infrastructure Migration (Day 4-5)

**Database Migration (Day 4 morning):**
1. Create database backup: `pg_dump ruta > ruta_backup_$(date +%Y%m%d).sql`
2. Create new database: `createdb rutiva`
3. Restore data: `psql rutiva < ruta_backup_*.sql`
4. Update .env files with new connection string
5. Test all database operations
6. Verify zero data loss

**S3 Bucket Migration (Day 4 afternoon):**
1. Create new bucket: `aws s3 mb s3://rutiva-content --region af-south-1`
2. Copy all objects: `aws s3 sync s3://ruta-content s3://rutiva-content`
3. Update bucket policies (same as ruta-content)
4. Update CORS settings
5. Test file access from web app

**Email Domain (Day 5 morning):**
1. Set up @rutiva.co.za in SMTP provider
2. Update FROM_EMAIL in config
3. Test email delivery (OTP, password reset, receipts)

**Deliverables:**
- Migrated database (rutiva)
- Migrated S3 bucket (rutiva-content)
- Email sending from @rutiva.co.za

**Dependencies:** M2.1 (code changes must be ready)

**Risk Assessment:** Medium
- Database migration: High risk (data loss potential)
- S3 migration: Medium risk (file access disruption)
- Mitigation: Full backups, keep old resources for 1 week

#### M2.3: Testing & Validation (Day 5-6)

**Critical Flow Testing:**
- [ ] Login/register flow works
- [ ] Product purchase completes end-to-end
- [ ] PDF downloads work from new S3 bucket
- [ ] Email delivery works (OTP, password reset)
- [ ] Timetable creation and tracking functional
- [ ] AI tutor chat responds correctly
- [ ] All API endpoints return 200 for valid requests

**Rollback Criteria:**
- If >2 critical flows fail → immediate rollback

**Deliverables:**
- Tested production-ready rebrand
- Updated STATE.md with migration results

**Success Criteria:**
- [ ] Zero data loss
- [ ] All features functional
- [ ] Infrastructure fully migrated
- [ ] No console errors

---

## Phase 3: React Native Mobile App (Weeks 3-6)

### Goal
Build production-ready mobile app with full feature parity to web application.

### Timeline: February 3 - March 2, 2025

### Milestones

#### M3.1: Foundation & Authentication (Week 3: Feb 3-9)

**Setup (Days 1-2):**
1. Initialize Expo project: `npx create-expo-app@latest apps/mobile`
2. Configure TypeScript, ESLint, Prettier
3. Set up Expo Router navigation structure
4. Create shared lib (API client, Zustand stores)
5. Build UI component library (Button, Input, Card, etc.)

**Authentication (Days 3-5):**
6. Implement login screen
7. Implement registration screen
8. Implement OTP verification
9. Implement password reset
10. Add auth state persistence with AsyncStorage

**Deliverables:**
- Functional Expo app running on iOS/Android
- Complete auth flow
- Reusable UI components

**Dependencies:** Phase 2 complete (stable API)

**Success Criteria:**
- [ ] App runs on both platforms
- [ ] Users can register and login
- [ ] OTP verification works
- [ ] Auth persists across app restarts

#### M3.2: E-Commerce (Week 4: Feb 10-16)

**Product Catalog (Days 1-2):**
11. Implement product listing with filters
12. Implement product detail view
13. Implement bundle listings
14. Add search functionality

**Shopping Cart & Checkout (Days 3-5):**
15. Implement cart management
16. Add promo code application
17. Implement checkout flow
18. Integrate payment WebView (PayFast/Yoco)
19. Add order confirmation screen

**Deliverables:**
- Complete shop experience
- Working checkout and payment

**Dependencies:** M3.1 (auth)

**Success Criteria:**
- [ ] Products browsable and filterable
- [ ] Cart operations work
- [ ] Payments process successfully
- [ ] Orders created correctly

#### M3.3: Study Features (Week 5: Feb 17-23)

**User Library (Days 1-2):**
20. Implement library listing
21. Integrate PDF viewer (react-native-pdf)
22. Add offline PDF downloads
23. Implement progress tracking

**Study Timetables (Days 3-5):**
24. Implement timetable listing
25. Create timetable wizard
26. Implement timetable detail view
27. Add session completion tracking
28. Implement calendar view
29. Add iCal export functionality

**Deliverables:**
- Functional library with PDF viewing
- Complete timetable features

**Dependencies:** M3.1 (auth), M3.2 (purchases for library)

**Success Criteria:**
- [ ] PDFs viewable and downloadable
- [ ] Timetables creatable
- [ ] Session tracking works
- [ ] Calendar integration functional

#### M3.4: AI Tutor, Profile & Polish (Week 6: Feb 24 - Mar 2)

**AI Tutor (Days 1-2):**
30. Implement chat interface
31. Add session management
32. Display subscription status
33. Add usage tracking UI

**User Profile (Day 3):**
34. Implement profile screen
35. Add edit profile functionality
36. Implement stats screen

**Backend Extensions (Day 3):**
37. Add device registration endpoint
38. Add notification settings endpoint
39. Add app version check endpoint
40. Create database migration for user_devices

**Polish (Days 4-5):**
41. Add app icons and splash screen
42. Implement loading states
43. Add error handling
44. Implement pull-to-refresh
45. Performance optimization
46. Write E2E tests (Detox)
47. Test on various devices
48. Prepare for TestFlight/Play Store

**Deliverables:**
- Complete mobile app with all features
- Backend API extensions
- Polished UI/UX
- E2E tests

**Dependencies:** M3.1, M3.2, M3.3

**Success Criteria:**
- [ ] 95%+ feature parity with web
- [ ] App launch time < 3 seconds
- [ ] All critical flows tested
- [ ] Crash rate < 5% in beta
- [ ] Ready for app store submission

**Risk Assessment:** High
- New platform: Learning curve, platform-specific bugs
- Feature parity: Ensuring mobile matches web
- Mitigation: Early testing on both platforms, Expo for consistency

---

## Phase 4: Past Questions Integration (Weeks 7-10)

### Goal
Build comprehensive past question papers system with AI-powered practice and analytics.

### Timeline: March 3-31, 2025

### Milestones

#### M4.1: Database & Backend API (Week 7: Mar 3-9)

**Database (Days 1-2):**
1. Create question models (QuestionPaper, Question, QuestionOption, UserQuestionAttempt, PracticeSession)
2. Create and run database migration
3. Add indexes for filtering (grade, subject, topic)

**Backend API (Days 3-5):**
4. Implement question papers API
5. Implement questions API (list, get, submit attempt, random)
6. Implement practice sessions API
7. Implement analytics API

**Deliverables:**
- Complete question database schema
- All question/practice API endpoints

**Dependencies:** Phase 2 complete (database must be rutiva)

**Success Criteria:**
- [ ] Migration runs successfully
- [ ] All endpoints functional
- [ ] Filtering works correctly
- [ ] Scoring accurate

#### M4.2: Data Collection (Week 8: Mar 10-16)

**Pipeline Setup (Days 1-2):**
8. Identify and download DBE papers (manual)
9. Set up OCR pipeline (Google Cloud Vision or Tesseract)
10. Create import scripts (JSON to database)

**Content Digitization (Days 3-5):**
11. Digitize first 500 questions (manual with educators)
12. Quality review process (2-person verification)
13. Import to database
14. Validate imported questions

**Deliverables:**
- OCR pipeline operational
- Import scripts tested
- 500+ questions imported

**Dependencies:** M4.1 (database schema)

**Success Criteria:**
- [ ] OCR produces accurate results
- [ ] Import scripts handle edge cases
- [ ] Quality review catches errors
- [ ] Questions tagged with CAPS topics

**Risk Assessment:** Medium
- Data quality: Manual digitization errors
- Mitigation: 2-person review, educator sign-off

#### M4.3: Frontend Implementation (Week 9: Mar 17-23)

**Web UI (Days 1-3):**
15. Implement practice mode selection
16. Implement topic practice interface
17. Implement exam simulation interface
18. Implement analytics dashboard
19. Create reusable components (QuestionCard, AnswerInput, ProgressIndicator)
20. Add to navigation/menu

**Mobile UI (Days 4-5):**
21. Implement practice mode selection (mobile)
22. Implement topic practice (mobile)
23. Implement exam simulation (mobile)
24. Implement analytics (mobile)
25. Add to tab navigation

**Deliverables:**
- Complete practice UI on web and mobile
- Consistent experience across platforms

**Dependencies:** M4.1 (API), Phase 3 (mobile app)

**Success Criteria:**
- [ ] UI responsive on all screen sizes
- [ ] Question display correct
- [ ] Answer submission smooth
- [ ] Results clear and informative

#### M4.4: AI Integration & Polish (Week 10: Mar 24-31)

**AI Enhancements (Days 1-2):**
26. Update RutivaBot system prompts
27. Implement AI explanations endpoint
28. Implement question recommendations
29. Implement weak area detection

**Testing & Optimization (Days 3-4):**
30. Test question submission
31. Test analytics calculations
32. Test AI integration
33. Performance optimization (database queries, pagination)
34. User acceptance testing

**Documentation & Launch (Day 5):**
35. Update ARCHITECTURE.md with question schema
36. Update STATE.md with completion
37. Prepare launch communications
38. Monitor initial usage

**Deliverables:**
- AI-powered explanations
- Tested and optimized system
- Updated documentation
- Launched feature

**Dependencies:** M4.1, M4.2, M4.3

**Success Criteria:**
- [ ] AI explanations accurate (educator reviewed)
- [ ] Performance acceptable with 5,000+ questions
- [ ] All practice modes functional
- [ ] User testing shows >80% satisfaction

**Risk Assessment:** Medium
- AI accuracy: Wrong explanations
- Performance: Large dataset queries slow
- Mitigation: Human review of AI, database optimization

---

## Ongoing: Content Expansion (Post-Week 10)

### Goal
Continuously expand question database to comprehensive coverage.

### Tasks (Ongoing)
- Digitize remaining questions (target: 15,000+)
- Expand to all CAPS subjects
- Add older years (2015-2019)
- Partner with schools for more papers
- Hire dedicated content team

### Milestones
- **Month 1 (April):** 10,000 questions
- **Month 2 (May):** 15,000 questions
- **Month 3 (June):** 20,000+ questions, all major subjects covered

---

## Dependencies Map

```
Phase 1: GSD Setup
    │
    ▼
Phase 2: Rebrand ──┐
    │              │
    ▼              │
Phase 3: Mobile ◄──┘
    │
    ├──► Week 3: Foundation & Auth
    ├──► Week 4: E-Commerce
    ├──► Week 5: Study Features
    └──► Week 6: AI, Profile, Polish
    │
    ▼
Phase 4: Questions ◄─ (Can start Week 7 in parallel with Week 6)
    │
    ├──► Week 7: Database & API
    ├──► Week 8: Data Collection
    ├──► Week 9: Frontend (needs Phase 3 mobile)
    └──► Week 10: AI & Polish
```

**Critical Path:**
Phase 1 → Phase 2 → Phase 3 Week 3-5 → Phase 4 Week 9 → Phase 4 Week 10

**Parallel Work Opportunities:**
- Phase 3 Week 6 can overlap with Phase 4 Week 7
- Phase 4 Week 8 (data collection) can start earlier as manual task

---

## Resource Requirements

### Team Composition (Recommended)

**Full Team:**
- 1 Full-stack developer (lead)
- 1 Mobile developer (React Native specialist)
- 1 Backend developer (Python/FastAPI)
- 1 Educator/Content specialist (question digitization)
- 1 QA tester (part-time)
- 1 DevOps engineer (part-time, for infrastructure)

**Solo/Small Team:**
- 1 Full-stack developer with React Native experience
- Contract educators for question digitization
- Timeline extends to 12-14 weeks

### Time Allocation
- **Phase 1:** 40 hours (1 week, 1 person)
- **Phase 2:** 40 hours (1 week, 1 person)
- **Phase 3:** 160 hours (4 weeks, 1 person or 2 weeks, 2 people)
- **Phase 4:** 160 hours (4 weeks, 1 developer + 1 content specialist)

**Total:** ~400 developer hours + ongoing content work

---

## Risk Management

### Phase 2 Risks

**Database Migration:**
- **Risk:** Data loss or corruption
- **Probability:** Low
- **Impact:** Critical
- **Mitigation:** Full backup, test on staging, keep old DB for 1 week

**S3 Migration:**
- **Risk:** File access broken
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** Keep old bucket active, gradual cutover

**Email Delivery:**
- **Risk:** Emails not sending
- **Probability:** Low
- **Impact:** High
- **Mitigation:** Test thoroughly before production, keep old email active

### Phase 3 Risks

**Platform-Specific Bugs:**
- **Risk:** Features work on iOS but not Android (or vice versa)
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** Test early on both platforms, use Expo for consistency

**Feature Parity Gap:**
- **Risk:** Mobile missing features from web
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** Detailed feature checklist, thorough testing

**Payment Integration:**
- **Risk:** Mobile payments fail
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** Thorough WebView testing, fallback to web checkout

### Phase 4 Risks

**Data Quality:**
- **Risk:** Questions digitized incorrectly
- **Probability:** Medium
- **Impact:** High
- **Mitigation:** 2-person review, educator sign-off

**AI Accuracy:**
- **Risk:** AI provides wrong explanations
- **Probability:** Medium
- **Impact:** Medium
- **Mitigation:** Human review, prompt tuning, disclaimers

**Performance Degradation:**
- **Risk:** Large dataset slows queries
- **Probability:** Low
- **Impact:** Medium
- **Mitigation:** Database indexing, query optimization, pagination

---

## Success Metrics

### Phase 1
- [ ] All 5 documentation files complete
- [ ] Team can set up environment using docs alone
- [ ] Git workflow tested and working

### Phase 2
- [ ] Zero data loss during migration
- [ ] All critical flows pass testing
- [ ] No production errors for 48 hours post-launch

### Phase 3
- [ ] App runs on iOS 13+ and Android 8+
- [ ] 95%+ feature parity with web
- [ ] App launch time < 3 seconds
- [ ] Crash rate < 5% in beta testing
- [ ] Submitted to app stores

### Phase 4
- [ ] 5,000+ questions imported
- [ ] All practice modes functional
- [ ] AI explanations 90%+ accurate (educator review)
- [ ] Performance acceptable (API < 500ms, pagination works)
- [ ] User testing shows >80% satisfaction

---

## Communication & Reporting

### Weekly Progress Updates
- **When:** Every Friday 4pm SAST
- **Who:** All team members
- **What:** Progress on milestones, blockers, next week plan

### Phase Completion Reviews
- **When:** End of each phase
- **Who:** Stakeholders + team
- **What:** Demo, metrics review, lessons learned

### Daily Standups (Optional)
- **When:** Every day 10am SAST
- **Who:** Dev team
- **What:** Yesterday, today, blockers (15min max)

---

## Next Steps

**Immediate (Week 1):**
1. ✅ Create PROJECT.md
2. ✅ Create REQUIREMENTS.md
3. 🟡 Create ROADMAP.md (this document)
4. ⚪ Create STATE.md
5. ⚪ Create ARCHITECTURE.md
6. ⚪ Review and approve all documentation

**Week 2 Prep:**
- Set up staging environment for Phase 2 testing
- Test database backup/restore procedure
- Prepare S3 migration scripts
- Configure @rutiva.co.za email

**Week 3 Prep:**
- Install Expo CLI and dependencies
- Set up iOS simulator (if Mac available)
- Set up Android emulator
- Review React Native best practices

**Week 7 Prep:**
- Research OCR tools (Google Cloud Vision vs Tesseract)
- Identify DBE paper sources
- Recruit educators for digitization
- Prepare import script templates

---

**Last Updated:** 2025-01-19
**Document Version:** 1.0
**Current Phase:** Phase 1 - GSD Framework Setup
**Current Week:** Week 1 (Jan 20-26, 2025)
**Next Milestone:** M1.2 - Workflow Validation
