# Infrastructure Migration Guide - RUTA to Rutiva

**Phase 2 Infrastructure Migration**
**Date:** 2026-01-20
**Status:** Ready to Execute

---

## Overview

This guide provides step-by-step instructions for migrating infrastructure from RUTA to Rutiva:
- PostgreSQL database: `ruta` → `rutiva`
- AWS S3 bucket: `ruta-content` → `rutiva-content`
- Email domain: `@ruta.co.za` → `@rutiva.co.za`
- Domain: `ruta.co.za` → `rutiva.co.za`

**Critical:** Follow steps in order. Test after each major change. Keep old infrastructure active for 1 week as rollback safety.

---

## Prerequisites

**Required Access:**
- [ ] PostgreSQL database admin access
- [ ] AWS account with S3 permissions
- [ ] SMTP provider admin access (for email domain)
- [ ] Domain registrar access (for DNS)

**Required Tools:**
- [ ] `pg_dump` and `psql` (PostgreSQL client tools)
- [ ] AWS CLI configured (`aws configure`)
- [ ] Git access to repository

**Backup Checklist:**
- [ ] Current database backed up
- [ ] Current S3 bucket accessible
- [ ] Environment variables documented
- [ ] Git repository up to date

---

## Part 1: Database Migration

### Step 1.1: Backup Current Database

```bash
# On your database server or local machine with pg_dump access
pg_dump -h localhost -U postgres -d ruta -F c -b -v -f "ruta_backup_$(date +%Y%m%d_%H%M%S).backup"

# For SQL format (more portable)
pg_dump -h localhost -U postgres -d ruta > "ruta_backup_$(date +%Y%m%d_%H%M%S).sql"
```

**Verify backup:**
```bash
# Check file size (should be >0 bytes)
ls -lh ruta_backup_*.backup

# For SQL format, check it contains data
head -n 50 ruta_backup_*.sql
```

### Step 1.2: Create New Database

```bash
# Connect to PostgreSQL
psql -h localhost -U postgres

# Create new database
CREATE DATABASE rutiva;

# Grant permissions (adjust user as needed)
GRANT ALL PRIVILEGES ON DATABASE rutiva TO postgres;

# Exit psql
\q
```

### Step 1.3: Restore Data to New Database

**Option A: From custom format backup**
```bash
pg_restore -h localhost -U postgres -d rutiva -v ruta_backup_*.backup
```

**Option B: From SQL format**
```bash
psql -h localhost -U postgres -d rutiva < ruta_backup_*.sql
```

### Step 1.4: Verify Database Migration

```bash
# Connect to new database
psql -h localhost -U postgres -d rutiva

# Check tables exist
\dt

# Check row counts match (compare with old database)
SELECT 'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'user_library', COUNT(*) FROM user_library;

# Exit
\q
```

**Compare with old database:**
```bash
psql -h localhost -U postgres -d ruta -c "SELECT COUNT(*) FROM users;"
psql -h localhost -U postgres -d rutiva -c "SELECT COUNT(*) FROM users;"
```

Counts should match exactly.

---

## Part 2: S3 Bucket Migration

### Step 2.1: Create New S3 Bucket

```bash
# Create bucket in af-south-1 region
aws s3 mb s3://rutiva-content --region af-south-1

# Verify creation
aws s3 ls | grep rutiva-content
```

### Step 2.2: Configure Bucket Policies

**Get current bucket policy from old bucket:**
```bash
aws s3api get-bucket-policy --bucket ruta-content > ruta-bucket-policy.json
```

