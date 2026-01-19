# Phase 2: Rutiva Rebrand - Implementation Context

**Phase:** 2 - Rutiva Rebrand
**Created:** 2025-01-19
**Status:** Ready for Planning

---

## Phase Overview

**Goal:** Complete transformation from RUTA to Rutiva across code, infrastructure, and branding without breaking functionality.

**Timeline:** Week 2 (January 27 - February 2, 2025)

**Scope:**
- Update 53+ files with "ruta" → "Rutiva" references
- Migrate infrastructure (database, S3 bucket, email domain)
- Full domain change: ruta.co.za → rutiva.co.za
- Test all critical user flows
- Minimal disruption to users

---

## Implementation Decisions

### 1. User Communication Strategy

**Approach:** Minimal proactive communication with gradual discovery

**Key Decisions:**
- ✅ **No advance notice** - Users will discover rebrand naturally when they visit
- ✅ **No email announcement** - Unless users contact support with questions
- ✅ **No in-app banners** - Clean rebrand without notification modals
- ✅ **No special handling for active users** - Existing timetables, carts, sessions continue to work seamlessly

**Rationale:**
- Rebrand is purely cosmetic (name, logo, colors)
- All functionality remains identical
- Users care about their study materials working, not branding changes
- Simpler implementation with less risk of user confusion

### 2. Support & Communication Channels

**Reactive Support:**
- ✅ **Monitor support email** - Respond to any rebrand-related questions
- ✅ **Create FAQ page** at rutiva.co.za/rebrand-faq
- ✅ **Email users who ask** - Only reactive, not proactive

**FAQ Page Content:**
- **Focus:** "What stays the same"
- **Message:** Same platform, same content, same team, same features
- **Tone:** Brief and reassuring
- **Keep it simple:** No lengthy explanations, just reassurance

**FAQ Structure:**
```
# Rebrand FAQ

## We're now Rutiva!

**Q: What changed?**
A: Just our name and logo. We're now Rutiva (previously RUTA).

**Q: Do I need to do anything?**
A: No. Your account, study guides, timetables, and everything else works exactly the same.

**Q: Why did you change the name?**
A: Our original domain wasn't available, so we chose Rutiva as our new name.

**Q: What about my purchased content?**
A: All your study guides and subscriptions remain active. Nothing changed except our name.

**Q: Questions?**
A: Email us at hello@rutiva.co.za
```

### 3. Domain Migration

**Decision:** Full domain change with 301 redirects

**Implementation:**
- ✅ **New domain:** rutiva.co.za (primary)
- ✅ **Old domain:** ruta.co.za (301 redirect to rutiva.co.za)
- ✅ **Redirect duration:** Permanent (keep old domain pointing to new)
- ✅ **DNS update:** Point rutiva.co.za to production servers
- ✅ **SSL certificate:** Obtain for rutiva.co.za

**Technical Details:**
```nginx
# nginx redirect configuration
server {
    server_name ruta.co.za www.ruta.co.za;
    return 301 https://rutiva.co.za$request_uri;
}
```

**Why full domain change:**
- Clean rebrand with consistent naming
- Users will use new domain going forward
- Old bookmarks/links will redirect automatically
- SEO: 301 redirects preserve search rankings

### 4. Email Domain

**Decision:** Full email rebrand to @rutiva.co.za

**Implementation:**
- ✅ **New email:** hello@rutiva.co.za, noreply@rutiva.co.za
- ✅ **Old email:** Keep ruta.co.za emails forwarding to rutiva.co.za (backup)
- ✅ **Update config:** FROM_EMAIL in backend/app/core/config.py
- ✅ **SMTP setup:** Configure @rutiva.co.za in email provider
- ✅ **Test:** OTP, password reset, purchase receipts

**Email Templates:**
- No changes to email template content (already generic)
- Only update sender email address
- Footer links update to rutiva.co.za

### 5. Migration Timing & Downtime

**Approach:** Zero-downtime for users

**Migration Strategy:**
1. **Code changes first** (Day 1-3) - Deploy code with new branding
2. **Infrastructure next** (Day 4-5) - Migrate database, S3, email
3. **DNS last** (Day 5) - Point rutiva.co.za to servers
4. **Redirects** (Day 5) - Set up ruta.co.za → rutiva.co.za redirects

**Downtime expectations:**
- **Code deployment:** None (rolling deployment)
- **Database migration:** Test on staging first, production migration during low-traffic (2-4am SAST)
- **S3 migration:** No downtime (copy files while old bucket active, switch after verification)
- **DNS propagation:** 0-48 hours (varies by ISP)

