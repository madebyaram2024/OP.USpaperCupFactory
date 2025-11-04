import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..src.main import app
from ..src.database import Base


@pytest.fixture
def client():
    # Create an in-memory SQLite database for testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[app.router.dependencies[0]] = lambda: TestingSessionLocal()
    
    with TestClient(app) as test_client:
        yield test_client


def test_create_customer(client):
    # Test data
    customer_data = {
        "company_name": "Test Company",
        "contact_person": "John Doe",
        "email": "john@testcompany.com",
        "phone": "+1234567890",
        "address_line1": "123 Test St",
        "city": "Test City",
        "state_province": "TS",
        "postal_code": "12345",
        "country": "Test Country"
    }
    
    # Mock the customer service
    with patch('src.api.v1.customers.CustomerService') as mock_service:
        mock_customer = MagicMock()
        mock_customer.id = "12345678-1234-5678-1234-123456789012"
        mock_customer.company_name = customer_data["company_name"]
        mock_customer.contact_person = customer_data["contact_person"]
        mock_customer.email = customer_data["email"]
        mock_customer.phone = customer_data["phone"]
        mock_customer.status = "active"
        
        mock_service_instance = MagicMock()
        mock_service_instance.create_customer.return_value = mock_customer
        mock_service.return_value = mock_service_instance
        
        response = client.post("/api/v1/customers/", json=customer_data)
        
        assert response.status_code == 201
        assert response.json()["company_name"] == customer_data["company_name"]
        assert response.json()["email"] == customer_data["email"]


def test_get_customers(client):
    response = client.get("/api/v1/customers/")
    
    assert response.status_code == 200
    assert "items" in response.json()
    assert "total" in response.json()


def test_get_customer_detail(client):
    # Test with a mock UUID
    customer_id = "12345678-1234-5678-1234-123456789012"
    
    with patch('src.api.v1.customers.CustomerService') as mock_service:
        mock_customer = MagicMock()
        mock_customer.id = customer_id
        mock_customer.company_name = "Test Company"
        mock_customer.contact_person = "John Doe"
        mock_customer.email = "john@testcompany.com"
        mock_customer.status = "active"
        
        mock_service_instance = MagicMock()
        mock_service_instance.get_customer_detail.return_value = mock_customer
        mock_service.return_value = mock_service_instance
        
        response = client.get(f"/api/v1/customers/{customer_id}")
        
        assert response.status_code == 200
        assert response.json()["id"] == customer_id