# API Contracts: Customer Management

## Customer Creation Contract

### Endpoint: `POST /api/v1/customers`

#### Request
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "company_name": "string (required, max 255)",
    "contact_person": "string (required, max 255)", 
    "email": "string (required, valid email format)",
    "phone": "string (optional, max 50)",
    "address_line1": "string (optional, max 255)",
    "address_line2": "string (optional, max 255)",
    "city": "string (optional, max 100)",
    "state_province": "string (optional, max 100)",
    "postal_code": "string (optional, max 20)",
    "country": "string (optional, max 100)",
    "notes": "string (optional, text)"
  }
  ```

#### Success Response (201 Created)
```json
{
  "id": "UUID string",
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
  "status": "enum: 'active' or 'archived'",
  "active_orders_count": 0,
  "total_orders_count": 0,
  "created_at": "ISO 8601 datetime string",
  "updated_at": "ISO 8601 datetime string"
}
```

#### Error Responses
- **400 Bad Request**: Validation errors
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

- **409 Conflict**: Email already exists
  ```json 
  {
    "detail": "A customer with this email already exists"
  }
  ```

## Customer List Contract

### Endpoint: `GET /api/v1/customers`

#### Query Parameters
- `search`: string (optional) - Search term for company name, contact name, or email
- `status`: enum ('active', 'archived', 'all') (optional) - Filter by customer status
- `page`: integer (optional, default: 1) - Page number for pagination
- `limit`: integer (optional, default: 50, max: 100) - Items per page

#### Success Response (200 OK)
```json
{
  "items": [
    {
      "id": "UUID string",
      "company_name": "string",
      "contact_person": "string",
      "email": "string", 
      "phone": "string or null",
      "active_orders_count": "integer",
      "total_orders_count": "integer",
      "status": "enum: 'active' or 'archived'",
      "created_at": "ISO 8601 datetime string"
    }
  ],
  "total": "integer",
  "page": "integer",
  "limit": "integer",
  "pages": "integer"
}
```

## Customer Detail Contract

### Endpoint: `GET /api/v1/customers/{id}`

#### Success Response (200 OK)
```json
{
  "id": "UUID string",
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
  "status": "enum: 'active' or 'archived'",
  "active_orders_count": "integer",
  "total_orders_count": "integer",
  "created_at": "ISO 8601 datetime string",
  "updated_at": "ISO 8601 datetime string",
  "order_history": [
    {
      "id": "UUID string",
      "order_id": "string",
      "status": "string",
      "created_at": "ISO 8601 datetime string",
      "total_amount": "decimal string"
    }
  ]
}
```

## Customer Update Contract

### Endpoint: `PUT /api/v1/customers/{id}`

#### Request
- **Content-Type**: `application/json`
- **Body**: Same as creation but all fields optional

#### Success Response (200 OK)
- Same as detail response

#### Error Responses
- **400 Bad Request**: Validation errors
- **404 Not Found**: Customer doesn't exist
- **409 Conflict**: Email already exists on another customer

## Customer Archive Contract

### Endpoint: `DELETE /api/v1/customers/{id}`

#### Success Response (204 No Content)

#### Error Responses
- **400 Bad Request**: Customer has active orders (cannot archive)
- **404 Not Found**: Customer doesn't exist

## Customer Import Contract

### Endpoint: `POST /api/v1/customers/import`

#### Request
- **Content-Type**: `multipart/form-data`
- **File**: `file` - CSV file with customer data

#### Success Response (200 OK)
```json
{
  "total_records": "integer",
  "successful_records": "integer", 
  "failed_records": "integer",
  "errors": [
    {
      "row": "integer",
      "field": "string",
      "error": "string"
    }
  ]
}
```

## Validation Rules

### Required Fields
- `company_name`: Required, non-empty string, max 255 characters
- `contact_person`: Required, non-empty string, max 255 characters  
- `email`: Required, valid email format, unique across all customers

### Field Formats
- `email`: Standard email format validation
- `phone`: Accept international formats, normalize for storage
- `status`: Only 'active' or 'archived' values allowed
- `id`: UUID format
- `active_orders_count`, `total_orders_count`: Non-negative integers

### Business Rules
- Cannot create customer with email that already exists
- Cannot archive customer with active work orders
- Archived customers excluded from default list/search
- Customer counts must be updated when related work orders change