**Create new policy (replace bucket name):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::rutiva-content/*"
    }
  ]
}
```

**Apply policy:**
```bash
aws s3api put-bucket-policy --bucket rutiva-content --policy file://rutiva-bucket-policy.json
```

**Configure CORS:**
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["https://rutiva.co.za", "http://localhost:3000"],
    "ExposeHeaders": ["ETag"]
  }
]
```

```bash
aws s3api put-bucket-cors --bucket rutiva-content --cors-configuration file://rutiva-cors.json
```

### Step 2.3: Copy Files from Old Bucket

```bash
# Sync all files from ruta-content to rutiva-content
aws s3 sync s3://ruta-content s3://rutiva-content --region af-south-1

# Show progress with size
aws s3 sync s3://ruta-content s3://rutiva-content --region af-south-1 --size-only
```

**This may take time depending on file count and size. Monitor progress.**

### Step 2.4: Verify S3 Files

```bash
# List files in new bucket
aws s3 ls s3://rutiva-content/ --recursive --summarize

# Compare counts
echo "Old bucket:"
aws s3 ls s3://ruta-content/ --recursive --summarize | grep "Total Objects"
echo "New bucket:"
aws s3 ls s3://rutiva-content/ --recursive --summarize | grep "Total Objects"
```

**Test public access to a sample file:**
```bash
# Get a sample file URL
echo "https://rutiva-content.s3.af-south-1.amazonaws.com/math-gr10-t1-2025.pdf"

# Test with curl (should return 200 OK)
curl -I https://rutiva-content.s3.af-south-1.amazonaws.com/math-gr10-t1-2025.pdf
```

---

## Part 3: Environment Configuration

### Step 3.1: Create Production .env File

```bash
cd backend

# Copy example to .env if not exists
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Update these values:**
```env
# Application
DEBUG=false
SECRET_KEY=<your-production-secret-key>
API_URL=https://api.rutiva.co.za
FRONTEND_URL=https://rutiva.co.za

# Database (UPDATED)
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<host>:5432/rutiva

# AWS S3 (UPDATED)
AWS_ACCESS_KEY_ID=<your-aws-key>
AWS_SECRET_ACCESS_KEY=<your-aws-secret>
AWS_REGION=af-south-1
S3_BUCKET=rutiva-content

# Email (UPDATED)
FROM_EMAIL=noreply@rutiva.co.za
SMTP_HOST=<your-smtp-host>
SMTP_PORT=587
SMTP_USER=<your-smtp-user>
SMTP_PASSWORD=<your-smtp-password>

# AI Providers
DEEPSEEK_API_KEY=<your-deepseek-key>
OPENAI_API_KEY=<your-openai-key>

# Payment Providers
PAYFAST_MERCHANT_ID=<your-payfast-id>
PAYFAST_MERCHANT_KEY=<your-payfast-key>
PAYFAST_PASSPHRASE=<your-passphrase>
PAYFAST_SANDBOX=false
```

### Step 3.2: Test Database Connection

```bash
cd backend

# Test connection with Python
python -c "
import asyncio
from app.core.config import settings
from sqlalchemy.ext.asyncio import create_async_engine

async def test():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database connection successful!')
    await engine.dispose()

asyncio.run(test())
"
```

### Step 3.3: Update Frontend Environment

```bash
cd apps/web

# Create .env.local if not exists
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
# For production: NEXT_PUBLIC_API_URL=https://api.rutiva.co.za
EOF
```

---

## Part 4: Email Domain Configuration

### Step 4.1: Configure SMTP Provider

**For AWS SES:**
1. Go to AWS SES Console
2. Verify domain: `rutiva.co.za`
3. Add DNS records (provided by SES)
4. Wait for verification (can take 24-72 hours)
5. Request production access (if in sandbox)

**For SendGrid/Mailgun/etc:**
1. Log into your provider
2. Add sender email: `noreply@rutiva.co.za`
3. Verify domain ownership via DNS
4. Get SMTP credentials
5. Update `.env` with credentials

### Step 4.2: Test Email Delivery

**Manual test:**
```bash
cd backend

# Run Python test script
python -c "
import asyncio
from app.services.email import send_email  # adjust import path

async def test():
    await send_email(
        to_email='your-test-email@example.com',
        subject='Rutiva Email Test',
        body='This is a test email from Rutiva.'
    )
    print('Email sent successfully!')

asyncio.run(test())
"
```

**Test OTP flow:**
1. Start backend server: `python -m uvicorn app.main:app --reload --port 8000`
2. Register new user via API
3. Check email for OTP
4. Verify sender shows `noreply@rutiva.co.za`

---

## Part 5: Testing Critical Flows

### Step 5.1: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # if using venv
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd apps/web
npm run dev
```

### Step 5.2: Authentication Flow

**Test registration:**
1. Navigate to http://localhost:3000/register
2. Register with new email
3. Check email for OTP (sender should be noreply@rutiva.co.za)
4. Verify OTP
5. Confirm login successful

**Test login:**
1. Logout
2. Login with credentials
3. Verify JWT token issued
4. Check session persists

### Step 5.3: E-commerce Flow

**Test product purchase:**
1. Browse products at /shop
2. Add product to cart
3. Proceed to checkout
4. Complete payment (use test mode)
5. Verify order created in database
6. Check purchase receipt email

**Verify database:**
```bash
psql -h localhost -U postgres -d rutiva -c "SELECT id, email, total_amount, status FROM orders ORDER BY created_at DESC LIMIT 5;"
```

### Step 5.4: Library & PDF Access

**Test PDF download:**
1. Navigate to /library
2. Select purchased guide
3. Click "Download PDF"
4. Verify file downloads from S3 (check Network tab - should be from rutiva-content bucket)
5. Open PDF and verify content

**Check S3 access logs:**
```bash
aws s3api list-objects-v2 --bucket rutiva-content --prefix math-gr10 --query 'Contents[].{Key:Key,Size:Size,LastModified:LastModified}'
```

### Step 5.5: Timetable Creation

**Test timetable:**
1. Go to purchased guide
2. Click "Create Timetable"
3. Fill in exam date, study days, preferences
4. Generate timetable
5. Verify schedule displays correctly
6. Mark a session complete
7. Export as iCal
8. Verify filename: `rutiva-<sku>.ics`
9. Open .ics file - events should show "Rutiva: <topic>"

### Step 5.6: AI Tutor

**Test chat:**
1. Navigate to /tutor (or wherever AI chat is)
2. Start new chat session
3. Ask a question (e.g., "Explain quadratic equations")
4. Verify response mentions "RutivaBot"
5. Check response quality and tone
6. Verify streaming works

**Check API logs:**
```bash
# In backend terminal, should see DeepSeek API calls
# Look for successful responses
```

---

## Part 6: Rollback Procedures

### If Database Migration Fails

```bash
# Option 1: Keep using old database
# In backend/.env, revert to:
DATABASE_URL=postgresql+asyncpg://postgres:<password>@<host>:5432/ruta

# Restart backend
```

### If S3 Migration Fails

```bash
# In backend/app/core/config.py, temporarily revert:
S3_BUCKET: str = "ruta-content"

# In apps/web/next.config.js, revert:
hostname: 'ruta-content.s3.af-south-1.amazonaws.com'

# Commit and deploy
```

### If Email Fails

```bash
# In backend/.env, use old email temporarily:
FROM_EMAIL=noreply@ruta.co.za

# Or disable email temporarily and investigate
```

### Complete Rollback

```bash
# Revert all code changes
git revert <commit-range>

# Update .env to old values
# Restart all services
```

---

## Part 7: DNS & Domain (Do Last)

**Only proceed after ALL testing passes.**

### Step 7.1: Configure DNS for rutiva.co.za

**Add A records (or CNAME):**
```
Type: A
Name: @
Value: <your-server-ip>
TTL: 3600

Type: A
Name: www
Value: <your-server-ip>
TTL: 3600

Type: CNAME
Name: api
Value: <your-api-server>
TTL: 3600
```

### Step 7.2: Set Up 301 Redirects from ruta.co.za

**Nginx configuration:**
```nginx
server {
    listen 80;
    listen 443 ssl;
    server_name ruta.co.za www.ruta.co.za;

    # SSL certificates (update paths)
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    return 301 https://rutiva.co.za$request_uri;
}
```

### Step 7.3: SSL Certificates

```bash
# Using Certbot (Let's Encrypt)
sudo certbot --nginx -d rutiva.co.za -d www.rutiva.co.za -d api.rutiva.co.za
```

---

## Success Criteria

**Migration is complete when:**
- [ ] Database `rutiva` has all data from `ruta` (verified row counts)
- [ ] S3 bucket `rutiva-content` has all files (verified object counts)
- [ ] All critical user flows pass (auth, purchase, library, timetable, AI)
- [ ] Emails send from `noreply@rutiva.co.za`
- [ ] PDFs download from `rutiva-content` bucket
- [ ] iCal exports show "Rutiva" branding
- [ ] AI chat identifies as "RutivaBot"
- [ ] No errors in backend logs for 1 hour of testing
- [ ] Domain `rutiva.co.za` accessible (if DNS configured)
- [ ] Old domain `ruta.co.za` redirects with 301 (if configured)

**Keep old infrastructure active for 1 week after successful migration as safety net.**

---

## Monitoring Post-Migration

**First 24 hours:**
- Monitor error logs closely
- Check email delivery rates
- Verify S3 access patterns
- Watch database performance

**Commands:**
```bash
# Backend logs
tail -f backend/logs/app.log

# Database connections
psql -h localhost -U postgres -d rutiva -c "SELECT count(*) FROM pg_stat_activity WHERE datname='rutiva';"

# S3 access test
curl -I https://rutiva-content.s3.af-south-1.amazonaws.com/<sample-file>.pdf
```

---

## Support Contacts

**If issues arise:**
1. Check rollback procedures above
2. Review error logs
3. Contact:
   - Database admin: <email>
   - AWS support: <link>
   - SMTP provider support: <link>

**Document all issues in GitHub issues for tracking.**

---

**Migration Guide Version:** 1.0
**Last Updated:** 2026-01-20
**Next Review:** After migration completion
