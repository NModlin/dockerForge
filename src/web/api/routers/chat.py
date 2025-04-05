"""
Chat router for the DockerForge Web UI.

This module provides the API endpoints for chat functionality, including
feedback, user preferences, command shortcuts, and WebSocket integration.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

from src.web.api.database import get_db
from src.web.api.models.chat import ChatMessage, ChatSession, ChatFeedback, ChatCommandShortcut, UserPreference
from src.web.api.models.user import User
from src.web.api.schemas.chat import (
    ChatMessageCreate, ChatMessage as ChatMessageSchema,
    ChatSessionCreate, ChatSessionUpdate, ChatSession as ChatSessionSchema,
    ChatResponse, EnhancedChatResponse, SessionsList, MessagesList, ContextData,
    ChatFeedbackCreate, ChatFeedback as ChatFeedbackSchema,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreference as UserPreferenceSchema,
    ChatCommandShortcutCreate, ChatCommandShortcutUpdate, ChatCommandShortcut as ChatCommandShortcutSchema,
    CommandShortcutsList
)
from src.security.vulnerability_scanner import get_vulnerability_scanner
from src.core.chat_handler import get_chat_handler
from src.core.conversation_memory import get_conversation_memory_manager
from src.core.user_preference_manager import get_user_preference_manager
from src.utils.logging_manager import get_logger
from src.monitoring.log_analyzer import get_log_analyzer
from src.monitoring.issue_detector import get_issue_detector
from src.web.api.routers.websocket import get_websocket_manager

# Set up logger
logger = get_logger("web.api.chat")

# Create router
router = APIRouter()

# Get services
vulnerability_scanner = get_vulnerability_scanner()
log_analyzer = get_log_analyzer()
issue_detector = get_issue_detector()
conversation_memory = get_conversation_memory_manager()
user_preference_manager = get_user_preference_manager()


@router.post("/security/start-workflow", response_model=ChatResponse)
async def start_security_workflow(
    vulnerability_id: str = Query(..., description="ID of the vulnerability to resolve"),
    session_id: Optional[int] = Query(None, description="Chat session ID (optional)"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Start a security resolution workflow for a vulnerability.

    Args:
        vulnerability_id: ID of the vulnerability to resolve
        session_id: Chat session ID (optional)
        background_tasks: Background tasks runner
        db: Database session
        user_id: User ID (optional)

    Returns:
        Initial workflow message
    """
    # Get vulnerability data
    try:
        # In a real implementation, this would get actual vulnerability data
        # vulnerability_data = vulnerability_scanner.get_vulnerability(vulnerability_id)

        # Mock vulnerability data for now
        vulnerability_data = {
            "id": vulnerability_id,
            "severity": "critical",
            "description": f"Mock vulnerability {vulnerability_id}",
            "affected_package": "demo-package",
            "current_version": "1.0.0",
            "fixed_version": "1.1.0",
            "cve_id": f"CVE-2024-{vulnerability_id}"
        }
    except Exception as e:
        logger.error(f"Error getting vulnerability data: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Vulnerability {vulnerability_id} not found")

    # Get or create chat session
    if session_id is None:
        # Create a new session
        session_title = f"Security Fix: {vulnerability_data['affected_package']} - {vulnerability_data['cve_id']}"
        db_session = ChatSession(
            user_id=user_id,
            title=session_title,
            is_active=True
        )
        db.add(db_session)
        db.flush()
        session_id = db_session.id
    else:
        # Verify session exists
        db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Chat session not found")

    # Prepare context data for the workflow
    context = {
        "current_page": "security",
        "vulnerability_id": vulnerability_data["id"],
        "vulnerability_severity": vulnerability_data["severity"],
        "vulnerability_description": vulnerability_data["description"],
        "affected_package": vulnerability_data["affected_package"],
        "current_version": vulnerability_data["current_version"],
        "fixed_version": vulnerability_data["fixed_version"],
        "cve_id": vulnerability_data["cve_id"]
    }

    # Get chat handler
    chat_handler = get_chat_handler()

    # Start security workflow
    try:
        response_text, suggestions, workflow_id = chat_handler.start_security_workflow(
            vulnerability_id=vulnerability_id,
            context=context
        )

        # Update context with workflow ID
        context["workflow_id"] = workflow_id

        # Create system message to start the workflow
        system_message = ChatMessage(
            user_id=None,  # System message doesn't have a user
            session_id=session_id,
            type="system",
            text="Starting security resolution workflow...",
            context=context
        )
        db.add(system_message)

        # Create AI message with the workflow response
        ai_message = ChatMessage(
            user_id=None,  # AI messages don't have a user
            session_id=session_id,
            type="ai",
            text=response_text,
            context=context
        )
        db.add(ai_message)
        db.commit()

        # Prepare response
        return ChatResponse(
            message=ChatMessageSchema.model_validate(ai_message),
            session_id=session_id,
            suggestions=suggestions
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting security workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting security workflow: {str(e)}")


@router.post("/container/start-troubleshooting", response_model=ChatResponse)
async def start_container_troubleshooting(
    container_id: str = Query(..., description="ID of the container to troubleshoot"),
    session_id: Optional[int] = Query(None, description="Chat session ID (optional)"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Start a troubleshooting workflow for a container.

    Args:
        container_id: ID of the container to troubleshoot
        session_id: Chat session ID (optional)
        background_tasks: Background tasks runner
        db: Database session
        user_id: User ID (optional)

    Returns:
        Initial workflow message
    """
    # Get container data
    try:
        # In a real implementation, this would get actual container data
        # from a container service or Docker API

        # Mock container data for now
        container_data = {
            "id": container_id,
            "name": f"container-{container_id[:8]}",
            "status": "running",
            "health": "unhealthy",
            "image": "example/image:latest",
            "created": datetime.now().isoformat(),
            "ports": "80/tcp -> 0.0.0.0:8080"
        }
    except Exception as e:
        logger.error(f"Error getting container data: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Container {container_id} not found")

    # Get or create chat session
    if session_id is None:
        # Create a new session
        session_title = f"Container Troubleshooting: {container_data['name']}"
        db_session = ChatSession(
            user_id=user_id,
            title=session_title,
            is_active=True
        )
        db.add(db_session)
        db.flush()
        session_id = db_session.id
    else:
        # Verify session exists
        db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Chat session not found")

    # Prepare context data for the workflow
    context = {
        "current_page": "containers",
        "current_container_id": container_id,
        "container_name": container_data["name"],
        "container_status": container_data["status"],
        "container_health": container_data["health"],
        "additional_data": {
            "image": container_data["image"],
            "created": container_data["created"],
            "ports": container_data["ports"]
        }
    }

    # Get issues for this container
    try:
        # In a real implementation, this would get actual issues
        # issues = issue_detector.get_container_issues(container_id)
        # if issues:
        #     context["issue_id"] = issues[0].id
        #     context["issue_title"] = issues[0].title
        #     context["issue_description"] = issues[0].description
        #     context["issue_severity"] = issues[0].severity.value
        pass
    except Exception as e:
        logger.warning(f"Error getting container issues: {str(e)}")

    # Get chat handler
    chat_handler = get_chat_handler()

    # Start container troubleshooting workflow
    try:
        response_text, suggestions, workflow_id = chat_handler.start_container_troubleshooting_workflow(
            container_id=container_id,
            context=context
        )

        # Update context with workflow ID
        context["workflow_id"] = workflow_id
        context["workflow_type"] = "container_troubleshooting"

        # Create system message to start the workflow
        system_message = ChatMessage(
            user_id=None,  # System message doesn't have a user
            session_id=session_id,
            type="system",
            text="Starting container troubleshooting workflow...",
            context=context
        )
        db.add(system_message)

        # Create AI message with the workflow response
        ai_message = ChatMessage(
            user_id=None,  # AI messages don't have a user
            session_id=session_id,
            type="ai",
            text=response_text,
            context=context
        )
        db.add(ai_message)
        db.commit()

        # Prepare response
        return ChatResponse(
            message=ChatMessageSchema.model_validate(ai_message),
            session_id=session_id,
            suggestions=suggestions
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error starting container workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting container troubleshooting workflow: {str(e)}")


@router.post("/messages", response_model=EnhancedChatResponse)
async def create_message(
    message: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Create a new chat message and get an AI response.
    Uses WebSockets for real-time updates and message streaming.

    Args:
        message: The message to create
        background_tasks: Background tasks runner
        db: Database session
        user_id: User ID (optional)

    Returns:
        AI response
    """
    # Get WebSocket manager
    websocket_manager = get_websocket_manager()

    # Get or create chat session
    session_id = message.session_id
    if session_id is None:
        # Create a new session
        db_session = ChatSession(
            user_id=user_id,
            title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            is_active=True
        )
        db.add(db_session)
        db.flush()
        session_id = db_session.id
    else:
        # Verify session exists
        db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not db_session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        # Update session timestamp
        db_session.updated_at = datetime.utcnow()

    # Create user message
    user_message = ChatMessage(
        user_id=user_id,
        session_id=session_id,
        type="user",
        text=message.text,
        context=message.context.model_dump() if message.context else None
    )
    db.add(user_message)
    db.flush()

    # Broadcast user message to all session subscribers
    user_message_schema = ChatMessageSchema.model_validate(user_message)
    background_tasks.add_task(
        websocket_manager.broadcast_message,
        user_message_schema,
        session_id
    )

    # Extract context data
    context = None
    if message.context:
        context = message.context.model_dump()

    # Get chat handler
    chat_handler = get_chat_handler()

    # Process message and get response
    try:
        # Set typing indicator to true via WebSocket
        if user_id:
            background_tasks.add_task(
                websocket_manager.set_typing_status,
                "ai", True, session_id
            )

        response_text, suggestions = chat_handler.process_message(message.text, context)

        # Create AI response message
        ai_message = ChatMessage(
            user_id=None,  # AI messages don't have a user
            session_id=session_id,
            type="ai",
            text=response_text,
            context=context
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        # Get user preferences
        user_preferences = None
        if user_id is not None:
            user_preferences = user_preference_manager.get_user_preferences(user_id, db)

        # Get command shortcuts
        command_shortcuts = []
        if user_id is not None:
            command_shortcuts = user_preference_manager.get_user_command_shortcuts(user_id, db)

        # Add to conversation memory
        if user_id is not None:
            conversation_memory.add_memory(
                user_id=user_id,
                message_text=ai_message.text,
                session_id=session_id,
                message_id=ai_message.id,
                context=context,
                db_session=db
            )

        # Set typing indicator to false via WebSocket
        if user_id:
            background_tasks.add_task(
                websocket_manager.set_typing_status,
                "ai", False, session_id
            )

        # Stream the response in chunks via WebSocket
        # Split the text into chunks (simulating streaming)
        text_chunks = split_text_into_chunks(response_text)
        background_tasks.add_task(
            websocket_manager.stream_ai_response,
            session_id,
            ai_message.id,
            text_chunks
        )

        # Broadcast AI message to all session subscribers
        ai_message_schema = ChatMessageSchema.model_validate(ai_message)
        background_tasks.add_task(
            websocket_manager.broadcast_message,
            ai_message_schema,
            session_id
        )

        # Prepare enhanced response
        return EnhancedChatResponse(
            message=ai_message_schema,
            session_id=session_id,
            suggestions=suggestions,
            feedback_id=None,  # No feedback yet
            command_shortcuts=command_shortcuts if command_shortcuts else None,
            user_preferences=user_preferences if user_preferences else None
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing chat message: {str(e)}")

        # Set typing indicator to false via WebSocket
        if user_id:
            background_tasks.add_task(
                websocket_manager.set_typing_status,
                "ai", False, session_id
            )

        # Create error message
        error_message = ChatMessage(
            user_id=None,
            session_id=session_id,
            type="system",
            text=f"I'm sorry, I encountered an error while processing your message. Please try again.",
            context=context
        )
        db.add(error_message)
        db.commit()

        # Broadcast error message to all session subscribers
        error_message_schema = ChatMessageSchema.model_validate(error_message)
        background_tasks.add_task(
            websocket_manager.broadcast_message,
            error_message_schema,
            session_id
        )

        # Return error response
        return EnhancedChatResponse(
            message=ChatMessageSchema.model_validate(error_message),
            session_id=session_id,
            suggestions=["Try a simpler question", "Ask about Docker basics", "Report this issue"],
            feedback_id=None,
            command_shortcuts=None,
            user_preferences=None
        )


def split_text_into_chunks(text: str, chunk_size: int = 50) -> List[str]:
    """
    Split text into chunks for streaming.

    Args:
        text: The text to split
        chunk_size: The maximum size of each chunk

    Returns:
        List of text chunks
    """
    # If the text is short enough, just return it as a single chunk
    if len(text) <= chunk_size:
        return [text]

    # Split text into sentences
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence would make the chunk too large, start a new chunk
        if len(current_chunk) + len(sentence) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
        else:
            current_chunk += sentence + " "

    # Add the last chunk if there's anything left
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


@router.get("/messages", response_model=MessagesList)
async def get_messages(
    session_id: int = Query(..., description="Chat session ID"),
    limit: int = Query(50, description="Maximum number of messages to return"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get chat messages for a session.

    Args:
        session_id: Chat session ID
        limit: Maximum number of messages to return
        offset: Offset for pagination
        db: Database session
        user_id: User ID (optional)

    Returns:
        List of chat messages
    """
    # Verify session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Get messages
    query = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.desc())

    total = query.count()
    messages = query.offset(offset).limit(limit).all()

    return MessagesList(
        messages=[ChatMessageSchema.model_validate(msg) for msg in messages],
        total=total
    )


@router.get("/sessions", response_model=SessionsList)
async def get_sessions(
    limit: int = Query(10, description="Maximum number of sessions to return"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get chat sessions for a user.

    Args:
        limit: Maximum number of sessions to return
        offset: Offset for pagination
        db: Database session
        user_id: User ID (optional)

    Returns:
        List of chat sessions
    """
    # Base query
    query = db.query(ChatSession).order_by(ChatSession.updated_at.desc())

    # Filter by user if provided
    if user_id is not None:
        query = query.filter(ChatSession.user_id == user_id)

    total = query.count()
    sessions = query.offset(offset).limit(limit).all()

    return SessionsList(
        sessions=[ChatSessionSchema.model_validate(session) for session in sessions],
        total=total
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
async def get_session(
    session_id: int = Path(..., description="Chat session ID"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get a specific chat session.

    Args:
        session_id: Chat session ID
        db: Database session
        user_id: User ID (optional)

    Returns:
        Chat session
    """
    # Get session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Get messages for session
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    # Create session schema
    session_schema = ChatSessionSchema.model_validate(session)
    session_schema.messages = [ChatMessageSchema.model_validate(msg) for msg in messages]

    return session_schema


@router.post("/sessions", response_model=ChatSessionSchema)
async def create_session(
    session: ChatSessionCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Create a new chat session.

    Args:
        session: Session creation data
        db: Database session
        user_id: User ID (optional)

    Returns:
        Created chat session
    """
    # Create session
    db_session = ChatSession(
        user_id=user_id,
        title=session.title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        is_active=session.is_active
    )
    db.add(db_session)
    db.flush()  # Flush to get the session ID

    # Create welcome message
    welcome_message = ChatMessage(
        user_id=None,
        session_id=db_session.id,  # Now we have the session ID
        type="ai",
        text="Hello! I'm your DockerForge AI assistant. How can I help you with your Docker containers today?",
        context=None
    )
    db.add(welcome_message)

    # Commit changes
    db.commit()
    db.refresh(db_session)

    # Return session with welcome message
    session_schema = ChatSessionSchema.model_validate(db_session)
    session_schema.messages = [ChatMessageSchema.model_validate(welcome_message)]

    return session_schema


@router.put("/sessions/{session_id}", response_model=ChatSessionSchema)
async def update_session(
    session_id: int,
    session_update: ChatSessionUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Update a chat session.

    Args:
        session_id: Session ID
        session_update: Session update data
        db: Database session
        user_id: User ID (optional)

    Returns:
        Updated chat session
    """
    # Get session
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Update fields
    if session_update.title is not None:
        db_session.title = session_update.title

    if session_update.is_active is not None:
        db_session.is_active = session_update.is_active

    # Update timestamp
    db_session.updated_at = datetime.utcnow()

    # Commit changes
    db.commit()
    db.refresh(db_session)

    # Get messages for session
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.timestamp.asc()).all()

    # Create session schema
    session_schema = ChatSessionSchema.model_validate(db_session)
    session_schema.messages = [ChatMessageSchema.model_validate(msg) for msg in messages]

    return session_schema


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Delete a chat session.

    Args:
        session_id: Session ID
        db: Database session
        user_id: User ID (optional)

    Returns:
        Success message
    """
    # Get session
    db_session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Delete session (will cascade delete messages)
    db.delete(db_session)
    db.commit()

    return {"success": True, "message": "Chat session deleted"}


# --- Feedback endpoints ---

@router.post("/feedback", response_model=ChatFeedbackSchema)
async def create_feedback(
    feedback: ChatFeedbackCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Create feedback for a message.

    Args:
        feedback: Feedback data
        db: Database session
        user_id: User ID (optional)

    Returns:
        Created feedback
    """
    # Validate message exists
    message = db.query(ChatMessage).filter(ChatMessage.id == feedback.message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Process feedback and update user preferences
    result = user_preference_manager.process_message_feedback(
        user_id=user_id,
        message_id=feedback.message_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        db_session=db
    )

    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Error processing feedback"))

    # Get the created feedback
    db_feedback = db.query(ChatFeedback).filter(ChatFeedback.id == result["feedback_id"]).first()

    return ChatFeedbackSchema.model_validate(db_feedback)


@router.get("/feedback/{message_id}", response_model=ChatFeedbackSchema)
async def get_feedback(
    message_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get feedback for a message.

    Args:
        message_id: Message ID
        db: Database session
        user_id: User ID (optional)

    Returns:
        Feedback for the message
    """
    # Get feedback for message
    feedback = db.query(ChatFeedback).filter(
        ChatFeedback.message_id == message_id
    ).first()

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return ChatFeedbackSchema.model_validate(feedback)


# --- User preferences endpoints ---

@router.get("/preferences", response_model=UserPreferenceSchema)
async def get_preferences(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get preferences for the current user.

    Args:
        db: Database session
        user_id: User ID (optional)

    Returns:
        User preferences
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Get preferences using the manager
    preferences = user_preference_manager.get_user_preferences(user_id, db)

    # Format response using Pydantic model
    return UserPreferenceSchema(
        id=preferences.get("id", 0),
        user_id=preferences.get("user_id", user_id),
        response_style=preferences.get("response_style", "balanced"),
        auto_suggestions=preferences.get("auto_suggestions", True),
        preferred_topics=preferences.get("preferred_topics", []),
        avoided_topics=preferences.get("avoided_topics", []),
        feedback_preferences=preferences.get("feedback_preferences", {}),
        created_at=datetime.fromisoformat(preferences.get("created_at", datetime.utcnow().isoformat())),
        updated_at=datetime.fromisoformat(preferences.get("updated_at", datetime.utcnow().isoformat()))
    )


@router.put("/preferences", response_model=UserPreferenceSchema)
async def update_preferences(
    preferences: UserPreferenceUpdate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Update preferences for the current user.

    Args:
        preferences: Preferences data to update
        db: Database session
        user_id: User ID (optional)

    Returns:
        Updated user preferences
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Update preferences using the manager
    result = user_preference_manager.update_user_preferences(
        user_id=user_id,
        preferences_data=preferences.model_dump(exclude_unset=True),
        db_session=db
    )

    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Error updating preferences"))

    # Return updated preferences
    updated = result["preferences"]

    # Format response using Pydantic model
    return UserPreferenceSchema(
        id=updated.get("id", 0),
        user_id=updated.get("user_id", user_id),
        response_style=updated.get("response_style", "balanced"),
        auto_suggestions=updated.get("auto_suggestions", True),
        preferred_topics=updated.get("preferred_topics", []),
        avoided_topics=updated.get("avoided_topics", []),
        feedback_preferences=updated.get("feedback_preferences", {}),
        created_at=datetime.fromisoformat(updated.get("created_at", datetime.utcnow().isoformat())),
        updated_at=datetime.fromisoformat(updated.get("updated_at", datetime.utcnow().isoformat()))
    )


# --- Command shortcuts endpoints ---

@router.get("/shortcuts", response_model=CommandShortcutsList)
async def get_shortcuts(
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get command shortcuts for the current user.

    Args:
        db: Database session
        user_id: User ID (optional)

    Returns:
        List of command shortcuts
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Get shortcuts using the manager
    shortcuts = user_preference_manager.get_user_command_shortcuts(user_id, db)

    # Format response
    return CommandShortcutsList(
        shortcuts=[ChatCommandShortcutSchema(
            id=shortcut.get("id"),
            user_id=shortcut.get("user_id"),
            command=shortcut.get("command"),
            description=shortcut.get("description"),
            template=shortcut.get("template"),
            usage_count=shortcut.get("usage_count"),
            created_at=datetime.fromisoformat(shortcut.get("created_at")),
            updated_at=datetime.fromisoformat(shortcut.get("updated_at"))
        ) for shortcut in shortcuts],
        total=len(shortcuts)
    )


@router.post("/shortcuts", response_model=ChatCommandShortcutSchema)
async def create_shortcut(
    shortcut: ChatCommandShortcutCreate,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Create a new command shortcut.

    Args:
        shortcut: Shortcut data
        db: Database session
        user_id: User ID (optional)

    Returns:
        Created command shortcut
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Create shortcut using the manager
    result = user_preference_manager.create_command_shortcut(
        user_id=user_id,
        command=shortcut.command,
        description=shortcut.description,
        template=shortcut.template,
        db_session=db
    )

    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Error creating shortcut"))

    # Return created shortcut
    created = result["shortcut"]

    # Format response using Pydantic model
    return ChatCommandShortcutSchema(
        id=created.get("id"),
        user_id=created.get("user_id"),
        command=created.get("command"),
        description=created.get("description"),
        template=created.get("template"),
        usage_count=created.get("usage_count"),
        created_at=datetime.fromisoformat(created.get("created_at")),
        updated_at=datetime.fromisoformat(created.get("updated_at"))
    )


@router.delete("/shortcuts/{shortcut_id}", response_model=dict)
async def delete_shortcut(
    shortcut_id: int,
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Delete a command shortcut.

    Args:
        shortcut_id: Shortcut ID
        db: Database session
        user_id: User ID (optional)

    Returns:
        Success message
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Delete shortcut using the manager
    result = user_preference_manager.delete_command_shortcut(
        user_id=user_id,
        shortcut_id=shortcut_id,
        db_session=db
    )

    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Shortcut not found"))

    return {"success": True, "message": result.get("message", "Shortcut deleted")}


@router.post("/shortcuts/use", response_model=dict)
async def use_shortcut(
    command: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Use a command shortcut and get its template.

    Args:
        command: Command string (e.g., "/logs")
        db: Database session
        user_id: User ID (optional)

    Returns:
        Shortcut template and usage information
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Use shortcut using the manager
    result = user_preference_manager.use_command_shortcut(
        user_id=user_id,
        command=command,
        db_session=db
    )

    if not result.get("success", False):
        raise HTTPException(status_code=404, detail=result.get("error", "Command not found"))

    return {
        "success": True,
        "shortcut": result.get("shortcut", {})
    }


@router.get("/memory", response_model=List[Dict[str, Any]])
async def get_relevant_memories(
    query: str = Query(..., description="Query text to find relevant memories"),
    context: Optional[str] = Query(None, description="Context data as JSON string"),
    limit: int = Query(5, description="Maximum number of memories to return"),
    db: Session = Depends(get_db),
    user_id: Optional[int] = None  # In a real app, this would come from token auth
):
    """
    Get relevant memories for a query.

    Args:
        query: Query text
        context: Optional context data as JSON string
        limit: Maximum number of memories to return
        db: Database session
        user_id: User ID (optional)

    Returns:
        List of relevant memories
    """
    # For demo purposes, use a default user ID if none provided
    if user_id is None:
        user_id = 1

    # Parse context if provided
    context_data = None
    if context:
        try:
            import json
            context_data = json.loads(context)
        except Exception as e:
            logger.warning(f"Error parsing context data: {str(e)}")

    # Get relevant memories
    memories = conversation_memory.get_relevant_memories(
        user_id=user_id,
        query_text=query,
        context=context_data,
        limit=limit,
        db_session=db
    )

    return memories
