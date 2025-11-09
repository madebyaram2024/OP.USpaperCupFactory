from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Numeric, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class WorkOrderStatus(enum.Enum):
    """Work Order Status Enum"""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    IN_PRODUCTION = "in_production"
    PRODUCTION_COMPLETE = "production_complete"
    QUALITY_CHECK = "quality_check"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Priority(enum.Enum):
    """Priority Level Enum"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    work_order_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Order Details
    product_type = Column(String(100), nullable=False)  # e.g., "Paper Cup 8oz", "Coffee Sleeve"
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)

    # Product Specifications
    cup_size = Column(String(20))  # e.g., "8oz", "12oz", "16oz"
    cup_type = Column(String(50))  # e.g., "Hot Cup", "Cold Cup", "Coffee Sleeve"
    material = Column(String(50))  # e.g., "Paper", "Cardboard", "Coated Paper"
    color = Column(String(30))
    design_specifications = Column(Text)  # Custom design requirements
    printing_requirements = Column(Text)  # Logo, text, artwork specifications

    # Production Details
    priority = Column(Enum(Priority), default=Priority.NORMAL)
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.DRAFT)

    # Dates
    order_date = Column(DateTime, default=datetime.utcnow)
    requested_delivery_date = Column(DateTime)
    scheduled_production_date = Column(DateTime)
    actual_production_start = Column(DateTime)
    actual_production_complete = Column(DateTime)
    estimated_ship_date = Column(DateTime)
    actual_ship_date = Column(DateTime)
    delivery_date = Column(DateTime)

    # Production Tracking
    production_notes = Column(Text)
    quality_check_notes = Column(Text)
    shipping_notes = Column(Text)
    special_instructions = Column(Text)

    # Status and Tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    updated_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    customer = relationship("Customer", back_populates="work_orders")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, work_order_number='{self.work_order_number}', status='{self.status.value}')>"


class WorkOrderUpdate(Base):
    """Track all work order updates for audit trail"""
    __tablename__ = "work_order_updates"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    old_status = Column(Enum(WorkOrderStatus))
    new_status = Column(Enum(WorkOrderStatus))
    notes = Column(Text)
    updated_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    work_order = relationship("WorkOrder")
    updater = relationship("User")


class ProductionSchedule(Base):
    """Production scheduling and queue management"""
    __tablename__ = "production_schedule"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime)
    actual_end = Column(DateTime)
    production_line = Column(String(50))  # e.g., "Line 1", "Line 2"
    machine_assigned = Column(String(100))
    operator_assigned = Column(String(100))
    status = Column(String(20), default="scheduled")  # scheduled, in_progress, completed, delayed

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    work_order = relationship("WorkOrder")