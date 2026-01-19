# Rutiva Testing Checklist

**Phase 2 - Post-Migration Testing**
**Version:** 1.0
**Date:** 2026-01-20

---

## Testing Environment

**Backend:** http://localhost:8000
**Frontend:** http://localhost:3000
**Database:** `rutiva` (PostgreSQL)
**S3 Bucket:** `rutiva-content`
**Email Domain:** `@rutiva.co.za`

---

## Pre-Testing Setup

- [ ] Backend running: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `cd apps/web && npm run dev`
- [ ] Database accessible: `psql -h localhost -U postgres -d rutiva`
- [ ] Environment variables configured in `backend/.env`
- [ ] Browser DevTools open (Network tab for debugging)

---

## 1. Authentication & User Management

### 1.1 User Registration

- [ ] Navigate to http://localhost:3000/register
- [ ] Fill in registration form:
  - Email: test-rutiva-{timestamp}@example.com
  - Password: SecurePass123!
  - First Name: Test
  - Last Name: User
- [ ] Submit form
- [ ] **Verify:** OTP email received at test email address
- [ ] **Verify:** Email sender shows `noreply@rutiva.co.za`
- [ ] **Verify:** Email subject/body mentions "Rutiva"
- [ ] Enter OTP code
- [ ] **Verify:** Account created successfully
- [ ] **Verify:** Redirected to dashboard/home

**Database Verification:**
```bash
psql -h localhost -U postgres -d rutiva -c "SELECT id, email, first_name, is_verified FROM users ORDER BY created_at DESC LIMIT 1;"
```

### 1.2 User Login

- [ ] Logout from current session
- [ ] Navigate to http://localhost:3000/login
- [ ] Enter email and password
- [ ] **Verify:** Login successful
- [ ] **Verify:** User name appears in header (should show "Test")
- [ ] **Verify:** JWT token stored (check browser localStorage/cookies)

### 1.3 Password Reset

- [ ] Logout
- [ ] Click "Forgot Password"
- [ ] Enter email address
- [ ] **Verify:** Password reset email received
- [ ] **Verify:** Email from `noreply@rutiva.co.za`
- [ ] Click reset link
- [ ] Set new password
- [ ] **Verify:** Password updated successfully
- [ ] Login with new password
- [ ] **Verify:** Login works

---

## 2. Product Browsing & E-commerce

### 2.1 Product Catalog

- [ ] Navigate to http://localhost:3000/shop
- [ ] **Verify:** Products display correctly
- [ ] **Verify:** Product images load (check Network tab - should be from Cloudinary or S3)
- [ ] Test grade filter (select Grade 10)
- [ ] **Verify:** Only Grade 10 products shown
- [ ] Test subject filter (select Mathematics)
- [ ] **Verify:** Only Math products shown
- [ ] Search for "Physics"
- [ ] **Verify:** Search results display Physics products

### 2.2 Product Details

- [ ] Click on a product
- [ ] **Verify:** Product detail page loads
- [ ] **Verify:** Title, description, price display
- [ ] **Verify:** "What You'll Learn" section visible
- [ ] **Verify:** "Add to Cart" button functional
- [ ] Scroll to bottom
- [ ] **Verify:** Related products show (if applicable)

### 2.3 Shopping Cart

- [ ] Click "Add to Cart" on a product
- [ ] **Verify:** Cart icon shows "1" badge
- [ ] Navigate to /cart
- [ ] **Verify:** Product appears in cart
- [ ] **Verify:** Price correct
- [ ] Update quantity to 2
- [ ] **Verify:** Subtotal updates
- [ ] Click "Remove"
- [ ] **Verify:** Item removed from cart
- [ ] Add product back to cart
- [ ] Enter promo code (if you have one): e.g., "WELCOME10"
- [ ] **Verify:** Discount applied (if code valid)
- [ ] Click "Proceed to Checkout"

### 2.4 Checkout & Payment

**Note:** Use test payment credentials for PayFast/Yoco sandbox mode.

