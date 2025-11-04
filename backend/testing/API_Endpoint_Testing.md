# API Endpoint Testing for Speckit Customer Management Backend

## API Testing Suite

### API Base URL: http://localhost:8080

---

## Test Suite 1: Health Check Endpoint
**Test ID:** API-001  
**Endpoint:** GET /  
**Purpose:** Verify API server is accessible  
**Method:** GET  
**URL:** http://localhost:8080/  
**Expected Result:** 200 OK with message  
**Steps:**
```bash
curl -X GET http://localhost:8080/
```
Expected Response:
```json
{
  "message": "Customer Management API"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 2: Health Check Endpoint
**Test ID:** API-002  
**Endpoint:** GET /health  
**Purpose:** Verify API health  
**Method:** GET  
**URL:** http://localhost:8080/health  
**Expected Result:** 200 OK with health status  
**Steps:**
```bash
curl -X GET http://localhost:8080/health
```
Expected Response:
```json
{
  "status": "healthy"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 3: Create Customer
**Test ID:** API-003  
**Endpoint:** POST /api/v1/customers  
**Purpose:** Test customer creation endpoint  
**Method:** POST  
**URL:** http://localhost:8080/api/v1/customers  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "Test Company",
  "contact_person": "John Doe",
  "email": "john.doe@testcompany.com",
  "phone": "+11234567890",
  "address_line1": "123 Test Street",
  "city": "Test City",
  "state_province": "Test State",
  "postal_code": "12345",
  "country": "Test Country",
  "notes": "Test customer for API testing"
}
```
**Expected Result:** 201 Created with customer details  
**Steps:**
```bash
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Company",
    "contact_person": "John Doe",
    "email": "john.doe@testcompany.com",
    "phone": "+11234567890",
    "address_line1": "123 Test Street",
    "city": "Test City",
    "state_province": "Test State",
    "postal_code": "12345",
    "country": "Test Country",
    "notes": "Test customer for API testing"
  }'
```
Expected Response (201 Created):
```json
{
  "id": "uuid-string",
  "company_name": "Test Company",
  "contact_person": "John Doe",
  "email": "john.doe@testcompany.com",
  "phone": "+11234567890",
  "address_line1": "123 Test Street",
  "address_line2": null,
  "city": "Test City",
  "state_province": "Test State",
  "postal_code": "12345",
  "country": "Test Country",
  "notes": "Test customer for API testing",
  "status": "active",
  "active_orders_count": 0,
  "total_orders_count": 0,
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": null,
  "updated_by": null
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 4: Create Customer - Validation Error (Email)
**Test ID:** API-004  
**Endpoint:** POST /api/v1/customers  
**Purpose:** Test email validation  
**Method:** POST  
**URL:** http://localhost:8080/api/v1/customers  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "Invalid Email Company",
  "contact_person": "Jane Smith",
  "email": "not-an-email",
  "phone": "+11234567890"
}
```
**Expected Result:** 422 Validation Error  
**Steps:**
```bash
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Invalid Email Company",
    "contact_person": "Jane Smith",
    "email": "not-an-email",
    "phone": "+11234567890"
  }'
