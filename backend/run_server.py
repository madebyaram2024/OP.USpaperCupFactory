#!/usr/bin/env python3
"""
Entry point script for the Customer Management API
"""

import uvicorn
import os
from src.main import app


def main():
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"Starting Customer Management API server on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "info"
    )


if __name__ == "__main__":
    main()