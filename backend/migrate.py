#!/usr/bin/env python3
"""
Database Migration Helper
Provides easy commands for database migrations
"""

import sys
import os
import subprocess
import argparse

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd='.')
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def check_database_connection():
    """Check if database is available."""
    print("🔍 Checking database connection...")
    try:
        from src.database import engine
        with engine.connect() as connection:
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def init_migrations():
    """Initialize Alembic migrations."""
    return run_command(
        "alembic init migrations",
        "Initializing Alembic migrations"
    )


def create_migration(message):
    """Create a new migration."""
    if not check_database_connection():
        return False

    return run_command(
        f"alembic revision --autogenerate -m \"{message}\"",
        f"Creating migration: {message}"
    )


def upgrade_database(revision="head"):
    """Upgrade database to specified revision."""
    if not check_database_connection():
        return False

    return run_command(
        f"alembic upgrade {revision}",
        f"Upgrading database to {revision}"
    )


def downgrade_database(revision):
    """Downgrade database to specified revision."""
    if not check_database_connection():
        return False

    return run_command(
        f"alembic downgrade {revision}",
        f"Downgrading database to {revision}"
    )


def show_history():
    """Show migration history."""
    return run_command(
        "alembic history",
        "Showing migration history"
    )


def show_current():
    """Show current revision."""
    return run_command(
        "alembic current",
        "Showing current revision"
    )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Database Migration Helper")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create a new migration")
    create_parser.add_argument("message", help="Migration message")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Upgrade database")
    upgrade_parser.add_argument(
        "--revision", default="head", help="Target revision (default: head)"
    )

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Downgrade database")
    downgrade_parser.add_argument("revision", help="Target revision")

    # Status commands
    subparsers.add_parser("history", help="Show migration history")
    subparsers.add_parser("current", help="Show current revision")

    # Check connection
    subparsers.add_parser("check", help="Check database connection")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    print("🚀 USPC Factory - Database Migration Helper")
    print("=" * 50)

    success = True

    if args.command == "create":
        success = create_migration(args.message)
    elif args.command == "upgrade":
        success = upgrade_database(args.revision)
    elif args.command == "downgrade":
        success = downgrade_database(args.revision)
    elif args.command == "history":
        success = show_history()
    elif args.command == "current":
        success = show_current()
    elif args.command == "check":
        success = check_database_connection()

    if success:
        print("\n🎉 Operation completed successfully!")
    else:
        print("\n❌ Operation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()