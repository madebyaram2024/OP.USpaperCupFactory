from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class SimpleWorkOrder(Base):
    __tablename__ = "simple_work_orders"

    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200), nullable=False)
    customer_phone = Column(String(50), nullable=True)

    # Order Details
    order_description = Column(Text, nullable=False)  # What they want
    quantity = Column(Integer, nullable=False)
    delivery_date = Column(DateTime, nullable=True)
    special_notes = Column(Text, nullable=True)

    # Simple Status - This matches your workflow exactly
    status = Column(String(50), default="new_order")  # new_order → design → approval → print → production → shipping

    # Who is responsible for current stage
    assigned_to = Column(String(100), nullable=True)  # Name of person working on it
    assigned_at = Column(DateTime, nullable=True)      # When they claimed it

    # Customer Files
    logo_file_path = Column(String(500), nullable=True)
    design_file_path = Column(String(500), nullable=True)  # Final design file
    other_files = Column(Text, nullable=True)  # JSON list of other file paths

    # Notifications
    last_notification = Column(DateTime, nullable=True)
    order_creator_notified = Column(Boolean, default=False)

    # Dates
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, customer='{self.customer_name}', status='{self.status}')>"


class WorkOrderFile(Base):
    __tablename__ = "work_order_files"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("simple_work_orders.id"), nullable=False)
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # logo, design, document, other
    uploaded_by = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    work_order = relationship("SimpleWorkOrder")


class WorkOrderUpdate(Base):
    __tablename__ = "simple_work_order_updates"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("simple_work_orders.id"), nullable=False)
    old_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    updated_by = Column(String(100), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    work_order = relationship("SimpleWorkOrder")