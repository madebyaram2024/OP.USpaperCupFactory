# This file makes models a Python package
# Import all models to ensure they are registered with SQLAlchemy Base

from .simple_user import SimpleUser
from .simple_work_order import SimpleWorkOrder, WorkOrderFile, WorkOrderUpdate

__all__ = ['SimpleUser', 'SimpleWorkOrder', 'WorkOrderFile', 'WorkOrderUpdate']