**User impact:**
- Existing sessions: Continue working
- Active carts: Preserved
- Timetables: Unaffected
- API tokens: Valid (no logout required)

### 6. Data Continuity

**Decision:** All user data continues seamlessly

**Database:**
- ✅ Create new database: `rutiva`
- ✅ Copy all data from `ruta` database
- ✅ Verify zero data loss
- ✅ Keep old database for 1 week (rollback safety)
- ✅ Test all queries with new database

**S3 Bucket:**
- ✅ Create new bucket: `rutiva-content`
- ✅ Copy all files from `ruta-content`
- ✅ Update config to point to new bucket
- ✅ Keep old bucket active for 1 week (rollback safety)
- ✅ Test PDF downloads and image loading

**Sessions & Carts:**
- ✅ Redis cache continues working (stored by user ID, not domain)
- ✅ JWT tokens remain valid (Secret key unchanged)
- ✅ Shopping carts preserved (tied to user accounts)

### 7. Order Number Format

**Decision:** Keep RT- prefix for backward compatibility

**Rationale:**
- Existing orders use RT- prefix (RT-20250119-0001)
- Changing to RV- could break order lookups
- Not user-facing enough to warrant migration complexity
- Can update for new orders in future if needed

**Implementation:**
- ✅ **Leave order.py unchanged** - Keep `generate_order_number()` using RT- prefix
- ✅ **Document decision** in code comments
- ✅ **Future consideration:** RV- prefix for v2.0 (Phase 5+)

### 8. Testing & Validation

**Critical User Flows to Test:**
- [ ] Login with existing account
- [ ] Register new account
- [ ] Browse products
- [ ] Add to cart
- [ ] Apply promo code
- [ ] Complete purchase (with test payment)
- [ ] Access user library
- [ ] Download PDF from new S3 bucket
- [ ] View/create timetable
- [ ] Chat with AI tutor
- [ ] Send OTP email (verify @rutiva.co.za sender)
- [ ] Password reset email

**Rollback Criteria:**
- If more than 2 critical flows fail → immediate rollback
- Database corruption → restore from backup
- S3 file access broken → revert to old bucket

**Rollback Procedures:**
1. Revert code changes (git revert)
2. Point config back to old database/S3
3. Update DNS to old domain
4. Notify users if downtime occurred

---

## Out of Scope for Phase 2

**Deferred to Future Phases:**
- ❌ Logo redesign (using text-only branding for now)
- ❌ Color scheme changes (keep existing Tailwind theme)
- ❌ Marketing announcement (no press release, social media posts)
- ❌ SEO optimization for new domain (let 301 redirects handle it)
- ❌ Mobile app rebrand (Phase 3 will build app with Rutiva branding)
- ❌ Updating third-party integrations (PayFast/Yoco already use generic names)

---

## Success Criteria

**Phase 2 is complete when:**
- [ ] All 53+ code files updated with Rutiva references
- [ ] Database migrated to `rutiva` with zero data loss
- [ ] S3 bucket migrated to `rutiva-content` with all files accessible
- [ ] Email sending from @rutiva.co.za successfully
- [ ] Domain rutiva.co.za live and accessible
- [ ] Old domain ruta.co.za redirecting with 301
- [ ] All critical user flows pass testing
- [ ] FAQ page published at rutiva.co.za/rebrand-faq
- [ ] No production errors for 48 hours post-launch
- [ ] Support email monitored for rebrand questions

---

## Technical Constraints

**Fixed Boundaries (Do Not Change):**
- JWT Secret Key (tokens must remain valid)
- Database schema (structure unchanged, only name)
- API endpoint paths (no breaking changes)
- Redis keys format (sessions must persist)
- File storage structure in S3 (same paths)

**Allowed Changes:**
- All text references "RUTA" → "Rutiva"
- All config values referencing "ruta" → "rutiva"
- Domain names
- Email addresses
- Database name
- S3 bucket name

---

## Next Steps

1. **Research Phase 2** - `/gsd:research-phase 2`
   - Identify all 53+ files needing updates
   - Document current database/S3 setup
   - Research migration best practices

2. **Plan Phase 2** - `/gsd:plan-phase 2`
   - Create atomic task list
   - Define verification steps per task
   - Identify dependencies and order

3. **Execute Phase 2** - `/gsd:execute-phase 2`
   - Run tasks in parallel waves
   - Fresh context per execution batch
   - Atomic commits per task

---

**Document Status:** Ready for Planning
**Last Updated:** 2025-01-19
**Approved By:** User (via discuss-phase workflow)
