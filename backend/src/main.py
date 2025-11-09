from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.simple_work_orders import router as simple_work_orders_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="USPC Factory - Simple Work Order System",
    version="1.0.0",
    description="Simple custom cup manufacturing workflow management - NO AUTH REQUIRED"
)

# Add CORS middleware - allow everything for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include simple work order router - NO AUTHENTICATION NEEDED
app.include_router(simple_work_orders_router, prefix="/api/v1/simple-work-orders", tags=["simple-work-orders"])

logger.info("Simple Work Order system started - NO auth required")

@app.get("/", response_class=HTMLResponse)
def home_page():
    """Simple home page that redirects to dashboard."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>USPC Factory - Work Orders</title>
        <meta http-equiv="refresh" content="0; url=/api/v1/simple-work-orders/">
    </head>
    <body>
        <h1>🏭 USPC Factory</h1>
        <p>Redirecting to work order dashboard...</p>
        <p>If not redirected, <a href="/api/v1/simple-work-orders/">click here</a></p>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "Simple Work Order Management"}

logger.info("Simple USPC Factory Work Order System started successfully")