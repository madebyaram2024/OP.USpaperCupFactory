from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...models.customer import Customer
from ...schemas.customer import Customer, CustomerCreate, CustomerUpdate, CustomerListResponse
from ...database import get_db
from ...api.v1.auth import get_current_active_user
from ...schemas.user import User
from sqlalchemy import or_, func

router = APIRouter()

@router.post("/", response_model=Customer)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if customer with this email already exists
    existing_customer = db.query(Customer).filter(
        Customer.email == customer.email
    ).first()

    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")

    # Create new customer
    db_customer = Customer(
        company_name=customer.company_name,
        contact_person=customer.contact_person,
        email=customer.email,
        phone=customer.phone,
        address_line1=customer.address_line1,
        address_line2=customer.address_line2,
        city=customer.city,
        state_province=customer.state_province,
        postal_code=customer.postal_code,
        country=customer.country,
        notes=customer.notes
        # status defaults to 'active' in the model
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=CustomerListResponse)
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by company name, contact person, or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Customer).filter(Customer.is_archived == False)

    # Add search functionality
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Customer.company_name.ilike(search_filter),
                Customer.contact_person.ilike(search_filter),
                Customer.email.ilike(search_filter)
            )
        )

    # Get total count for pagination
    total = query.count()

    # Apply pagination
    customers = query.offset((page - 1) * limit).limit(limit).all()

    return CustomerListResponse(
        items=customers,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit  # Ceiling division
    )

@router.get("/{customer_id}", response_model=Customer)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_archived == False
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer

@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_archived == False
    ).first()

    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check if email is being updated and if it already exists for another customer
    if customer.email and customer.email != db_customer.email:
        existing_customer = db.query(Customer).filter(
            Customer.email == customer.email,
            Customer.id != customer_id
        ).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Customer with this email already exists")

    # Update fields that are provided
    update_data = customer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)

    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.is_archived == False
    ).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Soft delete by setting is_archived to True
    customer.is_archived = True
    customer.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Customer deleted successfully"}