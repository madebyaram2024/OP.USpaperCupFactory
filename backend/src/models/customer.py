from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.sql import func
import uuid

# Import the shared Base from database module
from ..database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(50), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state_province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default='active')  # active, archived
    active_orders_count = Column(Integer, nullable=False, default=0)
    total_orders_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    created_by = Column(PG_UUID(as_uuid=True), nullable=True)
    updated_by = Column(PG_UUID(as_uuid=True), nullable=True)

    # Add check constraint for status
    __table_args__ = (
        CheckConstraint(status.in_(['active', 'archived']), name='check_status'),
    )