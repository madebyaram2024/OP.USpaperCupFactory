from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.customers import router as customers_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Customer Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
try:
    app.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
    logger.info("Customer router included successfully")
except Exception as e:
    logger.error(f"Error including router: {e}")

@app.get("/")
def read_root():
    return {"message": "Customer Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Startup event to ensure database is ready
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete")