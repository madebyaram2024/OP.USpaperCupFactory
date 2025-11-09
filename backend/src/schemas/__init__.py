from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CustomerStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class CustomerBase(BaseModel):
    company_name: str
    contact_person: str
    email: str
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "USA"
    notes: Optional[str] = None
    status: CustomerStatus = CustomerStatus.active

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[CustomerStatus] = None

class Customer(CustomerBase):
    id: int
    total_orders_count: int
    created_at: datetime
    updated_at: datetime
    is_archived: bool

    class Config:
        from_attributes = True

class CustomerListResponse(BaseModel):
    items: List[Customer]
    total_count: int
    offset: int
    limit: int