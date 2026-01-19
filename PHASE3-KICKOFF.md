# Phase 3: React Native Mobile App - Kickoff

**Status:** In Progress
**Started:** 2026-01-20
**Expected Duration:** 4 weeks
**Dependencies:** Phase 2 Complete ✓

---

## What We're Building

A production-ready **React Native mobile app** for both iOS and Android that provides 95%+ feature parity with the Rutiva web application.

**Why React Native + Expo:**
- Single codebase for iOS and Android
- Faster development with Expo managed workflow
- Hot reload for instant feedback
- Access to native features (camera, notifications, etc.)
- Large ecosystem and community support
- Easy deployment to app stores

---

## Phase 3 Timeline

### Week 3 (Current): Foundation & Authentication
**Goal:** Get the app running with complete auth system

**Tasks:**
1. ✓ Create Phase 3 context document
2. 🔄 Initialize Expo project with TypeScript
3. ⏳ Set up navigation (Expo Router)
4. ⏳ Create shared lib (API client, Zustand stores)
5. ⏳ Build UI component library
6. ⏳ Implement auth screens (login, register, OTP, password reset)
7. ⏳ Add auth persistence (AsyncStorage)

**Deliverable:** Users can register, verify OTP, login, and stay logged in

### Week 4: E-Commerce
**Goal:** Complete shopping experience

**Features:**
- Product catalog with filters (grade, subject, term)
- Search functionality
- Product details
- Shopping cart
- Promo codes
- Checkout flow
- Payment WebView (PayFast/Yoco)
- Order confirmation

**Deliverable:** Users can browse, add to cart, and purchase study guides

### Week 5: Study Features
**Goal:** Library and timetables fully functional

**Features:**
- User library (purchased guides)
- PDF viewer with offline download
- Create study timetables
- Timetable progress tracking
- Calendar integration
- iCal export

**Deliverable:** Users can access content and manage their study schedule

### Week 6: AI Tutor, Profile & Polish
**Goal:** Complete app ready for beta testing

**Features:**
- AI tutor chat interface
- User profile and settings
- Push notifications (optional)
- App icons and splash screen
- Loading states and error handling
- Performance optimization
- E2E tests

**Deliverable:** Production-ready app submitted to TestFlight and Google Play Internal Testing

---

## Tech Stack Summary

**Framework:** Expo (React Native managed workflow)
**Language:** TypeScript
**Navigation:** Expo Router (file-based routing)
**State:** Zustand (same as web)
**Styling:** NativeWind (Tailwind for React Native)
**UI Components:** React Native Paper + custom components
**Forms:** React Hook Form + Zod (same as web)
**API Client:** Axios (same as web)
**PDF Viewer:** react-native-pdf
**Storage:** AsyncStorage + expo-file-system
**Notifications:** Expo Notifications

**Why these choices:**
- Maximum consistency with web application
- Proven, well-maintained libraries
- Team familiarity (Zustand, React Hook Form, Zod, Axios)
- Good developer experience

---

## What's Being Set Up Now

### 1. Expo Project Initialization ✓
```bash
npx create-expo-app@latest mobile --template blank-typescript
```

This creates:
- TypeScript configuration
- Basic Expo app structure
- Default App.tsx entry point
- Package.json with Expo dependencies

### 2. Project Structure (To Be Created)
```
apps/mobile/
├── app/                    # Expo Router pages
│   ├── (auth)/            # Login, register, OTP
│   ├── (tabs)/            # Main app (5 tabs)
│   ├── _layout.tsx        # Root layout
│   └── +not-found.tsx
├── components/            # Reusable UI
│   ├── ui/                # Base components
│   ├── product/           # Product components
│   ├── cart/              # Cart components
│   ├── timetable/         # Timetable components
│   └── chat/              # AI tutor components
├── lib/                   # Shared logic
│   ├── api.ts             # API client
│   ├── store/             # Zustand stores
│   ├── hooks/             # Custom hooks
│   └── utils/             # Utilities
├── assets/                # Images, fonts
└── constants/             # Config, colors
```

### 3. Dependencies (To Be Installed)
```json
{
  "dependencies": {
    "expo": "~52.0.0",
    "expo-router": "~4.0.0",
    "react-native-paper": "^5.12.0",
    "zustand": "^5.0.0",
    "axios": "^1.7.0",
    "react-hook-form": "^7.54.0",
    "zod": "^3.24.0",
    "@hookform/resolvers": "^3.9.0",
    "react-native-pdf": "^6.7.0",
    "nativewind": "^4.0.0"
  }
}
```

