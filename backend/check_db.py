#!/usr/bin/env python3
"""Check database connectivity and list databases."""
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Default DATABASE_URL from config.py
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/ruta"

async def check_database():
    """Check if database exists and is accessible."""
    print("[*] Checking database connectivity...")
    print(f"    Connection: {DATABASE_URL}")

    try:
        # Try to connect to ruta database
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.begin() as conn:
            # Test connection
            result = await conn.execute(text("SELECT 1"))
            result.scalar()
            print("[+] Connected to 'ruta' database successfully!")

            # Get table count
            result = await conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"    Tables found: {table_count}")

            # Get row counts for key tables
            tables_to_check = ['users', 'products', 'orders', 'user_library', 'timetables']
            print("\n[*] Data Summary:")
            for table in tables_to_check:
                try:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"    {table}: {count} rows")
                except Exception as e:
                    print(f"    {table}: table not found or error")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"[-] Error connecting to 'ruta' database: {e}")
        print("\n[!] This might mean:")
        print("    1. Database 'ruta' doesn't exist yet")
        print("    2. PostgreSQL is not running")
        print("    3. Credentials are incorrect")
        print("    4. This is a fresh install")
        return False

async def check_postgres_connection():
    """Try to connect to postgres default database."""
    print("\n[*] Checking PostgreSQL server connectivity...")

    # Try connecting to default postgres database
    postgres_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    try:
        engine = create_async_engine(postgres_url, echo=False)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"[+] PostgreSQL server is running!")
            print(f"    Version: {version[:50]}...")

            # List all databases
            result = await conn.execute(text("""
                SELECT datname FROM pg_database
                WHERE datistemplate = false
                ORDER BY datname
            """))
            databases = [row[0] for row in result.fetchall()]
            print(f"\n[*] Existing databases:")
            for db in databases:
                marker = ">>>" if db == "ruta" else "   "
                print(f"    {marker} {db}")

            # Check if rutiva already exists
            if 'rutiva' in databases:
                print("\n[!] Database 'rutiva' already exists!")
                print("    You may want to drop it first or use a different approach.")
            else:
                print("\n[+] Database 'rutiva' does not exist - ready to create.")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"[-] Error connecting to PostgreSQL: {e}")
        print("\n[!] Please ensure:")
        print("    1. PostgreSQL is installed and running")
        print("    2. Password for 'postgres' user is 'postgres'")
        print("    3. PostgreSQL is listening on localhost:5432")
        return False

async def main():
    print("=" * 60)
    print("DATABASE MIGRATION - Pre-flight Check")
    print("=" * 60)

    # First check if PostgreSQL server is accessible
    postgres_ok = await check_postgres_connection()

    if not postgres_ok:
        print("\n[-] Cannot proceed - PostgreSQL server not accessible")
        sys.exit(1)

    # Then check if ruta database exists
    print("\n" + "=" * 60)
    ruta_exists = await check_database()
    print("=" * 60)

    print("\n[*] Summary:")
    if ruta_exists:
        print("    [+] Source database 'ruta' exists and is accessible")
        print("    [+] Ready to backup and migrate to 'rutiva'")
        print("\n[>>] Next step: Run backup command")
    else:
        print("    [!] Source database 'ruta' not found")
        print("    [!] This appears to be a fresh installation")
        print("\n[>>] Next step: Create 'rutiva' database directly (no migration needed)")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[!] Check interrupted by user")
        sys.exit(1)
