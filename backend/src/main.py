from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.customers import router as customers_router
from .api.v1.auth import router as auth_router
from .api.v1.users import router as users_router
from .api.v1.work_orders import router as work_orders_router
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="USPC Factory Work Order Management API",
    version="1.0.0",
    description="Paper Cup Manufacturing Work Order Management System for USPC Factory Speckit"
)

# Add CORS middleware
# In production, set ALLOWED_ORIGINS environment variable to specific origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routers
try:
    # Public routes (no authentication required)
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["authentication"])

    # Protected routes (authentication required)
    app.include_router(work_orders_router, prefix="/api/v1/work-orders", tags=["work-orders"])
    app.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
    app.include_router(users_router, prefix="/api/v1/users", tags=["users"])

    logger.info("All routers included successfully")
    logger.info("Authentication endpoints: /api/v1/auth/*")
    logger.info("Work Order endpoints: /api/v1/work-orders/* (protected)")
    logger.info("Customer endpoints: /api/v1/customers/* (protected)")
    logger.info("User endpoints: /api/v1/users/* (protected)")
except Exception as e:
    logger.error(f"Error including router: {e}")

@app.get("/")
def read_root():
    return {
        "message": "USPC Factory Work Order Management API",
        "system": "Paper Cup Manufacturing Work Order Processing",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Startup event to ensure database is ready
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")