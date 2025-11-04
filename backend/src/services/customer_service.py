from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import uuid
from ..models.customer import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, db: Session):
        self.db = db

    def create_customer(self, customer_data: CustomerCreate, user_id: Optional[uuid.UUID] = None) -> Customer:
        """Create a new customer"""
        # Check if customer with this email already exists
        existing_customer = self.db.query(Customer).filter(Customer.email == customer_data.email).first()
        if existing_customer:
            raise ValueError("A customer with this email already exists")
        
        # Create new customer
        db_customer = Customer(
            company_name=customer_data.company_name,
            contact_person=customer_data.contact_person,
            email=customer_data.email,
            phone=customer_data.phone,
            address_line1=customer_data.address_line1,
            address_line2=customer_data.address_line2,
            city=customer_data.city,
            state_province=customer_data.state_province,
            postal_code=customer_data.postal_code,
            country=customer_data.country,
            notes=customer_data.notes,
            created_by=user_id,
            updated_by=user_id
            # status defaults to 'active' in the model
            # active_orders_count and total_orders_count default to 0 in the model
            # created_at and updated_at have defaults in the model
        )
        
        try:
            self.db.add(db_customer)
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            self.db.rollback()
            raise ValueError("A customer with this email already exists")

    def get_customer(self, customer_id: uuid.UUID) -> Optional[Customer]:
        """Get a customer by ID"""
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def get_customers(
        self, 
        search: Optional[str] = None, 
        status: Optional[str] = None, 
        skip: int = 0, 
        limit: int = 50
    ) -> tuple[List[Customer], int]:
        """Get a list of customers with optional search and filtering"""
        query = self.db.query(Customer)
        
        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.company_name.ilike(search_filter)) |
                (Customer.contact_person.ilike(search_filter)) |
                (Customer.email.ilike(search_filter)) |
                (Customer.city.ilike(search_filter))
            )
        
        # Apply status filter if provided
        if status and status != 'all':
            query = query.filter(Customer.status == status)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        customers = query.offset(skip).limit(limit).all()
        
        return customers, total

    def update_customer(self, customer_id: uuid.UUID, customer_data: CustomerUpdate, user_id: Optional[uuid.UUID] = None) -> Optional[Customer]:
        """Update an existing customer"""
        db_customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not db_customer:
            return None
            
        # Check if email is being updated and if it already exists for another customer
        if customer_data.email and customer_data.email != db_customer.email:
            existing_customer = self.db.query(Customer).filter(
                Customer.email == customer_data.email,
                Customer.id != customer_id
            ).first()
            if existing_customer:
                raise ValueError("A customer with this email already exists")
        
        # Update customer fields
        for field, value in customer_data.dict(exclude_unset=True).items():
            setattr(db_customer, field, value)
        
        db_customer.updated_by = user_id
        
        try:
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            self.db.rollback()
            raise ValueError("A customer with this email already exists")

    def archive_customer(self, customer_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> bool:
        """Archive a customer by ID"""
        db_customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not db_customer:
            return False
            
        # Check if customer has active orders (this would require checking work orders)
        # For now, we'll implement the basic archiving logic
        # In a real implementation, you'd need to check for active work orders
        
        db_customer.status = "archived"
        db_customer.updated_by = user_id
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def get_customer_detail(self, customer_id: uuid.UUID):
        """Get detailed customer information including order history"""
        customer = self.db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            return None
            
        # In a real implementation, this would include order history and activity
        # For now, just return the customer
        return customer