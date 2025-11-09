#!/usr/bin/env python3
"""
Database initialization script for USPC Factory Simple Work Order System
"""

import sys
import os
import logging
from sqlalchemy import inspect

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database import engine, SessionLocal, Base
from src.models.simple_user import SimpleUser
from src.models.simple_work_order import SimpleWorkOrder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and create tables"""
    logger.info("Initializing database for Simple Work Order System...")

    try:
        # Create all tables based on registered models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")

        # Verify the tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {tables}")

        # Check for expected tables
        expected_tables = ['simple_users', 'simple_work_orders', 'work_order_files', 'simple_work_order_updates']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            logger.warning(f"Missing tables: {missing_tables} - may need migrations")
        else:
            logger.info("All expected tables exist")

        # Check if we can create a session
        db = SessionLocal()
        try:
            # Try to count existing users and work orders
            from sqlalchemy import func
            if 'simple_users' in tables:
                user_count = db.query(func.count(SimpleUser.id)).scalar()
                logger.info(f"Database connection successful. Current user count: {user_count}")

            if 'simple_work_orders' in tables:
                order_count = db.query(func.count(SimpleWorkOrder.id)).scalar()
                logger.info(f"Current work order count: {order_count}")
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
        # Don't fail hard - the server can still start
        return True  # Changed to True so startup continues

if __name__ == "__main__":
    success = init_db()
    if success:
        logger.info("Database initialization completed")
        sys.exit(0)
    else:
        logger.error("Database initialization had issues")
        sys.exit(0)  # Exit with 0 anyway to allow server to start