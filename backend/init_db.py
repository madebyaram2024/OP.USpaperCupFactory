#!/usr/bin/env python3
"""
Database initialization script for Speckit Customer Management API
"""

import sys
import os
import logging
from sqlalchemy import inspect

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.customer import Customer, Base
from src.database import engine, SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and create tables"""
    logger.info("Initializing database...")
    
    try:
        # Create all tables based on registered models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        
        # Verify the tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {tables}")
        
        if 'customers' in tables:
            logger.info("Customer table exists - database initialization successful")
        else:
            logger.warning("Customer table does not exist - there might be an issue")
        
        # Check if we can create a session
        db = SessionLocal()
        try:
            # Try to count existing customers
            from sqlalchemy import func
            count = db.query(func.count(Customer.id)).scalar()
            logger.info(f"Database connection successful. Current customer count: {count}")
        except Exception as e:
            logger.error(f"Error querying database: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
            
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_db()
    if success:
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)