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

from src.web.api.middleware.api_key_usage import ApiKeyUsageMiddleware

from .database import get_db, init_db, create_initial_data

# Create FastAPI app
app = FastAPI(
    title="DockerForge API",
    description="API for DockerForge Web UI",
    version="0.1.0",
)

# Initialize database and services on startup
@app.on_event("startup")
async def startup_event():
    """
    Initialize database and services on startup.
    """
    init_db()
    create_initial_data()

    # Initialize default security policies
    from src.web.api.services import policy as policy_service
    await policy_service.initialize_default_policies()

# Configure CORS
# Get environment
env = os.getenv("NODE_ENV", "development")
if env == "production":
    # In production, be more restrictive with CORS
    origins = [
        "http://localhost:8080",
        "http://localhost:54321",
        "http://dockerforge:8080",
        "http://dockerforge:54321",
    ]
    # Add any additional production domains from env var if specified
    additional_domains = os.getenv("ALLOWED_ORIGINS", "")
    if additional_domains:
        origins.extend(additional_domains.split(","))
else:
    # In development, allow all origins
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"] if env == "development" else ["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"] if env == "development" else ["Authorization", "Content-Type", "X-API-Key"],
)

# Add API key usage middleware
app.add_middleware(ApiKeyUsageMiddleware)

# Mount static files
# Get static directory from environment variable or use default
static_dir = os.getenv("STATIC_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../static")))
print(f"Using static directory: {static_dir}")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    print(f"Created static directory at {static_dir}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
from src.web.api.routers import auth, containers, images, backup, monitoring, chat, websocket, terminal, stats, networks, volumes, compose, compose_templates, security, policy, alerts, logs, daemon_config, api_key, api_key_usage, user_preferences
# Import additional routers as they are implemented
from src.web.api.models import __all__ as models  # Import all models to ensure they are registered

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(containers.router, prefix="/api/containers", tags=["Containers"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(backup.router, prefix="/api/backup", tags=["Backup"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(volumes.router, prefix="/api/volumes", tags=["Volumes"])
app.include_router(networks.router, prefix="/api/networks", tags=["Networks"])
app.include_router(compose.router, prefix="/api/compose", tags=["Compose"])
app.include_router(compose_templates.router, tags=["Compose Templates"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(policy.router, prefix="/api/security/policy", tags=["Security Policy"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(alerts.router, prefix="/api/monitoring/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/api/monitoring/logs", tags=["Logs"])
app.include_router(daemon_config.router, prefix="/api/settings/daemon", tags=["Docker Daemon Configuration"])
app.include_router(api_key.router, prefix="/api/settings/api-keys", tags=["API Keys"])
app.include_router(api_key_usage.router, prefix="/api/settings/api-keys", tags=["API Key Usage"])
app.include_router(user_preferences.router, prefix="/api/settings/user-preferences", tags=["User Preferences"])
app.include_router(websocket.router, tags=["WebSocket"])
app.include_router(terminal.router, prefix="/api/terminal", tags=["Terminal"])
app.include_router(stats.router, prefix="/api/stats", tags=["Stats"])

# Serve index.html for the root URL
@app.get("/", include_in_schema=False)
async def serve_index():
    """
    Serve the index.html file for the root URL.
    """
    return FileResponse(os.path.join(static_dir, "index.html"))

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
        static_path = os.path.join(static_dir, path)
        if os.path.isfile(static_path):
            return FileResponse(static_path)

    # For any other path, serve the index.html file
    return FileResponse(os.path.join(static_dir, "index.html"))

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
