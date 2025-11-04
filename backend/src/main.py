from fastapi import FastAPI
from .api.v1.customers import router as customers_router

app = FastAPI(title="Customer Management API", version="1.0.0")

# Include API routers
app.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])

@app.get("/")
def read_root():
    return {"message": "Customer Management API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}