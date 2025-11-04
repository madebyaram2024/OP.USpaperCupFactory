#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    port = 3000  # Default frontend port
    frontend_dir = Path(__file__).parent.parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"Frontend directory does not exist: {frontend_dir}")
        sys.exit(1)
    
    os.chdir(frontend_dir)
    print(f"Serving frontend from {frontend_dir}")
    print(f"Frontend available at: http://localhost:{port}")
    print(f"Backend API is running at: http://localhost:8080")
    print("\nNote: The frontend will connect to the backend API at http://localhost:8080")
    
    with socketserver.TCPServer(("", port), CORSRequestHandler) as httpd:
        print(f"\nStarting server on port {port}...")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()