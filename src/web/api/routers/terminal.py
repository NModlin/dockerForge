"""
Terminal router for the DockerForge Web UI.

This module provides the API endpoints for terminal functionality.
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging
import json
import time

from src.web.api.database import get_db
from src.web.api.services.terminal import get_terminal_manager, TerminalManager, TerminalSession
from src.web.api.auth.dependencies import get_current_active_user
from src.web.api.auth.models import User
from src.web.api.auth.permissions import check_permission

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.websocket("/terminal/{container_id}")
async def terminal_websocket(
    websocket: WebSocket,
    container_id: str,
    cols: int = Query(80, ge=10, le=500),
    rows: int = Query(24, ge=5, le=100),
    user_id: str = Query("anonymous"),
):
    """
    WebSocket endpoint for terminal connections.
    
    Args:
        websocket: WebSocket connection
        container_id: Container ID
        cols: Number of columns
        rows: Number of rows
        user_id: User ID
    """
    # Get terminal manager
    terminal_manager = get_terminal_manager()
    
    # Accept WebSocket connection
    await websocket.accept()
    
    # Create terminal session
    session_id = terminal_manager.create_session(container_id, user_id, cols, rows)
    session = terminal_manager.get_session(session_id)
    
    if not session:
        await websocket.send_json({
            "type": "error",
            "error": "Failed to create terminal session",
            "timestamp": time.time()
        })
        await websocket.close()
        return
    
    try:
        # Send session information
        await websocket.send_json({
            "type": "session_created",
            "session_id": session_id,
            "container_id": container_id,
            "timestamp": time.time()
        })
        
        # Connect terminal session to WebSocket
        if not await session.connect(websocket):
            await websocket.close()
            terminal_manager.close_session(session_id)
            return
        
        # Handle WebSocket messages
        while True:
            # Wait for messages from the client
            data = await websocket.receive()
            
            # Check if text or binary message
            if "text" in data:
                try:
                    # Parse the message
                    message_data = json.loads(data["text"])
                    message_type = message_data.get("type")
                    
                    # Process message based on type
                    if message_type == "input":
                        # Send input to terminal
                        input_data = message_data.get("data", "")
                        await session.send_input(input_data)
                        
                        # Add to command history if it's a complete command
                        if input_data.endswith("\r") or input_data.endswith("\n"):
                            command = input_data.strip()
                            if command:
                                session.command_history.append(command)
                    
                    elif message_type == "resize":
                        # Resize terminal
                        cols = message_data.get("cols", 80)
                        rows = message_data.get("rows", 24)
                        await session.resize(cols, rows)
                    
                    elif message_type == "ping":
                        # Ping to keep connection alive
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": time.time()
                        })
                    
                    else:
                        # Unknown message type
                        logger.warning(f"Unknown terminal message type: {message_type}")
                        await websocket.send_json({
                            "type": "error",
                            "error": f"Unknown message type: {message_type}",
                            "timestamp": time.time()
                        })
                
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {data['text']}")
                    await websocket.send_json({
                        "type": "error",
                        "error": "Invalid JSON",
                        "timestamp": time.time()
                    })
                
                except Exception as e:
                    logger.error(f"Error processing terminal message: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "error": f"Error processing message: {str(e)}",
                        "timestamp": time.time()
                    })
            
            elif "bytes" in data:
                # Binary data (e.g., control sequences)
                await session.send_input(data["bytes"].decode("utf-8"))
    
    except WebSocketDisconnect:
        logger.info(f"Terminal WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"Terminal WebSocket error for session {session_id}: {str(e)}")
    finally:
        # Close terminal session
        terminal_manager.close_session(session_id)


@router.get("/sessions", response_model=List[Dict[str, Any]])
async def list_terminal_sessions(
    container_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List terminal sessions.
    
    Args:
        container_id: Filter by container ID
        current_user: Current user
        db: Database session
        
    Returns:
        List of terminal sessions
    """
    # Check permission
    if not check_permission(current_user, "containers:terminal"):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    # Get terminal manager
    terminal_manager = get_terminal_manager()
    
    # Get sessions
    if container_id:
        sessions = terminal_manager.get_sessions_for_container(container_id)
    else:
        sessions = terminal_manager.get_sessions_for_user(str(current_user.id))
    
    # Convert to response format
    return [
        {
            "session_id": session.session_id,
            "container_id": session.container_id,
            "user_id": session.user_id,
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "is_active": session.is_active,
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}", response_model=Dict[str, Any])
async def close_terminal_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Close a terminal session.
    
    Args:
        session_id: Session ID
        current_user: Current user
        db: Database session
        
    Returns:
        Success message
    """
    # Check permission
    if not check_permission(current_user, "containers:terminal"):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    # Get terminal manager
    terminal_manager = get_terminal_manager()
    
    # Get session
    session = terminal_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Terminal session {session_id} not found",
        )
    
    # Check if user owns the session
    if str(current_user.id) != session.user_id and not check_permission(current_user, "admin"):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to close this terminal session",
        )
    
    # Close session
    terminal_manager.close_session(session_id)
    
    return {
        "success": True,
        "message": f"Terminal session {session_id} closed",
    }


@router.get("/history/{container_id}", response_model=List[str])
async def get_command_history(
    container_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get command history for a container.
    
    Args:
        container_id: Container ID
        current_user: Current user
        db: Database session
        
    Returns:
        List of commands
    """
    # Check permission
    if not check_permission(current_user, "containers:terminal"):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions",
        )
    
    # Get terminal manager
    terminal_manager = get_terminal_manager()
    
    # Get sessions for container
    sessions = terminal_manager.get_sessions_for_container(container_id)
    
    # Collect command history from all sessions
    commands = []
    for session in sessions:
        commands.extend(session.command_history)
    
    # Return unique commands in reverse chronological order
    unique_commands = []
    for cmd in reversed(commands):
        if cmd not in unique_commands:
            unique_commands.append(cmd)
    
    return unique_commands[:100]  # Limit to 100 commands