---

## Backend Extensions Needed

### New Endpoints (Week 6)
1. **Device Registration** - Push notification tokens
2. **Notification Settings** - User preferences
3. **App Version Check** - Force update mechanism
4. **Offline Sync** - Downloadable content tracking

### Database Changes (Week 6)
1. **user_devices table** - Store device tokens
2. **notification_settings column** - User preferences

**Note:** These are not blocking for Weeks 3-5. We can build the mobile app using existing API endpoints.

---

## Development Workflow

### Daily Development
```bash
# Start Expo dev server
cd apps/mobile
npm start

# Scan QR code with Expo Go app
# Changes hot-reload instantly
```

### Testing Strategy
1. **Expo Go** (Daily) - Quick iteration on physical devices
2. **Development Builds** (Weekly) - Test native features
3. **E2E Tests** (Before release) - Detox testing
4. **Manual Testing** - Various devices and scenarios

### Git Workflow
**Commit Format:** `[P3-M{milestone}-{FEATURE}] Description`

Examples:
- `[P3-M1-AUTH] Implement login screen`
- `[P3-M2-SHOP] Add product filtering`
- `[P3-M3-LIB] Implement PDF viewer`
- `[P3-M4-POLISH] Add app icons`

---

## Success Metrics

### Week 3 (Foundation)
- [ ] App runs on both iOS and Android
- [ ] Navigation works smoothly
- [ ] Complete auth flow functional
- [ ] Auth persists across restarts

### Week 4 (E-Commerce)
- [ ] Can browse all products
- [ ] Cart operations work
- [ ] Payments complete successfully
- [ ] Orders created correctly

### Week 5 (Study Features)
- [ ] PDFs viewable and downloadable
- [ ] Timetables creatable
- [ ] Progress tracking works
- [ ] Calendar integration functional

### Week 6 (Polish)
- [ ] AI chat works
- [ ] < 5% crash rate in testing
- [ ] App launch < 3 seconds
- [ ] Ready for app store submission

### Overall Phase 3
- [ ] **95%+ feature parity** with web
- [ ] **All critical flows** tested
- [ ] **Positive beta tester** feedback
- [ ] **App store compliant**

---

## What You Can Do Now

### Option 1: Watch the Setup (Passive)
The Expo project is initializing in the background. Once complete:
- I'll set up the project structure
- Install dependencies
- Create base components
- Implement first auth screen

### Option 2: Review Documentation (Active)
While setup runs, review:
- [3-CONTEXT.md](3-CONTEXT.md) - Complete Phase 3 plan
- [ROADMAP.md](ROADMAP.md) - Overall project timeline
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

### Option 3: Plan Ahead (Collaborative)
Questions to consider:
- Do you want push notifications in v1?
- Should we support offline mode from the start?
- Any mobile-specific features not on web?
- Color scheme adjustments for mobile?

---

## Next Immediate Steps

Once Expo initialization completes:

1. **Install Expo Router** - File-based navigation
2. **Set up folder structure** - app/, components/, lib/
3. **Create API client** - Reuse Axios config from web
4. **Set up Zustand stores** - Auth, cart, library, chat
5. **Build base UI components** - Button, Input, Card
6. **Implement login screen** - First functional screen
7. **Test on physical device** - Verify everything works

**Estimated setup time:** 30-45 minutes
**First functional screen:** 2-3 hours

---

## Questions or Issues?

**Common Setup Issues:**

1. **"Expo command not found"**
   - Solution: `npm install -g expo-cli`

2. **"Unable to scan QR code"**
   - Solution: Ensure phone and computer on same network

3. **"Metro bundler crashes"**
   - Solution: Clear cache with `npx expo start -c`

4. **"TypeScript errors"**
   - Solution: Run `npm install --save-dev @types/react @types/react-native`

**Need Help:**
- Check Expo docs: https://docs.expo.dev
- React Native docs: https://reactnative.dev
- Ask me for clarification on any step

---

**Status:** Expo initialization in progress...
**Next Update:** When project is ready for development

---

**Created:** 2026-01-20
**Last Updated:** 2026-01-20
**Phase:** 3 - Mobile App Development
