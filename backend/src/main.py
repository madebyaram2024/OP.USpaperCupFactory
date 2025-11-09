from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .api.v1.simple_work_orders import router as simple_work_orders_router
from .api.v1.simple_auth import router as simple_auth_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="USPC Factory - Simple Work Order System",
    version="1.0.0",
    description="Simple custom cup manufacturing workflow management with authentication"
)

# Add CORS middleware - allow everything for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include simple auth router
app.include_router(simple_auth_router, prefix="/api/v1/simple-auth", tags=["simple-auth"])

# Include simple work order router
app.include_router(simple_work_orders_router, prefix="/api/v1/simple-work-orders", tags=["simple-work-orders"])

logger.info("Simple Work Order system started with authentication")

@app.get("/", response_class=HTMLResponse)
def home_page():
    """Simple home page that redirects to dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>USPC Factory - Work Orders</title>
        <meta http-equiv="refresh" content="0; url=/api/v1/simple-auth/login">
    </head>
    <body>
        <h1>🏭 USPC Factory</h1>
        <p>Redirecting to login...</p>
        <p>If not redirected, <a href="/api/v1/simple-auth/login">click here</a></p>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "Simple Work Order Management"}

logger.info("Simple USPC Factory Work Order System started successfully")