- [ ] Review order summary
- [ ] **Verify:** All items listed
- [ ] **Verify:** Total amount correct
- [ ] Click "Pay with PayFast" (or Yoco)
- [ ] **Verify:** Redirected to payment gateway
- [ ] Complete test payment
- [ ] **Verify:** Redirected back to success page
- [ ] **Verify:** Order confirmation displayed
- [ ] **Verify:** Order number format: `RT-YYYYMMDD-####`

**Email Verification:**
- [ ] Check email for order confirmation
- [ ] **Verify:** Email from `noreply@rutiva.co.za`
- [ ] **Verify:** Order details correct
- [ ] **Verify:** Email mentions "Rutiva"

**Database Verification:**
```bash
psql -h localhost -U postgres -d rutiva -c "SELECT order_number, email, total_amount, status FROM orders ORDER BY created_at DESC LIMIT 1;"
```

---

## 3. User Library & Content Access

### 3.1 Library Listing

- [ ] Navigate to http://localhost:3000/library
- [ ] **Verify:** Purchased guide appears
- [ ] **Verify:** Product cover image displays
- [ ] **Verify:** "Download PDF" button visible
- [ ] **Verify:** "Create Timetable" button visible

### 3.2 PDF Download

- [ ] Click "Download PDF" on purchased guide
- [ ] **Verify:** PDF download starts
- [ ] **Verify:** Network tab shows request to `rutiva-content.s3.af-south-1.amazonaws.com`
- [ ] **Verify:** PDF opens correctly in viewer
- [ ] **Verify:** PDF contains study guide content

**S3 Verification:**
```bash
aws s3 ls s3://rutiva-content/ --recursive | grep "math-gr10"
curl -I https://rutiva-content.s3.af-south-1.amazonaws.com/math-gr10-t1-2025.pdf
```

### 3.3 Content Viewing

- [ ] Click "View Guide" (if web viewer exists)
- [ ] **Verify:** Content renders correctly
- [ ] **Verify:** Images load from S3
- [ ] **Verify:** Navigation between sections works
- [ ] **Verify:** Formulas and diagrams display properly

---

## 4. Study Timetables

### 4.1 Timetable Creation

- [ ] From library, click "Create Timetable" on a purchased guide
- [ ] Fill in timetable form:
  - Exam Date: 2026-06-15 (or future date)
  - Study Days: Monday, Wednesday, Friday
  - Hours per Session: 1.5
  - Preferred Time: Afternoon
  - Pace: Normal
- [ ] Click "Generate Timetable"
- [ ] **Verify:** Timetable generated successfully
- [ ] **Verify:** Schedule displays with dates and topics
- [ ] **Verify:** Session count shown (e.g., "0 of 20 sessions complete")

**Database Verification:**
```bash
psql -h localhost -U postgres -d rutiva -c "SELECT id, title, exam_date, total_sessions FROM timetables ORDER BY created_at DESC LIMIT 1;"
```

### 4.2 Session Tracking

- [ ] Find first session in timetable
- [ ] Click "Mark Complete"
- [ ] **Verify:** Session marked as complete (checkmark appears)
- [ ] **Verify:** Progress bar updates
- [ ] **Verify:** Completion percentage increases
- [ ] Add notes to session (if feature exists)
- [ ] **Verify:** Notes saved

### 4.3 iCal Export

- [ ] Click "Export to Calendar" or "Download .ics"
- [ ] **Verify:** File downloads with name: `rutiva-<sku>.ics`
- [ ] Open .ics file in text editor
- [ ] **Verify:** Contains `PRODID:-//Rutiva//Study Timetable//EN`
- [ ] **Verify:** Contains `X-WR-CALNAME:Rutiva Study Plan` (or custom name)
- [ ] **Verify:** Event summaries start with `Rutiva:`
- [ ] Import .ics into calendar app (Google Calendar, Outlook, etc.)
- [ ] **Verify:** Events appear correctly

---

## 5. AI Tutor (RutivaBot)

### 5.1 Chat Session

