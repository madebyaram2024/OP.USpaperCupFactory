from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ... import models
from ...schemas import Customer, CustomerCreate, CustomerUpdate, CustomerListResponse
from ...database import get_db
from sqlalchemy import or_, func

router = APIRouter()

@router.post("/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    # Check if customer with this email already exists
    existing_customer = db.query(models.Customer).filter(
        models.Customer.email == customer.email
    ).first()
    
    if existing_customer:
        raise HTTPException(status_code=400, detail="Customer with this email already exists")
    
    # Create new customer
    db_customer = models.Customer(
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
        notes=customer.notes,
        status=customer.status
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=schemas.CustomerListResponse)
def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by company name or email"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Customer).filter(models.Customer.is_archived == False)
    
    # Add search functionality
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                models.Customer.company_name.ilike(search_filter),
                models.Customer.contact_person.ilike(search_filter),
                models.Customer.email.ilike(search_filter)
            )
        )
    
    # Get total count for pagination
    total_count = query.count()
    
    # Apply pagination
    customers = query.offset(skip).limit(limit).all()
    
    return schemas.CustomerListResponse(
        items=customers,
        total_count=total_count,
        offset=skip,
        limit=limit
    )

@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.is_archived == False
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return customer

@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.is_archived == False
    ).first()
    
    if not db_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Update fields that are provided
    update_data = customer.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(
        models.Customer.id == customer_id,
        models.Customer.is_archived == False
    ).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Soft delete by setting is_archived to True
    customer.is_archived = True
    customer.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Customer deleted successfully"}