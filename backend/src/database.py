from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Import models to ensure they are registered with SQLAlchemy
from .models.simple_work_order import SimpleWorkOrder, WorkOrderFile, WorkOrderUpdate

# Use environment variable for database URL, with a default for development
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/customer_management")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()