"""
Stats router for the DockerForge Web UI.

This module provides the API endpoints for container stats.
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import json

from src.web.api.database import get_db
from src.web.api.services.stats import get_stats_manager, get_container_stats, get_container_stats_history, store_container_stats
from src.web.api.auth.dependencies import get_current_active_user
from src.web.api.auth.models import User
from src.web.api.auth.permissions import check_permission

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.websocket("/ws/{container_id}")
async def stats_websocket(
    websocket: WebSocket,
    container_id: str,
    user_id: str = Query("anonymous"),
):
    """
    WebSocket endpoint for container stats.
    
    Args:
        websocket: WebSocket connection
        container_id: Container ID
        user_id: User ID
    """
    # Get stats manager
    stats_manager = get_stats_manager()
    
    # Accept WebSocket connection
    await websocket.accept()
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection_established",
            "container_id": container_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # Subscribe to container stats
        await stats_manager.subscribe(container_id, websocket)
        
        # Start background collection if not already running
        await stats_manager.start_background_collection()
        
        # Handle WebSocket messages
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                # Parse the message
                message_data = json.loads(data)
                message_type = message_data.get("type")
                
                # Process message based on type
                if message_type == "ping":
                    # Ping to keep connection alive
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                
                else:
                    # Unknown message type
                    logger.warning(f"Unknown stats message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Unknown message type: {message_type}",
                        "timestamp": datetime.now().isoformat()
                    })
                
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON",
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error processing stats message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "error": f"Error processing message: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"Stats WebSocket disconnected for container {container_id}")
    except Exception as e:
        logger.error(f"Stats WebSocket error for container {container_id}: {str(e)}")
    finally:
        # Unsubscribe from container stats
        await stats_manager.unsubscribe(container_id, websocket)
        
        # Stop background collection if no subscribers left
        if stats_manager.get_total_subscriber_count() == 0:
            await stats_manager.stop_background_collection()


@router.get("/{container_id}/current", response_model=Dict[str, Any])
async def get_current_stats(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get current stats for a container.
    
    Args:
        container_id: Container ID
        current_user: Current user
        db: Database session
        
    Returns:
        Container stats
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    # Get container stats
    stats = await get_container_stats(container_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Container {container_id} not found or not running",
        )
    
    # Store stats in database
    await store_container_stats(container_id, stats, db)
    
    return stats


@router.get("/{container_id}/history", response_model=List[Dict[str, Any]])
async def get_stats_history(
    container_id: str,
    metric_type: Optional[str] = Query(None, description="Metric type (cpu, memory, network, disk)"),
    hours: int = Query(1, ge=1, le=24, description="Number of hours of history to retrieve"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get historical stats for a container.
    
    Args:
        container_id: Container ID
        metric_type: Metric type (cpu, memory, network, disk)
        hours: Number of hours of history to retrieve
        current_user: Current user
        db: Database session
        
    Returns:
        List of stats
    """
    # Check permission
    if not check_permission(current_user, "containers:read"):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    # Calculate time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    
    # Get container stats history
    stats = await get_container_stats_history(container_id, metric_type, start_time, end_time, db)
    
    return stats
