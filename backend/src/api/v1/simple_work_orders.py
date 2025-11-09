from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime

from ...services.simple_work_order_service import SimpleWorkOrderService
from ...api.v1.simple_auth import get_current_user_from_request
from ...database import get_db

router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    """Dashboard HTML page with authentication check."""
    # Check if user is logged in
    user = get_current_user_from_request(request, db)
    if not user:
        # Redirect to login page
        return RedirectResponse(url="/api/v1/simple-auth/login")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>USPC Factory - Work Orders</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #007bff; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
            .header h1 {{ margin: 0; }}
            .user-info {{ color: white; }}
            .status-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
            .status-section h2 {{ margin-top: 0; color: #333; }}
            .order-card {{
                background: #f9f9f9;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
            }}
            .order-card h4 {{ margin: 0 0 10px 0; }}
            .assigned {{ color: #28a745; font-weight: bold; }}
            .btn {{
                background: #007bff;
                color: white;
                padding: 8px 15px;
                border: none;
                cursor: pointer;
                margin: 5px;
            }}
            .btn:hover {{ background: #0056b3; }}
            .btn-danger {{ background: #dc3545; }}
            .btn-danger:hover {{ background: #c82333; }}
            .design {{ border-left-color: #ffc107; }}
            .approval {{ border-left-color: #17a2b8; }}
            .print {{ border-left-color: #28a745; }}
            .production {{ border-left-color: #6f42c1; }}
            .shipping {{ border-left-color: #fd7e14; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏭 USPC Factory - Work Orders</h1>
            <div class="user-info">
                <strong>{user.full_name}</strong> ({user.role})
                <a href="/api/v1/simple-auth/logout" class="btn btn-danger" style="background: #dc3545;">Logout</a>
            </div>
        </div>

        <div id="dashboard-content">
            <p>Loading work orders...</p>
        </div>

        <script>
            // Load dashboard data
            fetch('/api/v1/simple-work-orders/dashboard')
                .then(response => response.json())
                .then(data => {
                    let html = '';

                    // New Orders
                    html += '<div class="status-section">';
                    html += '<h2>📝 New Orders</h2>';
                    if (data.new_orders.length === 0) {
                        html += '<p>No new orders</p>';
                    } else {
                        data.new_orders.forEach(order => {
                            html += `<div class="order-card">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                <p>${order.order_description}</p>
                                <button class="btn" onclick="startDesign(${order.id})">🎨 Start Design</button>
                                <button class="btn" onclick="viewDetails(${order.id})">📋 Details</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    // Design Stage
                    html += '<div class="status-section">';
                    html += '<h2>🎨 Design Stage</h2>';
                    if (data.design.length === 0) {
                        html += '<p>No orders in design</p>';
                    } else {
                        data.design.forEach(order => {
                            html += `<div class="order-card design">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                ${order.assigned_to ? `<p class="assigned">Assigned to: ${order.assigned_to}</p>` : '<button class="btn" onclick="claimDesign(' + order.id + ')">Claim Design</button>'}
                                <button class="btn" onclick="designComplete(${order.id})">✅ Design Complete</button>
                                <button class="btn" onclick="uploadFile(${order.id})">📁 Upload Files</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    // Approval Stage
                    html += '<div class="status-section">';
                    html += '<h2>👤 Customer Approval</h2>';
                    if (data.approval.length === 0) {
                        html += '<p>No orders awaiting approval</p>';
                    } else {
                        data.approval.forEach(order => {
                            html += `<div class="order-card approval">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                <button class="btn" onclick="approved(${order.id})">✅ Approved</button>
                                <button class="btn" onclick="viewFiles(${order.id})">📄 View Files</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    // Print Stage
                    html += '<div class="status-section">';
                    html += '<h2>🖨️ Printing</h2>';
                    if (data.print.length === 0) {
                        html += '<p>No orders in printing</p>';
                    } else {
                        data.print.forEach(order => {
                            html += `<div class="order-card print">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                ${order.assigned_to ? `<p class="assigned">Assigned to: ${order.assigned_to}</p>` : '<button class="btn" onclick="claimPrint(' + order.id + ')">Claim Print Job</button>'}
                                <button class="btn" onclick="printComplete(${order.id})">✅ Printing Complete</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    // Production Stage
                    html += '<div class="status-section">';
                    html += '<h2>🏭 Production</h2>';
                    if (data.production.length === 0) {
                        html += '<p>No orders in production</p>';
                    } else {
                        data.production.forEach(order => {
                            html += `<div class="order-card production">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                <button class="btn" onclick="productionComplete(${order.id})">✅ Production Complete</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    // Shipping
                    html += '<div class="status-section">';
                    html += '<h2>📦 Shipping</h2>';
                    if (data.shipping.length === 0) {
                        html += '<p>No orders ready for shipping</p>';
                    } else {
                        data.shipping.forEach(order => {
                            html += `<div class="order-card shipping">
                                <h4>${order.customer_name} - ${order.quantity} units</h4>
                                <button class="btn" onclick="shipped(${order.id})">✅ Mark as Shipped</button>
                            </div>`;
                        });
                    }
                    html += '</div>';

                    document.getElementById('dashboard-content').innerHTML = html;
                });

            // Simple API call functions
            function startDesign(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'design', notes: 'Started design work'})
                });
                location.reload();
            }

            function claimDesign(orderId) {
                const personName = prompt('Enter your name:');
                if (personName) {
                    fetch(`/api/v1/simple-work-orders/${orderId}/claim`, {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({person_name: personName})
                    });
                    location.reload();
                }
            }

            function designComplete(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'approval', notes: 'Design ready for customer approval'})
                });
                location.reload();
            }

            function approved(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'print', notes: 'Customer approved - ready for printing'})
                });
                location.reload();
            }

            function printComplete(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'production', notes: 'Printing complete - ready for cup production'})
                });
                location.reload();
            }

            function productionComplete(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'shipping', notes: 'Cups produced - ready for shipping'})
                });
                location.reload();
            }

            function shipped(orderId) {
                fetch(`/api/v1/simple-work-orders/${orderId}/status`, {
                    method: 'PATCH',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status: 'completed', notes: 'Order shipped to customer'})
                });
                location.reload();
            }
        </script>

        // Admin Panel functionality (only for admin users)
        {"<button id='admin-panel-btn' onclick='toggleAdminPanel()' style='position: fixed; top: 80px; right: 20px; background: #28a745; color: white; padding: 10px; border-radius: 5px; cursor: pointer; z-index: 1000;'>👤 Admin Panel</button>" if user.is_admin else ""}

        {"<div id='admin-panel' style='position: fixed; top: 120px; right: 20px; background: white; border: 1px solid #ddd; border-radius: 5px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); z-index: 1000; width: 300px; display: none;'>" if user.is_admin else ""}
            <h3>👤 Admin Panel</h3>
            <button class="btn" onclick="showCreateUserForm()">➕ Create User</button>
            <button class="btn" onclick="showUserList()">📋 Manage Users</button>
            <button class="btn btn-danger" onclick="toggleAdminPanel()">❌</button>

            <!-- Create User Form -->
            <div id="create-user-form" style="display: none; margin-top: 15px;">
                <h4>Create New User</h4>
                <form id="createUserForm">
                    <div style="margin-bottom: 10px;">
                        <label>Full Name: <input type="text" id="fullName" name="fullName" required style="width: 100%; padding: 8px; box-sizing: border-box;"></label>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Username: <input type="text" id="username" name="username" required style="width: 100%; padding: 8px; box-sizing: border-box;"></label>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Email: <input type="email" id="email" name="email" required style="width: 100%; padding: 8px; box-sizing: border-box;"></label>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Password: <input type="password" id="password" name="password" required style="width: 100%; padding: 8px; box-sizing: border-box;"></label>
                    </div>
                    <div style="margin-bottom: 10px;">
                        <label>Role:
                            <select name="role" id="role" style="width: 100%; padding: 8px; box-sizing: border-box;">
                                <option value="employee">Employee</option>
                                <option value="designer">Designer</option>
                                <option value="printer">Printer</option>
                            </select>
                        </label>
                    </div>
                    <button type="submit" class="btn">Create User</button>
                    <button type="button" class="btn btn-danger" onclick="hideCreateUserForm()">Cancel</button>
                </form>
            </div>

            <!-- User List -->
            <div id="user-list" style="display: none; margin-top: 15px;">
                <h4>Manage Users</h4>
                <div id="users-content">Loading users...</div>
            </div>
        </div>

        <script>
            // Existing functions...

            // Admin Panel functions
            function toggleAdminPanel() {
                const panel = document.getElementById('admin-panel');
                if (panel.style.display === 'none') {
                    panel.style.display = 'block';
                } else {
                    panel.style.display = 'none';
                }
            }

            function showCreateUserForm() {
                document.getElementById('create-user-form').style.display = 'block';
                document.getElementById('user-list').style.display = 'none';
            }

            function showUserList() {
                document.getElementById('user-list').style.display = 'block';
                document.getElementById('create-user-form').style.display = 'none';
                loadUsers();
            }

            function hideCreateUserForm() {
                document.getElementById('create-user-form').style.display = 'none';
            }

            function loadUsers() {
                fetch('/api/v1/simple-auth/users')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            let html = '<h5>All Users:</h5>';
                            data.users.forEach(user => {
                                html += `
                                    <div style="background: #f8f9f9; padding: 10px; margin-bottom: 5px; border-radius: 3px;">
                                    <strong>${user.full_name}</strong> (${user.role})
                                    <br><small>${user.email}</small>
                                    <button class="btn btn-danger btn-sm" onclick="deactivateUser(${user.id})">Deactivate</button>
                                </div>`;
                            });
                            document.getElementById('users-content').innerHTML = html;
                        } else {
                            document.getElementById('users-content').innerHTML = 'Error loading users';
                        }
                    });
            }

            function createUser(formData) {
                fetch('/api/v1/simple-auth/create-user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('User created successfully!');
                        hideCreateUserForm();
                        loadUsers();
                    } else {
                        alert('Error: ' + data.error);
                    }
                });
            }

            function deactivateUser(userId) {
                if (confirm('Are you sure you want to deactivate this user?')) {
                    fetch(`/api/v1/simple-auth/deactivate-user/${userId}`, {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('User deactivated successfully!');
                            loadUsers();
                        } else {
                            alert('Error: ' + data.error);
                        }
                    });
                }
            }

            // Handle create user form submission
            document.getElementById('createUserForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = {
                    fullName: document.getElementById('fullName').value,
                    username: document.getElementById('username').value,
                    email: document.getElementById('email').value,
                    password: document.getElementById('password').value,
                    role: document.getElementById('role').value
                };
                createUser(formData);
            });
        </script>
    </body>
    </html>
    """


@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard data organized by status."""
    service = SimpleWorkOrderService(db)
    return service.get_dashboard_data()


@router.post("/create")
def create_work_order(
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    order_description: str = Form(...),
    quantity: int = Form(...),
    special_notes: str = Form(""),
    db: Session = Depends(get_db)
):
    """Create a new work order - super simple form."""
    service = SimpleWorkOrderService(db)
    try:
        work_order = service.create_work_order(
            customer_name=customer_name,
            customer_email=customer_email,
            order_description=order_description,
            quantity=quantity,
            special_notes=special_notes
        )
        return {"success": True, "order_id": work_order.id, "message": "Work order created successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.patch("/{order_id}/status")
def update_status(
    order_id: int,
    status_data: dict,
    db: Session = Depends(get_db)
):
    """Update work order status."""
    service = SimpleWorkOrderService(db)
    try:
        work_order = service.update_status(
            order_id=order_id,
            new_status=status_data.get("status"),
            notes=status_data.get("notes"),
            updated_by=status_data.get("updated_by", "Unknown")
        )
        return {"success": True, "message": f"Status updated to {work_order.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{order_id}/claim")
def claim_task(
    order_id: int,
    claim_data: dict,
    db: Session = Depends(get_db)
):
    """Claim responsibility for a work order."""
    service = SimpleWorkOrderService(db)
    try:
        work_order = service.claim_task(
            order_id=order_id,
            person_name=claim_data.get("person_name", "Unknown")
        )
        return {"success": True, "message": f"Task claimed by {work_order.assigned_to}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{order_id}/upload")
async def upload_file(
    order_id: int,
    file: UploadFile = File(...),
    file_type: str = Form(...),
    uploaded_by: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload a file for a work order."""
    service = SimpleWorkOrderService(db)

    try:
        # Create file path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else ''
        safe_filename = f"{timestamp}_{file.filename}" if file.filename else f"{timestamp}_{order_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Add to database
        work_order_file = service.add_file(
            work_order_id=order_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            uploaded_by=uploaded_by
        )

        return {"success": True, "message": f"File uploaded successfully", "file_id": work_order_file.id}

    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/{order_id}/files")
def get_order_files(order_id: int, db: Session = Depends(get_db)):
    """Get all files for a work order."""
    service = SimpleWorkOrderService(db)
    try:
        files = service.get_order_files(order_id)
        return {"success": True, "files": [{"name": f.file_name, "type": f.file_type, "uploaded_by": f.uploaded_by, "uploaded_at": f.uploaded_at} for f in files]}
    except Exception as e:
        return {"success": False, "error": str(e)}