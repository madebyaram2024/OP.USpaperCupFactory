from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..security import get_password_hash
from datetime import datetime


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user with this username already exists
        existing_user = self.db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        if existing_user:
            if existing_user.username == user_data.username:
                raise ValueError("A user with this username already exists")
            if existing_user.email == user_data.email:
                raise ValueError("A user with this email already exists")

        # Create new user
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            is_active=user_data.is_active
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Username or email already exists")

    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_users(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Get a list of users with optional search and filtering"""
        query = self.db.query(User)

        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_filter)) |
                (User.full_name.ilike(search_filter)) |
                (User.email.ilike(search_filter))
            )

        # Apply active filter if provided
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        users = query.offset(skip).limit(limit).all()

        return users, total

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user"""
        db_user = self.db.query(User).filter(User.id == user_id).first()

        if not db_user:
            return None

        # Check if username is being updated and if it already exists for another user
        if user_data.username and user_data.username != db_user.username:
            existing_user = self.db.query(User).filter(
                User.username == user_data.username,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("A user with this username already exists")

        # Check if email is being updated and if it already exists for another user
        if user_data.email and user_data.email != db_user.email:
            existing_user = self.db.query(User).filter(
                User.email == user_data.email,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("A user with this email already exists")

        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "password" and value:
                # Hash the new password
                setattr(db_user, "hashed_password", get_password_hash(value))
            else:
                setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Username or email already exists")

    def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID"""
        db_user = self.db.query(User).filter(User.id == user_id).first()

        if not db_user:
            return False

        try:
            self.db.delete(db_user)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        db_user = self.db.query(User).filter(User.id == user_id).first()

        if not db_user:
            return False

        try:
            db_user.last_login = datetime.utcnow()
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        db_user = self.db.query(User).filter(User.id == user_id).first()

        if not db_user:
            return False

        from ..security import verify_password, get_password_hash

        # Verify old password
        if not verify_password(old_password, db_user.hashed_password):
            raise ValueError("Current password is incorrect")

        # Set new password
        db_user.hashed_password = get_password_hash(new_password)

        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False