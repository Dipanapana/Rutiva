# Rutiva - Project Documentation

> Your roadmap to results. CAPS-aligned study guides for South African learners.

**Repository:** https://github.com/Dipanapana/Rutiva

## Project Vision

Rutiva is a comprehensive EdTech platform designed to empower South African learners (grades 6-12) with:
- CAPS-aligned study guides and resources
- Personalized study timetables
- AI-powered tutoring assistance
- Comprehensive past question papers for practice
- Accessible through both web and mobile platforms

**Mission:** Make quality education accessible to every South African learner through technology.

**Target Market:**
- Individual learners (grades 6-12)
- Parents monitoring children's education
- Schools (bulk licensing)
- Educators

---

## Tech Stack

### Frontend

**Web Application:**
- **Framework:** Next.js 14.2 (React 18)
- **Language:** TypeScript
- **Styling:** Tailwind CSS + custom theme system
- **Animation:** Framer Motion
- **State Management:** Zustand
- **Data Fetching:** TanStack React Query
- **Forms:** React Hook Form + Zod validation
- **HTTP Client:** Axios (with token refresh interceptors)
- **Icons:** Lucide Icons
- **Monorepo Location:** `apps/web/`

**Mobile Application (React Native):**
- **Framework:** React Native with Expo
- **Language:** TypeScript
- **Navigation:** React Navigation v6 (Expo Router)
- **State Management:** Zustand (consistency with web)
- **UI Library:** React Native Paper + NativeWind
- **Forms:** React Hook Form + Zod (consistency with web)
- **HTTP Client:** Axios (shared with web)
- **PDF Viewer:** react-native-pdf
- **Storage:** AsyncStorage
- **Notifications:** Expo Notifications
- **Monorepo Location:** `apps/mobile/`

### Backend

**API Server:**
- **Framework:** FastAPI (Python async framework)
- **Server:** Uvicorn (ASGI)
- **Language:** Python 3.11+
- **Database ORM:** SQLAlchemy 2.0 (async)
- **Database Driver:** asyncpg (PostgreSQL)
- **Migrations:** Alembic
- **Authentication:** JWT (access + refresh tokens)
- **Password Hashing:** Bcrypt
- **Validation:** Pydantic v2
- **Monorepo Location:** `backend/`

**Database:**
- **Primary Database:** PostgreSQL 15+
- **Caching:** Redis
- **Connection Pooling:** asyncpg built-in

**AI Integration:**
- **Providers:** OpenAI GPT-4, DeepSeek
- **Use Cases:**
  - RutivaBot AI tutor
  - Question explanations
  - Weak area analysis
  - Similar question generation

**Content Delivery:**
- **Storage:** AWS S3 (af-south-1 region)
- **Bucket:** `rutiva-content`
- **CDN:** S3 direct access (CloudFront optional)
- **Content Types:** PDF study guides, images, answer keys

**Payment Processing:**
- **Providers:** PayFast (primary), Yoco, EFT
- **Integration:** Server-side webhooks + client-side redirects

### Infrastructure

**Monorepo Management:**
- **Tool:** Turbo v2.0
- **Package Manager:** npm workspaces
- **Build System:** Parallel builds with caching

**Development:**
- **Local Frontend:** http://localhost:3000 (web)
- **Local Backend:** http://localhost:8000 (API)
- **Local Database:** PostgreSQL on localhost:5432
- **Local Cache:** Redis on localhost:6379

**Deployment (Production):**
- **Web:** Vercel / Netlify (recommended for Next.js)
- **Backend:** AWS EC2 / DigitalOcean / Railway
- **Database:** AWS RDS PostgreSQL / Managed PostgreSQL
- **Redis:** AWS ElastiCache / Upstash
- **Storage:** AWS S3
- **Domain:** rutiva.co.za

---

## Architecture Overview

### System Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Web Browser   │         │  Mobile App      │
│   (Next.js)     │         │  (React Native)  │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │    HTTPS/REST API         │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │   FastAPI Backend      │
         │   (Uvicorn ASGI)       │
         └───────────┬────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌───▼────┐
   │   DB    │  │ Redis  │  │  AWS   │
   │ (PG)    │  │ Cache  │  │   S3   │
   └─────────┘  └────────┘  └────────┘
