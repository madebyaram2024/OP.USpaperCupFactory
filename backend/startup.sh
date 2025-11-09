#!/bin/bash
set -e

echo "Starting database initialization..."
python init_db.py
INIT_RESULT=$?

if [ $INIT_RESULT -eq 0 ]; then
    echo "Database initialization completed successfully"
else
    echo "Database initialization failed with code $INIT_RESULT, but continuing startup..."
fi

echo "Starting server..."
exec python run_server.py