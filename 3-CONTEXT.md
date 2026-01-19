# Phase 3: React Native Mobile App - Implementation Context

**Phase:** 3 - React Native Mobile App
**Created:** 2026-01-20
**Status:** Ready to Start
**Dependencies:** Phase 2 Complete ✓

---

## Phase Overview

**Goal:** Build production-ready React Native mobile app with 95%+ feature parity to the web application.

**Timeline:** 4 weeks (Weeks 3-6)

**Scope:**
- Full-featured iOS and Android mobile app
- Authentication and user management
- E-commerce (product browsing, cart, checkout, payments)
- User library with PDF viewing and offline downloads
- Study timetables with calendar integration
- AI tutor chat interface
- User profile and settings
- Push notifications (optional)
- App store deployment preparation

---

## Tech Stack Decisions

### Core Framework
**Decision:** ✅ **Expo (managed workflow)**

**Rationale:**
- Faster development with managed workflow
- Built-in support for common features (camera, notifications, etc.)
- Over-the-air (OTA) updates
- Easier setup compared to bare React Native
- Can eject to bare workflow if needed later
- Excellent TypeScript support

**Alternative Considered:** Bare React Native
- Rejected: More complex setup, harder to maintain
- May revisit if we need custom native modules

### Navigation
**Decision:** ✅ **Expo Router (file-based routing)**

**Rationale:**
- File-based routing similar to Next.js (consistency)
- Built on React Navigation under the hood
- Automatic deep linking
- Type-safe navigation
- Simpler than manual React Navigation setup

### State Management
**Decision:** ✅ **Zustand** (same as web)

**Rationale:**
- Consistency with web application
- Lightweight and simple
- Works perfectly with React Native
- Team already familiar with it

### UI Components
**Decision:** ✅ **React Native Paper + Custom Components**

**Rationale:**
- React Native Paper provides Material Design components
- Customizable to match Rutiva branding
- Good accessibility support
- Will build custom components where needed

**Alternative:** NativeBase, React Native Elements
- Rejected: Heavier, less flexible

### Styling
**Decision:** ✅ **NativeWind** (Tailwind CSS for React Native)

**Rationale:**
- Tailwind-like utility classes
- Consistency with web styling approach
- Responsive design utilities
- Theme support

**Alternative:** Styled Components, StyleSheet
- Will use StyleSheet for complex/performance-critical components

### Forms
**Decision:** ✅ **React Hook Form + Zod** (same as web)

**Rationale:**
- Consistency with web
- Excellent performance
- TypeScript validation with Zod
- Less re-renders than Formik

### API Client
**Decision:** ✅ **Axios** (same as web)

**Rationale:**
- Consistency with web
- Reuse API configuration
- Interceptors for auth tokens
- Better error handling than fetch

### PDF Viewing
**Decision:** ✅ **react-native-pdf**

**Rationale:**
- Well-maintained library
- Good performance
- Offline support
- iOS and Android support

### Offline Storage
**Decision:** ✅ **AsyncStorage**

**Rationale:**
- Built into Expo
- Simple key-value storage
- Perfect for auth tokens, settings
- Will use expo-file-system for PDF caching

### Push Notifications
**Decision:** ✅ **Expo Notifications**

**Rationale:**
- Built into Expo
- Cross-platform
- Easy setup
- Backend integration ready

---

## Project Structure

```
apps/mobile/
├── app/                      # Expo Router pages
│   ├── (auth)/              # Auth group (login, register, otp)
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   ├── verify-otp.tsx
│   │   └── reset-password.tsx
│   ├── (tabs)/              # Main app tabs
│   │   ├── _layout.tsx      # Tab navigator
│   │   ├── index.tsx        # Shop/Home
│   │   ├── library.tsx      # User library
│   │   ├── study.tsx        # Timetables
│   │   ├── tutor.tsx        # AI chat
│   │   └── profile.tsx      # User profile
│   ├── cart.tsx             # Shopping cart (modal)
│   ├── product/[id].tsx     # Product details
│   ├── timetable/[id].tsx   # Timetable details
│   ├── _layout.tsx          # Root layout
│   └── +not-found.tsx       # 404 page
├── components/              # Reusable components
│   ├── ui/                  # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Loading.tsx
│   │   └── ErrorBoundary.tsx
│   ├── product/             # Product components
│   │   ├── ProductCard.tsx
│   │   ├── ProductList.tsx
│   │   └── ProductFilters.tsx
│   ├── cart/                # Cart components
│   │   ├── CartItem.tsx
│   │   └── CartSummary.tsx
│   ├── timetable/           # Timetable components
│   │   ├── TimetableCard.tsx
│   │   ├── SessionItem.tsx
│   │   └── CalendarView.tsx
│   └── chat/                # AI tutor components
│       ├── ChatMessage.tsx
│       ├── ChatInput.tsx
│       └── SessionList.tsx
├── lib/                     # Shared logic
│   ├── api.ts              # API client (Axios instance)
│   ├── store/              # Zustand stores
│   │   ├── auth.ts         # Auth store
│   │   ├── cart.ts         # Cart store
│   │   ├── library.ts      # Library store
│   │   └── chat.ts         # Chat store
│   ├── hooks/              # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useProducts.ts
│   │   └── useTimetable.ts
│   └── utils/              # Utility functions
│       ├── format.ts
│       ├── validation.ts
│       └── storage.ts
├── assets/                  # Images, fonts, etc.
│   ├── images/
│   ├── fonts/
│   └── icons/
├── constants/               # Constants
│   ├── Colors.ts
│   ├── Sizes.ts
│   └── Config.ts
├── app.json                 # Expo config
├── package.json
├── tsconfig.json
└── .env.local              # Environment variables
```