- [ ] Navigate to AI Tutor page (URL may vary)
- [ ] Start new chat session
- [ ] Enter question: "Explain the quadratic formula"
- [ ] **Verify:** Response appears (streaming or full)
- [ ] **Verify:** Response mentions it's from "RutivaBot"
- [ ] **Verify:** Response is relevant and helpful
- [ ] **Verify:** Response uses appropriate grade level language
- [ ] Ask follow-up: "Give me an example problem"
- [ ] **Verify:** Bot provides example without full solution (uses Socratic method)

### 5.2 Context Awareness

- [ ] If chat is linked to a guide, ask: "What topics are covered?"
- [ ] **Verify:** Bot references the specific guide
- [ ] **Verify:** Response mentions grade and subject
- [ ] Ask: "Help me with homework" (should refuse full answers)
- [ ] **Verify:** Bot refuses to complete full homework, offers to explain concepts

### 5.3 Subscription Check (if AI is premium)

- [ ] Logout and login as user without AI subscription
- [ ] Try to access AI tutor
- [ ] **Verify:** Prompt to upgrade or message about subscription required
- [ ] Login as subscribed user
- [ ] **Verify:** Chat works normally

**API Verification:**
```bash
# Check backend logs for AI API calls
# Should see calls to DeepSeek or OpenAI
tail -f backend/logs/*.log | grep -i "deepseek\|openai"
```

---

## 6. School Licensing (if applicable)

### 6.1 School Portal Access

- [ ] Navigate to http://localhost:3000/schools
- [ ] **Verify:** Page loads with school licensing info
- [ ] Fill in inquiry form
- [ ] **Verify:** Form submits successfully
- [ ] **Verify:** Confirmation message displays

### 6.2 Bulk Purchase (if implemented)

- [ ] Login as school admin (if you have test account)
- [ ] Access school dashboard
- [ ] **Verify:** Student management features work
- [ ] **Verify:** Bulk license assignment works

---

## 7. Email Functionality

### 7.1 Email Branding

**Check all email types received during testing:**

- [ ] Registration OTP
- [ ] Password reset
- [ ] Order confirmation
- [ ] Welcome email (if applicable)

**For each email, verify:**
- [ ] Sender: `noreply@rutiva.co.za`
- [ ] Subject line mentions "Rutiva"
- [ ] Email body uses "Rutiva" branding (not "RUTA")
- [ ] Footer links point to `rutiva.co.za` (if domain configured)
- [ ] Email signature mentions "Rutiva Education"

### 7.2 Email Deliverability

- [ ] Check spam folder
- [ ] **Verify:** No emails marked as spam
- [ ] Check email headers (show original)
- [ ] **Verify:** SPF, DKIM pass (if configured)

---

## 8. Performance & Error Handling

### 8.1 Page Load Speed

- [ ] Open Network tab in DevTools
- [ ] Disable cache
- [ ] Reload homepage
- [ ] **Verify:** Page loads < 3 seconds
- [ ] Check largest contentful paint (LCP)
- [ ] **Verify:** LCP < 2.5 seconds

### 8.2 Error Handling

**Test 404 errors:**
- [ ] Navigate to http://localhost:3000/nonexistent-page
- [ ] **Verify:** Custom 404 page displays (not generic error)
- [ ] **Verify:** Links to go back to home

**Test API errors:**
- [ ] Try to access protected route without login
- [ ] **Verify:** Redirected to login page
- [ ] Try invalid API request (inspect Network tab)
- [ ] **Verify:** Proper error message displayed

### 8.3 Database Connection

**Simulate connection loss:**
- [ ] Stop database temporarily
- [ ] Try to load library page
- [ ] **Verify:** Graceful error message (not crash)
- [ ] Restart database
- [ ] Reload page
- [ ] **Verify:** Page loads normally

---

## 9. Security Testing

### 9.1 Authentication Security

- [ ] Try accessing /library without login
- [ ] **Verify:** Redirected to login
- [ ] Try accessing /library with expired token
- [ ] **Verify:** Token refresh or logout
- [ ] Check JWT token in browser storage
- [ ] **Verify:** Token contains user ID but not sensitive data

