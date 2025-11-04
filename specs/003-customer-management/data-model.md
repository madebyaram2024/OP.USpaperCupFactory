# Data Model: Customer Management System

## Customer Entity

### Core Customer Table (`customers`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID (Primary Key) | NOT NULL, UNIQUE, Auto-generated | Unique identifier for customer |
| company_name | VARCHAR(255) | NOT NULL | Name of the company/organization |
| contact_person | VARCHAR(255) | NOT NULL | Primary contact person name |
| email | VARCHAR(255) | NOT NULL, UNIQUE | Primary contact email |
| phone | VARCHAR(50) | NULL | Primary contact phone number (E.164 format) |
| address_line1 | VARCHAR(255) | NULL | Street address line 1 |
| address_line2 | VARCHAR(255) | NULL | Street address line 2 |
| city | VARCHAR(100) | NULL | City |
| state_province | VARCHAR(100) | NULL | State or province |
| postal_code | VARCHAR(20) | NULL | Postal or ZIP code |
| country | VARCHAR(100) | NULL | Country |
| notes | TEXT | NULL | Additional notes about the customer |
| status | ENUM: 'active', 'archived' | NOT NULL, DEFAULT 'active' | Customer status |
| active_orders_count | INTEGER | NOT NULL, DEFAULT 0 | Count of active work orders |
| total_orders_count | INTEGER | NOT NULL, DEFAULT 0 | Total number of orders |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP | Record last update timestamp |
| created_by | UUID (Foreign Key) | NULL | User ID of creator |
| updated_by | UUID (Foreign Key) | NULL | User ID of last updater |

### Indexes

1. **Primary Index**: `id` (auto)
2. **Search Index**: `(company_name, contact_person, email)` - For full-text search capability
3. **Email Unique Index**: `email` - To prevent duplicate emails
4. **Status Index**: `status` - For filtering active/archived customers
5. **Created Date Index**: `created_at` - For chronological queries

### Validation Rules at Database Level

- `company_name` cannot be empty
- `contact_person` cannot be empty  
- `email` must follow email format (handled in application layer, enforced with check constraint)
- `email` must be unique across all customers
- `phone` format validation (lenient - accept international formats)
- `status` must be one of allowed values ('active', 'archived')

## Associated Entities

### Work Order Entity Relationship (`work_orders`)

The customer entity has a one-to-many relationship with work orders:
- Foreign Key: `customer_id` in `work_orders` table references `id` in `customers`
- When customer is archived, existing work orders remain accessible
- `active_orders_count` and `total_orders_count` are denormalized for performance

### Customer Activity Log (`customer_activities`)

- Foreign Key: `customer_id` references `customers.id`
- Tracks: CustomerCreated, CustomerUpdated, CustomerArchived, CustomerReactivated events
- Format: JSONB for flexible event data storage

## Migration Strategy

### Initial Migration (Version 1.0)

```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) NULL,
    address_line1 VARCHAR(255) NULL,
    address_line2 VARCHAR(255) NULL,
    city VARCHAR(100) NULL,
    state_province VARCHAR(100) NULL,
    postal_code VARCHAR(20) NULL,
    country VARCHAR(100) NULL,
    notes TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    active_orders_count INTEGER NOT NULL DEFAULT 0,
    total_orders_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NULL,
    updated_by UUID NULL,
    CONSTRAINT check_status CHECK (status IN ('active', 'archived')),
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_customers_search ON customers (company_name, contact_person, email);
CREATE INDEX idx_customers_status ON customers (status);
CREATE INDEX idx_customers_email ON customers (email);
CREATE INDEX idx_customers_created_at ON customers (created_at);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to call the function
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Future Extensions

### Separate Address Table (Potential v2.0 enhancement)

If multiple addresses per customer become necessary:

```sql
CREATE TABLE customer_addresses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(id),
    address_type VARCHAR(50) NOT NULL, -- billing, shipping, primary
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255) NULL,
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

This structure would require refactoring the main customer table to remove address fields.