"""
API key usage middleware for the DockerForge Web UI.

This middleware tracks API key usage for requests that use API key authentication.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from src.web.api.database import get_db
from src.web.api.services import api_key as api_key_service


class ApiKeyUsageMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking API key usage.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """
        Process the request and track API key usage.
        
        Args:
            request: Request object
            call_next: Next middleware in the chain
            
        Returns:
            Response from the next middleware
        """
        # Start timer
        start_time = time.time()
        
        # Get API key from request
        api_key = None
        if "X-API-Key" in request.headers:
            api_key = request.headers["X-API-Key"]
        
        # Process the request
        response = await call_next(request)
        
        # If API key was used, record usage
        if api_key:
            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            try:
                # Get database session
                db = next(get_db())
                
                # Verify API key
                api_key_obj = api_key_service.verify_api_key(db, api_key)
                
                if api_key_obj:
                    # Record usage
                    api_key_service.record_api_key_usage(
                        db=db,
                        api_key_id=api_key_obj.id,
                        endpoint=str(request.url.path),
                        method=request.method,
                        status_code=response.status_code,
                        response_time=response_time,
                        request_size=request.headers.get("content-length"),
                        response_size=response.headers.get("content-length"),
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent")
                    )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error recording API key usage: {str(e)}")
        
        return response
