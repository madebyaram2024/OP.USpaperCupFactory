from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid

# Shared properties
class CustomerBase(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


# Properties to receive on customer creation
class CustomerCreate(CustomerBase):
    company_name: str
    contact_person: str
    email: EmailStr


# Properties to receive on customer update
class CustomerUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


# Properties shared by models stored in DB
class CustomerInDBBase(CustomerBase):
    id: uuid.UUID
    status: str = "active"
    active_orders_count: int = 0
    total_orders_count: int = 0
    created_at: datetime
    updated_at: datetime
    created_by: Optional[uuid.UUID] = None
    updated_by: Optional[uuid.UUID] = None

    class Config:
        from_attributes = True


# Properties to return to client
class Customer(CustomerInDBBase):
    pass


# Properties for customer list response
class CustomerListResponse(BaseModel):
    items: List[Customer]
    total: int
    page: int
    limit: int
    pages: int


# Properties for customer import
class CustomerImportItem(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state_province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    notes: Optional[str] = None


class CustomerImportRequest(BaseModel):
    pass  # File will be handled separately


class CustomerImportResponse(BaseModel):
    total_records: int
    successful_records: int
    failed_records: int
    errors: List[dict]