---

## Feature Parity Matrix

### Must Have (95% Parity)

**Authentication:**
- ✅ User registration with OTP
- ✅ Login with email/password
- ✅ Password reset
- ✅ Parent account linking
- ✅ Session persistence

**E-Commerce:**
- ✅ Browse products (filter by grade, subject, term)
- ✅ Search products
- ✅ Product details
- ✅ Shopping cart
- ✅ Apply promo codes
- ✅ Checkout flow
- ✅ Payment integration (PayFast/Yoco WebView)
- ✅ Order history

**User Library:**
- ✅ View purchased guides
- ✅ PDF viewer
- ✅ Offline PDF downloads
- ✅ Progress tracking

**Study Timetables:**
- ✅ Create timetable
- ✅ View timetables
- ✅ Mark sessions complete
- ✅ Track progress
- ✅ Calendar view
- ✅ Export to iCal

**AI Tutor:**
- ✅ Chat interface
- ✅ Session history
- ✅ Subscription status
- ✅ Usage limits

**User Profile:**
- ✅ View profile
- ✅ Edit profile
- ✅ View stats
- ✅ Logout

### Nice to Have (Optional)

**Enhanced Features:**
- ⏳ Push notifications (timetable reminders)
- ⏳ Offline mode for purchased content
- ⏳ Dark mode
- ⏳ Share study progress with parents
- ⏳ In-app purchase restore

### Web-Only Features (Not on Mobile)

**Admin/Complex Features:**
- ❌ School admin dashboard (web only)
- ❌ Bulk license management (web only)
- ❌ Complex analytics dashboards (web only)

---

## Backend API Extensions Needed

### New Endpoints

**1. Device Management**
```python
# Register device for push notifications
POST /api/v1/users/devices
{
  "device_token": "ExponentPushToken[xxx]",
  "platform": "ios" | "android",
  "app_version": "1.0.0"
}

# Update device
PATCH /api/v1/users/devices/{device_id}

# Remove device
DELETE /api/v1/users/devices/{device_id}
```

**2. Notification Settings**
```python
# Get notification preferences
GET /api/v1/users/me/notification-settings

# Update preferences
PATCH /api/v1/users/me/notification-settings
{
  "timetable_reminders": true,
  "new_content": false,
  "marketing": false
}
```

**3. App Version Check**
```python
# Check if app update required
GET /api/v1/app/version
Response: {
  "current_version": "1.0.0",
  "minimum_version": "1.0.0",
  "update_required": false,
  "update_url": "https://..."
}
```

**4. Offline Content Sync**
```python
# Get list of downloadable content
GET /api/v1/users/me/library/downloadable

# Mark content as downloaded (for analytics)
POST /api/v1/users/me/library/{product_id}/download
```

### Database Changes

**New Table: user_devices**
```sql
CREATE TABLE user_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  device_token VARCHAR(500) NOT NULL,
  platform VARCHAR(10) NOT NULL CHECK (platform IN ('ios', 'android')),
  app_version VARCHAR(20),
  last_active_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(device_token)
);

CREATE INDEX idx_user_devices_user_id ON user_devices(user_id);
CREATE INDEX idx_user_devices_platform ON user_devices(platform);
```

**Update users table:**
```sql
ALTER TABLE users
ADD COLUMN notification_settings JSONB DEFAULT '{
  "timetable_reminders": true,
  "new_content": true,
  "marketing": false,
  "email_notifications": true,
  "push_notifications": true
}'::jsonb;
```

---

## Development Workflow

### Setup Checklist

- [ ] Initialize Expo project
- [ ] Set up TypeScript configuration
- [ ] Install dependencies (React Navigation, Zustand, NativeWind, etc.)
- [ ] Configure Expo Router
- [ ] Set up environment variables (.env.local)
- [ ] Create API client with auth interceptors
- [ ] Set up Zustand stores
- [ ] Create base UI components
- [ ] Configure app icons and splash screen

### Development Process

**1. Start with Expo Go (fastest iteration):**
```bash
cd apps/mobile
npm install
npx expo start
```

**2. Test on physical devices:**
- Install Expo Go app on iOS/Android
- Scan QR code to run app
- Instant reload on code changes

**3. Build development builds (when needed):**
```bash
# For features not supported by Expo Go
eas build --profile development --platform ios
eas build --profile development --platform android
```

**4. Testing strategy:**
- Manual testing on Expo Go (daily)
- Development builds for native features (weekly)
- E2E tests with Detox (before releases)

