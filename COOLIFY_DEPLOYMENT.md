# Deployment Guide for Coolify

This guide explains how to deploy the USPC Factory Speckit application on Coolify.

## Application Overview

The application consists of:
- **Backend**: Python FastAPI application running on port 8000
- **Frontend**: Static HTML/CSS/JS served via Nginx on port 80
- **Database**: PostgreSQL database

## Deployment Steps

### 1. Prepare the Repository
- Push the code to your Git repository
- Ensure the following files are in the root of your repository:
  - `docker-compose.prod.yml`
  - `backend/Dockerfile`
  - `frontend/Dockerfile`
  - `frontend/nginx.conf`

### 2. Deploy on Coolify

1. **Add your application on Coolify**
   - Go to Coolify dashboard
   - Click "Add new Application"
   - Select "Docker Compose" as the application type
   - Connect to your Git repository

2. **Configure the deployment**
   - Set the Docker Compose file path to `docker-compose.prod.yml`
   - Set the build path to the root of your project
   - Add the required environment variables (see below)

3. **Environment Variables**
   ```
   FRONTEND_HOST=yourdomain.com
   ```

4. **Deploy**
   - Click "Deploy" and wait for the build to complete

### 3. Coolify Configuration

The application is configured with the following services:

#### Backend Service (FastAPI)
- Built from `backend/Dockerfile`
- Exposes port 8000 internally
- Depends on the database service
- Environment variables:
  - `DATABASE_URL`: PostgreSQL connection string
  - `API_HOST`: Host to bind to (0.0.0.0 for container)
  - `API_PORT`: Port to run on (8000)
  - `DEBUG`: Debug mode (False for production)

#### Frontend Service (Nginx)
- Built from `frontend/Dockerfile`
- Serves static files via Nginx
- Proxied through Coolify to public domain
- Configured to proxy API requests to backend

#### Database Service (PostgreSQL)
- Uses PostgreSQL 15-alpine image
- Persistent data storage using Coolify volumes
- Health check configured
- Environment variables for database setup

### 4. Database Initialization

The application will initialize the database automatically on first run. The `init_db.py` script in the backend will be executed to set up the required tables.

### 5. Domain Configuration

After deployment:
1. Go to your application settings in Coolify
2. Navigate to the "Domains" section
3. Add your domain name (e.g., `yourdomain.com`)
4. Configure DNS settings as prompted by Coolify

### 6. SSL Certificate

Coolify will automatically provision SSL certificates for your domains.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify that the `DATABASE_URL` environment variable is correctly set
   - Check that the database service is running and healthy

2. **Frontend Not Loading**
   - Verify that the frontend service is built successfully
   - Check that the proxy configuration in Coolify is correct

3. **API Requests Failing**
   - Ensure the frontend nginx is correctly proxying to the backend
   - Check that the backend service is accessible within the Docker network

### Logs

To check application logs in Coolify:
1. Go to your application dashboard
2. Click on each service to view its logs
3. Check both frontend and backend services

### Health Checks

- Backend health check: `GET /health` (should return `{"status": "healthy"}`)
- Database health check: Built into the container configuration

## Scaling Recommendations

1. **Database**: Consider using Coolify's managed database service for production
2. **Storage**: Use external volumes for persistent data if needed
3. **Load Balancing**: Coolify handles this automatically for multiple instances

## Updating the Application

1. Push changes to your Git repository
2. In Coolify, go to your application
3. Click "Redeploy" to pull the latest changes and rebuild
4. Monitor the deployment logs for any issues

## Environment Variables for Production

The following environment variables can be configured in Coolify:

- `FRONTEND_HOST`: Domain name for the frontend (default: frontend.localhost)
- `DATABASE_URL`: PostgreSQL connection string (default: configured in docker-compose)

For security, always use Coolify's secure environment variables feature for sensitive data.