```

### Monorepo Structure

```
ruta/ (to be renamed: rutiva/)
├── apps/
│   ├── web/                 # Next.js web application
│   └── mobile/              # React Native mobile app
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API routes
│   │   ├── core/           # Config, database, security
│   │   ├── models/         # SQLAlchemy models
│   │   └── services/       # Business logic
│   └── alembic/            # Database migrations
├── packages/
│   └── shared/             # Shared utilities (future)
├── content/                # Sample content and schemas
├── PROJECT.md              # This file
├── REQUIREMENTS.md         # Feature specifications
├── ROADMAP.md             # Implementation timeline
├── STATE.md               # Current state tracker
├── ARCHITECTURE.md        # Detailed system design
├── package.json           # Root workspace config
└── turbo.json            # Turbo build configuration
```

### API Design

**Base URL:** `/api/v1/`

**Authentication:**
- JWT-based with access tokens (15min expiry) and refresh tokens (7 days)
- Header: `Authorization: Bearer <access_token>`
- Auto-refresh via Axios interceptors on 401 responses

**API Modules:**
- `/auth` - Authentication (login, register, OTP, password reset)
- `/products` - Product catalog, bundles, subjects
- `/cart` - Shopping cart management
- `/checkout` - Order processing
- `/library` - User's purchased content
- `/timetables` - Personalized study schedules
- `/chat` - AI tutor interactions
- `/users` - User profile and stats
- `/questions` - Past question papers (Phase 4)
- `/practice` - Practice sessions and analytics (Phase 4)

**Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message",
  "error": null
}
```

### Database Design

**Core Tables:**
- `users` - User accounts with roles (student, parent, school_admin, super_admin)
- `subjects` - CAPS curriculum subjects
- `products` - Individual study guides (grade + subject + term)
- `bundles` - Product packages
- `orders` - Purchase records
- `order_items` - Line items
- `user_library` - Purchased content per user
- `promo_codes` - Discount codes
- `timetables` - Generated study schedules
- `timetable_progress` - Session tracking
- `tutor_subscriptions` - AI tutor plans
- `chat_sessions` - Conversation threads
- `chat_messages` - Individual messages
- `schools` - School records
- `school_licenses` - Bulk licenses

**Future (Phase 4):**
- `question_papers` - Past exam papers
- `questions` - Individual questions
- `question_options` - MCQ choices
- `user_question_attempts` - Practice tracking
- `practice_sessions` - Practice session metadata

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete schema diagrams.

---

## Development Workflow

### Local Setup

**Prerequisites:**
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 15+
- Redis
- AWS CLI (for S3 access)

**First-Time Setup:**
```bash
# Clone repository
git clone <repository-url>
cd ruta  # Will be renamed to rutiva

# Install dependencies
npm install

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up database
createdb rutiva
cp .env.example .env  # Edit with your credentials
alembic upgrade head

# Return to root and start development
cd ..
npm run dev  # Starts both web and backend via Turbo
```

**Environment Variables:**
- Web: `apps/web/.env.local` (NEXT_PUBLIC_API_URL, NEXT_PUBLIC_APP_URL)
- Backend: `backend/.env` (DATABASE_URL, SECRET_KEY, AWS credentials, etc.)
- See `.env.example` files for complete variable lists

### Running the Application

**Development:**
```bash
# All services (uses Turbo)
npm run dev

# Individual services
cd apps/web && npm run dev        # Web on :3000
cd backend && uvicorn app.main:app --reload  # API on :8000
```

**Building:**
```bash
npm run build  # Build all apps
```

**Testing:**
```bash
# Backend tests
cd backend && pytest

# Frontend tests (when added)
cd apps/web && npm test
```

### Database Migrations

**Create Migration:**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

