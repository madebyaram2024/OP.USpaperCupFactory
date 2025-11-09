from fastapi import APIRouter, HTTPException, status, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from ...models.simple_user import SimpleUser
from ...security import verify_password, create_access_token, verify_token, get_password_hash
from ...database import get_db

router = APIRouter()

# Simple JWT for the system
SECRET_KEY = "simple-uspc-secret-key-change-in-production"

def create_simple_token(username: str):
    """Create a simple JWT token."""
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_simple_token(token: str) -> str:
    """Verify a simple JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")  # Changed from "sub" to match create_simple_token
        if username is None:
            return None
        return username
    except Exception as e:  # Changed from jwt.PyJWTError to generic Exception
        import logging
        logging.error(f"Token verification failed: {str(e)}")
        return None


@router.get("/login", response_class=HTMLResponse)
def login_page():
    """Simple login page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>USPC Factory - Login</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f5f5f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 400px; }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo h1 { color: #007bff; margin: 0; font-size: 28px; }
            .logo p { color: #666; margin: 5px 0; font-size: 14px; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            .form-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; box-sizing: border-box; }
            .form-group input:focus { outline: none; border-color: #007bff; }
            .login-btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
            .login-btn:hover { background: #0056b3; }
            .error { color: #dc3545; margin-top: 10px; text-align: center; }
            .success { color: #28a745; margin-top: 10px; text-align: center; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <div class="logo">
                <h1>🏭 USPC Factory</h1>
                <p>Work Order Management System</p>
            </div>

            <form id="loginForm">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit" class="login-btn">🔐 Login</button>
                <div id="message"></div>
            </form>
        </div>

        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const formData = new FormData(e.target);
                const data = {
                    username: formData.get('username'),
                    password: formData.get('password')
                };

                try {
                    const response = await fetch('/api/v1/simple-auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });

                    const result = await response.json();

                    if (result.success) {
                        // Store token and redirect
                        localStorage.setItem('auth_token', result.token);
                        document.getElementById('message').innerHTML = '<div class="success">✅ Login successful! Redirecting...</div>';
                        setTimeout(() => {
                            window.location.href = '/api/v1/simple-work-orders/';
                        }, 1000);
                    } else {
                        document.getElementById('message').innerHTML = '<div class="error">❌ ' + result.error + '</div>';
                    }
                } catch (error) {
                    document.getElementById('message').innerHTML = '<div class="error">❌ Login failed. Please try again.</div>';
                }
            });
        </script>
    </body>
    </html>
    """


@router.post("/login")
async def login_user(request: Request, db: Session = Depends(get_db)):
    """Simple login endpoint."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        logger.info(f"Login attempt for username: {username}")

        # Find user
        try:
            user = db.query(SimpleUser).filter(SimpleUser.username == username).first()
            logger.info(f"User query completed, found: {user is not None}")
        except Exception as e:
            logger.error(f"Database query error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Database error: {str(e)}"}

        if not user:
            logger.warning(f"User not found: {username}")
            return {"success": False, "error": "Invalid username or password"}

        # Verify password
        try:
            logger.info(f"Verifying password for user: {username}")
            password_valid = verify_password(password, user.hashed_password)
            logger.info(f"Password verification result: {password_valid}")
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Password verification failed: {str(e)}"}

        if not password_valid:
            logger.warning(f"Invalid password for user: {username}")
            return {"success": False, "error": "Invalid username or password"}

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {username}")
            return {"success": False, "error": "Account is disabled"}

        # Update last login
        try:
            user.last_login = datetime.utcnow()
            db.commit()
            logger.info(f"Updated last login for user: {username}")
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            # Don't fail login just because of this
            pass

        # Create token
        try:
            token = create_simple_token(user.username)
            logger.info(f"Token created for user: {username}")
        except Exception as e:
            logger.error(f"Token creation error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": f"Token creation failed: {str(e)}"}

        logger.info(f"Login successful for user: {username}")
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role,
                "is_admin": user.is_admin
            }
        }

    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": f"Login failed: {str(e)}"}


@router.get("/logout")
def logout_user():
    """Simple logout - just returns success (client-side handles token removal)."""
    return {"success": True, "message": "Logged out successfully"}


def get_current_user_from_request(request: Request, db: Session = Depends(get_db)):
    """Helper to get current user from request."""
    # Get token from Authorization header or cookie
    token = None
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    elif "token" in request.query:
        token = request.query["token"]
    elif "auth_token" in request.cookies:
        token = request.cookies["auth_token"]

    if not token:
        return None

    # Verify token
    username = verify_simple_token(token)
    if not username:
        return None

    # Get user from database
    user = db.query(SimpleUser).filter(SimpleUser.username == username).first()
    return user


def require_auth_or_redirect(request: Request, db: Session = Depends(get_db)):
    """Check authentication or return redirect to login."""
    user = get_current_user_from_request(request, db)

    if not user:
        return None, RedirectResponse(url="/api/v1/simple-auth/login")

    return user, None


# Simple dependency that can be used in other routes
def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """Get current user (optional - returns None if not authenticated)."""
    return get_current_user_from_request(request, db)


# Admin-only endpoints
def require_admin(request: Request, db: Session = Depends(get_db)):
    """Require admin authentication."""
    user = get_current_user_from_request(request, db)
    if not user or not user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/admin/create-user")
async def create_user(request: Request, db: Session = Depends(get_db)):
    """Create a new user (admin only)."""
    try:
        # Verify admin access
        admin = require_admin(request, db)

        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        full_name = data.get("full_name")
        role = data.get("role", "employee")
        is_admin = data.get("is_admin", False)

        # Validate required fields
        if not all([username, password, email, full_name]):
            return {"success": False, "error": "Missing required fields"}

        # Check if username already exists
        existing_user = db.query(SimpleUser).filter(SimpleUser.username == username).first()
        if existing_user:
            return {"success": False, "error": "Username already exists"}

        # Check if email already exists
        existing_email = db.query(SimpleUser).filter(SimpleUser.email == email).first()
        if existing_email:
            return {"success": False, "error": "Email already exists"}

        # Create new user
        new_user = SimpleUser(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            role=role,
            is_admin=is_admin,
            is_active=True,
            created_at=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "success": True,
            "message": f"User '{username}' created successfully",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email,
                "full_name": new_user.full_name,
                "role": new_user.role,
                "is_admin": new_user.is_admin,
                "is_active": new_user.is_active
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": f"Failed to create user: {str(e)}"}


@router.get("/admin/users")
def list_users(request: Request, db: Session = Depends(get_db)):
    """List all users (admin only)."""
    try:
        # Verify admin access
        admin = require_admin(request, db)

        users = db.query(SimpleUser).order_by(SimpleUser.created_at.desc()).all()

        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_admin": user.is_admin,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "last_login": user.last_login.isoformat() if user.last_login else None
            })

        return {"success": True, "users": user_list}

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": f"Failed to list users: {str(e)}"}


@router.post("/admin/toggle-user/{user_id}")
def toggle_user_status(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Toggle user active status (admin only)."""
    try:
        # Verify admin access
        admin = require_admin(request, db)

        user = db.query(SimpleUser).filter(SimpleUser.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        # Don't allow deactivating yourself
        if user.id == admin.id:
            return {"success": False, "error": "Cannot deactivate your own account"}

        user.is_active = not user.is_active
        db.commit()

        status = "activated" if user.is_active else "deactivated"
        return {
            "success": True,
            "message": f"User '{user.username}' {status} successfully",
            "is_active": user.is_active
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": f"Failed to toggle user status: {str(e)}"}


@router.post("/admin/reset-password/{user_id}")
async def reset_user_password(user_id: int, request: Request, db: Session = Depends(get_db)):
    """Reset user password (admin only)."""
    try:
        # Verify admin access
        admin = require_admin(request, db)

        data = await request.json()
        new_password = data.get("password")

        if not new_password or len(new_password) < 6:
            return {"success": False, "error": "Password must be at least 6 characters long"}

        user = db.query(SimpleUser).filter(SimpleUser.id == user_id).first()
        if not user:
            return {"success": False, "error": "User not found"}

        user.hashed_password = get_password_hash(new_password)
        db.commit()

        return {
            "success": True,
            "message": f"Password for '{user.username}' has been reset successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": f"Failed to reset password: {str(e)}"}