from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from ..models.simple_work_order import SimpleWorkOrder, WorkOrderFile, WorkOrderUpdate


class SimpleWorkOrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_work_order(self, customer_name: str, customer_email: str, order_description: str,
                          quantity: int, special_notes: str = None, delivery_date: datetime = None) -> SimpleWorkOrder:
        """Create a new work order - super simple."""
        work_order = SimpleWorkOrder(
            customer_name=customer_name,
            customer_email=customer_email,
            order_description=order_description,
            quantity=quantity,
            special_notes=special_notes,
            delivery_date=delivery_date,
            status="new_order"
        )

        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)
        return work_order

    def get_all_orders(self) -> List[SimpleWorkOrder]:
        """Get all orders with their current status."""
        return self.db.query(SimpleWorkOrder).order_by(SimpleWorkOrder.created_at.desc()).all()

    def get_orders_by_status(self, status: str) -> List[SimpleWorkOrder]:
        """Get orders by specific status."""
        return self.db.query(SimpleWorkOrder).filter(SimpleWorkOrder.status == status).all()

    def claim_task(self, work_order_id: int, person_name: str) -> SimpleWorkOrder:
        """Someone clicks button to take responsibility for this stage."""
        work_order = self.db.query(SimpleWorkOrder).filter(SimpleWorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError("Work order not found")

        work_order.assigned_to = person_name
        work_order.assigned_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(work_order)
        return work_order

    def update_status(self, work_order_id: int, new_status: str, notes: str = None, updated_by: str = None) -> SimpleWorkOrder:
        """Update work order status and create update record."""
        work_order = self.db.query(SimpleWorkOrder).filter(SimpleWorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError("Work order not found")

        old_status = work_order.status
        work_order.status = new_status
        work_order.updated_at = datetime.utcnow()

        # If moving to next stage, clear assignment
        if new_status != old_status:
            work_order.assigned_to = None
            work_order.assigned_at = None

        # Create update record
        update_record = WorkOrderUpdate(
            work_order_id=work_order_id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            updated_by=updated_by or "System"
        )
        self.db.add(update_record)

        self.db.commit()
        self.db.refresh(work_order)
        return work_order

    def add_file(self, work_order_id: int, file_name: str, file_path: str, file_type: str, uploaded_by: str) -> WorkOrderFile:
        """Add a file to work order."""
        work_order_file = WorkOrderFile(
            work_order_id=work_order_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            uploaded_by=uploaded_by
        )

        self.db.add(work_order_file)
        self.db.commit()
        self.db.refresh(work_order_file)
        return work_order_file

    def get_order_files(self, work_order_id: int) -> List[WorkOrderFile]:
        """Get all files for a work order."""
        return self.db.query(WorkOrderFile).filter(WorkOrderFile.work_order_id == work_order_id).all()

    def get_order_updates(self, work_order_id: int) -> List[WorkOrderUpdate]:
        """Get all updates for a work order."""
        return self.db.query(WorkOrderUpdate).filter(WorkOrderUpdate.work_order_id == work_order_id).order_by(WorkOrderUpdate.updated_at.desc()).all()

    def notify_design_ready(self, work_order_id: int) -> SimpleWorkOrder:
        """Notify order creator that design is ready for client approval."""
        work_order = self.db.query(SimpleWorkOrder).filter(SimpleWorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError("Work order not found")

        work_order.order_creator_notified = True
        work_order.last_notification = datetime.utcnow()

        self.db.commit()
        self.db.refresh(work_order)
        return work_order

    def get_dashboard_data(self) -> dict:
        """Get simple dashboard data."""
        def serialize_order(order):
            """Convert SimpleWorkOrder to dict for JSON serialization."""
            return {
                "id": order.id,
                "customer_name": order.customer_name,
                "customer_email": order.customer_email,
                "order_description": order.order_description,
                "quantity": order.quantity,
                "special_notes": order.special_notes,
                "status": order.status,
                "assigned_to": order.assigned_to,
                "assigned_at": order.assigned_at.isoformat() if order.assigned_at else None,
                "order_creator_notified": order.order_creator_notified,
                "last_notification": order.last_notification.isoformat() if order.last_notification else None,
                "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "updated_at": order.updated_at.isoformat() if order.updated_at else None
            }

        return {
            "new_orders": [serialize_order(o) for o in self.get_orders_by_status("new_order")],
            "design": [serialize_order(o) for o in self.get_orders_by_status("design")],
            "approval": [serialize_order(o) for o in self.get_orders_by_status("approval")],
            "print": [serialize_order(o) for o in self.get_orders_by_status("print")],
            "production": [serialize_order(o) for o in self.get_orders_by_status("production")],
            "shipping": [serialize_order(o) for o in self.get_orders_by_status("shipping")]
        }

    # Simple status validation
    VALID_STATUSES = ["new_order", "design", "approval", "print", "production", "shipping"]

    def is_valid_status(self, status: str) -> bool:
        return status in self.VALID_STATUSES