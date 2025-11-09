#!/usr/bin/env python3
"""
Initialize Simple System with Admin User
Creates the first admin user so they can create employee accounts
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from datetime import datetime

def create_admin_user():
    """Create the admin user if it doesn't exist."""

    try:
        from src.database import engine, SessionLocal
        from src.models.simple_user import SimpleUser
        from src.security import get_password_hash

        # Check if admin already exists
        db = SessionLocal()
        try:
            admin_user = db.query(SimpleUser).filter(SimpleUser.username == "admin").first()

            if admin_user:
                print("✅ Admin user already exists")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email}")
                print("   (If you don't know the password, you'll need to reset it)")
                return True

        finally:
            db.close()

        # Create admin user
        admin_user = SimpleUser(
            username="admin",
            email="admin@uspcfactory.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )

        db = SessionLocal()
        try:
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            print("✅ Admin user created successfully!")
            print("   Username: admin")
            print("   Email: admin@uspcfactory.com")
            print("   Password: admin123")
            print("   ⚠️  IMPORTANT: Change the default password immediately!")
            print("   🔗 Go to: http://localhost:8000/login to get started")

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


def run_migrations():
    """Run database migrations to create tables."""
    print("🔄 Running database migrations...")

    try:
        # Run alembic upgrade head
        import subprocess
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


def create_upload_directory():
    """Create uploads directory for customer files."""
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print(f"✅ Created uploads directory: {upload_dir}")
    else:
        print(f"✅ Uploads directory exists: {upload_dir}")


def main():
    """Main initialization function."""
    print("🏭 USPC Factory - Simple System Initialization")
    print("=" * 50)

    success = True

    # Create upload directory
    create_upload_directory()

    # Run migrations
    if success:
        success = run_migrations()

    # Create admin user
    if success:
        success = create_admin_user()

    if success:
        print("\n🎉 System initialization completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Login to admin: http://localhost:8000/login")
        print("3. Username: admin")
        print("4. Password: admin123")
        print("5. CHANGE PASSWORD IMMEDIATELY!")
        print("6. Create employee accounts")
        print("7. Start managing work orders!")
    else:
        print("\n❌ System initialization failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()