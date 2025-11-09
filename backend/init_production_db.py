#!/usr/bin/env python3
"""
Production Database Initialization Script
Runs database migrations and creates default admin user
"""

import sys
import os
import subprocess
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def wait_for_database(max_attempts=30, delay=2):
    """Wait for database to be ready."""
    print("⏳ Waiting for database to be ready...")

    for attempt in range(max_attempts):
        try:
            from src.database import engine
            with engine.connect() as connection:
                print("✅ Database is ready!")
                return True
        except Exception as e:
            print(f"   Attempt {attempt + 1}/{max_attempts}: Database not ready - {e}")
            time.sleep(delay)

    print("❌ Database failed to become ready")
    return False


def run_migrations():
    """Run database migrations using Alembic."""
    print("🔄 Running database migrations...")

    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd='.'
        )

        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


def create_admin_user():
    """Create default admin user."""
    print("👤 Creating default admin user...")

    try:
        from src.services.user_service import UserService
        from src.database import SessionLocal
        from src.security import get_password_hash
        from src.schemas.user import UserCreate

        db = SessionLocal()
        user_service = UserService(db)

        try:
            # Check if admin user already exists
            existing_admin = user_service.get_user_by_username("admin")
            if existing_admin:
                print("✅ Admin user already exists")
                return True

            # Create admin user
            admin_data = {
                "username": "admin",
                "email": "admin@uspcfactory.com",
                "full_name": "System Administrator",
                "password": "admin123",  # Change this in production!
                "is_active": True
            }

            admin_user = user_service.create_user(
                UserCreate(**admin_data)
            )

            # Set superuser status
            admin_user.is_superuser = True
            db.commit()

            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Email: admin@uspcfactory.com")
            print("   Password: admin123")
            print("   ⚠️  IMPORTANT: Change the default password in production!")

            return True

        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main initialization function."""
    print("🚀 USPC Factory - Production Database Initialization")
    print("=" * 60)

    success = True

    # Wait for database
    if not wait_for_database():
        success = False

    # Run migrations
    if success:
        success = run_migrations()

    # Create admin user
    if success:
        success = create_admin_user()

    if success:
        print("\n🎉 Production database initialization completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Database is ready")
        print("   ✅ Migrations applied")
        print("   ✅ Admin user created")
        print("\n🔑 Admin Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   URL: http://localhost:8000/docs")
        print("\n⚠️  IMPORTANT ACTIONS:")
        print("   1. Change the default admin password immediately")
        print("   2. Update JWT secret key in production")
        print("   3. Configure proper CORS origins")
        print("   4. Set up SSL/TLS for production")
    else:
        print("\n❌ Production database initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()