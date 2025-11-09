from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...models.work_order import WorkOrderStatus, Priority
from ...schemas.work_order import (
    WorkOrder, WorkOrderCreate, WorkOrderUpdate, WorkOrderDetail,
    WorkOrderListResponse, WorkOrderStats, WorkOrderStatusUpdate,
    ProductionQueue
)
from ...services.work_order_service import WorkOrderService
from ...api.v1.auth import get_current_active_user
from ...schemas.user import User
from ...database import get_db

router = APIRouter()


@router.post("/", response_model=WorkOrder, status_code=201)
def create_work_order(
    work_order: WorkOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new work order."""
    work_order_service = WorkOrderService(db)
    try:
        new_work_order = work_order_service.create_work_order(work_order, current_user.id)
        return new_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=WorkOrderListResponse)
def get_work_orders(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by work order number, product type, or customer"),
    status: Optional[WorkOrderStatus] = Query(None, description="Filter by status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    date_from: Optional[datetime] = Query(None, description="Filter orders from date"),
    date_to: Optional[datetime] = Query(None, description="Filter orders to date"),
    sort_by: str = Query("order_date", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work orders with filtering and pagination."""
    work_order_service = WorkOrderService(db)
    skip = (page - 1) * limit

    work_orders, total = work_order_service.get_work_orders(
        skip=skip,
        limit=limit,
        search=search,
        status=status,
        customer_id=customer_id,
        priority=priority,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return WorkOrderListResponse(
        items=work_orders,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/stats", response_model=WorkOrderStats)
def get_work_order_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work order statistics and dashboard data."""
    work_order_service = WorkOrderService(db)
    stats = work_order_service.get_work_order_statistics()
    return WorkOrderStats(**stats)


@router.get("/queue", response_model=ProductionQueue)
def get_production_queue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current production queue organized by status."""
    work_order_service = WorkOrderService(db)
    queue = work_order_service.get_production_queue()
    return ProductionQueue(**queue)


@router.get("/{work_order_id}", response_model=WorkOrderDetail)
def get_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work order by ID with full details."""
    work_order_service = WorkOrderService(db)
    work_order = work_order_service.get_work_order(work_order_id)

    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")

    # TODO: Add production schedule and status updates relationships
    return WorkOrderDetail(
        **work_order.__dict__,
        production_schedule=[],
        status_updates=[]
    )


@router.get("/number/{work_order_number}", response_model=WorkOrderDetail)
def get_work_order_by_number(
    work_order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get work order by work order number."""
    work_order_service = WorkOrderService(db)
    work_order = work_order_service.get_work_order_by_number(work_order_number)

    if not work_order:
        raise HTTPException(status_code=404, detail="Work order not found")

    return WorkOrderDetail(
        **work_order.__dict__,
        production_schedule=[],
        status_updates=[]
    )


@router.put("/{work_order_id}", response_model=WorkOrder)
def update_work_order(
    work_order_id: int,
    work_order: WorkOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update work order details."""
    work_order_service = WorkOrderService(db)
    try:
        updated_work_order = work_order_service.update_work_order(work_order_id, work_order, current_user.id)
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{work_order_id}/status", response_model=WorkOrder)
def update_work_order_status(
    work_order_id: int,
    status_update: WorkOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update work order status (creates audit trail)."""
    work_order_service = WorkOrderService(db)
    try:
        updated_work_order = work_order_service.update_work_order_status(
            work_order_id, status_update, current_user.id
        )
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{work_order_id}/approve", response_model=WorkOrder)
def approve_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve work order for production."""
    work_order_service = WorkOrderService(db)
    status_update = WorkOrderStatusUpdate(
        status=WorkOrderStatus.APPROVED.value,
        notes="Work order approved for production"
    )
    try:
        updated_work_order = work_order_service.update_work_order_status(
            work_order_id, status_update, current_user.id
        )
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{work_order_id}/start-production", response_model=WorkOrder)
def start_production(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start production for work order."""
    work_order_service = WorkOrderService(db)
    status_update = WorkOrderStatusUpdate(
        status=WorkOrderStatus.IN_PRODUCTION.value,
        notes="Production started"
    )
    try:
        updated_work_order = work_order_service.update_work_order_status(
            work_order_id, status_update, current_user.id
        )
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{work_order_id}/complete-production", response_model=WorkOrder)
def complete_production(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark production as complete and move to quality check."""
    work_order_service = WorkOrderService(db)
    status_update = WorkOrderStatusUpdate(
        status=WorkOrderStatus.PRODUCTION_COMPLETE.value,
        notes="Production completed, moving to quality check"
    )
    try:
        updated_work_order = work_order_service.update_work_order_status(
            work_order_id, status_update, current_user.id
        )
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{work_order_id}/pass-quality-check", response_model=WorkOrder)
def pass_quality_check(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pass quality check and move to shipping."""
    work_order_service = WorkOrderService(db)
    status_update = WorkOrderStatusUpdate(
        status=WorkOrderStatus.SHIPPED.value,
        notes="Quality check passed, ready for shipping"
    )
    try:
        updated_work_order = work_order_service.update_work_order_status(
            work_order_id, status_update, current_user.id
        )
        if not updated_work_order:
            raise HTTPException(status_code=404, detail="Work order not found")
        return updated_work_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{work_order_id}")
def delete_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete work order (only allowed for draft/pending orders)."""
    work_order_service = WorkOrderService(db)
    try:
        success = work_order_service.delete_work_order(work_order_id)
        if not success:
            raise HTTPException(status_code=404, detail="Work order not found")
        return {"message": "Work order deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))