"""
WebSocket router for the DockerForge Web UI.

This module provides WebSocket connections for real-time messaging, typing indicators,
and status updates for long-running tasks.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.core.chat_handler import get_chat_handler
from src.utils.logging_manager import get_logger
from src.web.api.database import get_db
from src.web.api.models.chat import ChatMessage, ChatSession
from src.web.api.models.user import User
from src.web.api.schemas.chat import ChatMessage as ChatMessageSchema

# Set up logger
logger = get_logger("web.api.websocket")

# Create router
router = APIRouter()


# Store active connections
class ConnectionManager:
    def __init__(self):
        # Dictionary mapping user IDs to WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}
        # Dictionary mapping session IDs to associated user IDs
        self.session_subscribers: Dict[int, List[str]] = {}
        # Dictionary mapping websocket connections to their typing status
        self.typing_status: Dict[str, bool] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.typing_status[user_id] = False
        logger.info(f"WebSocket connection established for user {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        if user_id in self.typing_status:
            del self.typing_status[user_id]

        # Remove user from session subscriptions
        for session_id, subscribers in list(self.session_subscribers.items()):
            if user_id in subscribers:
                subscribers.remove(user_id)
                if not subscribers:
                    # Remove the session key if there are no subscribers
                    del self.session_subscribers[session_id]

        logger.info(f"WebSocket connection closed for user {user_id}")

    def subscribe_to_session(self, user_id: str, session_id: int):
        if session_id not in self.session_subscribers:
            self.session_subscribers[session_id] = []

        if user_id not in self.session_subscribers[session_id]:
            self.session_subscribers[session_id].append(user_id)
            logger.info(f"User {user_id} subscribed to session {session_id}")

    def unsubscribe_from_session(self, user_id: str, session_id: int):
        if (
            session_id in self.session_subscribers
            and user_id in self.session_subscribers[session_id]
        ):
            self.session_subscribers[session_id].remove(user_id)
            logger.info(f"User {user_id} unsubscribed from session {session_id}")

            if not self.session_subscribers[session_id]:
                # Remove the session key if there are no subscribers
                del self.session_subscribers[session_id]

    def get_session_subscribers(self, session_id: int) -> List[str]:
        return self.session_subscribers.get(session_id, [])

    def set_typing_status(self, user_id: str, is_typing: bool, session_id: int):
        self.typing_status[user_id] = is_typing

        # Notify all subscribers of the session about the typing status
        asyncio.create_task(
            self.broadcast_typing_status(user_id, is_typing, session_id)
        )

    async def broadcast_typing_status(
        self, user_id: str, is_typing: bool, session_id: int
    ):
        subscribers = self.get_session_subscribers(session_id)

        # Don't send typing status to the user who is typing
        subscribers = [s for s in subscribers if s != user_id]

        message = {
            "type": "typing_status",
            "user_id": user_id,
            "is_typing": is_typing,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_users(subscribers, message)

    async def broadcast_message(self, message: ChatMessageSchema, session_id: int):
        subscribers = self.get_session_subscribers(session_id)

        ws_message = {
            "type": "chat_message",
            "message": message.dict(),
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_users(subscribers, ws_message)

    async def broadcast_to_users(self, user_ids: List[str], message: Dict[str, Any]):
        for user_id in user_ids:
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {str(e)}")

    async def send_message(self, user_id: str, message: Dict[str, Any]):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")

    async def stream_ai_response(
        self, session_id: int, message_id: int, text_chunks: List[str]
    ):
        """
        Stream an AI response in chunks to all session subscribers.

        Args:
            session_id: The chat session ID
            message_id: The message ID being streamed
            text_chunks: List of text chunks to stream
        """
        subscribers = self.get_session_subscribers(session_id)

        for i, chunk in enumerate(text_chunks):
            is_first = i == 0
            is_last = i == len(text_chunks) - 1

            message = {
                "type": "message_chunk",
                "message_id": message_id,
                "session_id": session_id,
                "chunk": chunk,
                "is_first": is_first,
                "is_last": is_last,
                "chunk_index": i,
                "total_chunks": len(text_chunks),
                "timestamp": datetime.utcnow().isoformat(),
            }

            await self.broadcast_to_users(subscribers, message)

            # Small delay between chunks to simulate typing
            if not is_last:
                await asyncio.sleep(0.05)

    async def send_task_update(
        self,
        session_id: int,
        task_id: str,
        status: str,
        progress: float,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ):
        """
        Send a task update to all session subscribers.

        Args:
            session_id: The chat session ID
            task_id: The ID of the task being updated
            status: The status of the task (running, complete, failed)
            progress: The progress percentage (0-100)
            message: A message describing the current state
            data: Optional additional data about the task
        """
        subscribers = self.get_session_subscribers(session_id)

        update = {
            "type": "task_update",
            "task_id": task_id,
            "session_id": session_id,
            "status": status,
            "progress": progress,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_users(subscribers, update)

    async def send_read_receipt(self, session_id: int, message_id: int, user_id: str):
        """
        Send a read receipt to all session subscribers.

        Args:
            session_id: The chat session ID
            message_id: The ID of the message that was read
            user_id: The ID of the user who read the message
        """
        subscribers = self.get_session_subscribers(session_id)

        # Don't send read receipt to the user who read the message
        subscribers = [s for s in subscribers if s != user_id]

        receipt = {
            "type": "read_receipt",
            "session_id": session_id,
            "message_id": message_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.broadcast_to_users(subscribers, receipt)


# Create connection manager
manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, user_id: str, db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time communication.

    Args:
        websocket: The WebSocket connection
        user_id: User ID (can be "anonymous" for unauthenticated users)
        db: Database session
    """
    await manager.connect(websocket, user_id)

    try:
        # Send initial connection confirmation
        await websocket.send_json(
            {
                "type": "connection_established",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()

            try:
                # Parse the message
                message_data = json.loads(data)
                message_type = message_data.get("type")

                # Process message based on type
                if message_type == "subscribe":
                    # Subscribe to a session
                    session_id = message_data.get("session_id")
                    if session_id:
                        manager.subscribe_to_session(user_id, session_id)
                        await websocket.send_json(
                            {
                                "type": "subscription_confirmed",
                                "session_id": session_id,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                elif message_type == "unsubscribe":
                    # Unsubscribe from a session
                    session_id = message_data.get("session_id")
                    if session_id:
                        manager.unsubscribe_from_session(user_id, session_id)
                        await websocket.send_json(
                            {
                                "type": "unsubscription_confirmed",
                                "session_id": session_id,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                elif message_type == "typing":
                    # Update typing status
                    is_typing = message_data.get("is_typing", False)
                    session_id = message_data.get("session_id")
                    if session_id:
                        manager.set_typing_status(user_id, is_typing, session_id)

                elif message_type == "read_receipt":
                    # Send read receipt
                    message_id = message_data.get("message_id")
                    session_id = message_data.get("session_id")
                    if message_id and session_id:
                        await manager.send_read_receipt(session_id, message_id, user_id)

                elif message_type == "ping":
                    # Respond to ping with pong
                    await websocket.send_json(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                    )

                else:
                    # Unknown message type
                    logger.warning(f"Unknown WebSocket message type: {message_type}")
                    await websocket.send_json(
                        {
                            "type": "error",
                            "error": f"Unknown message type: {message_type}",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "Invalid JSON",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": f"Error processing message: {str(e)}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        manager.disconnect(user_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(user_id)


# Export the connection manager to be used by other modules
def get_websocket_manager() -> ConnectionManager:
    return manager
