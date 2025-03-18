"""
DockerForge Web UI - FastAPI Backend

This module provides the main FastAPI application for the DockerForge Web UI.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .database import get_db, init_db, create_initial_data

# Create FastAPI app
app = FastAPI(
    title="DockerForge API",
    description="API for DockerForge Web UI",
    version="0.1.0",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup.
    """
    init_db()
    create_initial_data()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "ok", "version": "0.1.0"}

# Root endpoint
@app.get("/api", tags=["Root"])
async def root():
    """
    Root endpoint for the API.
    """
    return {
        "message": "Welcome to DockerForge API",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }

# Import and include routers
from .routers import auth, containers, images, backup, monitoring, chat, websocket
# Import additional routers as they are implemented
from .models import __all__ as models  # Import all models to ensure they are registered

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(containers.router, prefix="/api/containers", tags=["Containers"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(volumes.router, prefix="/api/volumes", tags=["Volumes"])
# app.include_router(networks.router, prefix="/api/networks", tags=["Networks"])
# app.include_router(compose.router, prefix="/api/compose", tags=["Compose"])
# app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(websocket.router, tags=["WebSocket"])

# Serve index.html for the root URL
@app.get("/", include_in_schema=False)
async def serve_index():
    """
    Serve the index.html file for the root URL.
    """
    return FileResponse("/app/static/index.html")

# Catch-all route for client-side routing
@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    """
    Catch-all route to handle client-side routing.
    If the path starts with 'api/', let the request pass through to the API endpoints.
    If the path appears to be a static file (has an extension), check if it exists and serve it.
    Otherwise, serve the index.html file for client-side routing.
    """
    if path.startswith("api/") or path == "api":
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check if the requested path exists in the static directory
    if "." in path:  # This is likely a file request
        static_path = f"/app/static/{path}"
        if os.path.isfile(static_path):
            return FileResponse(static_path)
    
    # For any other path, serve the index.html file
    return FileResponse("/app/static/index.html")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 54321))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
