from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum


class WorkOrderStatusEnum(str, Enum):
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


class PriorityEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


# Base properties
class WorkOrderBase(BaseModel):
    customer_id: int
    product_type: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    total_amount: Optional[Decimal] = None

    # Product specifications
    cup_size: Optional[str] = Field(None, max_length=20)
    cup_type: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    design_specifications: Optional[str] = None
    printing_requirements: Optional[str] = None

    # Production details
    priority: PriorityEnum = PriorityEnum.NORMAL
    requested_delivery_date: Optional[datetime] = None
    special_instructions: Optional[str] = None


# Properties to receive on work order creation
class WorkOrderCreate(WorkOrderBase):
    pass


# Properties to receive on work order update
class WorkOrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    product_type: Optional[str] = Field(None, min_length=1, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    total_amount: Optional[Decimal] = None

    cup_size: Optional[str] = Field(None, max_length=20)
    cup_type: Optional[str] = Field(None, max_length=50)
    material: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    design_specifications: Optional[str] = None
    printing_requirements: Optional[str] = None

    priority: Optional[PriorityEnum] = None
    requested_delivery_date: Optional[datetime] = None
    special_instructions: Optional[str] = None


# Status update specific schema
class WorkOrderStatusUpdate(BaseModel):
    status: WorkOrderStatusEnum
    notes: Optional[str] = None


# Production schedule schema
class ProductionScheduleUpdate(BaseModel):
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    production_line: Optional[str] = None
    machine_assigned: Optional[str] = None
    operator_assigned: Optional[str] = None
    production_notes: Optional[str] = None


# Properties shared by models stored in DB
class WorkOrderInDBBase(WorkOrderBase):
    id: int
    work_order_number: str
    status: WorkOrderStatusEnum
    total_amount: Decimal

    # Dates
    order_date: datetime
    scheduled_production_date: Optional[datetime] = None
    actual_production_start: Optional[datetime] = None
    actual_production_complete: Optional[datetime] = None
    estimated_ship_date: Optional[datetime] = None
    actual_ship_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None

    # Tracking
    production_notes: Optional[str] = None
    quality_check_notes: Optional[str] = None
    shipping_notes: Optional[str] = None
    is_active: bool

    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


# Properties to return to client
class WorkOrder(WorkOrderInDBBase):
    # Include customer information
    customer: Optional[dict] = None
    creator: Optional[dict] = None
    updater: Optional[dict] = None


# Work order with full details including schedule
class WorkOrderDetail(WorkOrder):
    production_schedule: Optional[List[dict]] = []
    status_updates: Optional[List[dict]] = []


# Work order list response
class WorkOrderListResponse(BaseModel):
    items: List[WorkOrder]
    total: int
    page: int
    limit: int
    pages: int


# Work order statistics
class WorkOrderStats(BaseModel):
    total_orders: int
    orders_by_status: dict[str, int]
    orders_by_priority: dict[str, int]
    pending_orders: int
    in_production_orders: int
    completed_this_month: int
    total_value: Decimal


# Production queue response
class ProductionQueue(BaseModel):
    scheduled: List[WorkOrder]
    in_progress: List[WorkOrder]
    delayed: List[WorkOrder]
    upcoming: List[WorkOrder]