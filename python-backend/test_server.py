#!/usr/bin/env python3
"""
Simple test server to verify Python backend works
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Python backend is working!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy", "backend": "python"}

if __name__ == "__main__":
    print("🚀 Starting Test Python Server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
