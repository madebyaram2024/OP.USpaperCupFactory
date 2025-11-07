# USPC Factory Speckit - Customer Management System

This project implements a customer management system as part of the USPC Factory Speckit framework. The system provides core CRUD functionality for customer records with search, filtering, and validation.

## Architecture

The application follows a component-based architecture with separation of concerns between:
- **Models**: Database entities and relationships
- **Services**: Business logic and operations
- **API**: HTTP endpoints and request handling
- **Schemas**: Data validation and serialization

## Features

### Implemented
- Customer creation with validation
- Customer listing with pagination
- Customer search functionality
- Customer detail view
- Customer update capability
- Customer archiving (soft delete)

### Planned
- Bulk customer import from CSV
- Advanced filtering and sorting
- Customer order history integration
- User activity logging

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL (via SQLAlchemy)
- **Validation**: Pydantic
- **Testing**: pytest

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd USPC_Factory_Speckit
   ```

2. Navigate to the backend directory:
   ```bash
   cd backend
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   export DATABASE_URL=postgresql://username:password@localhost:5432/customer_management
   export SECRET_KEY=your-secret-key-here
   ```

### Running the Application

Start the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Running Tests

Run unit tests:
```bash
python -m pytest tests/unit/
```

Run all tests:
```bash
python -m pytest
```

## API Endpoints

### Customers

- `POST /api/v1/customers` - Create a new customer
- `GET /api/v1/customers` - List customers with optional search and filtering
- `GET /api/v1/customers/{id}` - Get customer details
- `PUT /api/v1/customers/{id}` - Update customer information
- `DELETE /api/v1/customers/{id}` - Archive customer

## Development

### Speckit Framework

This project uses the Speckit framework for specification-driven development. The framework includes:

- `/specs/` - Feature specifications, research, and plans
- `/backend/` - Backend implementation
- `.specify/` - Templates and scripts for the development workflow

### Feature Implementation

To implement a new feature using Speckit:

1. Create a specification in `/specs/`
2. Generate implementation plan using `/speckit.plan`
3. Generate tasks using `/speckit.tasks`
4. Implement according to the generated tasks

## Project Structure

```
USPC_Factory_Speckit/
├── specs/                    # Feature specifications
│   └── 003-customer-management/  # Customer management spec
│       ├── spec.md           # Feature specification
│       ├── plan.md           # Implementation plan
│       ├── research.md       # Research notes
│       ├── data-model.md     # Data model documentation
│       ├── quickstart.md     # Quickstart guide
│       ├── contracts/        # API contracts
│       └── tasks.md          # Implementation tasks
├── backend/                  # Backend implementation
│   ├── src/                  # Source code
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   ├── api/              # API endpoints
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── database.py       # Database configuration
│   │   └── main.py           # Application entry point
│   ├── tests/                # Test files
│   │   ├── unit/             # Unit tests
│   │   ├── integration/      # Integration tests
│   │   └── contract/         # Contract tests
│   └── requirements.txt      # Dependencies
└── .specify/                 # Speckit framework files
```

## Contributing

1. Follow the Speckit framework for new features
2. Write tests for all new functionality
3. Use conventional commits for all changes
4. Update documentation as needed

## Deployment

### Docker Deployment

The application can be deployed using Docker and Docker Compose. The project includes:

- `Dockerfile` for the backend (Python/FastAPI)
- `Dockerfile` for the frontend (Nginx)
- `docker-compose.yml` for local development
- `docker-compose.prod.yml` for production deployment

#### Local Development
To run the application locally with Docker:

```bash
docker-compose up --build
```

The frontend will be available at `http://localhost:80` and the backend API at `http://localhost:8000`.

#### Production Deployment

For production deployment on Coolify:

1. Ensure your repository includes the Docker files and docker-compose configuration
2. Use `docker-compose.prod.yml` as your deployment configuration
3. Set the required environment variables in your Coolify deployment settings

### Coolify Deployment

Detailed Coolify deployment instructions are available in `COOLIFY_DEPLOYMENT.md`.

## License

[License information would go here]