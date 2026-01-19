# Rutiva Quick Start Guide

**Fresh Installation Setup**

This guide will help you set up the Rutiva application from scratch on your local machine.

---

## Current Status

Based on the database connectivity check:
- PostgreSQL is installed (version 14.19)
- No existing 'ruta' database found
- This is a **fresh installation** - no migration needed
- Will create 'rutiva' database directly

---

## Step 1: Configure PostgreSQL Password

First, you need to know your PostgreSQL `postgres` user password.

### Option A: You know the password
- Skip to Step 2 and use your password in the `.env` file

### Option B: Reset/set the password

**On Windows:**
1. Open Command Prompt as Administrator
2. Run:
   ```cmd
   psql -U postgres
   ```
3. If it asks for a password and you don't know it, or if it fails, you need to reset it:

**Reset password method:**
1. Find your PostgreSQL data directory (usually `C:\Program Files\PostgreSQL\14\data`)
2. Edit `pg_hba.conf` file:
   - Find line with `host all all 127.0.0.1/32 md5`
   - Change `md5` to `trust`
   - Save file
3. Restart PostgreSQL service:
   ```cmd
   net stop postgresql-x64-14
   net start postgresql-x64-14
   ```
4. Connect without password:
   ```cmd
   psql -U postgres
   ```
5. Set new password:
   ```sql
   ALTER USER postgres PASSWORD 'postgres';
   \q
   ```
6. Change `pg_hba.conf` back from `trust` to `md5`
7. Restart PostgreSQL again

---

## Step 2: Update .env File

The file `backend/.env` has been created for you. Update it:

1. Open `backend/.env` in a text editor
2. Find this line:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:YOUR_POSTGRES_PASSWORD@localhost:5432/rutiva
   ```
3. Replace `YOUR_POSTGRES_PASSWORD` with your actual password:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rutiva
   ```
4. Do the same for `DATABASE_URL_SYNC`
5. Save the file

---

## Step 3: Create Rutiva Database

Open Command Prompt and run:

```cmd
psql -U postgres
```

Enter your password when prompted, then run:

```sql
CREATE DATABASE rutiva;
\l
```

You should see `rutiva` in the list of databases. Exit with:

```sql
\q
```

**OR use the automated script:**

```cmd
cd "C:\Users\USER\Documents\CHIEF AIM\blaqedu\ruta\backend"
python setup_database.py
```

(Make sure to update the password in `setup_database.py` first)

---

## Step 4: Install Python Dependencies

```cmd
cd "C:\Users\USER\Documents\CHIEF AIM\blaqedu\ruta\backend"

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, install core dependencies:

```cmd
pip install fastapi uvicorn sqlalchemy asyncpg psycopg2-binary pydantic-settings alembic python-jose passlib bcrypt python-multipart httpx
```

---

## Step 5: Set Up Database Migrations (Alembic)

### Check if Alembic is initialized

```cmd
cd "C:\Users\USER\Documents\CHIEF AIM\blaqedu\ruta\backend"
dir alembic.ini
```

### If `alembic.ini` exists:

Just run migrations:

```cmd
alembic upgrade head
```

### If `alembic.ini` does NOT exist:

You need to initialize Alembic:

```cmd
# Initialize Alembic
alembic init alembic

# This creates:
# - alembic/ directory
# - alembic.ini file
```

Then edit `alembic.ini`:
- Find line: `sqlalchemy.url = driver://user:pass@localhost/dbname`
- Replace with: `sqlalchemy.url = postgresql://postgres:YOUR_PASSWORD@localhost:5432/rutiva`

Edit `alembic/env.py`:
- Add after imports:
  ```python
  from app.core.config import settings
  from app.models import Base  # Your SQLAlchemy Base

  config.set_main_option('sqlalchemy.url', settings.DATABASE_URL_SYNC)
  target_metadata = Base.metadata
  ```

Create initial migration:

```cmd
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Step 6: Start the Backend Server

```cmd
cd "C:\Users\USER\Documents\CHIEF AIM\blaqedu\ruta\backend"

# Activate venv if you created one
venv\Scripts\activate

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Test it:
- Open browser: http://localhost:8000
- You should see the API root response
- Check docs: http://localhost:8000/docs

---

## Step 7: Set Up Frontend

**Terminal 2** (keep backend running in Terminal 1):

```cmd
cd "C:\Users\USER\Documents\CHIEF AIM\blaqedu\ruta"

# Install root dependencies (if not done)
npm install

# Install web app dependencies
cd apps\web
npm install

# Start dev server
npm run dev
```

You should see:
```
  ▲ Next.js 14.2.21
  - Local:        http://localhost:3000
  - Ready in 2.5s
```

---

## Step 8: Test the Application

Open http://localhost:3000 in your browser.

You should see the Rutiva homepage with:
- Header showing "Rutiva" logo
- Footer showing "hello@rutiva.co.za"
- All branding updated from RUTA to Rutiva

---

## Troubleshooting

### Database connection fails

```
[-] Error connecting to PostgreSQL: password authentication failed
```

**Fix:** Update password in `backend/.env` file

### Module not found errors

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:** Install dependencies:
```cmd
cd backend
pip install -r requirements.txt
```

### Alembic migration errors

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) FATAL: database "rutiva" does not exist
```

**Fix:** Create database first (see Step 3)

### Port already in use

```
ERROR:    [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)
```

**Fix:**
- Kill the process using port 8000
- Or use a different port: `--port 8001`

---

## Next Steps After Setup

Once everything is running:

1. **Create test user**
   - Register at http://localhost:3000/register
   - (Email won't work yet - check database directly for verification)

2. **Test API endpoints**
   - Go to http://localhost:8000/docs
   - Try authentication endpoints

3. **Configure optional services:**
   - AWS S3 (for PDF storage)
   - Email SMTP (for OTP, password reset)
   - AI providers (DeepSeek/OpenAI for RutivaBot)
   - Payment providers (PayFast/Yoco)

4. **Add sample data:**
   - Create products
   - Test purchase flow
   - Create timetables

---

## Reference Commands

**Database operations:**
```cmd
# Connect to database
psql -U postgres -d rutiva

# List tables
\dt

# Count users
SELECT COUNT(*) FROM users;

# Exit
\q
```

**Backend operations:**
```cmd
# Start server
python -m uvicorn app.main:app --reload --port 8000

# Create migration
alembic revision --autogenerate -m "Description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

**Frontend operations:**
```cmd
# Dev server
npm run dev

# Build for production
npm run build

# Type check
npm run type-check

# Lint
npm run lint
```

---

## Files Created/Modified

During this setup, the following files were created:

- `backend/.env` - Environment variables (**Do not commit to git**)
- `backend/check_db.py` - Database connectivity checker
- `backend/setup_database.py` - Automated database setup script
- `QUICK-START.md` - This file

---

**Need help?** Check the documentation:
- [PROJECT.md](PROJECT.md) - Tech stack and architecture
- [INFRASTRUCTURE-MIGRATION.md](INFRASTRUCTURE-MIGRATION.md) - Full migration guide
- [TESTING-CHECKLIST.md](TESTING-CHECKLIST.md) - Testing procedures

**Ready to proceed!** 🚀