```
Expected Response (422):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 5: Create Customer - Required Fields Error
**Test ID:** API-005  
**Endpoint:** POST /api/v1/customers  
**Purpose:** Test required fields validation  
**Method:** POST  
**URL:** http://localhost:8080/api/v1/customers  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "",
  "contact_person": "",
  "email": ""
}
```
**Expected Result:** 422 Validation Error  
**Steps:**
```bash
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "",
    "contact_person": "",
    "email": ""
  }'
```
Expected Response (422):
```json
{
  "detail": [
    {
      "loc": ["body", "company_name"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "contact_person"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 6: Get All Customers
**Test ID:** API-006  
**Endpoint:** GET /api/v1/customers  
**Purpose:** Test customer listing endpoint  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers?limit=50&page=1  
**Expected Result:** 200 OK with customer list  
**Steps:**
```bash
curl -X GET "http://localhost:8080/api/v1/customers?limit=50&page=1"
```
Expected Response (200):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "company_name": "string",
      "contact_person": "string",
      "email": "string",
      "phone": "string or null",
      "active_orders_count": "integer",
      "total_orders_count": "integer",
      "status": "string",
      "created_at": "timestamp"
    }
  ],
  "total": "integer",
  "page": "integer",
  "limit": "integer",
  "pages": "integer"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 7: Get Single Customer
**Test ID:** API-007  
**Endpoint:** GET /api/v1/customers/{id}  
**Purpose:** Test single customer retrieval  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers/{customer_id}  
**Expected Result:** 200 OK with customer details  
**Steps:**
1. First create a customer using API-003
2. Use the returned ID in this test:
```bash
curl -X GET "http://localhost:8080/api/v1/customers/{customer_id}"
```
Expected Response (200):
```json
{
  "id": "uuid-string",
  "company_name": "string",
  "contact_person": "string",
  "email": "string",
  "phone": "string or null",
  "address_line1": "string or null",
  "address_line2": "string or null",
  "city": "string or null",
  "state_province": "string or null",
  "postal_code": "string or null",
  "country": "string or null",
  "notes": "string or null",
  "status": "string",
  "active_orders_count": "integer",
  "total_orders_count": "integer",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "uuid or null",
  "updated_by": "uuid or null"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 8: Get Single Customer - Not Found
**Test ID:** API-008  
**Endpoint:** GET /api/v1/customers/{id}  
**Purpose:** Test retrieval of non-existent customer  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers/{invalid_customer_id}  
**Expected Result:** 404 Not Found  
**Steps:**
```bash
curl -X GET "http://localhost:8080/api/v1/customers/00000000-0000-0000-0000-000000000000"
```
Expected Response (404):
```json
{
  "detail": "Customer not found"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 9: Update Customer
**Test ID:** API-009  
**Endpoint:** PUT /api/v1/customers/{id}  
**Purpose:** Test customer update endpoint  
**Method:** PUT  
**URL:** http://localhost:8080/api/v1/customers/{customer_id}  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "Updated Test Company",
  "contact_person": "Jane Updated",
  "email": "jane.updated@testcompany.com",
  "phone": "+10987654321"
}
```
**Expected Result:** 200 OK with updated customer details  
**Steps:**
1. First create a customer using API-003
2. Use the returned ID in this test:
```bash
curl -X PUT http://localhost:8080/api/v1/customers/{customer_id} \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Updated Test Company",
    "contact_person": "Jane Updated",
    "email": "jane.updated@testcompany.com",
    "phone": "+10987654321"
  }'
```
Expected Response (200):
```json
{
  "id": "uuid-string",
  "company_name": "Updated Test Company",
  "contact_person": "Jane Updated",
  "email": "jane.updated@testcompany.com",
  "phone": "+10987654321",
  "address_line1": "string or null",
  "address_line2": "string or null",
  "city": "string or null",
  "state_province": "string or null",
  "postal_code": "string or null",
  "country": "string or null",
  "notes": "string or null",
  "status": "string",
  "active_orders_count": "integer",
  "total_orders_count": "integer",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "created_by": "uuid or null",
  "updated_by": "uuid or null"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 10: Update Customer - Validation Error
**Test ID:** API-010  
**Endpoint:** PUT /api/v1/customers/{id}  
**Purpose:** Test update with invalid email  
**Method:** PUT  
**URL:** http://localhost:8080/api/v1/customers/{customer_id}  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "email": "invalid-email-format"
}
```
**Expected Result:** 422 Validation Error  
**Steps:**
```bash
curl -X PUT http://localhost:8080/api/v1/customers/{customer_id} \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email-format"
  }'
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 11: Archive Customer
**Test ID:** API-011  
**Endpoint:** DELETE /api/v1/customers/{id}  
**Purpose:** Test customer archiving endpoint  
**Method:** DELETE  
**URL:** http://localhost:8080/api/v1/customers/{customer_id}  
**Expected Result:** 204 No Content  
**Steps:**
1. First create a customer using API-003
2. Use the returned ID in this test:
```bash
curl -X DELETE "http://localhost:8080/api/v1/customers/{customer_id}"
```
Expected Response (204): No Content
Status: [ ] PASS [ ] FAIL

---

## Test Suite 12: Archive Customer - Not Found
**Test ID:** API-012  
**Endpoint:** DELETE /api/v1/customers/{id}  
**Purpose:** Test archiving non-existent customer  
**Method:** DELETE  
**URL:** http://localhost:8080/api/v1/customers/{invalid_customer_id}  
**Expected Result:** 404 Not Found  
**Steps:**
```bash
curl -X DELETE "http://localhost:8080/api/v1/customers/00000000-0000-0000-0000-000000000000"
```
Expected Response (404):
```json
{
  "detail": "Customer not found"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 13: Search Customers
**Test ID:** API-013  
**Endpoint:** GET /api/v1/customers  
**Purpose:** Test customer search functionality  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers?search=Test  
**Expected Result:** 200 OK with filtered customer list  
**Steps:**
```bash
curl -X GET "http://localhost:8080/api/v1/customers?search=Test"
```
Expected Response (200):
```json
{
  "items": [
    {
      "id": "uuid-string",
      "company_name": "Test Company",
      "contact_person": "string",
      "email": "string",
      "phone": "string or null",
      "active_orders_count": "integer",
      "total_orders_count": "integer",
      "status": "string",
      "created_at": "timestamp"
    }
  ],
  "total": "integer",
  "page": "integer",
  "limit": "integer",
  "pages": "integer"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 14: Filter Customers by Status
**Test ID:** API-014  
**Endpoint:** GET /api/v1/customers  
**Purpose:** Test customer filtering by status  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers?status=active  
**Expected Result:** 200 OK with filtered customer list  
**Steps:**
```bash
curl -X GET "http://localhost:8080/api/v1/customers?status=active"
```
Expected Response (200): Same structure as API-006 but filtered
Status: [ ] PASS [ ] FAIL

---

## Test Suite 15: Pagination
**Test ID:** API-015  
**Endpoint:** GET /api/v1/customers  
**Purpose:** Test customer pagination  
**Method:** GET  
**URL:** http://localhost:8080/api/v1/customers?page=1&limit=10  
**Expected Result:** 200 OK with first 10 customers  
**Steps:**
```bash
curl -X GET "http://localhost:8080/api/v1/customers?page=1&limit=10"
```
Expected Response (200): Same structure as API-006 but limited to 10 items
Status: [ ] PASS [ ] FAIL

---

## Test Suite 16: API Documentation
**Test ID:** API-016  
**Endpoint:** GET /docs  
**Purpose:** Verify API documentation is available  
**Method:** GET  
**URL:** http://localhost:8080/docs  
**Expected Result:** 200 OK with Swagger UI  
**Steps:**
```bash
curl -X GET http://localhost:8080/docs
```
Expected Response: HTML containing Swagger UI documentation
Status: [ ] PASS [ ] FAIL

---

## Test Suite 17: OpenAPI Schema
**Test ID:** API-017  
**Endpoint:** GET /openapi.json  
**Purpose:** Verify OpenAPI schema is available  
**Method:** GET  
**URL:** http://localhost:8080/openapi.json  
**Expected Result:** 200 OK with OpenAPI JSON  
**Steps:**
```bash
curl -X GET http://localhost:8080/openapi.json
```
Expected Response: Valid OpenAPI JSON schema
Status: [ ] PASS [ ] FAIL

---

## Test Suite 18: Duplicate Email Prevention
**Test ID:** API-018  
**Endpoint:** POST /api/v1/customers  
**Purpose:** Test duplicate email prevention  
**Method:** POST  
**URL:** http://localhost:8080/api/v1/customers  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "Duplicate Company",
  "contact_person": "Same Person",
  "email": "duplicate@test.com",
  "phone": "+11111111111"
}
```
**Expected Result:** 409 Conflict for duplicates  
**Steps:**
1. Create a customer with email "duplicate@test.com" using first request
2. Try to create another customer with same email using second request:
```bash
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Duplicate Company",
    "contact_person": "Same Person",
    "email": "duplicate@test.com",
    "phone": "+11111111111"
  }'
```
Expected Response (409):
```json
{
  "detail": "A customer with this email already exists"
}
```
Status: [ ] PASS [ ] FAIL

---

## Test Suite 19: Field Length Validation
**Test ID:** API-019  
**Endpoint:** POST /api/v1/customers  
**Purpose:** Test field length validation  
**Method:** POST  
**URL:** http://localhost:8080/api/v1/customers  
**Headers:**  
Content-Type: application/json  
**Request Body:**
```json
{
  "company_name": "A".repeat(256),  // Exceeds 255 char limit
  "contact_person": "B".repeat(256),  // Exceeds 255 char limit
  "email": "test@example.com"
}
```
**Expected Result:** 422 Validation Error  
**Steps:**
```bash
curl -X POST http://localhost:8080/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "'\"$(printf 'A%.0s' {1..256})\"'",
    "contact_person": "'\"$(printf 'B%.0s' {1..256})\"'",
    "email": "test@example.com"
  }'
```
Note: This test might need to be run with a different approach due to shell limitations
Status: [ ] PASS [ ] FAIL

---

## Test Execution Results
- Total API Tests: 19
- Passed: [___/19]
- Failed: [___/19]
- Pass Rate: [___%]
- Issues Found: [Number]

## Error Handling Tests Summary:
- [ ] Test invalid JSON format
- [ ] Test non-existent endpoints
- [ ] Test malformed UUIDs
- [ ] Test boundary values for pagination
- [ ] Test empty request bodies

## Performance Tests:
- [ ] Test response time for customer listing
- [ ] Test concurrent request handling
- [ ] Test with large payload sizes

## Security Tests:
- [ ] Test SQL injection attempts
- [ ] Test authentication (if implemented)
- [ ] Test authorization (if implemented)

## Test Execution Sign-off:
- Test Executed by: 
- Date: 
- Environment: 
- API Version: 
