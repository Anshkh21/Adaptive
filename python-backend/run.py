#!/usr/bin/env python3
"""
Startup script for Python backend
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8001))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    print("🚀 Starting Python Backend Server...")
    print(f"📡 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
