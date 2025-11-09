from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from ..models.work_order import WorkOrder, WorkOrderUpdate, ProductionSchedule, WorkOrderStatus, Priority
from ..models.customer import Customer
from ..schemas.work_order import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderStatusUpdate,
    ProductionScheduleUpdate, WorkOrderListResponse
)


class WorkOrderService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_work_order_number(self) -> str:
        """Generate a unique work order number."""
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Get the count for this month
        month_start = datetime(current_year, current_month, 1)
        if current_month == 12:
            month_end = datetime(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(current_year, current_month + 1, 1) - timedelta(days=1)

        count = self.db.query(WorkOrder).filter(
            WorkOrder.order_date.between(month_start, month_end)
        ).count()

        # Generate number like WO2024-0001
        return f"WO{current_year}-{count + 1:04d}"

    def create_work_order(self, work_order_data: WorkOrderCreate, user_id: int) -> WorkOrder:
        """Create a new work order."""
        # Validate customer exists
        customer = self.db.query(Customer).filter(Customer.id == work_order_data.customer_id).first()
        if not customer:
            raise ValueError(f"Customer with ID {work_order_data.customer_id} not found")

        # Calculate total amount if not provided
        total_amount = work_order_data.total_amount
        if not total_amount:
            total_amount = work_order_data.quantity * work_order_data.unit_price

        # Create work order
        db_work_order = WorkOrder(
            work_order_number=self._generate_work_order_number(),
            customer_id=work_order_data.customer_id,
            product_type=work_order_data.product_type,
            quantity=work_order_data.quantity,
            unit_price=work_order_data.unit_price,
            total_amount=total_amount,
            cup_size=work_order_data.cup_size,
            cup_type=work_order_data.cup_type,
            material=work_order_data.material,
            color=work_order_data.color,
            design_specifications=work_order_data.design_specifications,
            printing_requirements=work_order_data.printing_requirements,
            priority=work_order_data.priority,
            requested_delivery_date=work_order_data.requested_delivery_date,
            special_instructions=work_order_data.special_instructions,
            status=WorkOrderStatus.DRAFT,
            created_by=user_id,
            updated_by=user_id,
            order_date=datetime.utcnow()
        )

        try:
            self.db.add(db_work_order)
            self.db.commit()
            self.db.refresh(db_work_order)
            return db_work_order
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to create work order due to integrity constraint")

    def get_work_order(self, work_order_id: int) -> Optional[WorkOrder]:
        """Get a work order by ID with customer information."""
        return self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

    def get_work_order_by_number(self, work_order_number: str) -> Optional[WorkOrder]:
        """Get a work order by work order number."""
        return self.db.query(WorkOrder).filter(WorkOrder.work_order_number == work_order_number).first()

    def get_work_orders(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status: Optional[WorkOrderStatus] = None,
        customer_id: Optional[int] = None,
        priority: Optional[Priority] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "order_date",
        sort_order: str = "desc"
    ) -> Tuple[List[WorkOrder], int]:
        """Get work orders with filtering and pagination."""
        query = self.db.query(WorkOrder).join(Customer)

        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    WorkOrder.work_order_number.ilike(search_filter),
                    WorkOrder.product_type.ilike(search_filter),
                    Customer.company_name.ilike(search_filter),
                    Customer.contact_person.ilike(search_filter)
                )
            )

        if status:
            query = query.filter(WorkOrder.status == status)

        if customer_id:
            query = query.filter(WorkOrder.customer_id == customer_id)

        if priority:
            query = query.filter(WorkOrder.priority == priority)

        if date_from:
            query = query.filter(WorkOrder.order_date >= date_from)

        if date_to:
            query = query.filter(WorkOrder.order_date <= date_to)

        # Apply sorting
        sort_column = getattr(WorkOrder, sort_by, WorkOrder.order_date)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # Get total count
        total = query.count()

        # Apply pagination
        work_orders = query.offset(skip).limit(limit).all()

        return work_orders, total

    def update_work_order(self, work_order_id: int, work_order_data: WorkOrderUpdate, user_id: int) -> Optional[WorkOrder]:
        """Update an existing work order."""
        db_work_order = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

        if not db_work_order:
            return None

        # Validate customer if changing
        if work_order_data.customer_id and work_order_data.customer_id != db_work_order.customer_id:
            customer = self.db.query(Customer).filter(Customer.id == work_order_data.customer_id).first()
            if not customer:
                raise ValueError(f"Customer with ID {work_order_data.customer_id} not found")

        # Update fields
        update_data = work_order_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_work_order, field, value)

        # Recalculate total amount if quantity or unit price changed
        if 'quantity' in update_data or 'unit_price' in update_data:
            db_work_order.total_amount = db_work_order.quantity * db_work_order.unit_price

        db_work_order.updated_by = user_id
        db_work_order.updated_at = datetime.utcnow()

        try:
            self.db.commit()
            self.db.refresh(db_work_order)
            return db_work_order
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Failed to update work order due to integrity constraint")

    def update_work_order_status(self, work_order_id: int, status_update: WorkOrderStatusUpdate, user_id: int) -> Optional[WorkOrder]:
        """Update work order status and create audit trail."""
        db_work_order = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

        if not db_work_order:
            return None

        old_status = db_work_order.status
        new_status = WorkOrderStatus(status_update.status)

        # Validate status transitions
        if not self._is_valid_status_transition(old_status, new_status):
            raise ValueError(f"Invalid status transition from {old_status.value} to {new_status.value}")

        # Update status
        db_work_order.status = new_status
        db_work_order.updated_by = user_id
        db_work_order.updated_at = datetime.utcnow()

        # Update timestamp fields based on status
        self._update_status_timestamps(db_work_order, new_status)

        # Create audit trail
        work_order_update = WorkOrderUpdate(
            work_order_id=work_order_id,
            old_status=old_status,
            new_status=new_status,
            notes=status_update.notes,
            updated_by=user_id
        )
        self.db.add(work_order_update)

        try:
            self.db.commit()
            self.db.refresh(db_work_order)
            return db_work_order
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to update work order status: {str(e)}")

    def delete_work_order(self, work_order_id: int) -> bool:
        """Soft delete a work order."""
        db_work_order = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()

        if not db_work_order:
            return False

        # Only allow deletion of draft or pending orders
        if db_work_order.status not in [WorkOrderStatus.DRAFT, WorkOrderStatus.PENDING]:
            raise ValueError("Cannot delete work order that is in production or completed")

        db_work_order.is_active = False
        db_work_order.status = WorkOrderStatus.CANCELLED

        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def get_production_queue(self) -> dict:
        """Get current production queue organized by status."""
        scheduled = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.APPROVED,
            WorkOrder.is_active == True
        ).order_by(WorkOrder.priority.desc(), WorkOrder.requested_delivery_date.asc()).all()

        in_production = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.IN_PRODUCTION,
            WorkOrder.is_active == True
        ).order_by(WorkOrder.priority.desc(), WorkOrder.actual_production_start.asc()).all()

        quality_check = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.QUALITY_CHECK,
            WorkOrder.is_active == True
        ).order_by(WorkOrder.actual_production_complete.asc()).all()

        return {
            "scheduled": scheduled,
            "in_production": in_production,
            "quality_check": quality_check
        }

    def get_work_order_statistics(self) -> dict:
        """Get work order statistics."""
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        month_end = datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1], 23, 59, 59)

        # Total orders
        total_orders = self.db.query(WorkOrder).filter(WorkOrder.is_active == True).count()

        # Orders by status
        status_counts = {}
        for status in WorkOrderStatus:
            count = self.db.query(WorkOrder).filter(
                WorkOrder.status == status,
                WorkOrder.is_active == True
            ).count()
            status_counts[status.value] = count

        # Orders by priority
        priority_counts = {}
        for priority in Priority:
            count = self.db.query(WorkOrder).filter(
                WorkOrder.priority == priority,
                WorkOrder.is_active == True
            ).count()
            priority_counts[priority.value] = count

        # Pending and in production
        pending_orders = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.PENDING,
            WorkOrder.is_active == True
        ).count()

        in_production_orders = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.IN_PRODUCTION,
            WorkOrder.is_active == True
        ).count()

        # Completed this month
        completed_this_month = self.db.query(WorkOrder).filter(
            WorkOrder.status == WorkOrderStatus.DELIVERED,
            WorkOrder.delivery_date.between(month_start, month_end),
            WorkOrder.is_active == True
        ).count()

        # Total value of active orders
        total_value = self.db.query(WorkOrder).filter(
            WorkOrder.is_active == True,
            WorkOrder.status.in_([
                WorkOrderStatus.PENDING, WorkOrderStatus.APPROVED,
                WorkOrderStatus.IN_PRODUCTION, WorkOrderStatus.PRODUCTION_COMPLETE,
                WorkOrderStatus.QUALITY_CHECK
            ])
        ).with_entities(func.coalesce(func.sum(WorkOrder.total_amount), 0)).scalar()

        return {
            "total_orders": total_orders,
            "orders_by_status": status_counts,
            "orders_by_priority": priority_counts,
            "pending_orders": pending_orders,
            "in_production_orders": in_production_orders,
            "completed_this_month": completed_this_month,
            "total_value": total_value
        }

    def _is_valid_status_transition(self, old_status: WorkOrderStatus, new_status: WorkOrderStatus) -> bool:
        """Validate work order status transitions."""
        valid_transitions = {
            WorkOrderStatus.DRAFT: [WorkOrderStatus.PENDING, WorkOrderStatus.CANCELLED],
            WorkOrderStatus.PENDING: [WorkOrderStatus.APPROVED, WorkOrderStatus.CANCELLED, WorkOrderStatus.ON_HOLD],
            WorkOrderStatus.APPROVED: [WorkOrderStatus.IN_PRODUCTION, WorkOrderStatus.CANCELLED, WorkOrderStatus.ON_HOLD],
            WorkOrderStatus.IN_PRODUCTION: [WorkOrderStatus.PRODUCTION_COMPLETE, WorkOrderStatus.ON_HOLD, WorkOrderStatus.CANCELLED],
            WorkOrderStatus.PRODUCTION_COMPLETE: [WorkOrderStatus.QUALITY_CHECK, WorkOrderStatus.ON_HOLD],
            WorkOrderStatus.QUALITY_CHECK: [WorkOrderStatus.SHIPPED, WorkOrderStatus.IN_PRODUCTION],  # Return to production if fails QC
            WorkOrderStatus.SHIPPED: [WorkOrderStatus.DELIVERED],
            WorkOrderStatus.ON_HOLD: [WorkOrderStatus.PENDING, WorkOrderStatus.APPROVED, WorkOrderStatus.IN_PRODUCTION],
            WorkOrderStatus.DELIVERED: [],  # Final state
            WorkOrderStatus.CANCELLED: []   # Final state
        }

        return new_status in valid_transitions.get(old_status, [])

    def _update_status_timestamps(self, work_order: WorkOrder, new_status: WorkOrderStatus):
        """Update relevant timestamp fields based on status."""
        now = datetime.utcnow()

        if new_status == WorkOrderStatus.IN_PRODUCTION and not work_order.actual_production_start:
            work_order.actual_production_start = now
        elif new_status == WorkOrderStatus.PRODUCTION_COMPLETE and not work_order.actual_production_complete:
            work_order.actual_production_complete = now
        elif new_status == WorkOrderStatus.SHIPPED and not work_order.actual_ship_date:
            work_order.actual_ship_date = now
        elif new_status == WorkOrderStatus.DELIVERED and not work_order.delivery_date:
            work_order.delivery_date = now