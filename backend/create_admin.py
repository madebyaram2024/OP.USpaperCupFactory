#!/usr/bin/env python3
"""
Create Admin User Script
Creates a default superuser for the application
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models.user import User
from src.models.customer import Customer
from src.security import get_password_hash


def create_admin_user():
    """Create a default admin user if it doesn't exist."""
    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()

        if admin_user:
            print("✅ Admin user already exists")
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Superuser: {admin_user.is_superuser}")
            return admin_user

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@uspcfactory.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),  # Change this in production!
            is_active=True,
            is_superuser=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Email: admin@uspcfactory.com")
        print("   Password: admin123")
        print("   ⚠️  IMPORTANT: Change the default password in production!")

        return admin_user

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    try:
        print("Creating database tables...")

        # Import all models to ensure they are registered
        from src.models.user import User
        from src.models.customer import Customer

        # Create all tables
        from src.database import Base
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

    return True


def main():
    """Main function."""
    print("USPC Factory - Database Setup")
    print("=" * 40)

    # Create tables
    if not create_tables():
        sys.exit(1)

    # Create admin user
    admin_user = create_admin_user()

    if admin_user:
        print("\n🎉 Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the application: docker-compose up -d")
        print("2. Visit API docs: http://localhost:8000/docs")
        print("3. Login with admin credentials")
        print("4. Change the default password immediately!")
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()