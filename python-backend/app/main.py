"""
FastAPI Application for Adaptive Assessment Platform
Python Backend - Alternative to Node.js implementation
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
from dotenv import load_dotenv

from app.database import init_db
from app.routes import auth, assessments, aptitude, users, analytics, questions, admin, assignments

# Load environment variables
load_dotenv("config.env")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove disconnected connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

# Create FastAPI app
app = FastAPI(
    title="Adaptive Assessment Platform - Python Backend",
    description="Python implementation of the adaptive assessment system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # Use environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(aptitude.router, prefix="/api/aptitude", tags=["Aptitude Tests"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(assignments.router, prefix="/api/assignments", tags=["Assignments"])

# Remove redirect handlers and handle trailing slash in routes directly

@app.websocket("/socket.io/")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
            elif message.get("type") == "broadcast":
                await manager.broadcast(json.dumps(message))
            else:
                # Echo back the message
                await manager.send_personal_message(data, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await init_db()
    
    # Initialize sample aptitude tests
    from app.utils.aptitude_questions import create_sample_aptitude_tests
    await create_sample_aptitude_tests()
    
    print("🚀 Python Backend Server Started!")
    print("📊 Database connected successfully")
    print("🔗 API Documentation available at: http://localhost:8001/docs")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Adaptive Assessment Platform - Python Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "backend": "python"}

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"message": "Route not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Different port from Node.js (5000)
        reload=True,
        log_level="info"
    )