**Apply Migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1  # Go back one migration
```

---

## Git Workflow

### Branch Strategy

**Main Branches:**
- `main` - Production-ready code
- `develop` - Integration branch for features

**Feature Branches:**
- Format: `feature/phase-X-task-name`
- Example: `feature/phase-2-rebrand-config`

**Workflow:**
1. Create feature branch from `develop`
2. Make atomic commits (see below)
3. Open PR to `develop`
4. Code review
5. Merge to `develop`
6. Periodic releases from `develop` → `main`

### Commit Message Format

**Structure:** `[PHASE-TASK] Brief description`

**Examples:**
```
[P1-DOCS] Create PROJECT.md with tech stack
[P2-REBRAND-CONFIG] Update backend config to Rutiva
[P3-MOBILE-AUTH] Implement login screen
[P4-QUESTIONS-API] Add question papers endpoint
```

**Atomic Commits:**
- One logical change per commit
- Each commit should be reversible
- Commit early and often
- Include Co-Authored-By for AI pair programming:
  ```
  [P2-REBRAND-FOOTER] Update footer branding

  Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
  ```

### Code Review Guidelines

**Before Requesting Review:**
- [ ] Code follows project conventions
- [ ] No console.log or debug statements
- [ ] TypeScript types are complete
- [ ] Error handling implemented
- [ ] Tests pass (when test suite exists)
- [ ] No security vulnerabilities (SQL injection, XSS, etc.)

**Review Checklist:**
- [ ] Code is readable and maintainable
- [ ] No over-engineering (KISS principle)
- [ ] Edge cases handled
- [ ] Performance considerations addressed
- [ ] Database indexes added where needed

---

## Team Conventions

### Code Style

**TypeScript/JavaScript:**
- ESLint + Prettier (configured in each app)
- 2-space indentation
- Single quotes for strings
- No semicolons (Prettier handles this)
- Functional components with hooks
- Descriptive variable names (no abbreviations)

**Python:**
- PEP 8 compliance
- 4-space indentation
- Type hints for function signatures
- Async/await for I/O operations
- Descriptive variable names

### File Naming

**Frontend:**
- Components: PascalCase (`ProductCard.tsx`)
- Pages: kebab-case (`product-detail.tsx`)
- Utilities: camelCase (`apiClient.ts`)
- Types: PascalCase (`UserTypes.ts`)

**Backend:**
- Modules: snake_case (`ai_service.py`)
- Classes: PascalCase (`UserModel`)
- Functions: snake_case (`get_user_by_id()`)

### Component Organization

**Frontend Components:**
```tsx
// 1. Imports (external, then internal)
import { useState } from 'react'
import { Button } from '@/components/ui/Button'

// 2. Types/Interfaces
interface ProductCardProps {
  product: Product
  onAddToCart: () => void
}

// 3. Component
export function ProductCard({ product, onAddToCart }: ProductCardProps) {
  // Hooks
  const [loading, setLoading] = useState(false)

  // Handlers
  const handleClick = () => {
    setLoading(true)
    onAddToCart()
  }

  // Render
  return (
    <div className="...">
      {/* Component JSX */}
    </div>
  )
}
```

**Backend Endpoints:**
```python
@router.get("/products/{sku}")
async def get_product(
    sku: str,
    db: AsyncSession = Depends(get_db)
) -> ProductResponse:
    """
    Get product by SKU.

    Args:
        sku: Product SKU
        db: Database session

    Returns:
        ProductResponse with product details

    Raises:
        HTTPException: 404 if product not found
    """
    # Implementation
