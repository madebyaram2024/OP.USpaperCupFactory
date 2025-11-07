# Use nginx as base image
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for frontend files
RUN mkdir -p /usr/share/nginx/html

# Copy frontend files to nginx html directory
COPY . /usr/share/nginx/html

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]