from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...schemas.user import User, UserCreate, UserUpdate, UserListResponse
from ...services.user_service import UserService
from ...api.v1.auth import get_current_active_user, get_current_superuser
from ...database import get_db

router = APIRouter()


@router.get("/", response_model=UserListResponse)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by username, full name, or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can list users
):
    """Get a list of users (superuser only)."""
    user_service = UserService(db)
    skip = (page - 1) * limit

    users, total = user_service.get_users(
        skip=skip,
        limit=limit,
        search=search,
        is_active=is_active
    )

    return UserListResponse(
        items=users,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return current_user


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can get user details
):
    """Get user by ID (superuser only)."""
    user_service = UserService(db)
    user = user_service.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can create users
):
    """Create a new user (superuser only)."""
    user_service = UserService(db)
    try:
        user = user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me", response_model=User)
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information."""
    user_service = UserService(db)

    # Regular users can only update their own info, but cannot change is_active or is_superuser
    update_data = user_data.model_dump(exclude_unset=True)
    # Remove fields that regular users shouldn't be able to change
    update_data.pop('is_active', None)

    try:
        updated_user = user_service.update_user(current_user.id, UserUpdate(**update_data))
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can update other users
):
    """Update user by ID (superuser only)."""
    user_service = UserService(db)
    try:
        updated_user = user_service.update_user(user_id, user_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only superusers can delete users
):
    """Delete user by ID (superuser only)."""
    user_service = UserService(db)

    # Prevent users from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )

    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}