```

### Security Best Practices

**Never Commit:**
- API keys, secrets, passwords
- `.env` files (only `.env.example`)
- Database credentials
- AWS access keys

**Always:**
- Use environment variables for secrets
- Validate user input (Zod on frontend, Pydantic on backend)
- Sanitize database queries (use ORM, not raw SQL)
- Hash passwords with bcrypt
- Use HTTPS in production
- Implement rate limiting
- Add CORS restrictions
- Validate JWT tokens

### Performance Guidelines

**Frontend:**
- Lazy load routes and components
- Use React Query for caching
- Optimize images (Next.js Image component)
- Minimize bundle size (code splitting)
- Use memoization sparingly (profile first)

**Backend:**
- Use database indexes on filtered/sorted columns
- Batch database queries where possible
- Cache frequent read operations in Redis
- Paginate list endpoints
- Use async/await for I/O
- Profile slow endpoints

---

## Context Management (GSD Framework)

### Main Session Context Target: 30-40%

**Strategies:**
1. **Reference Documentation:**
   - "As per PROJECT.md, the tech stack uses Next.js 14..."
   - "According to ARCHITECTURE.md, the User model includes..."

2. **Use STATE.md for Progress:**
   - "Per STATE.md, Phase 1 tasks 1-3 are complete..."
   - Update STATE.md after every task completion

3. **Link to ROADMAP.md:**
   - "ROADMAP.md Phase 2 timeline indicates this task is week 2..."

4. **Modular Tasks:**
   - Break work into atomic, single-conversation tasks
   - Each task = one commit = one conversation

5. **Handoff Protocol:**
   - End of session: Update STATE.md with progress
   - Clearly identify next task
   - Document any blockers or decisions needed

### Multi-Agent Orchestration

**When to Use Subagents:**
- Research tasks (Explore agent for codebase understanding)
- Planning tasks (Plan agent for implementation strategy)
- Complex multi-step implementations (General-purpose agent)

**Keep Main Context For:**
- Task execution
- Code reviews
- Documentation updates
- Quick fixes

### Get-Shit-Done CLI Commands

**Installation:** ✅ Installed locally at `./.claude/` (v1.6.4)

The GSD framework provides workflow commands for Claude Code:

**Core Commands:**
- `/gsd:help` - Show available commands
- `/gsd:new-project` - Full project initialization (questions, research, requirements)
- `/gsd:discuss-phase [N]` - Capture implementation decisions before planning
- `/gsd:plan-phase [N]` - Research, create task plans, verify them
- `/gsd:execute-phase [N]` - Run plans in parallel waves with fresh context
- `/gsd:verify-work [N]` - User acceptance testing with diagnostics
- `/gsd:complete-milestone` - Archive and tag releases
- `/gsd:new-milestone` - Begin next version cycle

**Benefits:**
- Fresh 200k-token contexts per execution (prevents quality degradation)
- XML-formatted task definitions with verification steps
- Atomic git commits per task
- Multi-agent orchestration (parallel researchers, planners, executors)

**Usage:**
```bash
# In Claude Code CLI
/gsd:help                    # View all commands
/gsd:discuss-phase 2         # Discuss Phase 2 (Rebrand) decisions
/gsd:plan-phase 2            # Plan Phase 2 tasks
/gsd:execute-phase 2         # Execute Phase 2 plan
```

**Status:**
- Phase 1 (GSD Setup): ✅ Complete (manual documentation creation)
- Phase 2 onwards: Will use GSD commands for structured workflow

---

## Deployment

### Production Checklist

**Pre-Deployment:**
- [ ] All tests pass
- [ ] No console errors
- [ ] Environment variables set in production
- [ ] Database migrations applied
- [ ] S3 bucket configured with CORS
- [ ] SSL certificate installed
- [ ] DNS records updated
- [ ] Rate limiting configured
- [ ] Monitoring/logging set up (Sentry, LogRocket, etc.)

**Post-Deployment:**
- [ ] Smoke tests on production URLs
- [ ] Payment flow tested
- [ ] Email delivery verified
- [ ] S3 file access confirmed
- [ ] Database performance acceptable
- [ ] Error tracking active

### Rollback Procedure

**If Critical Issues:**
1. Revert to previous git tag/commit
2. Rollback database migration: `alembic downgrade -1`
3. Clear Redis cache if needed
4. Redeploy previous version
5. Investigate issue in development
6. Document in STATE.md

---

## Resources

**Documentation:**
- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Expo Docs](https://docs.expo.dev/)

**Internal Docs:**
- [REQUIREMENTS.md](REQUIREMENTS.md) - Feature specifications
- [ROADMAP.md](ROADMAP.md) - Implementation timeline
- [STATE.md](STATE.md) - Current progress
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed system design

**External Services:**
- AWS Console: https://console.aws.amazon.com
- PayFast Developer: https://developers.payfast.co.za
- Yoco Developer: https://developer.yoco.com

---

## Getting Help

**Questions About:**
- Architecture/Design → Review ARCHITECTURE.md, ask team lead
- Requirements → Check REQUIREMENTS.md
- Current State → Consult STATE.md
- Timeline → Reference ROADMAP.md

**Bug Reports:**
- Document in GitHub Issues
- Include steps to reproduce
- Tag with severity (critical, high, medium, low)

**Feature Requests:**
- Discuss with team lead
- Document in REQUIREMENTS.md if approved
- Update ROADMAP.md with timeline

---

## License

Proprietary - Rutiva Education © 2025

---

**Last Updated:** 2025-01-19
**Current Phase:** Phase 1 - GSD Framework Setup
**Next Milestone:** Complete documentation, begin Phase 2 rebrand
