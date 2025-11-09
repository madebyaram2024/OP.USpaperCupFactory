from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from .api.v1.simple_work_orders import router as simple_work_orders_router
from .api.v1.simple_auth import router as simple_auth_router
import logging

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import models to ensure they are registered with SQLAlchemy
try:
    logger.info("Importing models...")
    from .models import SimpleUser, SimpleWorkOrder, WorkOrderFile, WorkOrderUpdate
    logger.info("Models imported successfully")
except Exception as e:
    logger.error(f"Error importing models: {e}")
    import traceback
    traceback.print_exc()

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
logger.info("Registering simple auth router at /api/v1/simple-auth")
app.include_router(simple_auth_router, prefix="/api/v1/simple-auth", tags=["simple-auth"])

# Include simple work order router
logger.info("Registering simple work orders router at /api/v1/simple-work-orders")
app.include_router(simple_work_orders_router, prefix="/api/v1/simple-work-orders", tags=["simple-work-orders"])

@app.on_event("startup")
async def startup_event():
    """Log all registered routes on startup"""
    logger.info("=" * 50)
    logger.info("Application startup complete")
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'methods'):
            logger.info(f"  {route.methods} {route.path}")
    logger.info("=" * 50)

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

@app.get("/debug/routes")
def list_routes():
    """Debug endpoint to list all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name
            })
    return {"routes": routes, "total": len(routes)}