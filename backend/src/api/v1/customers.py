from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from ... import database
from ...schemas.customer import (
    CustomerCreate, CustomerUpdate, Customer, CustomerListResponse
)
from ...services.customer_service import CustomerService

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


@router.post("/", response_model=Customer, status_code=201)
def create_customer(
    customer: CustomerCreate,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Create a new customer"""
    try:
        return customer_service.create_customer(customer_data=customer)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/", response_model=CustomerListResponse)
def list_customers(
    search: Optional[str] = Query(None, description="Search term for company name, contact name, or email"),
    status: Optional[str] = Query(None, description="Filter by status: active, archived, all"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    customer_service: CustomerService = Depends(get_customer_service)
):
    """List customers with optional search and filtering"""
    skip = (page - 1) * limit
    customers, total = customer_service.get_customers(
        search=search,
        status=status,
        skip=skip,
        limit=limit
    )
    
    pages = (total + limit - 1) // limit  # Calculate total pages
    
    return CustomerListResponse(
        items=customers,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    customer_id: uuid.UUID,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Get a specific customer by ID"""
    customer = customer_service.get_customer_detail(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: uuid.UUID,
    customer: CustomerUpdate,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Update a customer"""
    updated_customer = customer_service.update_customer(customer_id, customer)
    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        return updated_customer
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{customer_id}", status_code=204)
def archive_customer(
    customer_id: uuid.UUID,
    customer_service: CustomerService = Depends(get_customer_service)
):
    """Archive a customer (soft delete)"""
    success = customer_service.archive_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return