### 9.2 SQL Injection Prevention

- [ ] In search box, enter: `' OR '1'='1`
- [ ] **Verify:** No database error
- [ ] **Verify:** Search returns safe results or no results

### 9.3 XSS Prevention

- [ ] In any text field, enter: `<script>alert('XSS')</script>`
- [ ] Submit form
- [ ] **Verify:** Script does not execute
- [ ] **Verify:** Text is escaped/sanitized

---

## 10. Mobile Responsiveness (Web)

### 10.1 Mobile View

- [ ] Open DevTools, toggle device toolbar
- [ ] Select iPhone 12 Pro (or similar)
- [ ] **Verify:** Header responsive (logo + menu icon)
- [ ] **Verify:** Navigation menu works (hamburger icon)
- [ ] Navigate to shop
- [ ] **Verify:** Product grid displays 1-2 columns
- [ ] **Verify:** Add to cart works on mobile
- [ ] Navigate to library
- [ ] **Verify:** Library cards stack vertically
- [ ] Test timetable view
- [ ] **Verify:** Timetable scrollable and readable

### 10.2 Touch Interactions

- [ ] Simulate touch events in DevTools
- [ ] **Verify:** Buttons have adequate tap targets (min 44x44px)
- [ ] **Verify:** Swipe gestures work (if applicable)

---

## 11. Browser Compatibility

Test on multiple browsers:

### Chrome
- [ ] All features work
- [ ] No console errors

### Firefox
- [ ] All features work
- [ ] No console errors

### Safari (if available)
- [ ] All features work
- [ ] No console errors

### Edge
- [ ] All features work
- [ ] No console errors

---

## 12. Rollback Verification

**Keep this section for emergency rollback testing.**

### 12.1 Database Rollback Test (DO NOT RUN IN PRODUCTION)

- [ ] Stop backend
- [ ] Update `.env` to point to old `ruta` database
- [ ] Start backend
- [ ] **Verify:** Application still works with old database
- [ ] Revert `.env` back to `rutiva`

### 12.2 S3 Rollback Test

- [ ] Update `backend/app/core/config.py`: `S3_BUCKET = "ruta-content"`
- [ ] Restart backend
- [ ] Try downloading PDF
- [ ] **Verify:** Download still works from old bucket
- [ ] Revert back to `S3_BUCKET = "rutiva-content"`

---

## Critical Issues - Rollback Criteria

**Rollback immediately if:**
- [ ] >2 critical user flows fail completely
- [ ] Database data loss or corruption detected
- [ ] S3 files inaccessible for >10 minutes
- [ ] Email delivery fails >50% of attempts
- [ ] Payment processing completely broken
- [ ] Security vulnerability exposed

**Minor issues - Document but don't rollback:**
- [ ] Minor UI glitches
- [ ] Slow loading on specific pages
- [ ] Non-critical features not working
- [ ] Email delivery delays (<30 minutes)

---

## Post-Testing Report

### Passed Tests
- Total tests: ___ / ___
- Critical flows passed: ___ / ___
- Secondary features passed: ___ / ___

### Failed Tests
- [ ] List any failed tests here
- [ ] Include error messages
- [ ] Include screenshots/logs

### Performance Metrics
- Homepage load time: ___ seconds
- Login time: ___ seconds
- PDF download time: ___ seconds
- API average response time: ___ ms

### Issues Found
1. **Issue:** Description
   - **Severity:** Critical / High / Medium / Low
   - **Steps to reproduce:**
   - **Expected behavior:**
   - **Actual behavior:**
   - **Screenshots/logs:**

2. (Add more as needed)

### Recommendations
- [ ] Proceed with DNS migration
- [ ] Fix issues before proceeding
- [ ] Need additional testing
- [ ] Rollback required

---

## Sign-Off

**Tester Name:** _______________
**Date:** _______________
**Result:** ☐ Pass ☐ Fail ☐ Pass with Minor Issues
**Notes:**

---

**Checklist Version:** 1.0
**Last Updated:** 2026-01-20
**Next Review:** After migration completion
