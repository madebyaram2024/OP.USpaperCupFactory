# USPC Factory Work Order System - Quick Start Guide

Welcome to the USPC Factory Work Order Management System! This guide will help you get the application up and running.

## What This Application Does

This is a complete **Work Order Management System** for a US Paper Cup Factory that allows you to:
- Manage work orders from creation to shipping
- Track orders through different stages (design, approval, printing, production, shipping)
- Assign work to team members
- Upload and manage design files
- Manage users and permissions

## Prerequisites

- Python 3.11+
- PostgreSQL database (installed and running)

## Quick Start (Local Development)

### 1. Start PostgreSQL

Make sure PostgreSQL is running:

```bash
service postgresql start
```

### 2. Set Up the Database

The database should already be configured, but if you need to set it up from scratch:

```bash
# As postgres user, create the database and user
su - postgres -c "psql" <<EOF
CREATE DATABASE customer_management;
CREATE USER "user" WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE customer_management TO "user";
GRANT ALL ON SCHEMA public TO "user";
EOF
```

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Create Admin User

```bash
cd backend
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

from database import SessionLocal
from models.simple_user import SimpleUser
from security import get_password_hash
from datetime import datetime

db = SessionLocal()

# Delete existing admin if exists
db.query(SimpleUser).filter(SimpleUser.username == "admin").delete()
db.commit()

# Create admin user
admin = SimpleUser(
    username="admin",
    email="admin@uspcfactory.com",
    full_name="System Administrator",
    hashed_password=get_password_hash("admin123"),
    role="admin",
    is_active=True,
    is_admin=True,
    created_at=datetime.utcnow()
)

db.add(admin)
db.commit()
print("✅ Admin user created!")
print("   Username: admin")
print("   Password: admin123")
db.close()
EOF
```

### 6. Start the Backend Server

```bash
cd backend
python3 run_server.py
```

The server will start on `http://localhost:8000`

### 7. Access the Application

Open your browser and navigate to:

**http://localhost:8000**

You'll be redirected to the login page.

### 8. Log In

Use these credentials:
- **Username:** admin
- **Password:** admin123

**⚠️ IMPORTANT:** Change the admin password immediately after first login!

## Application Structure

```
OP.USpaperCupFactory/
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── models/       # Database models
│   │   ├── services/     # Business logic
│   │   ├── main.py       # Application entry point
│   │   └── database.py   # Database configuration
│   ├── migrations/       # Database migrations
│   ├── run_server.py     # Server startup script
│   └── requirements.txt  # Python dependencies
├── frontend/             # Frontend files
├── .env                  # Environment variables
└── docker-compose.yml    # Docker configuration
```

## Key Features

### Work Order Management
- **New Orders**: Create and view incoming orders
- **Design Stage**: Assign designers and upload design files
- **Approval**: Customer approval workflow
- **Printing**: Manage print jobs
- **Production**: Track manufacturing progress
- **Shipping**: Mark orders as shipped

### User Management
- Admin can create employee accounts
- Role-based access control
- User activation/deactivation

## API Endpoints

### Authentication
- `GET /api/v1/simple-auth/login` - Login page
- `POST /api/v1/simple-auth/login` - Login endpoint
- `GET /api/v1/simple-auth/logout` - Logout
- `GET /api/v1/simple-auth/register` - User registration (admin only)

### Work Orders
- `GET /api/v1/simple-work-orders/` - Dashboard
- `GET /api/v1/simple-work-orders/dashboard` - Dashboard data
- `POST /api/v1/simple-work-orders/create` - Create work order
- `POST /api/v1/simple-work-orders/{id}/status` - Update status
- `POST /api/v1/simple-work-orders/{id}/claim` - Claim work order
- `POST /api/v1/simple-work-orders/{id}/upload-file` - Upload file

### Health Check
- `GET /health` - API health check

## Environment Variables

The `.env` file contains:

```env
# Database Configuration
DB_USER=user
DB_PASSWORD=password

# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# Database URL
DATABASE_URL=postgresql://user:password@localhost:5432/customer_management

# Secret key for JWT
SECRET_KEY=development-secret-key-change-in-production-12345
```

**⚠️ For production:** Change the `SECRET_KEY` to a secure random value!

## Troubleshooting

### PostgreSQL won't start
```bash
# Fix SSL certificate permissions
chmod 640 /etc/ssl/private/ssl-cert-snakeoil.key
chown root:ssl-cert /etc/ssl/private/ssl-cert-snakeoil.key
usermod -a -G ssl-cert postgres

# Or disable SSL in postgresql.conf
sed -i "s/ssl = on/ssl = off/" /etc/postgresql/16/main/postgresql.conf
```

### Port 8000 is already in use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
```

### Database connection errors
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check database exists
su - postgres -c "psql -l | grep customer_management"
```

### Import errors
```bash
# Make sure you're in the backend directory
cd backend

# Reinstall dependencies
pip install -r requirements.txt
```

## Creating Additional Users

1. Log in as admin
2. Click "Register New User" button
3. Fill in the user details:
   - Username
   - Email
   - Full Name
   - Password
   - Role (employee or admin)
4. Click "Register User"

## Workflow

### Typical Work Order Flow:

1. **New Order** → Customer submits order with requirements
2. **Design** → Designer creates cup design
3. **Approval** → Customer approves design
4. **Print** → Print plates are created
5. **Production** → Cups are manufactured
6. **Shipping** → Order is shipped to customer

## Security Notes

- All passwords are hashed using bcrypt
- JWT tokens are used for authentication
- Sessions expire after inactivity
- Admin users can create other users
- Inactive users cannot log in

## Support

For issues or questions:
1. Check the logs in the terminal where the server is running
2. Check PostgreSQL logs: `/var/log/postgresql/postgresql-16-main.log`
3. Review the deployment guide: `COOLIFY_DEPLOYMENT.md`

## What's Next?

- Change the default admin password
- Create employee user accounts
- Start creating work orders
- Customize the workflow for your needs
- Set up proper backups for the database

---

**Happy Manufacturing! 🏭**