### Atomic Commits

Follow same pattern as Phase 2:
```
[P3-M1-AUTH] Implement login screen
[P3-M2-SHOP] Add product listing
[P3-M3-LIB] Implement PDF viewer
etc.
```

**Commit Format:**
- `[P3-M{milestone}-{FEATURE}] Description`
- M1 = Foundation & Auth
- M2 = E-Commerce
- M3 = Study Features
- M4 = AI Tutor & Polish

---

## Testing Strategy

### Unit Tests
- Use Jest (built into Expo)
- Test utility functions, hooks
- Test Zustand store logic

### Component Tests
- React Testing Library for React Native
- Test UI components in isolation
- Mock API calls

### E2E Tests
- Detox for end-to-end testing
- Test critical flows:
  - Registration → OTP → Login
  - Browse → Add to cart → Checkout
  - View library → Open PDF
  - Create timetable → Mark session complete
  - Chat with AI tutor

### Manual Testing
- Test on multiple devices (iPhone SE, Pro Max, Android small/large)
- Test offline scenarios
- Test slow network conditions
- Test interruptions (phone calls, notifications)

---

## Deployment Strategy

### Beta Testing (Week 5-6)

**iOS TestFlight:**
1. Set up Apple Developer account
2. Create app in App Store Connect
3. Build with `eas build --platform ios`
4. Upload to TestFlight
5. Invite beta testers (10-20 users)

**Android Internal Testing:**
1. Set up Google Play Console
2. Build AAB: `eas build --platform android`
3. Upload to Internal Testing track
4. Invite beta testers

### Production Release (Post-Phase 3)

**App Store Submission Checklist:**
- [ ] App icons (all sizes)
- [ ] Screenshots (all device sizes)
- [ ] App description (Rutiva branding)
- [ ] Privacy policy URL
- [ ] Terms of service URL
- [ ] Support email (hello@rutiva.co.za)
- [ ] Age rating
- [ ] Categories (Education, Study Tools)

---

## Performance Targets

**App Launch:**
- Initial launch: < 3 seconds
- Subsequent launches: < 1.5 seconds

**Screen Transitions:**
- Navigation: < 300ms
- Animations: 60fps

**Memory:**
- Idle: < 100MB
- Active usage: < 200MB

**Bundle Size:**
- iOS IPA: < 50MB
- Android APK: < 30MB

**API Response Handling:**
- Show loading state within 100ms
- Timeout after 30 seconds
- Retry failed requests (3 attempts)

---

## Risk Mitigation

### High-Risk Areas

**1. PDF Viewing on Mobile**
- Risk: Large PDFs may crash app
- Mitigation: Implement pagination, limit file size, test with large files

**2. Payment Integration**
- Risk: WebView may have issues on different devices
- Mitigation: Thorough testing, fallback to browser for payment

**3. Offline Support**
- Risk: Sync conflicts when coming back online
- Mitigation: Simple conflict resolution (server wins), clear user feedback

**4. Push Notifications**
- Risk: Device token management, platform differences
- Mitigation: Use Expo's notification API, robust error handling

**5. App Store Rejection**
- Risk: Guidelines violations
- Mitigation: Review guidelines early, test thoroughly, prepare for iterations

---

## Success Criteria

### Milestone 1 (Week 3) - Foundation & Auth
- [ ] Expo app runs on iOS and Android
- [ ] Users can register with email + OTP
- [ ] Users can login and logout
- [ ] Auth persists across app restarts
- [ ] Basic UI components working

### Milestone 2 (Week 4) - E-Commerce
- [ ] Products browsable with filters
- [ ] Shopping cart functional
- [ ] Checkout flow works
- [ ] Payments process successfully
- [ ] Orders created in database

### Milestone 3 (Week 5) - Study Features
- [ ] Library shows purchased content
- [ ] PDFs viewable on device
- [ ] Timetables creatable
- [ ] Sessions trackable
- [ ] Progress displays correctly

### Milestone 4 (Week 6) - AI & Polish
- [ ] AI chat functional
- [ ] Profile editable
- [ ] App icons and splash screen
- [ ] Error handling robust
- [ ] Performance meets targets
- [ ] Ready for TestFlight/Internal Testing

### Overall Phase 3 Success
- [ ] 95%+ feature parity with web
- [ ] < 5% crash rate in beta
- [ ] All critical flows tested
- [ ] Positive beta tester feedback
- [ ] App store ready

---

## Out of Scope for Phase 3

**Deferred to Post-Launch:**
- ❌ iPad-specific UI
- ❌ Tablet optimization
- ❌ Apple Watch companion app
- ❌ Widget support
- ❌ Siri shortcuts
- ❌ Advanced offline sync
- ❌ Video content support

---

## Next Steps

1. **Initialize Project** - `/gsd:plan-phase 3` or direct implementation
2. **Set up Expo** - Create mobile app structure
3. **Implement M1** - Auth screens and flows
4. **Test Early** - Verify on both platforms

---

**Document Status:** Ready for Implementation
**Last Updated:** 2026-01-20
**Approved By:** User (transitioning from Phase 2)
