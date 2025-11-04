# Quickstart: Customer Management System

## Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Git

### Environment Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic python-multipart
   pip install pytest pytest-asyncio requests
   ```

4. **Set up database**:
   ```bash
   # Create database and run migrations (details in data-model.md)
   # You may need to adjust DATABASE_URL in your environment
   ```

5. **Environment variables**:
   ```bash
   export DATABASE_URL=postgresql://username:password@localhost:5432/customer_management
   export SECRET_KEY=your-secret-key-here
   ```

## API Usage Examples

### 1. Create a Customer

```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "The Coffee House",
    "contact_person": "John Smith",
    "email": "john@coffeehouse.com",
    "phone": "+15550123",
    "address_line1": "123 Main Street",
    "city": "Anytown",
    "state_province": "CA",
    "postal_code": "12345",
    "country": "USA"
  }'
```

### 2. List Customers

```bash
curl "http://localhost:8000/api/v1/customers"
```

### 3. Search Customers

```bash
curl "http://localhost:8000/api/v1/customers?search=Coffee"
```

### 4. Get Customer Detail

```bash
curl "http://localhost:8000/api/v1/customers/{customer_id}"
```

### 5. Update Customer

```bash
curl -X PUT "http://localhost:8000/api/v1/customers/{customer_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_person": "Sarah Johnson",
    "email": "sarah@coffeehouse.com"
  }'
```

### 6. Archive Customer

```bash
curl -X DELETE "http://localhost:8000/api/v1/customers/{customer_id}"
```

## Running the Server

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Running Tests

### Unit Tests
```bash
python -m pytest tests/unit/
```

### Integration Tests
```bash
python -m pytest tests/integration/
```

### All Tests
```bash
python -m pytest
```

## Data Import

### CSV Template
Download the template for bulk customer import:
```bash
curl "http://localhost:8000/api/v1/customers/import-template" -o customer_template.csv
```

### Import Customers
```bash
curl -X POST "http://localhost:8000/api/v1/customers/import" \
  -F "file=@customers.csv"
```

## Common Issues and Solutions

### 1. Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL environment variable
- Ensure database exists and credentials are correct

### 2. Validation Errors
- Email format must be valid
- Required fields (company_name, contact_person, email) must be provided
- Check API response for specific validation error messages

### 3. API Rate Limits
- The system is designed to handle high throughput
- If experiencing performance issues, check database indexing (see data-model.md)

## Development Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement customer management features** following the task list in tasks.md

3. **Write tests** for each implemented feature

4. **Run tests** to ensure no regressions

5. **Commit with conventional commit message**:
   ```bash
   git commit -m "feat(customer): add customer creation endpoint"
   ```

6. **Push and create pull request**

## Debugging Tips

- Enable debug logging by setting `DEBUG=true` environment variable
- Check the customer service logs for business logic issues
- Use database views to inspect customer statistics (active_orders_count, total_orders_count)