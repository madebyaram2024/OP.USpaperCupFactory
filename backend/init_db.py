#!/usr/bin/env python3
"""
Database initialization script for Speckit Customer Management API
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Import models first to register them with declarative base
from src.models.customer import Customer
from src.database import engine, Base


def init_db():
    """Initialize the database and create tables"""
    print("Initializing database...")
    
    # Create all tables based on registered models
    print(f"Base metadata tables: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    
    # Verify the Customer table was created by adding a test customer
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Try to count existing customers
        count = db.query(Customer).count()
        print(f"Database initialized successfully. Current customer count: {count}")
    except Exception as e:
        print(f"Error accessing database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()