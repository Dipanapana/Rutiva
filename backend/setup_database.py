#!/usr/bin/env python3
"""
Setup database for Rutiva application.
This script creates the 'rutiva' database and runs migrations.
"""
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def create_database():
    """Create the rutiva database."""
    print("=" * 60)
    print("RUTIVA DATABASE SETUP")
    print("=" * 60)

    # Note: You may need to update these credentials
    postgres_url = "postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/postgres"

    print("\n[*] Attempting to connect to PostgreSQL server...")
    print(f"    Connection URL: {postgres_url.replace(':YOUR_PASSWORD', ':****')}")
    print("\n[!] NOTE: If this fails, you need to:")
    print("    1. Ensure PostgreSQL is running")
    print("    2. Update credentials in this script or create .env file")
    print()

    try:
        # Connect to default postgres database
        engine = create_async_engine(postgres_url, echo=False, isolation_level="AUTOCOMMIT")

        async with engine.begin() as conn:
            # Check if rutiva database exists
            result = await conn.execute(text("""
                SELECT 1 FROM pg_database WHERE datname='rutiva'
            """))
            exists = result.scalar()

            if exists:
                print("[!] Database 'rutiva' already exists!")
                print("    Skipping creation...")
            else:
                print("[*] Creating database 'rutiva'...")
                await conn.execute(text("CREATE DATABASE rutiva"))
                print("[+] Database 'rutiva' created successfully!")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"[-] Error: {e}")
        print("\n[!] Manual setup required:")
        print("    Option 1: Create database manually")
        print("      psql -U postgres")
        print("      CREATE DATABASE rutiva;")
        print()
        print("    Option 2: Use pgAdmin or another PostgreSQL client")
        print()
        return False

async def run_migrations():
    """Run database migrations using Alembic."""
    print("\n" + "=" * 60)
    print("RUNNING DATABASE MIGRATIONS")
    print("=" * 60)

    print("\n[*] Checking for Alembic configuration...")

    if not os.path.exists("alembic.ini"):
        print("[!] Alembic not configured yet")
        print("    Skipping migrations...")
        print("\n[!] You'll need to:")
        print("    1. Set up Alembic: alembic init alembic")
        print("    2. Configure alembic.ini with database URL")
        print("    3. Create initial migration: alembic revision --autogenerate -m 'Initial'")
        print("    4. Run migration: alembic upgrade head")
        return False

    print("[*] Running Alembic migrations...")
    print("    Command: alembic upgrade head")

    import subprocess
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[+] Migrations completed successfully!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[-] Migration failed: {e}")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("[-] Alembic command not found")
        print("    Install with: pip install alembic")
        return False

async def verify_setup():
    """Verify database is accessible."""
    print("\n" + "=" * 60)
    print("VERIFYING SETUP")
    print("=" * 60)

    # Try to connect to rutiva database
    rutiva_url = "postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/rutiva"

    print("\n[*] Testing connection to 'rutiva' database...")

    try:
        engine = create_async_engine(rutiva_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"[+] Connected successfully!")
            print(f"    PostgreSQL version: {version[:60]}...")

            # Check if tables exist
            result = await conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"    Tables in database: {table_count}")

            if table_count == 0:
                print("\n[!] No tables found - you need to run migrations")
                print("    See instructions above")
            else:
                print("\n[+] Database appears to be set up correctly!")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False

async def main():
    """Main setup routine."""

    # Step 1: Create database
    db_created = await create_database()

    if not db_created:
        print("\n" + "=" * 60)
        print("SETUP INCOMPLETE")
        print("=" * 60)
        print("\n[!] Could not create database automatically.")
        print("    Please create the database manually and update .env file")
        sys.exit(1)

    # Step 2: Run migrations (if Alembic is set up)
    await run_migrations()

    # Step 3: Verify
    await verify_setup()

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("\n1. Create backend/.env file with:")
    print("   DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@localhost:5432/rutiva")
    print()
    print("2. If migrations aren't set up yet, initialize Alembic:")
    print("   cd backend")
    print("   alembic init alembic")
    print("   # Edit alembic/env.py to import your models")
    print("   alembic revision --autogenerate -m 'Initial migration'")
    print("   alembic upgrade head")
    print()
    print("3. Start the application:")
    print("   python -m uvicorn app.main:app --reload --port 8000")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Setup interrupted by user")
        sys.exit(1)
